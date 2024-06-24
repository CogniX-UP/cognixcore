"""
This module defines the abstract flow, managing node, edges, etc.
Flow execution is implemented by FlowExecutor class.

A *flow* is a directed, usually but not necessarily acyclic multi-graph of *nodes*
and *edges* (connections between nodes). The nodes are the computational units and
the edges define the flow of data between them. The fundamental operations to
perform on a flow are:

* adding a node
* removing a node and incident edges
* adding an edge between a node output and another node's input
* removing an edge

Flow Execution Modes
--------------------

There are a couple of different modes / algorithms for executing a flow.

**Data Flow**

In the normal data flow mode, data is simply *forward propagated on change*.
Specifically, this means the following:

A node output may have 0 or more outgoing connections/edges. When a node's output
value is updated, the new value is propagated to all connected nodes' inputs. If
there are multiple edges, the order of activation is undefined.

A node input may have 0 or 1 incoming connections/edges. When a node's input receives
new data, the node's *update event* is invoked.

A *flow execution* is started once some node's *update event* is invoked (either
by direct invocation through ``node.update()``, or by receiving input data), or
some node's output value is updated.

A node can consume inputs and update outputs at any time.

Assumptions:

    * no non-terminating feedback loops.

**Data Flow with Optimization**

Since the naive implementation of the above specification can be highly inefficient
in some cases, a more advanced algorithm can be used.
This algorithm ensures that, during a *flow execution*, each *edge* is updated at most
once.
It should implement the same semantics as the data flow algorithm, but with a slightly
tightened assumption:

    * no feedback loops / cycles in the graph
    * nodes never modify their ports (inputs, outputs) during execution (*update event*)

The additional work required for this at the beginning of a *flow execution* is based
on a DP algorithm running in :math:`\\mathcal{O}(|V|+ |E|)` time, where
:math:`|V|` is the number of nodes and
:math:`|E|` is the number of edges.
However, when there are multiple consecutive executions without
any subsequent changes to the graph, this work does not need to be repeated and execution
is fast.

**Execution Flow**

The special *exec mode* uses an additional type of connection (edge): the
*execution connection*.
While pure data flows are the more common use case, some applications call for a slightly
different paradigm. You can think of the exec mode as e.g. UnrealEngine's blueprint system.

In *exec mode*, calling ``node.exec_output(index)`` has a similar effect as calling
``node.set_output_val(index, val)`` in *data mode*,
but without any data being propagated, so it's just a trigger signal.
Pushing output data, however, does not cause updates in successor nodes.

When a node is updated (it received an *update event* through an *exec connection*), once it
needs input data (it calls ``self.input(index)``), if that input is connected to some
predecessor node `P`, then `P` receives an *update event* with ``inp=-1``, during which
it should push the output data.
Therefore, data is not forward propagated on change (``node.set_output_val(index, value)``),
but generated on request (backwards,
``node.input()`` -> ``pred.update_event()`` -> ``pred.set_output_val()`` -> return).

The *exec mode* is still somewhat experimental, because the *data mode* is the far more
common use case. It is not yet clear how to best implement the *exec mode* in a way that
is both efficient and easy to use.

Assumptions:

    * no non-terminating feedback loops with exec connections

"""
from __future__ import annotations
from .base import Base, Event, find_identifiable
from .flow_executor import FlowExecutor, executor_from_flow_alg, flow_alg_from_executor
from .node import Node, NodeType
from .port import NodeOutput, NodeInput, check_valid_conn
from .rc import FlowAlg, ConnValidType, ConnectionInfo
from .utils import *
from typing import TYPE_CHECKING
from logging import Logger

if TYPE_CHECKING:
    from .session import Session
    from .flow_player import GraphPlayer

