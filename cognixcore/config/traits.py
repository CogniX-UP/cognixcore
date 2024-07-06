"""
This module defines the default implementation of the :class:`cognixcore.config.NodeConfig`
provided using the Traits Library. Some of the basic traits have been extended through new classes
using the CX suffix. To non-GUI applications, this change is irrelevant. The :class:`CX_Float` and :class:`traits.api.Float`
Traits are identical. However, for GUI applications, there is one significasnt difference. The CX
prefixed traits are designed so they don't invoke a :code:`trait_changed_event` on each keystroke
of the keyboard.

Please refer to the `Traits <https://docs.enthought.com/traits/>`_ and `Traits UI <https://docs.enthought.com/traitsui/>`_
for an in-depth tutorial on how to use the default configuration classes. 
"""

from traits.api import *
from traits.observation.expression import ObserverExpression, trait, anytrait
from traits.trait_base import not_false, not_event
from traits.observation.events import (
    TraitChangeEvent, 
    ListChangeEvent,
    DictChangeEvent,
    SetChangeEvent,
)

from traitsui.api import View, Item
from typing import Callable, Any as AnyType
from json import loads, dumps
from importlib import import_module

from collections.abc import (
    Sequence, 
    MutableSequence, 
    MutableMapping, 
    MutableSet, 
    Set as ColSet
)

from enum import IntEnum
from dataclasses import dataclass

from ..port import PortConfig, NodePort
from ..node import Node
from ._abc import NodeConfig

#   UTIL

def __process_expression_str(c_trait: CTrait, trait_name: str, expr: str):
    """
    Processes an ongoing string expression given a trait and its name. Extends the
    expression based on whether the trait is an Instance, a List, a Dict or a Set.
    """
    
    if not c_trait:
        return None, f'{expr}.*' if expr else '*'
        
    trait_type = c_trait.trait_type
    
    if isinstance(trait_type, Instance) and issubclass(trait_type.klass, HasTraits):
        
        # it's guaranteed that if a trait_name doesnt exist,
        # an expr will and vice-versa
        if expr:
            return (
                trait_type.klass,
                f'{expr}.{trait_name}' if trait_name else expr
            )
        else:
            return trait_type.klass, trait_name
    
    elif isinstance(trait_type, (List, Set, Dict)):
        
        return_type = (
            trait_type.item_trait 
            if isinstance(trait_type, (List, Set)) 
            else trait_type.value_trait
        )
        
        if expr:
            return (
                return_type,
                f'{expr}.{trait_name}.items' if trait_name else f'{expr}.items'
            )
        else:
            return return_type, f'{trait_name}.items'
            
    return (None, None)

__item_methods: dict = {
    List: lambda expr: expr.list_items(),
    Set: lambda expr: expr.set_items(),
    Dict: lambda expr: expr.dict_items(),
}

def __process_expression_obs(c_trait: CTrait, trait_name: str, expr: ObserverExpression):
    """
    Processes an ongoing object expression given a trait and its name. Extends the
    expression based on whether the trait is an Instance, a List, a Dict or a Set.
    """
    
    if not c_trait:
        return None, expr.anytrait() if expr else anytrait()
        
    trait_type = c_trait.trait_type
    
    if isinstance(trait_type, Instance) and issubclass(trait_type.klass, HasTraits):
        
        # it's guaranteed that if a trait_name doesnt exist,
        # an expr will and vice-versa
        if expr:
            return (
                trait_type.klass,
                expr.trait(trait_name) if trait_name else expr
            )
        else:
            return trait_type.klass, trait(trait_name)
        
    elif isinstance(trait_type, (List, Set, Dict)):
        
        return_type = (
            trait_type.item_trait 
            if isinstance(trait_type, (List, Set)) 
            else trait_type.value_trait
        )
        items_method = __item_methods[type(trait_type)]
        
        if expr:
            return (
                return_type,
                items_method(expr.trait(trait_name)) if trait_name else items_method(expr)
            )
        else:
            return return_type, items_method(trait(trait_name))
            
    return (None, None)


__process_expression_methods: dict[type, Callable[[CTrait, str, Any], None]]= {
    str : __process_expression_str,
    ObserverExpression: __process_expression_obs,
}         

