A good starting example
--------------------

In this example, we're going to see how to create two nodes that can work together. One node represents a :code:`Number` while the other adds two :code:`Numbers`.

First, our imports. All we need is the :class:`cognixcore.Node` and :class:`cognixcore.PortConfig` from :mod:`cognixcore` and the :code:`Number` from :code:`numbers` Python package.

.. literalinclude:: examples/simple_add.py
   :language: python
   :linenos:
   :lines: 1-6

Now, we will define two classes that represent our nodes.

NumberNode
^^^^^^^^^^
.. literalinclude:: examples/simple_add.py
   :language: python
   :linenos:
   :lines: 8-23


Notice that our class extends the :class:`cognixcore.Node` class. In doing so we've created a node blueprint. We've also defined two class attributes, namely :attr:`cognixcore.Node.title` and :attr:`cognixcore.Node.version`. It's a good convention to define these attributes, as they might be used in some other context. *For example*, in the CogniX Editor, the :code:`title` is displayed over a node's GUI, while the :code:`version` is used to filter out which nodes we want to include (no :code:`version` means the node won't be included in the editor packages)

The :attr:`cognixcore.Node.init_outputs` attribute is a list that contains the output ports that we want our node to have at instantiation. The :class:`cognixcore.PortConfig` class is responsible for generating the port that we want. We can give the port a :code:`label` and also set restrictions on its output type, by using the :attr:`cognixcore.PortConfig.allowed_data` attribute. The :code:`allowed_data` can be :code:`None`, which essentially tells :code:`cognixcore` that this port can output anything, or any kind fo python `type hint <https://docs.python.org/3/library/typing.html>`_. Allowed data through :code:`type hinting` is checked when nodes are connected as well as when outputing data through a port. These checks are made possible through the excellent `beartype <https://beartype.readthedocs.io/en/latest/>`_ package.

Alls that's left is our "processing" logic. How will the node update itself? By overriding the :meth:`cognixcore.Node.update_event` method. The :code:`update_event` updates the node based on an input port. In this case, the :code:`NumberNode` does not have any inputs and only needs to output the internal number it represents.

AddNode
^^^^^^^

.. literalinclude:: examples/simple_add.py
   :language: python
   :linenos:
   :lines: 25-63

In similar fashion, we define an :code:`AddNode`. The difference between the :code:`AddNode` and the :code:`NumberNode` is that this node has input ports through the :attr:`cognixcore.Node.init_inputs` attribute. Notice that that both of the inputs have their :code:`allowed_data` set to :code:`Number`. This is an essential part that will be explained later.

Lets interpret the :code:`update_event`. The :code:`AddNode` is updated with a given input. Using the :meth:`cognixcore.Node.input` method, we're reading the value of the connected output of a port that outputs a :code:`Number` as input to the :code:`AddNode`. In our case, this should be an output port of a :code:`NumberNode`, since we have not defined any other nodes that output numbers. We're then checking to see if our input is indeed a number, otherwise we set it to 0. We proceed to grab the value of the other input port in a similar fashion, add them together and output them through the only output port of the :code:`AddNode`.

Using the nodes
^^^^^^^^^^^^^^^

Defining the nodes is a good starting point for any kind of node-based library. However, there is a need to also be able to create, connect them and eventually evaluate a graph. This would typically happen in a visual editor, such as the CogniX Editor, but can also happen in a script.


.. literalinclude:: examples/simple_add.py
   :language: python
   :linenos:
   :lines: 65-90

We're starting by creating a :class:`cognixcore.Session`, then registering our nodes to the :code:`Session`. :code:`cognixcore`, despite offering saving and loading capabilities, does not save/load the node types. This is left to the external "package" manager that any user of the library might have to create.

After the :code:`Session` is created, we create a :class:`cognixcore.Flow` to the session, titled :code:`Example`. We then proceed to create two :code:`NumberNodes` and assign a number to each of them. Lastly, an :code:`AddNode` is created and the two outputs of the number nodes are connected to the inputs of the add node. Notice that the :meth:`cognixcore.Flow.connect_nodes` has a :code:`silent` parameter, which is defaulted to :code:`False`. When set to :code:`False`, data will be propagated from the  number node to the add node through the :code:`update_event` and :code:`set_ouput` methods, based on the kind of :class:`cognixcore.FlowExecutor` executor attached to :code:`Flow`. More on that later.

And that's it, we have defined two different kind of nodes, imported them in a session, connected them and let them do their magic. Easy, isn't it?