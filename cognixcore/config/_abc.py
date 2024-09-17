from __future__ import annotations

from abc import abstractmethod, ABCMeta
from typing import TYPE_CHECKING, Callable, Any, TypeAlias
from collections.abc import MutableSequence, MutableSet, MutableMapping

if TYPE_CHECKING:
    from ..node import Node

# ----CONFIGURATION----

# TODO Provide a standard for defining and setting metadata for configs.
# Each config or property of the config should have some way of accesssing metadata
# through a unified API (most likely an abstract method on NodeConfig)

class ConfigChange:

    def __init__(self, config: NodeConfig, name: str):
        self.config = config
        self.name = name

class ParamChange(ConfigChange):

    def __init__(self, config: NodeConfig, name: str, old: Any, new: Any):
        self.config = config
        self.name = name
        self.old = old
        self.new = new

class ListChange(ConfigChange):

    def __init__(
        self, 
        config: NodeConfig, 
        name: str, 
        index: int, 
        added: MutableSequence, 
        removed: MutableSequence
    ):
        super().__init__(config, name)
        self.index = index
        self.added = added
        self.removed = removed

class SetChange(ConfigChange):

    def __init__(self, config: NodeConfig, name: str, added: MutableSet, removed: MutableSet):
        super().__init__(config, name)
        self.added = added
        self.removed = removed

class DictChange(ConfigChange):

    def __init__(self, config: NodeConfig, name: str, added: MutableMapping, removed: MutableMapping):
        super().__init__(config, name)
        self.added = added
        self.removed = removed

ChangeFunc: TypeAlias = Callable[[ConfigChange], None]

class NodeConfig:
    """An interface representing a node's configuration"""    

    def __init__(self, node: Node = None):
        self._node = node
        self._config_changed: set[ChangeFunc] = set()
        self._param_changed: dict[str, set[ChangeFunc]] = {}

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
    
    def add_changed_event(self, e: ChangeFunc):
        """
        Adds an event to be called when any parameter of the config changes.
        """
        
        self._config_changed.add(e)
    
    def remove_changed_event(self, e: ChangeFunc):
        """Removes any global change event previously added."""
        self._config_changed.remove(e)
    
    def sub(self, param: str, e: ChangeFunc):
        """"Adds an event to be called when a specific parameter of the config changes."""
        param_set = self._param_changed.get(param)
        if not param_set:
            param_set = set()
        param_set.add(e)
    
    def unsub(self, param: str, e: ChangeFunc):
        """Removes a specific param change event from the config changes."""
        param_set = self._param_changed.get(param)
        if not param_set:
            return
        param_set.remove(e)

    def _on_config_changed(self, change: ConfigChange):
        """
        Called when a configuration parameter changes. Depending on the
        implementation, this may need to be assigned to another event.
        """
                
        if not self._allow_change[0]:
            return
        
        # global events
        for ev in self._config_changed:
            ev(change)
        
        # per param event
        param_set = self._param_changed.get(change.name)
        if param_set:
            for ev in param_set:
                ev(change)
    
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