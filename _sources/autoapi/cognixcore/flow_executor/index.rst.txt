cognixcore.flow_executor
========================

.. py:module:: cognixcore.flow_executor

.. autoapi-nested-parse::

   The flow executors are responsible for executing the flow. They have access to
   the flow as well as the nodes' internals and are able to perform optimizations.



Classes
-------

.. autoapisummary::

   cognixcore.flow_executor.FlowExecutor
   cognixcore.flow_executor.ManualFlow
   cognixcore.flow_executor.DataFlowNaive
   cognixcore.flow_executor.DataFlowOptimized
   cognixcore.flow_executor.ExecFlowNaive


Functions
---------

.. autoapisummary::

   cognixcore.flow_executor.executor_from_flow_alg
   cognixcore.flow_executor.flow_alg_from_executor


Module Contents
---------------

.. py:class:: FlowExecutor(flow: cognixcore.flow.Flow)

   Base class for special flow execution algorithms.


   .. py:property:: graph


   .. py:property:: graph_rev


   .. py:method:: update_node(node: cognixcore.flow.Node, inp: int)


   .. py:method:: input(node: cognixcore.flow.Node, index: int) -> Any


   .. py:method:: set_output(node: cognixcore.flow.Node, index: int, val)


   .. py:method:: exec_output(node: cognixcore.flow.Node, index: int)


   .. py:method:: conn_added(out: cognixcore.port.NodeOutput, inp: cognixcore.port.NodeInput, silent=False)


   .. py:method:: conn_removed(out: cognixcore.port.NodeOutput, inp: cognixcore.port.NodeInput, silent=False)


.. py:class:: ManualFlow(flow: cognixcore.flow.Flow)

   Bases: :py:obj:`FlowExecutor`


   An executor that doesn't propagate any data between nodes. Doesn't
   handle the exec_output.

   To be used for manual and/or external evaluation of the whole flow graph.


   .. py:method:: update_node(node: cognixcore.flow.Node, inp: int)


   .. py:method:: input(node: cognixcore.flow.Node, index: int)


   .. py:method:: set_output(node: cognixcore.flow.Node, index: int, data)


   .. py:method:: should_input_update(inp: cognixcore.port.NodeInput) -> bool


   .. py:method:: has_updated_outputs(node: cognixcore.flow.Node) -> bool


   .. py:method:: clear_updates()


.. py:class:: DataFlowNaive(flow: cognixcore.flow.Flow)

   Bases: :py:obj:`FlowExecutor`


   The naive implementation of data-flow execution. Naive meaning setting a node output
   leads to an immediate update in all successors consecutively. No runtime optimization
   if performed, and some types of graphs can run really slow here, especially if they
   include "diamonds".

   Assumptions for the graph:
   - no non-terminating feedback loops


   .. py:method:: update_node(node: cognixcore.flow.Node, inp: int)


   .. py:method:: input(node: cognixcore.flow.Node, index: int)


   .. py:method:: set_output(node: cognixcore.flow.Node, index: int, data)


   .. py:method:: exec_output(node: cognixcore.flow.Node, index: int)


   .. py:method:: conn_added(out: cognixcore.port.NodeOutput, inp: cognixcore.port.NodeInput, silent=False)


   .. py:method:: conn_removed(out, inp, silent=False)


.. py:class:: DataFlowOptimized(flow)

   Bases: :py:obj:`DataFlowNaive`


   *(see also documentation in Flow)*

   A special flow executor which implements some node functions to optimise flow execution.
   Whenever a new execution is invoked somewhere (some node or output is updated), it
   analyses the graph's connected component (of successors) where the execution was invoked
   and creates a few data structures to reverse engineer how many input
   updates every node possibly receives in this execution. A node's outputs are
   propagated once no input can still receive new data from a predecessor node.
   Therefore, while a node gets updated every time an input receives some data,
   every OUTPUT is only updated ONCE.
   This implies that every connection is activated at most once in an execution.
   This can result in asymptotic speedup in large data flows compared to normal data flow
   execution where any two executed branches which merge again in the future result in two
   complete executions of everything that comes after the merge, which quickly produces
   exponential performance issues.


   .. py:method:: update_node(node: cognixcore.flow.Node, inp=-1)


   .. py:method:: set_output(node: cognixcore.flow.Node, index: int, data)


   .. py:method:: exec_output(node, index)


   .. py:method:: start_execution(root_node: cognixcore.flow.Node = None, root_output: cognixcore.port.NodeOutput = None)


   .. py:method:: stop_execution()


   .. py:method:: generate_waiting_count(root_node=None, root_output=None)


   .. py:method:: invoke_node_update_event(node, inp)


   .. py:method:: decrease_wait(node)

      decreases the wait count of the node;
      if the count reaches zero, which means there is no other input waiting for data,
      the output values get propagated



   .. py:method:: propagate_outputs(node: cognixcore.flow.Node)

      propagates all outputs of node



   .. py:method:: propagate_output(out)

      pushes an output's value to successors if it has been changed in the execution



.. py:class:: ExecFlowNaive(flow)

   Bases: :py:obj:`FlowExecutor`


   ...


   .. py:method:: update_node(node: cognixcore.flow.Node, inp: int)


   .. py:method:: input(node: cognixcore.flow.Node, index: int)


   .. py:method:: set_output(node: cognixcore.flow.Node, index: int, data)


   .. py:method:: exec_output(node: cognixcore.flow.Node, index)


.. py:function:: executor_from_flow_alg(algorithm: cognixcore.rc.FlowAlg)

.. py:function:: flow_alg_from_executor(exec_type: type[FlowExecutor])

