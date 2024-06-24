cognixcore.addons.logging
=========================

.. py:module:: cognixcore.addons.logging


Classes
-------

.. autoapisummary::

   cognixcore.addons.logging.LoggingAddon


Module Contents
---------------

.. py:class:: LoggingAddon

   Bases: :py:obj:`cognixcore.addons._base.AddOn`


   This addon implements :class:`cognixcore.flow.Flow` and :class:`cognixcore.node.Node` logging functionality.

   It provides functions to create and delete loggers that are owned
   by a particular node. The loggers get enabled/disabled
   automatically when the owning node is added to/removed from
   the flow.

   The contents of logs are currently not preserved. If a log's
   content should be preserved, it should be saved explicitly.

   Refer to Python's logging module documentation.


   .. py:attribute:: version
      :value: '1.0'



   .. py:attribute:: root_logger_name
      :value: 'session'



   .. py:property:: log_level
      :type: int

      The log level assigned to a logger at creation. Refer to python's logging module.


   .. py:property:: root_looger
      :type: logging.Logger

      The top-level logger associated with the Logging Addon.


   .. py:property:: loggers
      :type: collections.abc.Mapping[cognixcore.flow.Flow | cognixcore.node.Node, logging.Logger]

      A map from a Flow or Node to their respective loggers


   .. py:method:: on_flow_created(flow: cognixcore.flow.Flow)

      *VIRTUAL*

      Called when a flow is created.



   .. py:method:: on_flow_destroyed(flow: cognixcore.flow.Flow)

      *VIRTUAL*

      Called when a flow is destroyed.



   .. py:method:: on_node_created(node: cognixcore.node.Node)

      *VIRTUAL*

      Called when a node is created and fully initialized
      (:code:`Node.load()` has already been called, if necessary),
      but not yet added to the flow. Therefore, this is a good place
      to initialize the node with add-on-specific data.

      This happens only once per node, whereas it can be added and
      removed multiple times, see :code:`AddOn.on_node_added()` and
      :code:`AddOn.on_node_removed()`.



   .. py:method:: on_nodes_loaded(nodes: Sequence[cognixcore.node.Node])

      *VIRTUAL*

      Called when a node is loaded and fully initialized
      from data. The node has been added to the flow, however
      the :code:`Node.place_event()` has not been called yet.



   .. py:method:: on_node_added(node: cognixcore.node.Node)

      *VIRTUAL*

      Called when a node is added to a flow.



   .. py:method:: on_node_removed(node)

      *VIRTUAL*

      Called when a node is removed from a flow.



   .. py:method:: on_loaded()

      *VIRTUAL*

      Called when an addon is loaded from data. This is invoked
      after the flows and nodes have been loaded.



