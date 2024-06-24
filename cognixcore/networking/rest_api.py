"""
This module defines the RESTful API deployed for a :class:`cognixcore.session.Session`.
The rest of the documentation is automatically generated through FastAPI and is part of
the documentation package.
"""

from __future__ import annotations
from json import dumps, loads

from threading import Thread, Event
from ..addons.variables import VarsAddon
from fastapi import HTTPException # FastAPI is wrapped form FastAPIOffline
from fastapi_offline import FastAPIOffline # replaces FastAPI for offline access to docs
from uvicorn import Server, Config
from http import HTTPStatus
from time import sleep

from ..flow_player import GraphState, GraphActionResponse
from ..models import FlowModel, VarModel


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..session import Session

class RestAPI:
    """Handles FastAPI app creation"""
    
    message = 'msg'
    error = 'error'
    
    def __init__(self, session: Session):
        self._session = session
        self._vars_addon: VarsAddon = self.session.addon(VarsAddon)
        self._app = FastAPIOffline()
    
    @property
    def session(self):
        return self._session
    
    @property
    def vars_addon(self):
        return self._vars_addon
    
    @property
    def app(self):
        return self._app
    
    def flow_exists(self, name: str):
        return not self.session.new_flow_title_valid(name)
    
    def var_exists(self, flow_name: str, name: str):
        flow = self.session.flows[flow_name]
        return self.vars_addon.var_exists(flow, name)
    
    def flow_action(self, flow_name: str, action: str):
            _ = self.get_flow(flow_name)
            
            # pass by reference
            result = {
                'response': None,
                'message': None,
                'finished': False
            }
            
            def callback(resp: GraphActionResponse, mess: str):
                print('callback')
                result['response'] = resp
                result['message'] = mess
                result['finished'] = True
            
            try:
                if action == 'play':    
                    self.session.play_flow(flow_name, True, callback)
                elif action == 'stop':
                    self.session.stop_flow(flow_name, callback)
                elif action == 'pause':
                    self.session.pause_flow(flow_name, callback)
                elif action =='resume':
                    self.session.resume_flow(flow_name, callback)
                else:
                    raise HTTPException(
                        HTTPStatus.BAD_REQUEST, 
                        detail=f"Invalid flow action <{action}>. Available actions: [play, pause, resume, stop]"
                    )
            except Exception as e:
                raise HTTPException(HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"An exception was called when trying to {action} the flow.\n{e}")
            
            while not result['finished']:
                continue
            
            response: GraphActionResponse = result['response']
            message: str = result['message']
            
            if response != GraphActionResponse.SUCCESS:
                raise HTTPException(HTTPStatus.BAD_REQUEST, detail=f"Error Message: {message}")
            
            return True
    
    def get_flow(self, flow_name: str):
        if not self.flow_exists(flow_name):
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Flow: <{flow_name}> doesn't exist!")
        return self.session.flows[flow_name]

    def get_var(self, flow_name: str, var_name: str):
        flow = self.get_flow(flow_name)
        var_sub = self.vars_addon.flow_variables[flow].get(var_name)
        if not var_sub:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Variables: <{var_name}> doesn't exist in Flow: <{flow_name}>")
        return var_sub.variable
    
    def create_routes(self):
        
        @self.app.get("/")
        def read_root():
            return {
                self.message: "Welcome to the REST API for your Cognix Session! You can browse the docs via /docs or /redocs"
            }
        
        #   FLOWS
        
        @self.app.get("/session/flows/")
        def get_flows() -> dict[str, FlowModel]:
            """Retrieves all flows from the session"""
            return {
                    flow_name: FlowModel(**flow.data()) 
                    for flow_name, flow in self.session.flows.items()
            }
        
        @self.app.post("/session/flows/{flow_name}/")
        def create_flow(flow_name: str) -> FlowModel:
            """Creates a new flow if it doesn't exist."""
            if self.flow_exists(flow_name):
                raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=f"Flow: <{flow_name}> already exists!")
            
            flow = self.session.create_flow(flow_name)
            return FlowModel(**flow.data())
        
        @self.app.delete("/session/flows/{flow_name}/")
        def delete_flow(flow_name: str) -> str:
            """Deletes a flow if it doesn't exist."""
            flow = self.get_flow(flow_name)
            self.session.delete_flow(flow)
            return f"Flow: <{flow_name}> was deleted!"
        
        @self.app.get("/session/flows/{flow_name}/")
        def get_flow(flow_name: str) -> FlowModel:
            """Retrieves a flow from the session"""
            flow = self.get_flow(flow_name)
            flow_data = flow.data()
            print(flow_data)
            return FlowModel(**flow_data)
        
        @self.app.get("/session/flows/{flow_name}/play/")
        def flow_play(flow_name: str) -> bool:
            """Plays the flow graph."""
            return self.flow_action(flow_name, 'play')
        
        @self.app.get("/session/flows/{flow_name}/pause/")
        def flow_pause(flow_name: str) -> bool:
            """Pauses the flow graph."""
            return self.flow_action(flow_name, 'pause')
        
        @self.app.get("/session/flows/{flow_name}/resume/")
        def flow_resume(flow_name: str) -> bool:
            """Resumes the flow graph."""
            return self.flow_action(flow_name, 'resume')
        
        @self.app.get("/session/flows/{flow_name}/stop/")
        def flow_stop(flow_name: str) -> bool:
            """Stops the flow graph."""
            return self.flow_action(flow_name, 'stop')
        
        #   VARIABLES

        @self.app.get("/session/flows/{flow_name}/vars/")
        def get_vars(flow_name: str) -> dict[str, VarModel]:
            """Retrieves all variables from a specific flow."""
            flow = self.get_flow(flow_name)
            vars = self.vars_addon.flow_variables[flow]
            return {
                name: VarModel(
                    name=name, 
                    value=var_sub.variable.data()
                )
                for name, var_sub in vars.items()
            }
        
        @self.app.get("/session/flows/{flow_name}/vars/{var_name}")
        def get_var(flow_name: str, var_name: str) -> VarModel:
            """Retrieves a variable from a specific flow."""
            var = self.get_var(flow_name, var_name)
            return VarModel(name=var.name, value=var.data())
        
        @self.app.post("/session/flows/{flow_name}/vars/")
        def create_var(flow_name: str, var_model: VarModel) -> VarModel:
            """Creates a new variable"""
            
            flow = self.get_flow(flow_name)
            
            if self.vars_addon.var_exists(flow, var_model.name):
                raise HTTPException(HTTPStatus.BAD_REQUEST, f"Variable <{var_model.name}> already exists!")
            
            self.vars_addon.create_var(flow, var_model.name, load_from=var_model.value)
            return VarModel
        
        @self.app.put("/session/flows/{flow_name}/vars")
        def update_var(flow_name: str, var_model: VarModel) -> VarModel:
            """Updates an existing variable"""
            
            var = self.get_var(flow_name, var_model.name)
            
            if var_model.value_type_id:
                var.set_type(var_model.value_type_id, True)
            
            if var_model.value:
                var.set_type(var_model.value_type_id, load_form=var_model.value)
            
            return var_model
        
