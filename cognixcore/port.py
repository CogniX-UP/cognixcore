from __future__ import annotations

from .base import Base, Event
from .utils import serialize, deserialize
from .rc import PortObjPos, ConnValidType
from .config._abc import ConfigChange
from dataclasses import dataclass
from beartype.door import is_subhint
from types import UnionType
from collections.abc import Iterable
from copy import copy

from typing import (
    TYPE_CHECKING, 
    Any, 
    get_args, 
    Protocol, 
    Callable, 
    TypeVar, 
    Generic
)

if TYPE_CHECKING:
    from .node import Node

class _NoPortValue:
    pass

NO_VALUE = _NoPortValue()

class PortGroup(Protocol):
    """A protocol that provides ports. A class::`Port` is also a PortGroup."""

    def __init__(self) -> None:
        super().__init__()
        self._node: Node = None
        self._name: str = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def io_type(self) -> PortObjPos:
        pass

    def copy(self) -> PortGroup:
        """Shallow copy of a group"""
        return copy(self)
    
    def init(self, node: Node, name: str):
        """Connects the port group to a class::`Node`"""
        pass

    def ports(self) -> Iterable[Port]:
        """Iterable of what ports are contained in this group"""
        pass

class PortGenerator(PortGroup):
    """Used to generate ports for a Node."""

    def refresh():
        pass

class Port(PortGroup):
    """
    The base class that represents a port. Can be used to describe a port to a class::`Node`.
    Ports that are defined in a class as class fields will then be instantiated for each instance of the class.
    """

    def __init__(
        self,
        io_pos: PortObjPos,
        type_: str = 'data',
        allowed_data: Any = None       
    ) -> None:
        
        self.type_ = type_
        self.allowed_data = allowed_data
        self._io_type = io_pos

        # Should be set when added to a node
        super().__init__()
        self._name: str = None
        self.node: Node = None
        self._value = NO_VALUE
        self._name_changed: Event[Port, str] = None
    
    @property
    def value(self):
        return self._value
    
    @property
    def io_type(self) -> PortObjPos:
        return self._io_type
    
    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, value: str):
        old_val = self._name
        if old_val == value:
            return
        self._name = value
        self._name_changed.emit(self, old_val)

    def ports(self) -> Iterable[Port]:
        yield self

    def init(self, node: Node, name: str):
        """Adds the port to a node"""
        self._name_changed = Event()
        self.node = node
        self._name = name
    
    def has_value(self):
        return self._value != NO_VALUE

class Input(Port):
    """Represents input ports."""

    def __init__(
        self, 
        type_: str = 'data', 
        allowed_data: Any = None,
        default = None
    ) -> None:
        super().__init__(PortObjPos.INPUT, type_, allowed_data)
        self.default = default
    
class Output(Port):
    """Represents output ports"""
    
    def __init__(
        self, 
        type_: str = 'data', 
        allowed_data: Any = None
    ) -> None:
        super().__init__(PortObjPos.OUTPUT, type_, allowed_data)

P = TypeVar('P', bound=Port)

class MultiPort(PortGenerator, Generic[P]):
    """
    A multi port allows a number of inputs or outputs to be dynamically generated
    together, based on a configuration or a custom condition. These ports
    belong to the same multi-port but are separate ports.

    Just like :class:`Input` and :class:`Output`, this class acts as a definition
    and is also used to instantiate a copy of itself at runtime.
    """    

    def __init__(
        self,
        port: P,
        minmax: tuple[int, int] = (1, -1),
        conf_cond: str | Callable[[Node], list[str]] = None,
    ) -> None:
        self.min, self. max = minmax
        self.min = max(1, self.min)
        self._port = port

        if self.max > 0 and self.max < self.min:
            self.max = self.min
        self.conf_cond = conf_cond

        # Should be set when added to Node
        super().__init__()
        self._ports: list[P] = []
        self._node: None = None

    @property
    def node(self) -> Node:
        return self.node
    
    @property
    def io_type(self) -> PortObjPos:
        return self._port._io_type
    
    def ports(self) -> Iterable[Port]:
        return self._ports
    
    def init(self, node: Node, name: str):
        self._name = name
        self._node = node
        self._ports = []

        if node.config is None:
            raise RuntimeError(f'Node type {type(node)} has no configuration')
        
        # prepare config changed callbacks
        def _on_conf_changed(e: ConfigChange):
            self.refresh()
        node.config.add_changed_event(_on_conf_changed)

        # refresh
        self.refresh()

    def refresh(self):
        """Changes the port count based on a condition"""

        if self.node.config is None or self.conf_cond is None:
            return
        
        conf = self.node.config
        port_count: int | None = None
        port_list: list[str] | None = None
        if isinstance(self.conf_cond, Callable):
            port_list = self.conf_cond(self.node)
        else:
            attr = getattr(conf, self.conf_cond)
            port_count = attr
            if (isinstance(attr, list)):
                port_list = attr
        
        # ensure that there are no duplicates and keep them in order
        if port_list is not None:
            temp_dict = { port:0 for port in port_list }
            port_list = list(temp_dict.keys())
            port_count = len(port_list)

        if port_count is None:
            return
        
        port_count = max(1, port_count)
        current_count = len(self._ports)
        delta_count = port_count - current_count

        # Making sure port count is consistent with the parameters
        if delta_count < 0:
            for i in range(-1, delta_count - 1, -1):
                self._ports.pop()
        elif delta_count > 0:
            for i in range(delta_count):
                temp_name = f'@@{i}'
                p = self._port.copy()
                p._name = temp_name
                self._ports.append(p)

        # At this point, we have either a count or a count + list
        # If we have a list, we use the names in the list
        if port_list is not None:
            for i in range(port_count):
                name = port_list[i]
                name = name if name else i
                p = self._ports[i]
                self._rename_port(p, name)
        else:
            for i in range(port_count):
                self._rename_port(self._ports[i], i)

        self.node._setup_ports()

    def _rename_port(self, port: Port, name: str | int):
        new_name = self._create_port_name(name)
        if port.name == new_name:
            return
        port.name = new_name
    
    def _create_port_name(self, p_name: str | int) -> str:
        return f'{self.name}_{p_name}'

