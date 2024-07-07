from .base import Base
from .utils import serialize, deserialize
from .rc import PortObjPos, ConnValidType

from dataclasses import dataclass
from beartype.door import is_subhint
from types import UnionType

from typing import TYPE_CHECKING, Any, get_args

if TYPE_CHECKING:
    from .node import Node

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
    
    