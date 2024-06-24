cognixcore.port
===============

.. py:module:: cognixcore.port


Attributes
----------

.. autoapisummary::

   cognixcore.port.default_config


Classes
-------

.. autoapisummary::

   cognixcore.port.PortConfig
   cognixcore.port.NodePort
   cognixcore.port.NodeInput
   cognixcore.port.NodeOutput


Functions
---------

.. autoapisummary::

   cognixcore.port.check_valid_data
   cognixcore.port.check_valid_conn
   cognixcore.port.check_valid_conn_tuple


Module Contents
---------------

.. py:class:: PortConfig

   The PortConfig class is a configuration class for creating ports. It's mainly used for the static init_input
   and init_outputs of custom Node classes, but can also be used for dynamically creating ports for Nodes.
   An instantiated Node's actual inputs and outputs will be of type :class:`NodePort` (:class:`NodeInput`, :class:`NodeOutput`).


   .. py:attribute:: label
      :type:  str
      :value: ''



   .. py:attribute:: type_
      :type:  str
      :value: 'data'



   .. py:attribute:: allowed_data
      :type:  Any
      :value: None



   .. py:attribute:: default
      :type:  Any
      :value: None



.. py:data:: default_config

   An instance of a default port configuration

.. py:class:: NodePort(node, io_pos: cognixcore.rc.PortObjPos, type_: str, label_str: str, allowed_data: type | None = None)

   Bases: :py:obj:`cognixcore.base.Base`


   Base class for inputs and outputs of nodes


   .. py:method:: load(data: dict)

      Recreate the object state from the data dict returned by :code:`data()`.

      Convention: don't call this method in the constructor, invoke it manually
      from outside, if other components can depend on it (and be notified of its
      creation).
      Reason: If another component `X` depends on this one (and
      gets notified when this one is created), `X` should be notified *before*
      it gets notified of creation or loading of subcomponents created during
      this load. (E.g. add-ons need to know the flow before nodes are loaded.)



   .. py:method:: data() -> dict

      Convert the object to a JSON compatible dict.
      Reserved field names are 'GID' and 'version'.



.. py:class:: NodeInput(node, type_: str, label_str: str = '', default=None, allowed_data: type | None = None)

   Bases: :py:obj:`NodePort`


   A port that is an input


   .. py:method:: load(data: dict)

      Recreate the object state from the data dict returned by :code:`data()`.

      Convention: don't call this method in the constructor, invoke it manually
      from outside, if other components can depend on it (and be notified of its
      creation).
      Reason: If another component `X` depends on this one (and
      gets notified when this one is created), `X` should be notified *before*
      it gets notified of creation or loading of subcomponents created during
      this load. (E.g. add-ons need to know the flow before nodes are loaded.)



   .. py:method:: data() -> dict

      Convert the object to a JSON compatible dict.
      Reserved field names are 'GID' and 'version'.



.. py:class:: NodeOutput(node, type_: str, label_str: str = '', allowed_data: type | None = None)

   Bases: :py:obj:`NodePort`


   A port that is an output


.. py:function:: check_valid_data(type_out: type, type_in: type) -> bool

   Checks whether out and input can be connected via their allowed data types.


.. py:function:: check_valid_conn(out: NodeOutput, inp: NodeInput) -> cognixcore.rc.ConnValidType

   Checks if a connection is valid between two node ports.

   :returns: An enum representing the check result


.. py:function:: check_valid_conn_tuple(connection: tuple[NodeOutput, NodeInput])

