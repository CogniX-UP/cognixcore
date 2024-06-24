from .base import Base, Event, IdentifiableGroups
from .flow import Flow
from .info_msgs import InfoMsgs
from .utils import pkg_version, pkg_path, print_err, get_mod_classes
from .node import Node
from .addons._base import AddOn, AddonType
from .addons.builtin import VarsAddon, LoggingAddon
from .flow_player import (
    GraphPlayer,
    GraphState,
    GraphActionResponse,
    FlowPlayer
)
from .networking.rest_api import SessionServer

from concurrent.futures import ThreadPoolExecutor, Future
from typing import Callable
from importlib import import_module
from types import MappingProxyType
from collections.abc import Iterable, Mapping
from logging import Logger

class Session(Base):
    """
    The Session is the top level interface to your project. It mainly manages flows, nodes, and add-ons and
    provides methods for serialization and deserialization of the project.
    """

    version = pkg_version()
    
    _flow_base_type = Flow
    """
    Forces the Session to accept a specific type of base Flow.
    """
    
    def __init__(
            self,
            gui: bool = False,
            load_optional_addons: bool = False,
    ):
        Base.__init__(self)

        # events
        self.flow_created = Event[Flow]()
        self.flow_renamed = Event[Flow, str]()
        self.flow_deleted = Event[Flow]()
        
        # ATTRIBUTES
        self._addons: dict[str, AddOn] = {}
        self._addons_proxy = MappingProxyType(self._addons)
        self._addons_by_type: dict[type, AddOn] = {}
         
        self._flows: dict[str, Flow] = {}
        self._flows_proxy = MappingProxyType(self._flows)
        
        self.invis_node_types: set[type[Node]] = set()
        
        self.gui: bool = gui
        self.init_data = None

        # node group
        self._node_type_groups = IdentifiableGroups[type[Node]]()
        
        # Load Variables and Logging Addons
        self.register_addon(VarsAddon)
        self.register_addon(LoggingAddon)
        
        # Load optional built-in addons
        if load_optional_addons:
            from .addons.builtin import built_in_addons
            for addon_type in built_in_addons:
                self.register_addon(addon_type)
        
        # players
        self._graphs_playing: set[GraphPlayer] = set()
        self._graph_executor = ThreadPoolExecutor()
        self._flow_to_future: dict[str, Future] = {}
        self._rest_api = SessionServer(self)
    
    @property
    def vars_addon(self) -> VarsAddon:
        return self.addon(VarsAddon)
    
    @property
    def logg_addon(self) -> LoggingAddon:
        return self.addon(LoggingAddon)
    
    @property
    def logger(self) -> Logger:
        return self.addon(LoggingAddon).root_looger
    
    @property
    def node_types(self) -> set[type[Node]]:
        return self._node_type_groups.infos
    
    @property
    def addons(self) -> Mapping[str, AddOn]:
        return self._addons_proxy
    
    @property
    def flows(self) -> Mapping[str, Flow]:
        return self._flows_proxy
    
    @property
    def node_groups(self) -> IdentifiableGroups[type[Node]]:
        """The identifiables of Node types groupped by their id prefix. If it doesn't exist, the key is global"""
        return self._node_type_groups

    @property
    def rest_api(self) -> SessionServer:
        return self._rest_api
    
    def graph_player(self, title: str) -> GraphPlayer | None:
        """A proxy to the graph players dictionary contained in the session"""
        flow: Flow = self._flows.get(title)
        return flow.player if flow else None
    
    # TODO: Think of an importing solution for external addons
    # def load_addons(self, location: str | None = None):
    #     """Loads all addons found in every module inside the given directory"""
        
    #     pkg_loc = location if location else pkg_path('addons/')
    #     addons = filter(lambda p: not p.endswith('__init__.py'), glob.glob(pkg_loc + '/*.py'))
        
    #     for path in addons:
    #         mod_name = basename(path).removesuffix('.py')
    #         self.import_mod_addons(mod_name)

    def import_mod_addons(self, mod_name: str, package_name: str | None = None):
        """Imports all addons found in a specific module using importlib import_module"""
        
        try:
            addon_mod = import_module(mod_name, package_name)
        except Exception as e:
            InfoMsgs.write(str(e))
            return
        
        def addon_class_filter(obj):
            return issubclass(obj, AddOn) and obj.__class__ != AddOn
        
        mod_addons: list[type[AddOn]] = get_mod_classes(addon_mod, filter=addon_class_filter)
        for addon_type in mod_addons:
            addon_name = addon_type.addon_name()
            if addon_name in self._addons:
                InfoMsgs.write(f"Addon with name {addon_name} has already been registered!")
                continue
            
            addon = addon_type()
            self.register_addon(addon)
        
    def addon(self, t: type[AddonType] | str) -> AddonType:
        if isinstance(t, str):
            return self._addons[t]
        else:
            return self._addons_by_type[t]
      
    def register_addon(self, addon: AddOn | type[AddOn]):
        """Registers an addon"""
        
        addon_name = addon.addon_name()
        if addon.addon_name() in self._addons:
            return
        if not isinstance(addon, AddOn):
            addon = addon()
        
        self._addons[addon_name] = addon
        self._addons_by_type[type(addon)] = addon
        addon.register(self)
    
    def unregister_addon(self, addon: str | AddOn):
        """Unregisters an addon"""
        addon_name = addon if isinstance(addon, str) else addon.addon_name()
        if addon_name in self._addons:
            to_remove = self._addons[addon_name]
            to_remove.unregister()
            
            del self._addons[addon_name]
            del self._addons_by_type[type(to_remove)]


    def register_node_types(self, node_types: Iterable[type[Node]]):
        """
        Registers a list of Nodes which then become available in the flows.
        Do not attempt to place nodes in flows that haven't been registered in the session before.
        """

        for n in node_types:
            self.register_node_type(n)


    def register_node_type(self, node_class: type[Node]):
        """
        Registers a single node.
        """
        node_class.build_identifiable() # if it was modified externally
        self._node_type_groups.add(node_class.identifiable())


    def unregister_node_type(self, node_class: type[Node]):
        """
        Unregisters a node which will then be removed from the available list.
        Existing instances won't be affected.
        """

        self._node_type_groups.remove(node_class.identifiable())
     
                
    def all_node_objects(self) -> list[Node]:
        """
        Returns a list of all node objects instantiated in any flow.
        """

        return [n for f in self._flows.values() for n in f.nodes]
        
        
    def create_flow(
        self, 
        title: str = None, 
        data: dict = None,
        player_type: type[GraphPlayer] = None,
        frames = 30
    ) -> Flow | None:
        """
        Creates and returns a new flow.
        If data is provided the title parameter will be ignored.
        """

        flow = self._flow_base_type(session=self, title=title)
        player = player_type(flow, frames) if player_type else FlowPlayer(frames)
        if data:
            flow.load(data)
        
        flow.player = player
        player.flow = flow
        
        # Titles should be unique
        if not self.new_flow_title_valid(flow.title):
            return None
        
        self._flows[flow.title] = flow
        
        self.flow_created.emit(flow)

        return flow


    def rename_flow(self, flow: Flow, title: str) -> bool:
        """
        Renames an existing flow and returns success boolean.
        """

        success = False

        if self.new_flow_title_valid(title):
            del self._flows[flow.title]
            old_title = flow.title
            flow.title = title
            self._flows[title] = flow
            success = True
            self.flow_renamed.emit(flow, title)
            flow.renamed.emit(old_title, title)
            
        return success


    def new_flow_title_valid(self, title: str) -> bool:
        """
        Checks whether a considered title for a new flow is valid (unique) or not.
        """

        return len(title) != 0 and title not in self._flows


    def delete_flow(self, flow: Flow):
        """
        Deletes an existing flow.
        """
        
        if flow.title not in self._flows or flow != self._flows[flow.title]:
            return False
        
        del self._flows[flow.title]
        self.flow_deleted.emit(flow)
        return True

    # Player Evaluation
    
    def play_flow(self, flow_name: str, on_other_thread=False, callback: Callable[[GraphActionResponse, str], None] = None):
        """Plays the flow through the graph player"""
        
        graph_player = self.graph_player(flow_name)
        if not graph_player:
            callback(GraphActionResponse.NO_GRAPH, f"No flow associated with name {flow_name}")
            return
        
        if graph_player in self._graphs_playing or graph_player.state == GraphState.PLAYING:
            callback(GraphActionResponse.NOT_ALLOWED, f"Flow {flow_name} is currently playing")
            return
        
        if graph_player.state == GraphState.PAUSED:
            callback(GraphActionResponse.NOT_ALLOWED, f"Flow {flow_name} is paused")
            return
        
        # To avoid any race conditions because we may start the flow in another thread
        self._graphs_playing.add(graph_player)
        if callback:
            graph_player.graph_events.sub_event(
                GraphState.PLAYING,
                lambda: callback(GraphActionResponse.SUCCESS, f"Flow {flow_name} is playing!"),
                one_off=True
            )
        
        if not on_other_thread:
            self.__play_flow(flow_name, graph_player)
        else:
            play_task = self._graph_executor.submit(self.__play_flow, flow_name, graph_player)
            self._flow_to_future[flow_name] = play_task
            
    
    def __play_flow(self, flow_name: str, graph_player: GraphPlayer):
        if graph_player not in self._graphs_playing:
            self._graphs_playing.add(graph_player)
        try:
            graph_player.play()
        except Exception as e:
            raise e
        finally:
            self._graphs_playing.remove(graph_player)
            # handles the case where we have threads
            if flow_name in self._flow_to_future:
                del self._flow_to_future[flow_name]
     
    def pause_flow(self, flow_name: str, callback: Callable[[GraphActionResponse, str], None] = None):
        """Pauses the graph player"""
        
        graph = self.graph_player(flow_name)
        if not graph and callback:
            callback(GraphActionResponse.NO_GRAPH, f"No flow associated with name {flow_name}")
            return
        
        if graph.state == GraphState.PAUSED and callback:
            callback(GraphActionResponse.NOT_ALLOWED, f"Flow {flow_name} already paused")
            return
        
        if graph.state == GraphState.STOPPED and callback:
            callback(GraphActionResponse.NOT_ALLOWED, f"Flow {flow_name} isn't playing")
            return
        
        if callback:
            graph.graph_events.sub_event(
                GraphState.PAUSED, 
                lambda: callback(GraphActionResponse.SUCCESS, f"Flow {flow_name} has paused"),
                one_off=True
            )
        
        graph.pause()
    
    def resume_flow(self, flow_name: str, callback: Callable[[GraphActionResponse, str], None] = None):
        
        graph = self.graph_player(flow_name)
        if not graph and callback:
            callback(GraphActionResponse.NO_GRAPH, f"No flow associated with name {flow_name}")
            return

        if graph.state != GraphState.PAUSED and callable:
            callback(GraphActionResponse.NO_GRAPH, f"Flow {flow_name} is not paused")
            return

        if callback:
            graph.graph_events.sub_event(
                GraphState.PLAYING,
                lambda: callback(GraphActionResponse.SUCCESS, f"Flow {flow_name} resumted"),
                one_off=True
            )
        
        graph.resume()
    
    def stop_flow(self, flow_name: str, callback: Callable[[GraphActionResponse, str], None] = None):
        """Stops the graph player"""
        
        graph = self.graph_player(flow_name)
        if not graph:
            if callback:
                callback(GraphActionResponse.NO_GRAPH, f"No flow associated with name {flow_name}")
            return
        
        if graph.state != GraphState.PLAYING and callback:
            callback(GraphActionResponse.NOT_ALLOWED, f"Flow {flow_name} is not playing!")
            return
        
        if callback:
            graph.graph_events.sub_event(
                GraphState.STOPPED,
                lambda: callback(GraphActionResponse.SUCCESS, f"Flow {flow_name} has stopped"),
                one_off=True
            )
            
        graph.stop()
    
    def shutdown(self):
        
        # shut down any players
        for flow_title in self.flows.keys():
            self.stop_flow(flow_title)
        
        self._graph_executor.shutdown()
        
        # shut down the rest api
        self.rest_api.shutdown()
        
               
    def _info_messenger(self):
        """
        Returns a reference to InfoMsgs to print info data.
        """

        return InfoMsgs


    def load(self, data: dict) -> list[Flow]:
        """
        Loads a project and raises an exception if required nodes are missing
        (not registered).
        """

        super().load(data)

        self.init_data = data

        # load flows
        new_flows = []
        flows_data = data['flows']

        for title, flow_data in flows_data.items():
            new_flows.append(self.create_flow(title=title, data=flow_data))

        # load addons
        for name, addon_data in data['addons'].items():
            if name in self._addons:
                self._addons[name].load(addon_data)
            else:
                print(f'found missing addon: {name}; attempting to load anyway')
                
        return new_flows

    def serialize(self) -> dict:
        """
        Returns the project as JSON compatible dict to be saved and
        loaded again using load()
        """

        return self.complete_data(self.data())


    def data(self) -> dict:
        """
        Serializes the project's abstract state into a JSON compatible
        dict. Pass to :code:`load()` in a new session to restore.
        Don't use this function for saving, use :code:`serialize()` in
        order to include the effects of :code:`Base.complete_data()`.
        """

        return {
            **super().data(),
            'flows': {
                f.title: f.data()
                for f in self._flows.values()
            },
            'addons': {
                name: addon.data() for name, addon in self._addons.items()
            }
        }
        
