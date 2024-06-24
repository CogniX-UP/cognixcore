.. _tutorial:

Tutorial
========

Welcome to the :mod:`cognixcore` tutorial. Creating nodes and using them is
quite simple, as you will see.

.. include:: start example.rst

Now that we've covered the most basic aspects of the library, such as defining nodes, ports and the :code:`update_event`,
lets dive in the various functionalities and gotchas of :code:`cognixcore`. Most of the sections below are also detailed
in the concrete API documentation.

Initializations
---------------

This section briefly explains the initializations and de-initializations that may occur for a node.

__init__
^^^^^^^^

As is typical with every Python class, the :meth:`cognixcore.Node.__init__` constructor is called upon
instantiation of a :code:`Node`. This constructor is only called once.

place_event
^^^^^^^^^^^

The :meth:`cognixcore.Node.place_event` method is invoked whenever a :code:`Node` is placed inside a flow.
Essentially, this defines what should happen when someone "drops" or "creates" a node inside a :code:`Flow`.

.. warning::

   This event might be deprecated in the near future in favor of the :meth:`cognixcore.Node.init` method.

init
^^^^

The :meth:`cognixcore.Node.init` method is defined as an initialization point for a node, but not only at
construction time. Currently, it is invoked whenever a :code:`Flow` is evaluated through a :class:`cognixcore.GraphPlayer`,
right before the :code:`update_event`. More on the :code:`GraphPlayer` later.

stop
^^^^

The :meth:`cognixcore.Node.stop` method is invoked whenever a :code:`Flow` has finished evaluating through a :code:`GraphPlayer`. 

.. include:: executor_graph_player.rst

Frame Node
----------

The :class:`cognixcore.FrameNode` is a special type of node that in conjuction with a :code:`GraphPlayer`. A frame node is evaluated once per "frame". A frame in a :code:`GraphPlayer` denotes an execution step where the player needs to update all its frame nodes, through the approach
described previously. Lets see a basic example.

.. literalinclude:: examples/executors.py
   :language: python
   :linenos:
   :lines: 14-53

We begin by defining a :code:`FrameNode`. This node has only one output. We then implement its :meth:`cognixcore.FrameNode.frame_update` method. This method will be called one per frame, generating
a random number and outputting it through its port. We then create a session, register our node and
instantiate it, along with the :code:`AddNode` from our first example. We then connect the nodes and
play the flow. If we want the current flow of execution to not be stopped, we should pass :code:`True` to the :code:`on_other_thread` parameter, as shown.

.. include:: qol.rst

A better example
----------------

To incorporate the above, we will iterate upon our first example to optimize the code and make it work better with the CogniX Editor.

First, our imports. We're using quite a lot more than before.

.. literalinclude:: examples/better_add.py
   :language: python
   :linenos:
   :lines: 1-13

Number Node
^^^^^^^^^^^

.. literalinclude:: examples/better_add.py
   :language: python
   :linenos:
   :lines: 15-45

Notice that the :code:`NumberNode` now contains a configuration class. In this, we define a mode, giving our node different types of number generation. There is a :code:`random` mode, where the node returns a random number. Then there are two other modes, :code:`int` and :code:`float` for integers and floats respectively. This can also be seen from the :code:`int_num` and :code:`float_num` attributes.

In the :code:`update_event`, we now also set a progress to indicate that our node has started generating the number and that it has finished. Granted, this operation will be really fast and hence won't be visible in the CogniX Editor or any other GUI implementation for a progress state.

Add Node
^^^^^^^^

.. literalinclude:: examples/better_add.py
   :language: Python
   :linenos:
   :lines: 47-95

The :code:`AddNode` now also contains a configuration class, with only one configuration. This configuration allows for easily and dynamically changing the ports of a node. Notice that for this node, we're only altering the inputs. Thus, we have removed the :code:`init_inputs` static attribute, since it is no longer needed.

Our :code:`update_event` logic is now written for the :code:`AddNode` to work with an arbitrary number of inputs. We're also making sure to output a result only if the result is different than a previous iteration. These implementation details might not work for you and you might choose to output the result despite it being the same as a previous iteration. This is specific to the role of the node and the developer behind it.

Finally, note that we're also logging the result. This would show in the CogniX Editor, or any other GUI that taps into the logging system of :code:`cognixcore`.

Using the nodes
^^^^^^^^^^^^^^^

.. literalinclude:: examples/better_add.py
   :language: Python
   :linenos:
   :lines: 101-129

Finally, we're using the nodes in a scripting rather than visual manner. We're creating a session, registering the nodes and creating a flow. We're instantiating two :code:`NumberNode` (s) and one :code:`AddNode`. The first number node generates a random number while the second outputs the number 25. We're then making sure that the add node has two ports, which we set dynamically. Finally, we connect the nodes that work through the default :code:`DataFlowNaive` algorithm.

Better yet, instead of relying on the :code:`DataFlowNaive` algorithm, we can evaluate our graph as a Python program, like this:

.. literalinclude:: examples/better_add.py
   :language: python
   :linenos:
   :lines: 131-131


