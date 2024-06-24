cognixcore.config.traits
========================

.. py:module:: cognixcore.config.traits

.. autoapi-nested-parse::

   This module defines the default implementation of the :class:`cognixcore.config.NodeConfig`
   provided using the Traits Library. Some of the basic traits have been extended through new classes
   using the CX suffix. To non-GUI applications, this change is irrelevant. The :class:`CX_Float` and :class:`traits.api.Float`
   Traits are identical. However, for GUI applications, there is one significasnt difference. The CX
   prefixed traits are designed so they don't invoke a :code:`trait_changed_event` on each keystroke
   of the keyboard.

   Please refer to the `Traits <https://docs.enthought.com/traits/>`_ and `Traits UI <https://docs.enthought.com/traitsui/>`_
   for an in-depth tutorial on how to use the default configuration classes.



Classes
-------

.. autoapisummary::

   cognixcore.config.traits.CX_Int
   cognixcore.config.traits.CX_Float
   cognixcore.config.traits.CX_Str
   cognixcore.config.traits.CX_Complex
   cognixcore.config.traits.CX_Unicode
   cognixcore.config.traits.CX_String
   cognixcore.config.traits.CX_CStr
   cognixcore.config.traits.CX_CUnicode
   cognixcore.config.traits.CX_Password
   cognixcore.config.traits.CX_Tuple
   cognixcore.config.traits.NodeTraitsConfig
   cognixcore.config.traits.NodeTraitsGroupConfig
   cognixcore.config.traits.PortList


Functions
---------

.. autoapisummary::

   cognixcore.config.traits.find_expressions


Module Contents
---------------

.. py:function:: find_expressions(obj: type[traits.api.HasTraits] | traits.api.List | traits.api.Dict, expr: traits.observation.expression.ObserverExpression, obs_exprs: list[traits.observation.expression.ObserverExpression | str], exp_type: type[str | traits.observation.expression.ObserverExpression] = ObserverExpression)

   Recursively searches an object to find all the possible observer
   expressions. The starting expr should be :code:`None`.


.. py:class:: CX_Int(default_value=NoDefaultSpecified, **metadata)

   Bases: :py:obj:`__CX_Interface`, :py:obj:`traits.api.Int`


   This is a class helper to define trait parameters. This class
   ensures that, in the context of a Trait Configuration UI, change
   events are only invoked when pressing the enter button.


.. py:class:: CX_Float(default_value=NoDefaultSpecified, **metadata)

   Bases: :py:obj:`__CX_Interface`, :py:obj:`traits.api.Float`


   This is a class helper to define trait parameters. This class
   ensures that, in the context of a Trait Configuration UI, change
   events are only invoked when pressing the enter button.


.. py:class:: CX_Str(default_value=NoDefaultSpecified, **metadata)

   Bases: :py:obj:`__CX_Interface`, :py:obj:`traits.api.Str`


   This is a class helper to define trait parameters. This class
   ensures that, in the context of a Trait Configuration UI, change
   events are only invoked when pressing the enter button.


.. py:class:: CX_Complex(default_value=NoDefaultSpecified, **metadata)

   Bases: :py:obj:`__CX_Interface`, :py:obj:`traits.api.Complex`


   This is a class helper to define trait parameters. This class
   ensures that, in the context of a Trait Configuration UI, change
   events are only invoked when pressing the enter button.


.. py:class:: CX_Unicode(default_value=NoDefaultSpecified, **metadata)

   Bases: :py:obj:`__CX_Interface`, :py:obj:`traits.api.Unicode`


   This is a class helper to define trait parameters. This class
   ensures that, in the context of a Trait Configuration UI, change
   events are only invoked when pressing the enter button.


.. py:class:: CX_String(default_value=NoDefaultSpecified, **metadata)

   Bases: :py:obj:`__CX_Interface`, :py:obj:`traits.api.String`


   This is a class helper to define trait parameters. This class
   ensures that, in the context of a Trait Configuration UI, change
   events are only invoked when pressing the enter button.


.. py:class:: CX_CStr(default_value=NoDefaultSpecified, **metadata)

   Bases: :py:obj:`__CX_Interface`, :py:obj:`traits.api.CStr`


   This is a class helper to define trait parameters. This class
   ensures that, in the context of a Trait Configuration UI, change
   events are only invoked when pressing the enter button.


.. py:class:: CX_CUnicode(default_value=NoDefaultSpecified, **metadata)

   Bases: :py:obj:`__CX_Interface`, :py:obj:`traits.api.CUnicode`


   This is a class helper to define trait parameters. This class
   ensures that, in the context of a Trait Configuration UI, change
   events are only invoked when pressing the enter button.


