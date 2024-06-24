Flow Executors - Graph Players
--------------

This section notes the importance of :class:`cognixcore.FlowExecutor` (s) and :class:`cognixcore.GraphPlayer` (s). 

Per the original `ryvencore <https://github.com/leon-thomm/ryvencore>`_, there were different algorithms to handle the :meth:`cognixcore.Node.update_event` and :meth:`cognixcore.Node.set_output`. The basis of these algorithms is the class :class:`cognixcore.FlowExecutor` and its implementations. Each flow can have its executor set from :meth:`cognixcore.Flow.set_algorithm_mode` or :meth:`cognixcore.Flow.algorithm_mode`. Detailed documentation can be found in :mod:`cognixcore.flow_executor` and :class:`cognixcore.flow_executor.Flow`.

Data Flow
^^^^^^^^^

The :class:`cognixcore.DataFlowNaive` is a simple implementation of data-flow execution. Setting a node output leads to an immediate update in all successors consecutively. No runtime optimization is performed, and some types of graphs can run really slow here, especially if the include "diamonds".

Assumptions for the graph:
- no non-terminating feedback loops

Data Flow Optimized
^^^^^^^^^^^^^^^^^^^

.. warning::

   Check the documentation in :class:`cognixcore.Flow`. This is an original :code:`ryvencore` functionality and is documented
   as such. However, at its current state, :code:`cognixcore` is better suited for such operations through the :code:`GraphPlayer`.

This is a special flow executor which implements some node functions to optimize flow execution. Whenever a new execution is invoked somewhere (some node :class:`cognixcore.Node.update` or output :class:`cognixcore.Node.set_output` is updated), it analyses the graph's connected component (of successors) where the execution was invoked and creates a few data structures to reverse engineer how many input updates every node possibly receives in this execution. A node's outputs are propagated once
no input can still receive new data from a predecessor node. Therefore, while a node gets updated every time an input receives some data, every OUTPUT is only updated ONCE.

This implies that every connection is activated at most once in an execution. This can result in asymptotic speedup in large data flows compared to normal data flow execution where any two executed branches which merge again in the future result in two complete executions of anything that comes after the merge, which quickly produces exponential performance issues.

Exec Flow Naive
^^^^^^^^^^^^^^^

In :class:`cognixcore.ExecFlowNaive`, we deviate from the common data flow paradigm. No data is propagated and instead of :code:`set_output` we have :meth:`cognixcore.Node.exec_output`. For more information, look at the documentation of :class:`cognixcore.Flow`.

Manual Flow
^^^^^^^^^^^

The :class:`cognixcore.ManualFlow` is an executor that doesn't propagate any data between nodes at default. It also doesn't handle the :code:`exec_output` method. This execution algorithm simply keeps a state of the outputs that have been updated through a call to :meth:`cognixcore.Node.set_output`. What we refer to as "manual execution" thus is the external evaluation  of the whole flow graph, through the means of a :class:`cognixcore.GraphPlayer`. While the other executors update their nodes upon connecting and disconnecting their ports, this executor is simply of a state of the current updates and the graph's evaluation is done externally.

Graph Player
^^^^^^^^^^^^

A :class:`cognixcore.GraphPlayer` and its concrete implementation :class:`cognixcore.FlowPlayer` act as evaluators of a graph
as a Python program. Through this component, nodes that are formed into a flow are assembled and eventually evaluated. This
class is associated with the following methods:

- :meth:`cognixcore.GraphPlayer.play`: This method is called when the graph starts playing or is evaluated and will invoked the :meth:`cognixcore.Node.init` method.

- :meth:`cognixcore.GraphPlayer.pause`: This method is called when the graph is paused, but can continue. A pause state is only available on graphs that have a :code:`FrameNode` incorporated, otherwise the graph will evaluate only once and exit, akin to a Python program running and finishing without any other user input.

- :meth:`cognixcore.GraphPlayer.resume`: If the graph can be paused, then it can also be resumed. This method resumes the execution of the current graph.

- :meth:`cognixcore.GraphPlayer.stop`: This method stops the graph completely and is called on demand if the graph contains :code:`FrameNode` (s) or automatically if it doesn't. Invokes the :meth:`cognixcore.Node.stop` method.

How does the default :class:`cognixcore.FlowPlayer` work? The first step is to find all the active nodes in a flow. A node is considered active when it has connections or is a :code:`FrameNode` Subsequently, these nodes are separated into two categories. The root nodes and the frame nodes. The root nodes are nodes that have no input ports connected to them. Essentially, they act as a starting point for the evaluation. The frame nodes will be evaluated per :code:`frame`.

The active nodes are then initialized. Each node may have resources that need to be initialized based on their configuration. The nodes are then evaluated based on a Breadth First Search (BFS) algorithm to ensure that each node is evaluated only once for each connected input. After the evaluation, the algorithm checks the number of active frame nodes. If there are frame nodes present in the graph that need evaluation, they are evaluated. The successors of the frame nodes are then updated as if they were the root nodes. This frame node evaluation process is repeated until the user manually stops the graph or every frame node has finished its operation based on an internal condition.

A simple example on how to play a graph is provided below. Note that the executor is automatically changed to :code:`ManualFlow`, but will be changed back to the previous algorithm node when the
graph evaluation is stopped.

.. literalinclude:: examples/executors.py
   :language: python
   :linenos:
   :lines: 1-11

It's always better to use the :code:`Session` to evaluate a graph through a :code:`GraphPlayer` rather
than through the :code:`GraphPlayer` or the :code:`Flow`, as these methods also invoke certain events and handle threading better, if the player is invoked in another thread (check the :code:`on_other_thread`) parameter of the :meth:`cognixcore.Session.play_flow` method.