"""Gathers all the most important classes and utilities under a unified namespace/package"""

from .base import (
    TypeMeta,
    TypeSerializer,
    BasicSerializer,
    EP,
    Event,
    NoArgsEvent,
    Base,
    InfoType,
    Identifiable,
    IHaveIdentifiable,
    find_identifiable,
    IdentifiableGroups
)
from .flow import Flow, FlowAlg
from .node import (
    Node,
    FrameNode,
    NodeAction,
    GenericNodeAction,
    NodeType,
    node_from_identifier,
)
from .config import NodeConfig
from .config.traits import NodeTraitsConfig
from .session import Session
from .flow_executor import (
    FlowExecutor,
    ManualFlow,
    DataFlowNaive,
    DataFlowOptimized,
    ExecFlowNaive,
)
from .flow_player import (
    GraphState,
    GraphTime,
    GraphActionResponse,
    GraphStateEvent,
    GraphEvents,
    GraphPlayer,
    FlowPlayer,
)
from .info_msgs import InfoMsgs
from .rc import (
    ConnectionInfo,
    ConnValidType,
    ProgressState,
)
from .addons import AddonType, AddOn
from .port import PortConfig, NodePort, NodeInput, NodeOutput
from .utils import serialize, deserialize

def set_complete_data_func(func):
    from .base import Base
    Base.complete_data_function = func