.. py:class:: CX_Password(default_value=NoDefaultSpecified, **metadata)

   Bases: :py:obj:`__CX_Interface`, :py:obj:`traits.api.Password`


   This is a class helper to define trait parameters. This class
   ensures that, in the context of a Trait Configuration UI, change
   events are only invoked when pressing the enter button.


.. py:class:: CX_Tuple(*types, **metadata)

   Bases: :py:obj:`__CX_Interface`, :py:obj:`traits.api.Tuple`


   This is a class helper to define trait parameters. This class
   ensures that, in the context of a Trait Configuration UI, change
   events are only invoked when pressing the enter button.


.. py:class:: NodeTraitsConfig(node: cognixcore.node.Node = None, *args, **kwargs)

   Bases: :py:obj:`cognixcore.config._abc.NodeConfig`, :py:obj:`traits.api.HasTraits`


   An implementation of a Node Configuration using the traits library


   .. py:method:: obs_exprs()
      :classmethod:



   .. py:method:: serializable_traits()
      :classmethod:


      Returns the serializable traits of this class



   .. py:method:: find_trait_exprs(exp_type: type[str | traits.observation.expression.ObserverExpression] = ObserverExpression)
      :classmethod:


      Finds all the observer expressions available for this node, for
      traits that are not an event, are visible and do not have the
      dont_save metadata atrribute set to True.



   .. py:method:: __init_subclass__(**kwargs)
      :classmethod:



   .. py:attribute:: traits_view
      :value: None



   .. py:method:: is_duplicate_notif(ev: traits.observation.events.TraitChangeEvent | traits.observation.events.ListChangeEvent | traits.observation.events.SetChangeEvent | traits.observation.events.DictChangeEvent) -> bool

      In some cases, a change notification can be invoked when the
      trait hasn't changed value.



   .. py:method:: allow_notifications()

      Allows the invocation of events when a trait changes



   .. py:method:: block_notifications()

      Blocks the invocation of events when a trait changes



   .. py:method:: load(data: dict)

      Loads the configuration from its serialized form.
      This is a recursive operation that includes nested
      configurations and configurations inside lists, dicts,
      sets and tuples.



   .. py:method:: data() -> dict

      Creates a JSON compatible dict with the data
      needed to reconstruct this traits config.

      This is a recursive operation.



   .. py:method:: to_json(indent=1) -> str

      Returns JSON representation of the object as a string



   .. py:method:: serializable_traits() -> dict[str, Any]

      Returns the traits that should be serialized.

      To avoid having a trait serialized, you can set
      its visible metadata attribute to False - :code:`visible=False`



   .. py:method:: inspected_traits() -> dict[str, traits.api.CTrait]

      Returns the traits that should be inspected in case
      of a GUI implementation.



.. py:class:: NodeTraitsGroupConfig(node: cognixcore.node.Node = None, *args, **kwargs)

   Bases: :py:obj:`NodeTraitsConfig`


   A type meant to represent a group in traits ui. Currently not used
   and will probably be removed.


.. py:class:: PortList(node: cognixcore.node.Node = None, *args, **kwargs)

   Bases: :py:obj:`NodeTraitsConfig`


   This is a `Traits <https://docs.enthought.com/traitsui/>`_ and `TraitsUI <https://docs.enthought.com/traitsui/>`_
   specific configuration option, which allows the dynamic altering of the ports of a node. This is especially useful
   for scenarios where the library is used in conjuction with a GUI to generate the corresponding graph.


   .. py:class:: ListType

      Bases: :py:obj:`enum.IntEnum`


       A flag type that determines whether this list
      generates inputs, outputs or both.


      .. py:attribute:: OUTPUTS
         :value: 1



      .. py:attribute:: INPUTS
         :value: 2




   .. py:class:: Params

      Parameters for prefix, suffix and allowed data for the generation of the ports.


      .. py:attribute:: prefix
         :type:  str
         :value: ''



      .. py:attribute:: suffix
         :type:  str
         :value: ''



      .. py:attribute:: allowed_data
         :type:  type
         :value: None




   .. py:attribute:: ports
      :type:  list[str]


   .. py:attribute:: list_type
      :type:  PortList.ListType


   .. py:attribute:: min_port_count


   .. py:attribute:: inp_params


   .. py:attribute:: out_params


   .. py:method:: notify_ports_change(event)


   .. py:property:: valid_names


   .. py:method:: mods_inputs()

      Whether it modifies inputs



   .. py:method:: mods_outputs()

      Whether it modifies outputs



   .. py:method:: mods_inp_out()

      Whether it modifies both inputs and outputs



   .. py:attribute:: traits_view