class Flow(Base):
    """
    Manages all abstract flow components (nodes, edges, executors, etc.)
    and exposes methods for modification.
    """
    
    _node_base_type: type[Node] = Node
    """
    Forces the flow to accept a specific type of base node.
    """
    
    def __init__(self, session: Session, title: str):
        Base.__init__(self)

        # player - will be set through the session
        self._player: GraphPlayer = None 
        # events
        self.node_added = Event[Node]()
        self.node_removed = Event[Node]()
        self.node_created = Event[Node]()
        self.connection_added = Event[tuple[NodeOutput, NodeInput]]()    
        self.connection_removed = Event[tuple[NodeOutput, NodeInput]]()     
        self.renamed = Event[str, str]()

        self.connection_request_valid = Event[ConnValidType]()
        self.nodes_created_from_data = Event[list[Node]]()
        self.connections_created_from_data = Event[list[tuple[NodeOutput, NodeInput]]]()

        self.algorithm_mode_changed = Event[FlowAlg]()

        # connect events to add-ons
        for addon in session.addons.values():
            addon.connect_flow_events(self)

        # general attributes
        self.session = session
        self.title = title
        self.nodes: list[Node] = []
        self.load_data = None

        self.node_successors: dict[Node, list[Node]] = {}   # additional data structure for executors
        self.graph_adj: dict[NodeOutput, list[NodeInput]] = {}         # directed adjacency list relating node ports
        self.graph_adj_rev: dict[NodeInput, NodeOutput] = {}     # reverse adjacency; reverse of graph_adj

        self._executor: FlowExecutor = executor_from_flow_alg(FlowAlg.DATA)(self)
        
        self._logger: Logger = None

    @property
    def algorithm_mode(self) -> FlowAlg:
        """
        The current algorithm mode of the flow as an enum.
        
        One-to-one with an executor type.
        """
        return flow_alg_from_executor(type(self._executor))
    
    @algorithm_mode.setter
    def algorithm_mode(self, value: FlowAlg | str):
        self.set_algorithm_mode(value)
        
    @property
    def executor(self) -> FlowExecutor:
        """Returns the current executor of the Flow"""
        return self._executor
    
    @executor.setter
    def executor(self, value: FlowExecutor):
        self.set_executor(value)
    
    @property
    def logger(self) -> Logger:
        """Returns the logger of the flow, based on the logging addon."""
        if not self._logger:
            self._logger = self.session.logg_addon.loggers[self]
        return self._logger
    
    @property
    def player(self) -> GraphPlayer:
        """A player that can evaluate the flow as if it were a python program."""
        return self._player
    
    @player.setter
    def player(self, value: GraphPlayer):
        if self._player:
            self._player.stop()
        
        self._player = value
        self._player._flow = self
        
    def load(self, data: dict):
        """Loading a flow from data as previously returned by ``Flow.data()``."""
        super().load(data)
        self.load_data = data

        # set algorithm mode
        self.set_algorithm_mode(
            FlowAlg.from_str(data['algorithm mode']),
            False
        )

        # build flow
        self.load_components(data['nodes'], data['connections'])


    def load_components(self, nodes_data, conns_data):
        """Loading nodes and their connections from data as previously returned
        by :code:`Flow.data()`. This method will call :code:`Node.rebuilt()` after
        connections are established on all nodes.
        Returns the new nodes and connections."""

        new_nodes = self._create_nodes_from_data(nodes_data)
        new_conns = self._connect_nodes_from_data(new_nodes, conns_data)

        for n in new_nodes:
            n.rebuilt()

        return new_nodes, new_conns


    def _create_nodes_from_data(self, nodes_data: list) -> list[Node]:
        """create nodes from nodes_data as previously returned by data()"""

        nodes = []

        identifiables = [
            node.identifiable()
            for node in 
            self.session.node_types.union(self.session.invis_node_types) 
        ]
        for n_c in nodes_data:

            # find class
            node_class = find_identifiable(
                n_c['identifier'],
                identifiables
            ).info

            node = self.create_node(node_class, n_c, True)
            nodes.append(node)

        self.nodes_created_from_data.emit(nodes)

        return nodes

    def create_node(self, node_class: type[NodeType], data=None, silent=False) -> NodeType:
        """Creates, adds and returns a new node object"""

        if not issubclass(node_class, self._node_base_type):
            raise RuntimeError(f'Node class is not of base type {self._node_base_type}')
        
        if node_class not in self.session.node_types:
            raise RuntimeError(f'Node class {node_class} not registered in Session')

        # instantiate node
        node = node_class(self)
        # connect to node events
        node.input_added.sub(lambda n, i, inp: self.add_node_input(n, inp), nice=-5)
        node.output_added.sub(lambda n, i, out: self.add_node_output(n, out), nice=-5)
        node.input_removed.sub(lambda n, i, inp: self.remove_node_input(n, inp), nice=-5)
        node.output_removed.sub(lambda n, i, out: self.remove_node_output(n, out), nice=-5)
        # initialize node ports
        node._setup_ports()
        # load node
        if data is not None:
            node.load(data)

        if not silent:
            self.node_created.emit(node)
        self.add_node(node, silent)
        
        return node


    def add_node(self, node: Node, silent=False):
        """
        Places the node object in the graph, Stores it, and causes the node's
        ``Node.place_event()`` to be executed. ``Flow.create_node()`` automatically
        adds the node already, so no need to call this manually.
        """

        if not isinstance(node, self._node_base_type):
            print_err(f'Object {node} is not of base type {self._node_base_type}')
            return
        
        self.nodes.append(node)

        self.node_successors[node] = []

        # catch up on node ports
        # notice that add_node_output() and add_node_input() are called by Node.
        # but it's ignored when the node is not currently placed in the flow
        for out in node._outputs:
            self.add_node_output(node, out, False)
            # self.graph_adj[out] = []
        for inp in node._inputs:
            self.add_node_input(node, inp, False)
            # self.graph_adj_rev[inp] = None

        node.after_placement()
        self._flow_changed()

        if not silent:
            self.node_added.emit(node)


    def remove_node(self, node: Node, silent=False):
        """
        Removes a node from the flow without deleting it. Can be added again
        with ``Flow.add_node()``.
        """

        node.prepare_removal()
        self.nodes.remove(node)

        del self.node_successors[node]
        for out in node._outputs:
            self.remove_node_output(node, out, False)
            # del self.graph_adj[out]
        for inp in node._inputs:
            self.remove_node_input(node, inp, False)
            # del self.graph_adj_rev[inp]

        self._flow_changed()
        
        if not silent:
            self.node_removed.emit(node)


    def add_node_input(self, node: Node, inp: NodeInput, _call_flow_changed=True):
        """updates internal data structures"""
        if node in self.node_successors:
            self.graph_adj_rev[inp] = None
            if _call_flow_changed:
                self._flow_changed()


    def add_node_output(self, node: Node, out: NodeOutput, _call_flow_changed=True):
        """updates internal data structures."""
        if node in self.node_successors:
            self.graph_adj[out] = []
            if _call_flow_changed:
                self._flow_changed()


    def remove_node_input(self, node: Node, inp: NodeInput, _call_flow_changed=True):
        """updates internal data structures."""
        if node in self.node_successors:
            del self.graph_adj_rev[inp]
            if _call_flow_changed:
                self._flow_changed()


    def remove_node_output(self, node: Node, out: NodeOutput, _call_flow_changed=True):
        """updates internal data structures."""
        if node in self.node_successors:
            del self.graph_adj[out]
            if _call_flow_changed:
                self._flow_changed()


    def _connect_nodes_from_data(self, nodes: list[Node], data: list):
        connections: list[tuple[NodeOutput, NodeInput]] = []

        for c in data:

            c_parent_node_index: int = c['parent node index']
            c_connected_node_index: int = c['connected node']
            c_output_port_index: int = c['output port index']
            c_connected_input_port_index: int = c['connected input port index']

            if c_connected_node_index is not None:  # which can be the case when pasting
                parent_node = nodes[c_parent_node_index]
                connected_node = nodes[c_connected_node_index]

                connections.append(
                    self.connect_ports(
                        parent_node._outputs[c_output_port_index],
                        connected_node._inputs[c_connected_input_port_index],
                        silent=True
                    ))

        self.connections_created_from_data.emit(connections)

        return connections

    def connection_info(self, c:tuple[NodeOutput, NodeInput]):
        """Returns information about a connection without the ports"""
        out, inp = c
        out_node, inp_node = out.node, inp.node
        out_i = out.node._outputs.index(out)
        inp_i = inp.node._inputs.index(inp)
        
        return ConnectionInfo(out_node, out_i, inp_node, inp_i)

    def check_connection_validity(self, c: tuple[NodeOutput, NodeInput]) -> ConnValidType:
        """
        Checks whether a considered connect action is legal.
        
        Does not check if the ports are connected or disconnected
        """

        out, inp = c

        valid_result = check_valid_conn(out, inp)
        
        self.connection_request_valid.emit(valid_result)
        
        return valid_result

    
    def can_ports_connect(self, c: tuple[NodeOutput, NodeInput]) -> ConnValidType:
        """
        Same as :code:`Flow.check_connection_validity()`
        
        Also checks if nodes already connected or if input is connected to another output
        """
        
        out, inp = c
        
        valid_result = check_valid_conn(out, inp)
        
        if valid_result == ConnValidType.VALID: 
            if inp in self.graph_adj[out]:
                # Connect action invalid on already connected nodes!
                valid_result = ConnValidType.ALREADY_CONNECTED 
            elif self.graph_adj_rev.get(inp) is not None:
                # Input is connected to another output
                valid_result = ConnValidType.INPUT_TAKEN
        
        self.connection_request_valid.emit(valid_result)
        
        return valid_result
    
    
    def can_ports_disconnect(self, c: tuple[NodeOutput, NodeInput]) -> ConnValidType:
        """
        Same as :code:`Flow.check_connection_validity()`
        
        Also checks if nodes already disconnected
        """
        
        out, inp = c
        
        if inp not in self.graph_adj[out]:
            # Disconnect action invalid on already disconnected nodes!
            valid_result = ConnValidType.ALREADY_DISCONNECTED
        else:
            valid_result = check_valid_conn(out, inp)
            
        self.connection_request_valid.emit(valid_result)
        
        return valid_result
    
    def connect_from_info(self, conn: ConnectionInfo, silent=False):
        return self.connect_nodes(
            conn.node_out,
            conn.out_i,
            conn.node_inp,
            conn.inp__i,    
            silent
        )
        
    def connect_nodes(self, out: Node, out_i: int, inp: Node, inp_i: int, silent=False):
        out = out._outputs[out_i]
        inp = inp._inputs[inp_i]
        return self.connect_ports(out, inp, silent)

    def connect_ports(self, out: NodeOutput | int, inp: NodeInput | int, silent=False) -> tuple[NodeOutput, NodeInput] | None:
        """
        Connects two node ports. Returns the connection if successful, None otherwise.
        """
        
        valid_result = self.can_ports_connect((out, inp))
        
        if valid_result != ConnValidType.VALID:
            print_err(f'Invalid connect request')
            return None

        self.add_connection((out, inp), silent=silent)

        return out, inp

    def disconnect_from_info(self, conn: ConnectionInfo, silent=False):
        return self.disconnect_nodes(
            conn.node_out,
            conn.out_i,
            conn.node_inp,
            conn.inp__i,
            silent    
        )
        
    def disconnect_nodes(self, out: Node, out_i: int, inp: Node, inp_i: int, silent=False):
        out = out._outputs[out_i]
        inp = inp._inputs[inp_i]
        return self.disconnect_ports(out, inp, silent)
    
    def disconnect_ports(self, out: NodeOutput, inp: NodeInput, silent=False):
        """
        Disconnects two node ports.
        """

        valid_result = self.can_ports_disconnect((out, inp))
        
        if valid_result != ConnValidType.VALID:
            print_err(f'Invalid disconnect request')
            return

        self.remove_connection((out, inp), silent=silent)


    def add_connection(self, c: tuple[NodeOutput, NodeInput], silent=False):
        """
        Adds an edge between two node ports.
        """

        out, inp = c

        self.graph_adj[out].append(inp)
        self.graph_adj_rev[inp] = out

        self.node_successors[out.node].append(inp.node)
        self._flow_changed()


        self._executor.conn_added(out, inp, silent=silent)

        self.connection_added.emit((out, inp))


    def remove_connection(self, c: tuple[NodeOutput, NodeInput], silent=False):
        """
        Removes an edge.
        """

        out, inp = c

        self.graph_adj[out].remove(inp)
        self.graph_adj_rev[inp] = None

        self.node_successors[out.node].remove(inp.node)
        self._flow_changed()

        self._executor.conn_removed(out, inp, silent=silent)
