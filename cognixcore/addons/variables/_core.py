from __future__ import annotations
from packaging.version import parse as parse_version
from .._base import AddOn
from ...base import Event
from ...info_msgs import InfoMsgs
from types import MappingProxyType
from ...base import TypeMeta, TypeSerializer

from typing import Callable, Any, TYPE_CHECKING
if TYPE_CHECKING:
    from ... import Node, Flow
    
ADDON_VERSION = '1.0'
# TODO: replace print_err with InfoMsgs
    
class VarType:
    """
    Holds all the information for a subscribed type to the Variables Addon.
    
    One can define their own variable types for use with the Addon.
    Only defined variable types that are registered in the Addon are allowed to
    be used.
    """
    
    @staticmethod
    def create(val_type: type, name: str, pkg: str, serializer: TypeSerializer):
        type_meta = TypeMeta(pkg, name)
        return VarType(val_type, type_meta, serializer)
    
    def __init__(self, val_type: type, type_meta: TypeMeta, type_ser: TypeSerializer):
        self._type_meta = type_meta
        assert self._type_meta != None, "Type Meta must not be None!"
        self._type_ser = type_ser
        assert self._type_ser != None, "Type Serializer must not be None!"
        self._val_type = val_type
        assert self._val_type != None, "Value Type must not be None!"
    
    # Access to internal objects
    @property
    def type_meta(self):
        return self._type_meta
    
    @property
    def serializer(self):
        return self._type_ser
    
    @property
    def val_type(self):
        return self._val_type
    
    # Easier access to internals
    @property
    def name(self):
        return self._type_meta.type_id
    
    @property
    def package(self):
        return self._type_meta.package
    
    @property
    def identifier(self):
        return self._type_meta.identifier()
    
    def serialize(self, obj):
        return self._type_ser.serialize(obj)
    
    def deserialize(self, data: dict):
        return self._type_ser.deserialize(data)
    
    def default(self):
        return self._type_ser.default()
    
    def is_valid_val(self, val):
        return isinstance(val, self._val_type)
    
        
class Variable:
    """
    Implementation of flow variables. This implementation relies on
    registering valid data types for use utilizing the VarsAddon API.
    """

    def __init__(self, addon: VarsAddon, flow: Flow, name, val, data=None):
        # val must be an instance of a registered type
        self._addon = addon
        self._flow = flow
        self._name = name
        self._value = None
        self._var_type: VarType = None
        
        if data:
            self.load(data)
        else:
            self.set_type(type(val), True)
            self.set(val, True)
    
    def __str__(self):
        return str(self.value)

    @property
    def value(self):
        """Retrieves the value of the variable"""
        return self._value
    
    @value.setter
    def value(self, val):
        """Sets the value of the variable"""
        self.set(val)
    
    @property
    def name(self):
        return self._name
    
    @property
    def addon(self):
        return self._addon
    
    @property
    def flow(self):
        return self._flow
        
    @property
    def subscriber(self):
        return self.addon.var_sub(self.flow, self.name)
    
    @property
    def var_type(self):
        return self._var_type
    
    @var_type.setter
    def var_type(self, val: type):
        self.set_type(val)
    
    def set(self, val, silent=False):
        """
        Sets the value of the variable and notifies that the value is changed.
        """
        if not self._var_type.is_valid_val(val):
            raise ValueError(f"Value must be of type {self._var_type.val_type}, but received {type(val)} instead!")
        old_val = self._value
        self._value = val
        if not silent:
            self.addon.update_subscribers(self.flow, self._name)
            self.addon.var_value_changed.emit(self, old_val)
    
    def set_type(self, val_type: type | str, silent=False):
        """
        Sets the underlying VarType using a type or its identifier. The value type must be
        registered in the Addon beforehand.
        """
        
        var_type = self._addon.var_type(val_type)
        self.set_var_type(var_type, silent)
    
    def set_var_type(self, var_type: VarType, silent=False):
        """Sets the VarType of this Variable"""

        if not var_type:
            raise ValueError(f"Cannot register {None} type!")
        
        old_type = self._var_type
        if not var_type.val_type in self._addon.var_types:
            raise ValueError(f"{var_type.val_type} has not been registered!")
        
        self._var_type = var_type
        self.set(var_type.default(), True)
        if not silent:
            self.addon.update_subscribers(self.flow, self._name)
            self.addon.var_type_changed.emit(self, old_type)       
                  
    def update_subscribers(self):
        return self.addon.update_subscribers(self.flow, self._name)
    
    def data(self):
        return {
            'name': self.name,
            'var_type': self.var_type.identifier,
            'value': self.var_type.serialize(self._value)
        }
    
    def load(self, data: dict):
        """Loads the variable from a JSON compatible dict"""
        self._name = data['name']
        self._var_type = self.addon.var_type(data['var_type'])
        self._value = self.var_type.deserialize(data['value'])
    
    
