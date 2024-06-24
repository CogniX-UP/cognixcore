cognixcore.info_msgs
====================

.. py:module:: cognixcore.info_msgs


Classes
-------

.. autoapisummary::

   cognixcore.info_msgs.InfoMsgs
   cognixcore.info_msgs.MSG_COLORS


Module Contents
---------------

.. py:class:: InfoMsgs

   A few handy static methods for writing different kinds of messages to the output console only if info msgs are
   enabled.


   .. py:attribute:: enabled
      :value: False



   .. py:attribute:: enabled_errors
      :value: False



   .. py:attribute:: traceback_enabled
      :value: False



   .. py:method:: enable(traceback=False)
      :staticmethod:



   .. py:method:: enable_errors(traceback=True)
      :staticmethod:



   .. py:method:: disable()
      :staticmethod:



   .. py:method:: write(*args)
      :staticmethod:



   .. py:method:: write_err(*args)
      :staticmethod:



.. py:class:: MSG_COLORS

   .. py:attribute:: HEADER
      :value: '\x1b[95m'



   .. py:attribute:: OKBLUE
      :value: '\x1b[94m'



   .. py:attribute:: OKCYAN
      :value: '\x1b[96m'



   .. py:attribute:: OKGREEN
      :value: '\x1b[92m'



   .. py:attribute:: WARNING
      :value: '\x1b[93m'



   .. py:attribute:: FAIL
      :value: '\x1b[91m'



   .. py:attribute:: ENDC
      :value: '\x1b[0m'



   .. py:attribute:: BOLD
      :value: '\x1b[1m'



   .. py:attribute:: UNDERLINE
      :value: '\x1b[4m'



