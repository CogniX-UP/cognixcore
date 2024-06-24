cognixcore.addons.variables
===========================

.. py:module:: cognixcore.addons.variables

.. autoapi-nested-parse::

   Implements the functionality for the Variables Addon. The VarType,
   which holds information regarding a variable is defined here, as well as the
   VarsAddon.



Submodules
----------

.. toctree::
   :maxdepth: 1

   /autoapi/cognixcore/addons/variables/builtin/index


Attributes
----------

.. autoapisummary::

   cognixcore.addons.variables.ADDON_VERSION


Classes
-------

.. autoapisummary::

   cognixcore.addons.variables.VarType
   cognixcore.addons.variables.Variable
   cognixcore.addons.variables.VarSubscriber
   cognixcore.addons.variables.VarsAddon


Package Contents
----------------

.. py:class:: VarType(val_type: type, type_meta: cognixcore.base.TypeMeta, type_ser: cognixcore.base.TypeSerializer)

   Holds all the information for a subscribed type to the Variables Addon.

   One can define their own variable types for use with the Addon.
   Only defined variable types that are registered in the Addon are allowed to
   be used.


   .. py:method:: create(val_type: type, name: str, pkg: str, serializer: cognixcore.base.TypeSerializer)
      :staticmethod:



   .. py:property:: type_meta


   .. py:property:: serializer


   .. py:property:: val_type


   .. py:property:: name


   .. py:property:: package


   .. py:property:: identifier


   .. py:method:: serialize(obj)


   .. py:method:: deserialize(data: dict)


   .. py:method:: default()


   .. py:method:: is_valid_val(val)


.. py:class:: Variable(addon: VarsAddon, flow: cognixcore.Flow, name, val, data=None)

   Implementation of flow variables. This implementation relies on
   registering valid data types for use utilizing the VarsAddon API.


   .. py:method:: __str__()

      Return str(self).



   .. py:property:: value
      Retrieves the value of the variable


   .. py:property:: name


   .. py:property:: addon


   .. py:property:: flow


   .. py:property:: subscriber


   .. py:property:: var_type


   .. py:method:: set(val, silent=False)

      Sets the value of the variable and notifies that the value is changed.



   .. py:method:: set_type(val_type: type | str, silent=False)

      Sets the underlying VarType using a type or its identifier. The value type must be
      registered in the Addon beforehand.



   .. py:method:: set_var_type(var_type: VarType, silent=False)

      Sets the VarType of this Variable



   .. py:method:: update_subscribers()


   .. py:method:: data()


   .. py:method:: load(data: dict)

      Loads the variable from a JSON compatible dict



.. py:class:: VarSubscriber(var: Variable)

   Simple class to handle subscriptions for a variable


   .. py:attribute:: subscriptions
      :type:  list[tuple[cognixcore.Node, Callable[[Variable], None]]]
      :value: []


      The subscriptions are a callback that is a method on a node