#
        self.connection_removed.emit((out, inp))


    def connected_inputs(self, out: NodeOutput) -> list[NodeInput]:
        """
        Returns a list of all connected inputs to the given output port.
        """
        return self.graph_adj[out]


    def connected_output(self, inp: NodeInput) -> NodeOutput | None:
        """
        Returns the connected output port to the given input port, or
        :code:`None` if it is not connected.
        """
        return self.graph_adj_rev[inp]

    def set_executor(self, executor: FlowExecutor, silent=False):
        """
        Sets the flow executor
        """
        if not isinstance(executor, FlowExecutor):
            raise ValueError(f'Executor must be of type {FlowExecutor}, but was of type {type(executor)}')
        
        prev_alg = self.algorithm_mode
        self._executor = executor
        if not silent and prev_alg != self.algorithm_mode:
            self.algorithm_mode_changed.emit(self.algorithm_mode)
            
    def set_algorithm_mode(self, mode: FlowAlg | str, silent=False):
        """
        Sets the algorithm mode of the flow, possible string values
        are 'manual', 'data', 'data opt', and 'exec'.
        
        Internally sets the corresponding executor.
        """

        if isinstance(mode, str):
            mode = FlowAlg.from_str(mode)
        if mode is None or mode == self.algorithm_mode:
            return False

        self.set_executor(executor_from_flow_alg(mode)(self), silent)
        return True


    def _flow_changed(self):
        self._executor.flow_changed = True


    def data(self) -> dict:
        """
        Serializes the flow: returns a JSON compatible dict containing all
        data of the flow.
        """
        return {
            **super().data(),
            'algorithm mode': flow_alg_from_executor(type(self._executor)) if self._executor else FlowAlg.DATA,
            'nodes': self._gen_nodes_data(self.nodes),
            'connections': self._gen_conns_data(self.nodes),
            # 'output data': self._gen_output_data(self.nodes),
        }


    def _gen_nodes_data(self, nodes: list[Node]) -> list[dict]:
        """Returns the data dicts of the nodes given"""

        return [n.data() for n in nodes]


    def _gen_conns_data(self, nodes: list[Node]) -> list[dict]:
        """Generates the connections data between and relative to the nodes passed"""

        data = []
        for i, n in enumerate(nodes):
            for j, out in enumerate(n._outputs):
                for inp in self.graph_adj[out]:
                    if inp.node in nodes:
                        data.append({
                            'parent node index': i,
                            'output port index': j,
                            'connected node': nodes.index(inp.node),
                            'connected input port index': inp.node._inputs.index(inp),
                        })

        return data