class _RootPortGroup(PortGroup, Generic[P]):

    def __init__(self, io_type: PortObjPos) -> None:
        super().__init__()
        self._io_type = io_type

        self._ports_changed = True
        self._node: Node = None
        self._port_groups: dict[str, PortGroup] = None
        self._port_list: list[P] = []
        self._ports: dict[str, P] = {}

    @property
    def io_type(self) -> PortObjPos:
        return self._io_type
    
    def init(self, node: Node, name: str):
        self._name = name
        self._node = node

        self._port_groups = {}
        self._port_list = []
        self._ports = {}

    def ports(self) -> Iterable[Port]:
        if not self._ports_changed:
            return self._port_list
        self.fix_order()
        return self._port_list
    
    def add_port(port: P, fix_order=True):
        pass

    def remove_port(port: P, fix_order=True):
        pass

    def fix_order(self):
        pass

@dataclass
class PortConfig:
    """
    The PortConfig class is a configuration class for creating ports. It's mainly used for the static init_input 
    and init_outputs of custom Node classes, but can also be used for dynamically creating ports for Nodes.
    An instantiated Node's actual inputs and outputs will be of type :class:`NodePort` (:class:`NodeInput`, :class:`NodeOutput`).
    """
    
    label: str = ''
    type_: str = 'data'
    allowed_data: Any = None
    default: Any = None

default_config = PortConfig()
"""An instance of a default port configuration"""
 
class NodePort(Base):
    """Base class for inputs and outputs of nodes"""

    def __init__(
        self, 
        node, 
        io_pos: PortObjPos, 
        type_: str, 
        label_str: str, 
        allowed_data: type | None = None
    ):
        Base.__init__(self)

        self.node: Node = node
        self.io_pos = io_pos
        self.type_ = type_
        self.label_str = label_str
        self.load_data = None
        self.allowed_data = allowed_data

    def load(self, data: dict):
        
        self.load_data = data
        self.type_ = data['port_type']
        self.label_str = data['label']
        
        allowed_data = data['allowed_data']
        allowed_data = deserialize(allowed_data) if allowed_data else None
        self.allowed_data = allowed_data
        
    def data(self) -> dict:
        
        return {
            **super().data(),
            'port_type': self.type_,
            'label': self.label_str,
            'allowed_data': serialize(self.allowed_data) if self.allowed_data else None,
            'allowed_data_str': str(self.allowed_data) if self.allowed_data else None,
        }


class NodeInput(NodePort):
    """A port that is an input"""
    
    def __init__(self, node, type_: str, label_str: str = '', default = None, allowed_data: type | None = None):
        super().__init__(node, PortObjPos.INPUT, type_, label_str, allowed_data)
        self.default = default

    def load(self, data: dict):
        super().load(data)
        self.default = deserialize(data['default'])

    def data(self) -> dict:
        
        return {
            **super().data(),
            'default': serialize(self.default)
        }

class NodeOutput(NodePort):
    """A port that is an output"""
    
    def __init__(self, node, type_: str, label_str: str = '', allowed_data: type | None = None):
        super().__init__(node, PortObjPos.OUTPUT, type_, label_str, allowed_data)

        self.val: allowed_data = None

def check_valid_data(type_out: type, type_in: type) -> bool:
    """Checks whether out and input can be connected via their allowed data types."""
    if not type_out:
        type_out = object
    if not type_in:
        type_in = object
    
    # If it's a Union, we break it into its parts to check
    if isinstance(type_out, UnionType):
        ar = get_args(type_out)
        for t in ar:
            if is_subhint(t, type_in):
                return True
        return False
    
    # Not a Union, simple type checking
    return is_subhint(type_out, type_in)

def check_valid_conn(out: NodeOutput, inp: NodeInput) -> ConnValidType:
    """
    Checks if a connection is valid between two node ports.

    Returns:
        An enum representing the check result
    """
    
    if out.node == inp.node:
        return ConnValidType.SAME_NODE
    
    if out.io_pos == inp.io_pos:
        return ConnValidType.SAME_IO
    
    if out.io_pos != PortObjPos.OUTPUT:
        return ConnValidType.IO_MISSMATCH
    
    if out.type_ != inp.type_:
        return ConnValidType.DIFF_ALG_TYPE
    
    if not check_valid_data(out.allowed_data, inp.allowed_data):
        return ConnValidType.DATA_MISSMATCH
    
    return ConnValidType.VALID

def check_valid_conn_tuple(connection: tuple[NodeOutput, NodeInput]):
    out, inp = connection
    return check_valid_conn(out, inp)
    
    