.. py:class:: VarsAddon(load_builtins=True)

   Bases: :py:obj:`cognixcore.addons._base.AddOn`


   This addon provides a simple variable system.

   It provides an API to create Variable objects which can wrap any Python object,
   provided the object's type has been registered in the Addon beforehand.

   Nodes can subscribe to variable names with a callback that is executed once a
   variable with that name changes or is created. The callback must be a method of
   the node, so the subscription can be re-established on loading.

   This way nodes can react to changes of data and non-trivial data-flow is introduced,
   meaning that data dependencies are determined also by variable subscriptions and not
   purely by the edges in the graph anymore. This can be useful, but it can also prevent
   optimization. Variables are flow-local.


   .. py:attribute:: version


   .. py:property:: var_types


   .. py:property:: var_type_ids


   .. py:property:: var_created
      Event emitted when a variable is created

      args: Variable


   .. py:property:: var_deleted
      Event emitted when a variable is deleted

      args: Variable


   .. py:property:: var_value_changed
      Event emitted when a variable's value changes

      args: Variable, old_value


   .. py:property:: var_type_changed
      Event emitted when a variable's data type is changed

      args: Variable, data_type: Data


   .. py:property:: var_renamed
      Event emitted when a variable's name is changed

      args: Variable, old_name:


   .. py:property:: var_data_loaded
      Event emitted when a variable has changed due to data loading

      args: Variable


   .. py:method:: var_type(id: type | str)

      Retrieves the var type.



   .. py:method:: var_type_get(id: type | str)

      Retrieves the var type. Returns None if it doesn't exist



   .. py:method:: register_var_type(var_type: VarType)

      A function that registers various data types to be valid variables.

      This could be used in the future to import a whole range of data types for variables
      automatically. However, it is left up to the user.



   .. py:method:: on_flow_created(flow)

      *VIRTUAL*

      Called when a flow is created.



   .. py:method:: on_flow_deleted(flow)


   .. py:method:: on_node_added(node)

      Reconstruction of subscriptions.



   .. py:method:: on_node_removed(node)

      Remove all subscriptions of the node.



   .. py:method:: var_name_valid(flow, name: str) -> bool

      Checks if :code:`name` is a valid variable identifier and hasn't been take yet.



   .. py:method:: rename_var(flow: cognixcore.Flow, old_name: str, new_name: str, silent=False) -> bool

      Renames the variable if it exists



   .. py:method:: add_var(flow: cognixcore.Flow, var_sub: VarSubscriber)

      Forcibly adds a var. Helpful for undo



   .. py:method:: remove_var(flow: cognixcore.Flow, var: Variable)

      Forcibly removes a var if it exists. Helpful for undo



   .. py:method:: create_var(flow: cognixcore.Flow, name: str, val=None, load_from=None, silent=False) -> Variable

      Creates and returns a new variable and None if the name isn't valid.

      Val can be the value itself or the corresponding type



   .. py:method:: delete_var(flow: cognixcore.Flow, name: str, silent=False)

      Deletes a variable and causes subscription update. Subscriptions are preserved.



   .. py:method:: change_var_value(flow: cognixcore.Flow, name: str, value=None, silent=False)

      Changes a variables value



   .. py:method:: change_val_type(flow: cognixcore.Flow, name: str, val_type: type, silent=False)

      Changes a variables underlying variable type based on a value type



   .. py:method:: set_var_from_data(flow: cognixcore.Flow, name: str, data: dict, silent=False)

      Loads a variable's value with serialized data



   .. py:method:: var_exists(flow, name: str) -> bool


   .. py:method:: var(flow, name: str) -> Variable

      Returns the variable with the given name.



   .. py:method:: get_var(flow, name: str) -> Variable | None

      Returns the variable with the given name or None.



   .. py:method:: var_sub(flow, name: str) -> VarSubscriber | None

      Returns the wrapper that holds the variable and its subscribers



   .. py:method:: update_subscribers(flow, name: str)

      Called when a Variable object changes or when the var is created or deleted.



   .. py:method:: subscribe(node: cognixcore.Node, name: str, callback: Callable[[Variable], None])

      Subscribe to a variable. ``callback`` must be a method of the node.



   .. py:method:: unsubscribe(node: cognixcore.Node, name: str, callback: Callable[[Variable], None])

      Unsubscribe from a variable.



   .. py:method:: extend_node_data(node, data: dict)

      Extends the node data with the variable subscriptions.



   .. py:method:: get_state() -> dict

      *VIRTUAL*

      Return the state of the add-on as JSON-compatible a dict.
      This dict will be extended by :code:`AddOn.complete_data()`.



   .. py:method:: set_state(state: dict, version: str)

      *VIRTUAL*

      Set the state of the add-on from the dict generated in
      :code:`AddOn.get_state()`. Addons are loaded after the
      Flows.



.. py:data:: ADDON_VERSION
   :value: '1.0'


