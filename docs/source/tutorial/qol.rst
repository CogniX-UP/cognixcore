Quality of Life
---------------

The above sections include the main functionalities of the :code:`cognixcore` library. In this section, we'll focus on  some QoL utilities that work out of the box with the CogniX Editor.

Loading/saving
^^^^^^^^^^^^^^

The nodes support state saving and loading through the :meth:`cognixcore.Node.load` and :meth:`cognixcore.Node.data` methods. Additionally, there are similar methods that can be found for the :code:`Session` and :code:`Flow`, however these should rarely be overriden.

Progress State
^^^^^^^^^^^^^^

The :class:`cognixcore.ProgressState` is a class that helps with setting the state of a node. In the context of simply scripting, this doesn't do much. However, it exists as an out of the box solution for any kind of GUI library that needs to define ongoing progress for a node. For example, the CogniX Editor automatically utilizes this to set a GUI that reacts to progress changes.

Loggers
^^^^^^^

Each node and flow have a logger through the :mod:`cognixcore.addons.logging` module, based on Python's `logging <https://docs.python.org/3/library/logging.html>`_ module. This can be accessed through their respective properties (:attr:`cognixcore.Node.logger` and :attr:`cognixcore.Flow.logger`).

Variables
^^^^^^^^^

Each node has access to a :class:`cognixcore.addons.variables.VarsAddon` for reading and setting the
state of dynamic variables. Refer to the documentation for further details.

Node Actions
^^^^^^^^^^^^

A node can define actions through the :class:`cognixcore.NodeAction` and the :meth:`cognixcore.Node.add_action` and :meth:`cognixcore.Node.add_generic_action` methods. In doing so, a context menu is populated for a node's GUI with the actions defined in the CogniX Editor. You would typically define the actions in the :code:`__init__` method of a node.

Dynamic ports

The static :attr:`cognixcore.Node.init_inputs` and :attr:`cognixcore.Node.init_outputs` initialization lists only work when a node is instantiated but not loaded through data. A node instance supports adding or removing ports dynamically at runtime. This is done through the following methods:

- :meth:`cognixcore.Node.create_input`
- :meth:`cognixcore.Node.delete_output`
- :meth:`cognixcore.Node.create_output`
- :meth:`cognixcore.Node.delete_output`


Node Configuration
^^^^^^^^^^^^^^^^^^

A node can have a configuration attached to it. This is done by either defining an internal to the node class explicitly named :code:`Config` or by setting the :attr:`cognixcore.Node.inner_config_type` type to a specific node config. The base class for a configuration is the :class:`cognixcore.NodeConfig` class. A developer can override this class to create a custom configurable class.

Configuration by Traits
#######################

The standard implementation for a node configuration is the :class:`cognixcore.config.traits.NodeTraitsConfig` class. It utilizes the `Traits <https://docs.enthought.com/traits/traits_tutorial/introduction.html>`_ and `Traits UI <https://docs.enthought.com/traitsui/>`_ for out of the box data validation and GUI generation (for the CogniX Editor). This implementation allows for dynamic nesting of multiple configurations, all of which are saveable/loadable. Traits with the "CX" prefix should be preferred over typical traits (such as :code:`CX_Float` instead of :code:`Float`), because they invoke their changed event when pressing the enter button. This is mainly a CogniX Editor concern, coupled with its undo functionality. This section only serves as an introduction to traits and its :code:`cognixcore` configuration counterpart. Please refer to the original traits documentation for additional user-manuals and tutorials.

Port list
#########

Along with the standard implementation for configuration, the :mod:`cognixcore.config.traits` module offers a class that makes it easier to incorporate dynamic port handling. This class is :class:`cognixcore.config.traits.PortList` class.

RESTful API
^^^^^^^^^^^

:code:`cognixcore` also offers the ability to run a RESTful API for a session. This can be done by accessing the API through the :attr:`cognixcore.Session.rest_api` property. For more info regarding the API, you can run a session and the api and check the docs through :code:`localhost:<port_number>/docs`. 