def find_expressions (
    obj: type[HasTraits] | List | Dict, 
    expr: ObserverExpression, 
    obs_exprs: list[ObserverExpression | str],
    exp_type: type[str | ObserverExpression] = ObserverExpression
):
    """
    Recursively searches an object to find all the possible observer
    expressions. The starting expr should be :code:`None`.
    """
    
    if not obj:
        return
    
    process_method = __process_expression_methods[exp_type]
    
    if isinstance(obj, type) and issubclass(obj, HasTraits):
        
        # main class filter
        new_obj, new_expr = process_method(None, None, expr)
        obs_exprs.append(new_expr)
        
        # search for additional traits in the class
        
        cls_traits = obj.class_traits(visible=not_false)
        for trait_name, c_trait in cls_traits.items():
            new_obj, new_expr = process_method(c_trait, trait_name, expr)
            find_expressions(new_obj, new_expr, obs_exprs, exp_type)
    
    elif isinstance(obj, CTrait):
        
        obs_exprs.append(expr)
        new_obj, new_expr = process_method(obj, None, expr)
        find_expressions(new_obj, new_expr, obs_exprs, exp_type)

_auto_enter = {
    'enter_set': True,
    'auto_set': False
}

#   These are all set so that not every keystroke creates a change event

class __CX_Interface:
    """
    This is a class helper to define trait parameters. This class
    ensures that, in the context of a Trait Configuration UI, change
    events are only invoked when pressing the enter button.
    """
    
    def __init__(self, default_value=NoDefaultSpecified, **metadata):
        metadata.update(_auto_enter)
        # second class is the Trait class
        self.__class__.__bases__[1].__init__(self, default_value, **metadata)
        
class CX_Int(__CX_Interface, Int):
    pass

class CX_Float(__CX_Interface, Float):
    pass

class CX_Str(__CX_Interface, Str):
    pass

class CX_Complex(__CX_Interface, Complex):
    pass

class CX_Unicode(__CX_Interface, Unicode):
    pass

class CX_String(__CX_Interface, String):
    pass

class CX_CStr(__CX_Interface, CStr):
    pass

class CX_CUnicode(__CX_Interface, CUnicode):
    pass

class CX_Password(__CX_Interface, Password):
    pass

class CX_Tuple(__CX_Interface, Tuple):
    
    def __init__(self, *types, **metadata):
        metadata.update(_auto_enter)
        Tuple.__init__(self, *types, **metadata)

