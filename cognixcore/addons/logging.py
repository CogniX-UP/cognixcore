from logging import (
    getLogger, 
    Logger,
    NOTSET,
    DEBUG,
    INFO,
    WARNING,
    ERROR,
    CRITICAL,
)
from types import MappingProxyType
from typing import Sequence

from ._base import AddOn
from ..base import NoArgsEvent, Event
from ..flow import Flow
from ..node import Node
from collections.abc import Mapping


class LoggingAddon(AddOn):
    """
    This addon implements :class:`cognixcore.flow.Flow` and :class:`cognixcore.node.Node` logging functionality.

    It provides functions to create and delete loggers that are owned
    by a particular node. The loggers get enabled/disabled
    automatically when the owning node is added to/removed from
    the flow.

    The contents of logs are currently not preserved. If a log's
    content should be preserved, it should be saved explicitly.

    Refer to Python's logging module documentation.
    """

    _name = 'Logging'
    version = '1.0'
    root_logger_name = 'session'
    
    def __init__(self):
        super().__init__()

        self._loggers: dict[Flow | Node, Logger] = {}
        self._loggers_proxy = MappingProxyType(self._loggers)
        
        self.flow_created = Event[Flow, Logger]()
        self.flow_destroyed = Event[Flow, Logger]()
        self.node_created = Event[Node, Logger]()
        self.node_added = Event[Node, Logger]()
        self.node_removed = Event[Node, Logger]()

        self._log_level = NOTSET
        self._root_logger = getLogger(self.root_logger_name)
    
    @property 
    def log_level(self) -> int:
        """The log level assigned to a logger at creation. Refer to python's logging module."""
        return self._log_level
    
    @log_level.setter
    def log_level(self, value: int):
        """Sets the log level to all the currently available loggers."""
        self._log_level = value
        for logger in self._loggers.values():
            logger.setLevel(value)
            
    @property
    def root_looger(self) -> Logger:
        """The top-level logger associated with the Logging Addon."""
        return self._root_logger
    
    @property
    def loggers(self) -> Mapping[Flow | Node, Logger]:
        """A map from a Flow or Node to their respective loggers"""
        return self._loggers_proxy
    
    @property
    def __rn(self):
        return self.root_logger_name
        
    def on_flow_created(self, flow: Flow):
        self._loggers[flow] = logger = getLogger(f"{self.__rn}.{flow.global_id}")
        logger.setLevel(self._log_level)
        self.flow_created.emit(flow, logger)
    
    def on_flow_destroyed(self, flow: Flow):
        logger = self._loggers[flow]
        logger.disabled = True
        del self._loggers[flow]
        
        for node in flow.nodes:
            self._loggers[node].disabled = True
            del self._loggers[node]
        
        self.flow_destroyed.emit(flow, logger)
            
    def on_node_created(self, node: Node):
        
        self._loggers[node] = logger = getLogger(f"{self.__rn}.{node.flow.global_id}.{node.global_id}")
        logger.setLevel(self._log_level)
        self.node_created.emit(node, logger)
    
    def on_nodes_loaded(self, nodes: Sequence[Node]):
        for node in nodes:
            self.on_node_created(node)
    
    def on_node_added(self, node: Node):
        self._loggers[node].disabled = False
        self.node_added.emit(node, self._loggers[node])

    def on_node_removed(self, node):
        self._loggers[node].disabled = True
        self.node_removed.emit(node, self._loggers[node])
    
    def on_loaded(self):
        for flow in self.session.flows.values():
            self.on_flow_created(flow)
            
            for node in flow.nodes:
                self.on_node_created(node)
