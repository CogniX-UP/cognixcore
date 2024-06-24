cognixcore.addons
=================

.. py:module:: cognixcore.addons

.. autoapi-nested-parse::

   Defines an add-on system to extend congixcore's functionalities.
   The :class:`cognixcore.addons.variables.VarsAddon` and :class:`cognixcore.addons.logging.LoggingAddon`
   addons are built-in. Additional add-ons can be implemented and registered in the :class:`cognixcore.session.Session`.

   An add-on
       - has a unique name and a version
       - is session-local, not flow-local but can implement per-Flow functionality
       - manages its own state (in particular :code:`get_state()` and :code:`set_state()`)
       - can store additional node-specific data in the node's :code:`data` dict when it's serialized
       - will be accessible through the nodes API: :code:`self.get_addon('your_addon')` in your nodes

   Add-on access is blocked during loading (deserialization), so nodes should not access any
   add-ons during the execution of :code:`Node.__init__` or :code:`Node.set_data`.
   This prevents inconsistent states. Nodes are loaded first, then the add-ons.
   Therefore, the add-on should be sufficiently isolated and self-contained.

   To define a custom add-on:
       - create a class :code:`YourAddon(cognixcore.addons.base.AddOn)` that defines your add-on's functionality
       - register your addon directory in the Session: :code:`session.register_addon_dir(YourAddon | YourAddon())`



Subpackages
-----------

.. toctree::
   :maxdepth: 1

   /autoapi/cognixcore/addons/variables/index


Submodules
----------

.. toctree::
   :maxdepth: 1

   /autoapi/cognixcore/addons/builtin/index
   /autoapi/cognixcore/addons/logging/index


Attributes
----------

.. autoapisummary::

   cognixcore.addons.AddonType


Classes
-------

.. autoapisummary::

   cognixcore.addons.AddOn


Package Contents
----------------

.. py:class:: AddOn

   Bases: :py:obj:`cognixcore.base.Base`


   Base class for all abstract components. It provides:

   Functionality for ID counting:
       - an automatic :code:`GLOBAL_ID` unique during the lifetime of the program
       - a :code:`PREV_GLOBAL_ID` for re-identification after save & load,
         automatically set in :code:`load()`

   Serialization:
       - the :code:`data()` method gets reimplemented by subclasses to serialize
       - the :code:`load()` method gets reimplemented by subclasses to deserialize
       - the static attribute :code:`Base.complete_data_function` can be set to
         a function which extends the serialization process by supplementing the
         data dict with additional information, which is useful in many
         contexts, e.g. a frontend does not need to implement separate save & load
         functions for its GUI components


   .. py:attribute:: version
      :value: ''



   .. py:method:: addon_name()
      :classmethod:



   .. py:method:: register(session: cognixcore.session.Session)

      Called when the add-on is registered to a session.



   .. py:method:: unregister()

      Called when the add-on is unregistered from a session.



   .. py:method:: connect_flow_events(flow: cognixcore.flow.Flow)

      Connects flow events to the add-on. There are events for
      when a node is created, added, removed or created from data.



   .. py:method:: disconnect_flow_events(flow: cognixcore.flow.Flow)

      Disconnects flow events to the add-on



   .. py:method:: on_loaded()

      *VIRTUAL*

      Called when an addon is loaded from data. This is invoked
      after the flows and nodes have been loaded.



   .. py:method:: on_flow_created(flow: cognixcore.flow.Flow)

      *VIRTUAL*

      Called when a flow is created.



   .. py:method:: on_flow_destroyed(flow: cognixcore.flow.Flow)

      *VIRTUAL*

      Called when a flow is destroyed.



   .. py:method:: on_flow_renamed(flow: cognixcore.flow.Flow)

      *VIRTUAL*

      Called when a flow is renamed



   .. py:method:: on_node_created(node: cognixcore.node.Node)

      *VIRTUAL*

      Called when a node is created and fully initialized
      (:code:`Node.load()` has already been called, if necessary),
      but not yet added to the flow. Therefore, this is a good place
      to initialize the node with add-on-specific data.

      This happens only once per node, whereas it can be added and
      removed multiple times, see :code:`AddOn.on_node_added()` and
      :code:`AddOn.on_node_removed()`.



   .. py:method:: on_nodes_loaded(nodes: collections.abc.Sequence[cognixcore.node.Node])

      *VIRTUAL*

      Called when a node is loaded and fully initialized
      from data. The node has been added to the flow, however
      the :code:`Node.place_event()` has not been called yet.



   .. py:method:: on_node_added(node: cognixcore.node.Node)

      *VIRTUAL*

      Called when a node is added to a flow.



   .. py:method:: on_node_removed(node: cognixcore.node.Node)

      *VIRTUAL*

      Called when a node is removed from a flow.



   .. py:method:: extend_node_data(node: cognixcore.node.Node, data: dict)

      *VIRTUAL*

      Invoked whenever any node is serialized. This method can be
      used to extend the node's data dict with additional
      add-on.related data.



   .. py:method:: get_state() -> dict

      *VIRTUAL*

      Return the state of the add-on as JSON-compatible a dict.
      This dict will be extended by :code:`AddOn.complete_data()`.



   .. py:method:: set_state(state: dict, version: str)

      *VIRTUAL*

      Set the state of the add-on from the dict generated in
      :code:`AddOn.get_state()`. Addons are loaded after the
      Flows.



   .. py:method:: data() -> dict

      Supplements the data dict with additional data.



   .. py:method:: load(data: dict)

      Loads the data dict generated in :code:`AddOn.data()`.



.. py:data:: AddonType

   A :code:`TypeVar` referencing the :class:`AddOn` type for generic use

