from .base import Base
from .utils import serialize, deserialize
from .rc import PortObjPos, ConnValidType
from .config._abc import ConfigChange, ParamChange, ListChange

from dataclasses import dataclass
from beartype.door import is_subhint
from types import UnionType

from typing import TYPE_CHECKING, Any, get_args, Protocol, Callable
from queue import Queue
from asyncio import Event

if TYPE_CHECKING:
    from .node import Node

class _NoPortValue:
    pass

NO_VALUE = _NoPortValue()

class PortGenerator(Protocol):
    """A protocol that is used to generate ports for a Node."""

    def refresh():
        pass

    def connect(node: Node):
        pass

class Port:
    """
    The base class that represents a port. Can be used to describe a port to a class::`Node`.
    Ports that are defined in a class as class fields will then be instantiated for each instance of the class.
    """

    def __init__(
        self,
        name: str,
        io_pos: PortObjPos,
        label: str = '',
        type_: str = 'data',
        allowed_data: Any = None       
    ) -> None:
        
        self.name = name
        self.label = label
        self.type_ = type_
        self.allowed_data = allowed_data
        self.io_pos = io_pos

        # Should be set from outside
        self.node: Node = None
        self._value = NO_VALUE
    
    @property
    def value(self):
        return self._value

    def add_to_node(self, node: Node):
        """Adds the port to a node"""
        self.node = node
    
    def has_value(self):
        return self._value != NO_VALUE

class Input(Port):
    """
    Represents input ports.
    """

    def __init__(
        self, 
        name: str,
        label: str = '', 
        type_: str = 'data', 
        allowed_data: Any = None,
        default = None
    ) -> None:
        super().__init__(name, PortObjPos.INPUT, label, type_, allowed_data)
        self.default = default

        # Related to Inputs and only initialized when added to a Node
        self._data_queue: Queue = None
        self._value_event: Event = None
    
    def add_to_node(self, node: Node):
        super().add_to_node(node)
        self._data_queue = Queue()
        self._value = Event()
    
    async def value_async(self):
        """Awaits until the value of this port has been set at least once."""
        await self._value_event.wait()
        return self._value

    def push_value(self, value):
        self._data_queue.put(value)
    
    def get_value(self) -> Any:
        if self._data_queue.qsize() == 0:
            return self._value
        self._value = self._data_queue.get()
        return self._value
    
class Output(Port):
    """Represents output ports"""
    
    def __init__(
        self, 
        name: str, 
        label: str = '', 
        type_: str = 'data', 
        allowed_data: Any = None
    ) -> None:
        super().__init__(name, PortObjPos.OUTPUT, label, type_, allowed_data)

class MultiPort(PortGenerator):
    """
    A multi port allows a number of inputs or outputs to be dynamically generated
    together, based on a configuration or a custom condition. These ports
    belong to the same multi-port but are separate ports.

    Just like :class:`Input` and :class:`Output`, this class acts as a definition
    and is also used to instantiate a copy of itself at runtime.
    """    

    def __init__(
        self,
        minmax: tuple[int, int] = (1, -1),
        conf_cond: str | Callable[[Node], int] = None,
        prefix: str = None,
        suffix: str = None,
    ) -> None:
        self.prefix = prefix
        self.suffix = suffix
        self.min, self. max = minmax
        self.min = max(1, self.min)
        if self.max > 0 and self.max < self.min:
            self.max = self.min
        self.conf_cond = conf_cond
        
        # 
        self._ports: list[Port] = None
        self._node: None = None
    
    @property
    def node(self) -> Node:
        return self.node
    
    def add_to_node(self, node: Node):
        self._node = node
        self._ports = []

        if node.config is None:
            raise RuntimeError(f'Node type {type(node)} has no configuration')
        
        node.config.add_changed_event(self.refresh)

    def refresh(self):
        """Changes the port count based on a condition"""

        if self.node.config is None or self.conf_cond is None:
            print("OH NO")
            return
        
        conf = self.node.config
        if isinstance(self.conf_cond, str):
            port_count = getattr(conf, self.conf_cond)
            port_count = max(1, port_count)
            
        else:
            pass
    
    def _on_conf_changed(self, e: Changefun)
    
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
    
    