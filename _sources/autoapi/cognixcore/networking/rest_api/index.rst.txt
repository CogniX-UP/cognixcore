cognixcore.networking.rest_api
==============================

.. py:module:: cognixcore.networking.rest_api

.. autoapi-nested-parse::

   This module defines the RESTful API deployed for a :class:`cognixcore.session.Session`.
   The rest of the documentation is automatically generated through FastAPI and is part of
   the documentation package.



Classes
-------

.. autoapisummary::

   cognixcore.networking.rest_api.RestAPI
   cognixcore.networking.rest_api.SessionServer


Module Contents
---------------

.. py:class:: RestAPI(session: cognixcore.session.Session)

   Handles FastAPI app creation


   .. py:attribute:: message
      :value: 'msg'



   .. py:attribute:: error
      :value: 'error'



   .. py:property:: session


   .. py:property:: vars_addon


   .. py:property:: app


   .. py:method:: flow_exists(name: str)


   .. py:method:: var_exists(flow_name: str, name: str)


   .. py:method:: flow_action(flow_name: str, action: str)


   .. py:method:: get_flow(flow_name: str)


   .. py:method:: get_var(flow_name: str, var_name: str)


   .. py:method:: create_routes()


.. py:class:: SessionServer(session: cognixcore.session.Session, api: RestAPI = None)

   This is a class for creating a REST Api to communicate with a CogniX Session.


   .. py:property:: running
      Indicates whether the server is running.

      Due to the asynchronous nature of the server, this value might
      not always be synchronized.


   .. py:property:: port


   .. py:method:: run(host: str | None = None, port: int | None = None, on_other_thread: bool = False, wait_time_if_thread=0, bypass_uvicorn_log=False)


   .. py:method:: shutdown()

      Shutdowns the RESTful API server, if it was started previously.