class NodeTraitsConfig(NodeConfig, HasTraits):
    """
    An implementation of a Node Configuration using the traits library
    """
    
    # CLASS
    
    __s_metadata = {
        'type': not_event,
        'visible': not_false,
    }
    __hidden_trait_names = {
        'trait_added',
        'trait_modified',
        'label',
    }
    _type_id = '$#t'
    """
    Used for serialization purposes. Intentionally complicated to avoid
    collision with user defined data.
    """
    __obs_exprs = None
    """Holds all the important observer expressions"""
    
    __str_to_type = {
        'set': set,
        'frozenset': frozenset,
        'list': list,
        'tuple': tuple,
        'dict': dict
    }
    
    @classmethod
    def __type_to_str(cls, t: type):
        if issubclass(t, MutableSet):
            return 'set'
        elif issubclass(t, ColSet):
            return 'frozenset'
        elif issubclass(t, MutableSequence):
            return 'list'
        elif issubclass(t, Sequence):
            return 'tuple'
        elif issubclass(t, MutableMapping):
            return 'dict'
    
    @classmethod
    def obs_exprs(cls):
        return cls.__obs_exprs
    
    @classmethod
    def serializable_traits(cls):
        """Returns the serializable traits of this class"""
        return cls.class_traits(**cls.__s_metadata)
    
    @classmethod
    def find_trait_exprs(cls, exp_type: type[str | ObserverExpression] = ObserverExpression):
        
        """
        Finds all the observer expressions available for this node, for
        traits that are not an event, are visible and do not have the 
        dont_save metadata atrribute set to True.
        """
        cls.__obs_exprs = []
        find_expressions(cls, None, cls.__obs_exprs, exp_type)
    
    def __init_subclass__(cls, **kwargs):
        cls.find_trait_exprs(str)

    # INSTANCE
    # redefine them as non serializable traits
    _node = Instance(Node, visible=False)
    _config_changed = Set(visible=False)
    _allow_change = List([True], visible=False)
    traits_view = None
    
    def __init__(self, node: Node = None, *args, **kwargs):
        NodeConfig.__init__(self, node)        
        HasTraits.__init__(self, *args, **kwargs)
        self.allow_notifications()
        self._init_children(node)
        
    def _init_children(self, node: Node):
        """
        All the child traits that are :code:`HasTraits` instances themselves
        are passed the node through this function.
        """
        self._node = node
        for _, trait in self.serializable_traits().items():
            if isinstance(trait, NodeTraitsConfig):
                trait._init_children(node)
    # Traits only
    
    def is_duplicate_notif(
        self, 
        ev: TraitChangeEvent | ListChangeEvent | SetChangeEvent | DictChangeEvent
    ) -> bool:
        """
        In some cases, a change notification can be invoked when the
        trait hasn't changed value.
        """
        if isinstance(ev, TraitChangeEvent):
            return ev.new == ev.old
        elif isinstance(ev, (ListChangeEvent, SetChangeEvent, DictChangeEvent)):
            return ev.added == ev.removed
        return False
    
    def allow_notifications(self):
        """Allows the invocation of events when a trait changes"""
        self.observe(self._on_config_changed, self.__obs_exprs)

    def block_notifications(self):
        """Blocks the invocation of events when a trait changes"""
        self.observe(self._on_config_changed, self.__obs_exprs, remove=True)
        
    def load(self, data: dict):
        """
        Loads the configuration from its serialized form.
        This is a recursive operation that includes nested
        configurations and configurations inside lists, dicts,
        sets and tuples.
        """
        
        self._trait_change_notify(False)
        self.block_change_events()
        for name, inner_data in data.items():
            try:
                d_result = self._deserialize_trait_data(inner_data)
                attr_val = getattr(self, name)
                if isinstance(attr_val, NodeTraitsConfig):
                    attr_val.load(d_result)
                else:
                    setattr(self, name, d_result)
            except:
                continue
        
        self.allow_change_events()
        self._trait_change_notify(True)
    
    def _deserialize_trait_data(self, data):
        result = data
        
        if isinstance(data, dict):
            type_id = data[self._type_id]
            content: dict | list = data['content']
        
            if type_id == 'traits config':
                result = content
        
            elif type_id == 'dict':
                result = {
                    key: self._deserialize_trait_data(value)
                    for key, value in content.items()
                }
            elif type_id in ('tuple', 'set', 'list', 'frozenset'):           
                for i in range(len(content)):
                    content[i] = self._deserialize_trait_data(content[i])
                result = self.__str_to_type[type_id](content)
        return result
    
    def data(self) -> dict:
        """
        Creates a JSON compatible dict with the data
        needed to reconstruct this traits config. 
        
        This is a recursive operation.
        """
        result = {}
        s_traits = self.serializable_traits()
        for name in s_traits:
            trait_value = getattr(self, name)
            result[name] = self._serialize_trait_value(trait_value)    
        return result
    
    def _serialize_trait_value(self, trait_value):
        trait_data = trait_value
        type_id = None
        content = None
        module = None
        cls_name = None
        
        if (isinstance(trait_value, NodeTraitsConfig)):
            type_id = 'traits config'
            content = trait_value.data()
            t = type(trait_value)
        
        elif isinstance(trait_value, (tuple, set, list, frozenset)):
            type_id = self.__type_to_str(type(trait_value))
            content = list(trait_value)
            # recursively serialize the non serializable
            for i in range(len(content)):
                content[i] = self._serialize_trait_value(content[i])
                
        elif isinstance(trait_value, dict):
            type_id = self.__type_to_str(dict)
            content = {
                key: self._serialize_trait_value(val)
                for key, val in trait_value.items()
            }
        
        if not type_id:
            return trait_data
        else:
            return {
                self._type_id: type_id,
                'content': content,
            }
            
    def to_json(self, indent=1) -> str:
        return dumps(
            self.data(), 
            indent=indent, skipkeys=True,
        )
    
    def serializable_traits(self) -> dict[str, AnyType]:
        """
        Returns the traits that should be serialized.
        
        To avoid having a trait serialized, you can set
        its visible metadata attribute to False - :code:`visible=False`
        """
        return self.trait_get(**self.__s_metadata)
    
    def inspected_traits(self) -> dict[str, CTrait]:
        """
        Returns the traits that should be inspected in case
        of a GUI implementation.
        """
        # the trait_get func seems to ignore traits like Button
        # however, the traits funct adds some additional traits
        # that shouldn't be visible, despite visible=not_false
        # that's why this is a workaround
        return {
            key: trait 
            for key, trait in self.traits(visible=not_false).items()
            if key not in self.__hidden_trait_names
        }
    
