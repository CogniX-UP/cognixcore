from __future__ import annotations

from abc import abstractmethod, ABCMeta
from typing import TYPE_CHECKING, Callable, Any

if TYPE_CHECKING:
    from ..node import Node

# ----CONFIGURATION----

# TODO Provide a standard for defining and setting metadata for configs.
# Each config or property of the config should have some way of accesssing metadata
# through a unified API (most likely an abstract method on NodeConfig)

class NodeConfig:
    """An interface representing a node's configuration"""
    
    def __init__(self, node: Node = None):
        self._node = node
        self._config_changed: set = set()
        # we're using a list to avoid any implications with
        # frameworks such as traits that might behave differently
        # when setting an instance's member
        self._allow_change = [True]
        """
        We're using a list to avoid some implications that may
        occur when using the Traits package. Ideally, this could
        be changed to an abstract method to avoid any confusions.
        """
    
    @property
    def node(self) -> Node:
        """A property returning the node of this configuration"""
        return self._node
    
    def add_changed_event(self, e: Callable[[Any], None]):
        """
        Adds an event to be called when a parameter of the config changes. The
        event must be a function with a single parameter.
        """
        
        self._config_changed.add(e)
    
    def remove_changed_event(self, e: Callable[[Any], None]):
        """Removes any change event previously added."""
        self._config_changed.remove(e)
    
    def _on_config_changed(self, params):
        """
        Called when a configuration parameter changes. Depending on the
        implementation, this may need to be assigned to another event.
        """
                
        if self._allow_change[0]:
            for ev in self._config_changed:
                ev(params)
    
    def allow_change_events(self):
        """Allows the invocation of change events."""
        self._allow_change[0] = True
    
    def block_change_events(self):
        """Blocks the invocation of change events."""
        self._allow_change[0] = False
        
    @abstractmethod
    def to_json(self, indent=1) -> str:
        """Returns JSON representation of the object as a string"""
        pass
    
    @abstractmethod
    def load(self, data: dict):
        """Loads the configuration from a JSON compatible dict"""
        pass
    
    @abstractmethod
    def data(self) -> dict:
        """Serializes this configuartion to a JSON compatible dict."""
        pass