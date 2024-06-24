"""
This module defines pydantic models for the session, nodes, ports

While pydantic is not a requirement for this library, this optional module
provides utilities to work with the serialized versions of the corresponding
cognix core objects.

This model is a requirement if cognixcore is installed with the Rest API
dependency.
"""

try:    
    from pydantic import BaseModel, Field
except ImportError as e:
    print("Pydantic V2 is required!")
    raise e

from .base import Base

class CognixModel(BaseModel):
    """The base model for a cognixcore Base class"""
    GID: int
    
class PortModel(CognixModel):
    """A model representing a port"""
    port_type: str
    label: str
    allowed_data: str

class ConnectionModel(BaseModel):
    """A model representing a connection between two nodes"""
    parent_node_index: int = Field(validation_alias='parent node index')
    out_port_index: int = Field(validate_alias='output port index')
    conn_node_index: int = Field(validation_alias='connected node')
    conn_inp_port_index: int = Field(validation_alias='connected input port index')

class NodeTypeModel(BaseModel):
    """A model representing a node type"""
    identifier: str
    version: str
    desc: str
    
class NodeModel(CognixModel):
    """A model representing a Node with its most basic structure"""
    identifier: str
    version: str
    title: str
    inputs: list[PortModel]
    outputs: list[PortModel]

class FlowModel(CognixModel):
    """A model representing a Flow."""
    #currently does not include the output data
    title: str
    alg_mode: str = Field(validation_alias='algorithm mode')
    nodes: list[NodeModel]
    connections: list[ConnectionModel]

class VarModel(BaseModel):
    """A model representing a Variable."""
    name: str | None
    value_type_id: str | None
    value: dict | None

class SessionModel(BaseModel):
    """A mode representing a whole s"""