class SessionServer:
    """This is a class for creating a REST Api to communicate with a CogniX Session."""
    
    def __init__(self, session: Session, api: RestAPI = None):
        
        self.session = session
        self.api = api if api else RestAPI(session)
        self.api.create_routes()
        
        self.run_task = None
        self._run_thread: Thread = None
        self._server = None
        self._running = False
        self._port = -1

    @property
    def running(self):
        """
        Indicates whether the server is running.
        
        Due to the asynchronous nature of the server, this value might
        not always be synchronized.
        """
        return self._running
    
    @property
    def port(self):
        return self._port
    
    def run(self, 
            host: str | None = None, 
            port: int | None = None,
            on_other_thread: bool = False,
            wait_time_if_thread = 0,
            bypass_uvicorn_log = False
    ):
        if self._running:
            raise RuntimeError('Server already running!!')
        
        if not host:
            host = '127.0.0.1'
        
        if bypass_uvicorn_log:
            config = Config(self.api.app, host=host, port=port, log_config=None)
            config.logger = self.session.logger
        else:
            config = Config(self.api.app, host=host, port=port)
        self._server = Server(config)
        self._port = port
        
        error_event = Event()
        def _run():
            try:    
                self._running = True
                self._server.run()
            except:
                self._running = False
                error_event.set()
                raise
            
        if not on_other_thread:
            _run()
        else:
            self._run_thread = Thread(target=_run)
            self._run_thread.setDaemon(True)
            self._run_thread.start()
            if wait_time_if_thread > 0:
                sleep(wait_time_if_thread)
            if error_event.is_set():
                raise RuntimeError(f"Something went wrong with the REST API. The port {port} is probably taken!")
    
    def shutdown(self):
        """Shutdowns the RESTful API server, if it was started previously."""
        self._port = -1
        self._running = False
        if self._server:
            self._server.should_exit = True