class VarSubscriber:
    """Simple class to handle subscriptions for a variable"""
    
    def __init__(self, var: Variable):
        self.variable = var
        self.subscriptions: list[tuple[Node, Callable[[Variable], None]]] = []
        """The subscriptions are a callback that is a method on a node"""


class VarsAddon(AddOn):
    """
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
    """

    _name = 'Variables'
    version = ADDON_VERSION

    def __init__(self, load_builtins=True):
        AddOn.__init__(self)

        self.flow_variables: dict[Flow, dict[str, VarSubscriber]] = {}
        
        # nodes can be removed and re-added, so we need to keep track of the broken
        # subscriptions when nodes get removed, because they might get re-added
        # in which case we need to re-establish their subscriptions
        # dict[Node, dict[variable_name, callback_name]]
        self.removed_subscriptions: dict[Node, dict[str, str]] = {}
        
        # subscribed types that can be variables
        self._var_types: dict[type, VarType] = {}
        self._var_types_proxy = MappingProxyType(self._var_types)
        self._var_type_ids: dict[str, VarType] = {}
        self._var_type_ids_proxy = MappingProxyType(self._var_type_ids)
        
        # events
        self._var_created = Event[Variable]()
        self._var_deleted = Event[Variable, VarSubscriber]()
        self._var_renamed = Event[Variable, str]()
        self._var_value_changed = Event[Variable, Any]()
        self._var_type_changed = Event[Variable, Any]()
        self._var_data_loaded = Event[Variable]()
        
        if load_builtins:
            from .builtin import built_in_types
            for _, var_type in built_in_types.items():
                self.register_var_type(var_type)
    
    @property
    def var_types(self):
        return self._var_types_proxy
    
    @property
    def var_type_ids(self):
        return self._var_type_ids_proxy
    
    @property
    def var_created(self):
        """
        Event emitted when a variable is created
        
        args: Variable
        """
        return self._var_created 
    
    @property
    def var_deleted(self):
        """
        Event emitted when a variable is deleted
        
        args: Variable
        """
        return self._var_deleted
    
    @property
    def var_value_changed(self):
        """
        Event emitted when a variable's value changes
        
        args: Variable, old_value
        """
        return self._var_value_changed
    
    @property
    def var_type_changed(self):
        """
        Event emitted when a variable's data type is changed
        
        args: Variable, data_type: Data
        """
        
        return self._var_type_changed
        
    @property
    def var_renamed(self):
        """
        Event emitted when a variable's name is changed
        
        args: Variable, old_name: 
        """
        return self._var_renamed
    
    @property
    def var_data_loaded(self):
        """
        Event emitted when a variable has changed due to data loading
        
        args: Variable
        """
        return self._var_data_loaded
    
    def var_type(self, id: type | str):
        """Retrieves the var type."""
        if isinstance(id, type):
            return self._var_types[id]
        elif isinstance(id, str):
            return self._var_type_ids[id]
    
    def var_type_get(self, id: type | str):
        """Retrieves the var type. Returns None if it doesn't exist"""
        if isinstance(id, type):
            return self._var_types.get(id)
        elif isinstance(id, str):
            return self._var_type_ids.get(id)
        return None
        
    def register_var_type(self, var_type: VarType):
        """
        A function that registers various data types to be valid variables.
        
        This could be used in the future to import a whole range of data types for variables
        automatically. However, it is left up to the user.
        """
        
        self._var_types[var_type.val_type] = var_type
        self._var_type_ids[var_type.identifier] = var_type
        
    """
    flow management
    """

    def on_flow_created(self, flow):
        self.flow_variables[flow] = {}
        
    def on_flow_deleted(self, flow):
        del self.flow_variables[flow]

    """
    subscription management
    """

    def on_node_added(self, node):
        """
        Reconstruction of subscriptions.
        """
        # if node had subscriptions previously (so it was removed)
        if node in self.removed_subscriptions:
            for name, cb_name in self.removed_subscriptions[node].items():
                self.subscribe(node, name, getattr(node, cb_name))
            del self.removed_subscriptions[node]

    def on_node_removed(self, node):
        """
        Remove all subscriptions of the node.
        """

        # store subscription in removed_subscriptions
        # because the node might get re-added later
        self.removed_subscriptions[node] = {}

        for name, v_sub in self.flow_variables[node.flow].items():
            for (n, cb) in v_sub.subscriptions:
                if n == node:
                    self.removed_subscriptions[node][name] = cb.__name__
                    self.unsubscribe(node, name, cb)

    """
    variables api
    """

    def var_name_valid(self, flow, name: str) -> bool:
        """
        Checks if :code:`name` is a valid variable identifier and hasn't been take yet.
        """

        return name.isidentifier() and not self.var_exists(flow, name)

    def rename_var(self, flow: Flow, old_name: str, new_name: str, silent=False) -> bool:
        """Renames the variable if it exists"""
        
        if not self.var_exists(flow, old_name) or not new_name.isidentifier():
            return False
        
        v_sub = self.flow_variables[flow][old_name]
        del self.flow_variables[flow][old_name]
        
        v_sub.variable._name = new_name
        self.flow_variables[flow][new_name] = v_sub
        
        if not silent:
            self._var_renamed.emit(v_sub.variable, old_name)
        return True
    
    def add_var(self, flow: Flow, var_sub: VarSubscriber):
        """Forcibly adds a var. Helpful for undo"""
        self.flow_variables[flow][var_sub.variable.name] = var_sub
    
    def remove_var(self, flow: Flow, var: Variable):
        """Forcibly removes a var if it exists. Helpful for undo"""
        if self.var_exists(flow, var.name):
            del self.flow_variables[flow][var.name]
        
    def create_var(self, flow: Flow, name: str, val=None, load_from=None, silent=False) -> Variable:
        """
        Creates and returns a new variable and None if the name isn't valid.
        
        Val can be the value itself or the corresponding type
        """

        # if there isn't a value, create an integer
        if not val:
            val = 0
            
        if not self.var_name_valid(flow, name):
            raise ValueError(f"Name: <{name}> already exists or is not a proper python identifier")
            
        v = Variable(self, flow, name, val, load_from)
        v_sub = VarSubscriber(v)
        
        self.flow_variables[flow][name] = v_sub
        
        if not silent:
            self._var_created.emit(v)
        return v
                
    def delete_var(self, flow: Flow, name: str, silent=False):
        """
        Deletes a variable and causes subscription update. Subscriptions are preserved.
        """
        if not self.var_exists(flow, name):
            raise KeyError(f"Variable <{name}> doesn't exist!")

        v_sub = self.flow_variables[flow][name]
        del self.flow_variables[flow][name]
        
        if not silent:
            self._var_deleted.emit(v_sub.variable, v_sub)

    def change_var_value(self, flow: Flow, name: str, value=None, silent=False):
        """Changes a variables value"""
        v = self.var(flow, name)
        v.set(value, silent)
    
    def change_val_type(self, flow: Flow, name: str, val_type: type, silent=False):
        """Changes a variables underlying variable type based on a value type"""
        v = self.var(flow, name)
        v.set_type(val_type, silent)
    
    def set_var_from_data(self, flow: Flow, name: str, data: dict, silent=False):
        """Loads a variable's value with serialized data"""
        v = self.var(flow, name)
        v.load(data)
        
        if not silent:
            self._var_data_loaded.emit(v)
    
    def var_exists(self, flow, name: str) -> bool:
        return flow in self.flow_variables and name in self.flow_variables[flow]

    def var(self, flow, name: str) -> Variable:
        """Returns the variable with the given name."""
        return self.flow_variables[flow][name].variable
    
    def get_var(self, flow, name: str) -> Variable | None:
        """Returns the variable with the given name or None."""
        if not self.var_exists(flow, name):
            return None
        return self.var(flow, name)
    
    def var_sub(self, flow, name: str) -> VarSubscriber | None:
        """Returns the wrapper that holds the variable and its subscribers"""
        if self.var_exists(flow, name):
            return self.flow_variables[flow][name]
    
    def update_subscribers(self, flow, name: str):
        """
        Called when a Variable object changes or when the var is created or deleted.
        """

        v_sub = self.flow_variables[flow][name]
        v = v_sub.variable
        
        for (node, cb) in v_sub.subscriptions:
            cb(v)

    def subscribe(self, node: Node, name: str, callback: Callable[[Variable], None]):
        """
        Subscribe to a variable. ``callback`` must be a method of the node.
        """
        if not self.var_exists(node.flow, name):
            raise RuntimeError(f"Variable <{name}> doesn't exist.")

        self.flow_variables[node.flow][name].subscriptions.append((node, callback))

    def unsubscribe(self, node: Node, name: str, callback: Callable[[Variable], None]):
        """
        Unsubscribe from a variable.
        """
        if not self.var_exists(node.flow, name):
            # print_err(f'Variable {name} does not exist.')
            return

        self.flow_variables[node.flow][name].subscriptions.remove((node, callback))

    """
    serialization
    """

    def extend_node_data(self, node, data: dict):
        """
        Extends the node data with the variable subscriptions.
        """

        if self.flow_variables.get(node.flow) == {}:
            return

        data['Variables'] = {
            'subscriptions': {
                name: cb.__name__
                for name, v_sub in self.flow_variables[node.flow].items()
                for (n, cb) in v_sub.subscriptions
                if node == n
            }
        }

    def get_state(self) -> dict:
        
        return {
            f.global_id: {
                name: v_sub.variable.data()
                for name, v_sub in self.flow_variables[f].items()
            }
            for f in self.flow_variables.keys()
        }

    def set_state(self, state: dict, version: str):

        if parse_version(version) < parse_version('0.4'):
            
            InfoMsgs.write_err('Variables addon state version too old, skipping')
            return

        # JSON converts int keys to strings, so we need to convert them back
        state = {
            int(flow_id): flow_vars
            for flow_id, flow_vars in state.items()
        }
        
        # the flows have already loaded here
        for flow in self.session.flows.values():
            if flow.prev_global_id in state:
                for name, data in state[flow.prev_global_id].items():
                    self.create_var(flow, name, val=None, load_from=data)
            
            for node in flow.nodes:        
                # otherwise, check if it has load data and reconstruct subscriptions
                if node.load_data and 'Variables' in node.load_data:
                    for name, cb_name in node.load_data['Variables']['subscriptions'].items():
                        print(cb_name, getattr(node, cb_name))
                        self.subscribe(node, name, getattr(node, cb_name))