class NodeTraitsGroupConfig(NodeTraitsConfig):
    """
    A type meant to represent a group in traits ui. Currently not used
    and will probably be removed.
    """  
    pass

class PortList(NodeTraitsConfig):
    """
    This is a `Traits <https://docs.enthought.com/traitsui/>`_ and `TraitsUI <https://docs.enthought.com/traitsui/>`_
    specific configuration option, which allows the dynamic altering of the ports of a node. This is especially useful
    for scenarios where the library is used in conjuction with a GUI to generate the corresponding graph.
    """
    
    class ListType(IntEnum):
        """
         A flag type that determines whether this list 
        generates inputs, outputs or both.
        """
        OUTPUTS = 1
        INPUTS = 2
    
    @dataclass
    class Params:
        """Parameters for prefix, suffix and allowed data for the generation of the ports."""
        prefix: str = ''
        suffix: str = ''
        allowed_data: type = None
        
    ports: list[str] =  List(CX_Str(), desc="dynamic ports")
    list_type: ListType = Int(ListType.INPUTS, visible=False)
    min_port_count = Int(0, visible=False) # this essentially protects from deleting static ports
    inp_params = Instance(Params, visible=False)
    out_params = Instance(Params, visible=False)
    
    @observe("ports.items", post_init=True)
    def notify_ports_change(self, event):
        if self.is_duplicate_notif(event):
            return
        
        valid_names = self.valid_names
        
        def fix_ports(
            port_list: Sequence[NodePort], 
            delete_func, 
            create_func, 
            rename_func,
            params: PortList.Params
        ):
            port_diff = len(valid_names) - len(port_list) + self.min_port_count
            if port_diff < 0:
                for i in range(abs(port_diff)):
                    if len(port_list) == self.min_port_count:
                        break
                    delete_func(len(port_list) - 1)
            else:
                for i in range(port_diff):
                    create_func(
                        PortConfig(
                            'port',
                            allowed_data=params.allowed_data
                        )
                    )
            
            for i in range(self.min_port_count, len(port_list)):
                rename_func(
                    i,
                    f"{params.prefix}{valid_names[i-self.min_port_count]}{params.suffix}"
                )
         
        if self.mods_inputs():
            fix_ports(
                self._node._inputs,
                self._node.delete_input,
                self._node.create_input,
                self._node.rename_input,
                self.inp_params
            )
               
        if self.mods_outputs():
            fix_ports(
                self._node._outputs,
                self._node.delete_output,
                self._node.create_output,
                self._node.rename_output,
                self.out_params
            )
    
    @property
    def valid_names(self):
        valid_names: list[str] = []
        for stream in self.ports:
            valid_s = stream.strip()
            if valid_s:
                valid_names.append(valid_s)
        return valid_names
    
    def mods_inputs(self):
        """Whether it modifies inputs"""
        return self.list_type & PortList.ListType.INPUTS == PortList.ListType.INPUTS
    
    def mods_outputs(self):
        """Whether it modifies outputs"""
        return self.list_type & PortList.ListType.OUTPUTS == PortList.ListType.OUTPUTS
    
    def mods_inp_out(self):
        """Whether it modifies both inputs and outputs"""
        return self.mods_inputs() and self.mods_outputs()
    
    traits_view = View(
        Item('ports', show_label=False)
    )