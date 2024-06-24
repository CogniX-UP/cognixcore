cognixcore.rc
=============

.. py:module:: cognixcore.rc

.. autoapi-nested-parse::

   Namespace for enum types etc.



Classes
-------

.. autoapisummary::

   cognixcore.rc.ConnectionInfo
   cognixcore.rc.FlowAlg
   cognixcore.rc.PortObjPos
   cognixcore.rc.ConnValidType
   cognixcore.rc.ProgressState


Module Contents
---------------

.. py:class:: ConnectionInfo

   Characterizes a connection without the ports


   .. py:attribute:: node_out
      :type:  cognixcore.node.Node
      :value: None



   .. py:attribute:: out_i
      :type:  int
      :value: 0



   .. py:attribute:: node_inp
      :type:  cognixcore.node.Node
      :value: None



   .. py:attribute:: inp__i
      :type:  int
      :value: 0



   .. py:property:: out_port


   .. py:property:: inp_port


.. py:class:: FlowAlg

   Bases: :py:obj:`enum.IntEnum`


   Used for serialization purposes


   .. py:attribute:: MANUAL
      :value: 0



   .. py:attribute:: DATA
      :value: 1



   .. py:attribute:: EXEC
      :value: 2



   .. py:attribute:: DATA_OPT
      :value: 3



   .. py:method:: str(mode) -> str
      :staticmethod:


      Returns one of the following: [manual, data, exec, data opt]



   .. py:method:: from_str(mode)
      :staticmethod:


      Returns a FlowAlg from a string



.. py:class:: PortObjPos

   Bases: :py:obj:`enum.IntEnum`


   Used for performance reasons


   .. py:attribute:: INPUT
      :value: 1



   .. py:attribute:: OUTPUT
      :value: 2



.. py:class:: ConnValidType

   Bases: :py:obj:`enum.IntEnum`


   Result from a connection validity test between two node ports


   .. py:attribute:: VALID

      Valid Connection


   .. py:attribute:: SAME_NODE

      Invalid Connection due to same node


   .. py:attribute:: SAME_IO

      Invalid Connection due to both ports being input or output


   .. py:attribute:: IO_MISSMATCH

      Invalid Connection due to output being an input and vice-versa


   .. py:attribute:: DIFF_ALG_TYPE

      Invalid Connection due to different algorithm types (data or exec)


   .. py:attribute:: DATA_MISSMATCH

      Invalid Connection due to input / output Data type checking


   .. py:attribute:: INPUT_TAKEN

      Invalid Connection due to input being connected to another output


   .. py:attribute:: ALREADY_CONNECTED

      Invalid Connect check

      Optional Check - A connect action was attempted but nodes were already connected!


   .. py:attribute:: ALREADY_DISCONNECTED

      Invalid Disconnect check

      Optional Check - A disconnect action was attemped on disconnected ports!


   .. py:method:: get_error_message(conn_valid_type: ConnValidType, out: cognixcore.port.NodeOutput, inp: cognixcore.port.NodeInput) -> str
      :classmethod:


      An error message for the various ConnValidType types



.. py:class:: ProgressState(max_value: numbers.Real = 1, value: numbers.Real = 0, message: str = '')

   Represents a progress state / bar.

   A negative value indicates indefinite progress


   .. py:method:: INDEFINITE_PROGRESS()
      :classmethod:



   .. py:method:: __str__() -> str

      Return str(self).



   .. py:property:: max_value
      :type: numbers.Real

      Max value of the progress.


   .. py:property:: value
      :type: numbers.Real

      Current value of the progress. A negative value indicates indefinite progress


   .. py:method:: is_indefinite() -> bool

      Returns true if there is indefinite progress



   .. py:method:: percentage() -> numbers.Real


   .. py:method:: as_percentage() -> ProgressState

      Returns a new progress state so that max_value = 1



