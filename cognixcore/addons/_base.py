from __future__ import annotations
from ..base import Base
from collections.abc import Sequence
from typing import TYPE_CHECKING, TypeVar
if TYPE_CHECKING:
    from ..session import Session
    from ..flow import Flow
    from ..node import Node


class AddOn(Base):
    
    _name = ''
    version = ''

    @classmethod
    def addon_name(cls):
        return cls._name if cls._name else cls.__name__
    
    def register(self, session: Session):
        """Called when the add-on is registered to a session."""
        self.session = session
        self.session.flow_created.sub(self.on_flow_created, nice=-5)
        self.session.flow_deleted.sub(self.on_flow_destroyed, nice=-5)
        
        for f in self.session.flows.values():
            self.connect_flow_events(f)
    
    def unregister(self):
        """Called when the add-on is unregistered from a session."""
        self.session.flow_created.unsub(self.on_flow_created)
        self.session.flow_deleted.unsub(self.on_flow_destroyed)
            
        for f in self.session.flows.values():
            self.disconnect_flow_events(f)
        self.session = None

    def connect_flow_events(self, flow: Flow):
        """
        Connects flow events to the add-on. There are events for
        when a node is created, added, removed or created from data.
        """
        flow.node_created.sub(self.on_node_created, nice=-4)
        flow.node_added.sub(self.on_node_added, nice=-4)
        flow.node_removed.sub(self.on_node_removed, nice=-4)
        flow.nodes_created_from_data.sub(self.on_nodes_loaded, nice=-4)
    
    def disconnect_flow_events(self, flow: Flow):
        """Disconnects flow events to the add-on"""
        
        flow.node_created.unsub(self.on_node_created)
        flow.node_added.unsub(self.on_node_added)
        flow.node_removed.unsub(self.on_node_removed)
        flow.nodes_created_from_data.unsub(self.on_nodes_loaded)
    
    def on_loaded(self):
        """
        *VIRTUAL*
        
        Called when an addon is loaded from data. This is invoked
        after the flows and nodes have been loaded.
        """

    def on_flow_created(self, flow: Flow):
        """
        *VIRTUAL*

        Called when a flow is created.
        """
        pass

    def on_flow_destroyed(self, flow: Flow):
        """
        *VIRTUAL*

        Called when a flow is destroyed.
        """
        pass
    
    def on_flow_renamed(self, flow: Flow):
        """
        *VIRTUAL*
        
        Called when a flow is renamed
        """

    def on_node_created(self, node: Node):
        """
        *VIRTUAL*

        Called when a node is created and fully initialized
        (:code:`Node.load()` has already been called, if necessary),
        but not yet added to the flow. Therefore, this is a good place
        to initialize the node with add-on-specific data.

        This happens only once per node, whereas it can be added and
        removed multiple times, see :code:`AddOn.on_node_added()` and
        :code:`AddOn.on_node_removed()`.
        """
        pass

    def on_nodes_loaded(self, nodes: Sequence[Node]):
        """
        *VIRTUAL*

        Called when a node is loaded and fully initialized
        from data. The node has been added to the flow, however
        the :code:`Node.place_event()` has not been called yet.
        """
        pass
        
    def on_node_added(self, node: Node):
        """
        *VIRTUAL*

        Called when a node is added to a flow.
        """
        pass

    def on_node_removed(self, node: Node):
        """
        *VIRTUAL*

        Called when a node is removed from a flow.
        """
        pass

    def extend_node_data(self, node: Node, data: dict):
        """
        *VIRTUAL*

        Invoked whenever any node is serialized. This method can be
        used to extend the node's data dict with additional
        add-on.related data.
        """
        pass

    def get_state(self) -> dict:
        """
        *VIRTUAL*

        Return the state of the add-on as JSON-compatible a dict.
        This dict will be extended by :code:`AddOn.complete_data()`.
        """
        return {}

    def set_state(self, state: dict, version: str):
        """
        *VIRTUAL*

        Set the state of the add-on from the dict generated in
        :code:`AddOn.get_state()`. Addons are loaded after the
        Flows.
        """
        pass

    def data(self) -> dict:
        """
        Supplements the data dict with additional data.
        """
        return {
            **super().data(),
            'custom state': self.get_state()
        }

    def load(self, data: dict):
        """
        Loads the data dict generated in :code:`AddOn.data()`.
        """
        self.set_state(data['custom state'], data['version'])
        self.on_loaded()


AddonType = TypeVar('AddonType', bound=AddOn)
"""A :code:`TypeVar` referencing the :class:`AddOn` type for generic use"""