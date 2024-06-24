cognixcore.flow
===============

.. py:module:: cognixcore.flow

.. autoapi-nested-parse::

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
   on a DP algorithm running in :math:`\mathcal{O}(|V|+ |E|)` time, where
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



Classes
-------

.. autoapisummary::

   cognixcore.flow.Flow


Module Contents
---------------

.. py:class:: Flow(session: cognixcore.session.Session, title: str)

   Bases: :py:obj:`cognixcore.base.Base`


   Manages all abstract flow components (nodes, edges, executors, etc.)
   and exposes methods for modification.


   .. py:property:: algorithm_mode
      :type: cognixcore.rc.FlowAlg

      The current algorithm mode of the flow as an enum.

      One-to-one with an executor type.


   .. py:property:: executor
      :type: cognixcore.flow_executor.FlowExecutor

      Returns the current executor of the Flow


   .. py:property:: logger
      :type: logging.Logger

      Returns the logger of the flow, based on the logging addon.


   .. py:property:: player
      :type: cognixcore.flow_player.GraphPlayer

      A player that can evaluate the flow as if it were a python program.


   .. py:method:: load(data: dict)

      Loading a flow from data as previously returned by ``Flow.data()``.



   .. py:method:: load_components(nodes_data, conns_data)

      Loading nodes and their connections from data as previously returned
      by :code:`Flow.data()`. This method will call :code:`Node.rebuilt()` after
      connections are established on all nodes.
      Returns the new nodes and connections.



   .. py:method:: create_node(node_class: type[cognixcore.node.NodeType], data=None, silent=False) -> cognixcore.node.NodeType

      Creates, adds and returns a new node object



   .. py:method:: add_node(node: cognixcore.node.Node, silent=False)

      Places the node object in the graph, Stores it, and causes the node's
      ``Node.place_event()`` to be executed. ``Flow.create_node()`` automatically
      adds the node already, so no need to call this manually.



   .. py:method:: remove_node(node: cognixcore.node.Node, silent=False)

      Removes a node from the flow without deleting it. Can be added again
      with ``Flow.add_node()``.



   .. py:method:: add_node_input(node: cognixcore.node.Node, inp: cognixcore.port.NodeInput, _call_flow_changed=True)

      updates internal data structures



   .. py:method:: add_node_output(node: cognixcore.node.Node, out: cognixcore.port.NodeOutput, _call_flow_changed=True)

      updates internal data structures.



   .. py:method:: remove_node_input(node: cognixcore.node.Node, inp: cognixcore.port.NodeInput, _call_flow_changed=True)

      updates internal data structures.



   .. py:method:: remove_node_output(node: cognixcore.node.Node, out: cognixcore.port.NodeOutput, _call_flow_changed=True)

      updates internal data structures.



   .. py:method:: connection_info(c: tuple[cognixcore.port.NodeOutput, cognixcore.port.NodeInput])

      Returns information about a connection without the ports



   .. py:method:: check_connection_validity(c: tuple[cognixcore.port.NodeOutput, cognixcore.port.NodeInput]) -> cognixcore.rc.ConnValidType

      Checks whether a considered connect action is legal.

      Does not check if the ports are connected or disconnected



   .. py:method:: can_ports_connect(c: tuple[cognixcore.port.NodeOutput, cognixcore.port.NodeInput]) -> cognixcore.rc.ConnValidType

      Same as :code:`Flow.check_connection_validity()`

      Also checks if nodes already connected or if input is connected to another output



   .. py:method:: can_ports_disconnect(c: tuple[cognixcore.port.NodeOutput, cognixcore.port.NodeInput]) -> cognixcore.rc.ConnValidType

      Same as :code:`Flow.check_connection_validity()`

      Also checks if nodes already disconnected



   .. py:method:: connect_from_info(conn: cognixcore.rc.ConnectionInfo, silent=False)


   .. py:method:: connect_nodes(out: cognixcore.node.Node, out_i: int, inp: cognixcore.node.Node, inp_i: int, silent=False)


   .. py:method:: connect_ports(out: cognixcore.port.NodeOutput | int, inp: cognixcore.port.NodeInput | int, silent=False) -> tuple[cognixcore.port.NodeOutput, cognixcore.port.NodeInput] | None

      Connects two node ports. Returns the connection if successful, None otherwise.



   .. py:method:: disconnect_from_info(conn: cognixcore.rc.ConnectionInfo, silent=False)


   .. py:method:: disconnect_nodes(out: cognixcore.node.Node, out_i: int, inp: cognixcore.node.Node, inp_i: int, silent=False)


   .. py:method:: disconnect_ports(out: cognixcore.port.NodeOutput, inp: cognixcore.port.NodeInput, silent=False)

      Disconnects two node ports.



   .. py:method:: add_connection(c: tuple[cognixcore.port.NodeOutput, cognixcore.port.NodeInput], silent=False)

      Adds an edge between two node ports.



   .. py:method:: remove_connection(c: tuple[cognixcore.port.NodeOutput, cognixcore.port.NodeInput], silent=False)

      Removes an edge.



   .. py:method:: connected_inputs(out: cognixcore.port.NodeOutput) -> list[cognixcore.port.NodeInput]

      Returns a list of all connected inputs to the given output port.



   .. py:method:: connected_output(inp: cognixcore.port.NodeInput) -> cognixcore.port.NodeOutput | None

      Returns the connected output port to the given input port, or
      :code:`None` if it is not connected.



   .. py:method:: set_executor(executor: cognixcore.flow_executor.FlowExecutor, silent=False)

      Sets the flow executor



   .. py:method:: set_algorithm_mode(mode: cognixcore.rc.FlowAlg | str, silent=False)

      Sets the algorithm mode of the flow, possible string values
      are 'manual', 'data', 'data opt', and 'exec'.

      Internally sets the corresponding executor.



   .. py:method:: data() -> dict

      Serializes the flow: returns a JSON compatible dict containing all
      data of the flow.



