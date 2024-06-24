cognixcore.models
=================

.. py:module:: cognixcore.models

.. autoapi-nested-parse::

   This module defines pydantic models for the session, nodes, ports

   While pydantic is not a requirement for this library, this optional module
   provides utilities to work with the serialized versions of the corresponding
   cognix core objects.

   This model is a requirement if cognixcore is installed with the Rest API
   dependency.



Classes
-------

.. autoapisummary::

   cognixcore.models.CognixModel
   cognixcore.models.PortModel
   cognixcore.models.ConnectionModel
   cognixcore.models.NodeTypeModel
   cognixcore.models.NodeModel
   cognixcore.models.FlowModel
   cognixcore.models.VarModel
   cognixcore.models.SessionModel


Module Contents
---------------

.. py:class:: CognixModel(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   The base model for a cognixcore Base class


   .. py:attribute:: GID
      :type:  int


.. py:class:: PortModel(/, **data: Any)

   Bases: :py:obj:`CognixModel`


   A model representing a port


   .. py:attribute:: port_type
      :type:  str


   .. py:attribute:: label
      :type:  str


   .. py:attribute:: allowed_data
      :type:  str


.. py:class:: ConnectionModel(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   A model representing a connection between two nodes


   .. py:attribute:: parent_node_index
      :type:  int


   .. py:attribute:: out_port_index
      :type:  int


   .. py:attribute:: conn_node_index
      :type:  int


   .. py:attribute:: conn_inp_port_index
      :type:  int


.. py:class:: NodeTypeModel(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   A model representing a node type


   .. py:attribute:: identifier
      :type:  str


   .. py:attribute:: version
      :type:  str


   .. py:attribute:: desc
      :type:  str


.. py:class:: NodeModel(/, **data: Any)

   Bases: :py:obj:`CognixModel`


   A model representing a Node with its most basic structure


   .. py:attribute:: identifier
      :type:  str


   .. py:attribute:: version
      :type:  str


   .. py:attribute:: title
      :type:  str


   .. py:attribute:: inputs
      :type:  list[PortModel]


   .. py:attribute:: outputs
      :type:  list[PortModel]


.. py:class:: FlowModel(/, **data: Any)

   Bases: :py:obj:`CognixModel`


   A model representing a Flow.


   .. py:attribute:: title
      :type:  str


   .. py:attribute:: alg_mode
      :type:  str


   .. py:attribute:: nodes
      :type:  list[NodeModel]


   .. py:attribute:: connections
      :type:  list[ConnectionModel]


.. py:class:: VarModel(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   A model representing a Variable.


   .. py:attribute:: name
      :type:  str | None


   .. py:attribute:: value_type_id
      :type:  str | None


   .. py:attribute:: value
      :type:  dict | None


.. py:class:: SessionModel(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   A mode representing a whole s


