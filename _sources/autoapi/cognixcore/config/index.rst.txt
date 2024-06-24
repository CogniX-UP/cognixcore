cognixcore.config
=================

.. py:module:: cognixcore.config

.. autoapi-nested-parse::

   Defines the :class:`NodeConfig` interface class. Implement this
   class for creating a specific configuration base type. The default implementation
   for this, using the `Traits <https://docs.enthought.com/traitsui/>`_ library, is :class:`cognixcore.config.traits.NodeTraitsConfig`



Submodules
----------

.. toctree::
   :maxdepth: 1

   /autoapi/cognixcore/config/traits/index


Classes
-------

.. autoapisummary::

   cognixcore.config.NodeConfig


Package Contents
----------------

.. py:class:: NodeConfig(node: cognixcore.node.Node = None)

   An interface representing a node's configuration


   .. py:property:: node
      :type: cognixcore.node.Node

      A property returning the node of this configuration


   .. py:method:: add_changed_event(e: Callable[[Any], None])

      Adds an event to be called when a parameter of the config changes. The
      event must be a function with a single parameter.



   .. py:method:: remove_changed_event(e: Callable[[Any], None])

      Removes any change event previously added.



   .. py:method:: allow_change_events()

      Allows the invocation of change events.



   .. py:method:: block_change_events()

      Blocks the invocation of change events.



   .. py:method:: to_json(indent=1) -> str
      :abstractmethod:


      Returns JSON representation of the object as a string



   .. py:method:: load(data: dict)
      :abstractmethod:


      Loads the configuration from a JSON compatible dict



   .. py:method:: data() -> dict
      :abstractmethod:


      Serializes this configuartion to a JSON compatible dict.



