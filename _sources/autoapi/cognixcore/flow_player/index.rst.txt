cognixcore.flow_player
======================

.. py:module:: cognixcore.flow_player

.. autoapi-nested-parse::

   This module defines the flow players. A flow player is responsible for evaluating
   and executing the graph, much like a :class:`cognixcore.flow_executor.FlowExecutor`.

   However, it is meant as an evaluator that reads the graph as a "python program".
   It gathers all the valid nodes it can find and simultaneously markes the roots nodes.
   Root nodes are nodes that have no inputs associated to them. By implementing a BFS (Breadth-First-Search)
   algorithm, the graph is traversed and nodes are evaluated, avoiding duplicate evaluations.

   This default behavior can be found at the :class:`FlowPlayer` class. For a custom implementation
   of how a graph should be evaluated, refer to :class:`GraphPlayer`.

   The above approach was deemed essential to ensure that graphs can also support streaming contexts for
   real-time applications out of the box, efficiently and easily.



Classes
-------

.. autoapisummary::

   cognixcore.flow_player.GraphActionResponse
   cognixcore.flow_player.GraphState
   cognixcore.flow_player.GraphStateEvent
   cognixcore.flow_player.GraphEvents
   cognixcore.flow_player.GraphTime
   cognixcore.flow_player.GraphPlayer
   cognixcore.flow_player.FlowPlayer


Module Contents
---------------

.. py:class:: GraphActionResponse

   Bases: :py:obj:`enum.IntEnum`


   An enum indicating a response to an action for a graph requested on the Session


   .. py:attribute:: NO_GRAPH

      No graph found to play


   .. py:attribute:: NOT_ALLOWED

      The action requested (play, pause, stop) is being invoked already


   .. py:attribute:: SUCCESS

      The action was succesful


.. py:class:: GraphState(*args, **kwds)

   Bases: :py:obj:`enum.Enum`


   Enum that represents a graph player's state.


   .. py:attribute:: PLAYING


   .. py:attribute:: PAUSED


   .. py:attribute:: STOPPED


.. py:class:: GraphStateEvent(old_state: GraphState, new_state: GraphState)

   Represents a change event


   .. py:method:: __str__()

      Return str(self).



.. py:class:: GraphEvents

   All the events that a graph player may have, associated with the
   :class:`GraphState` states.


   .. py:method:: sub_state_changed(func: Callable[[GraphStateEvent], None], nice=0, one_off=False)


   .. py:method:: unsub_state_changed(func: Callable[[GraphStateEvent], None])


   .. py:method:: sub_event(e_type: GraphState | str, func, nice=0, one_off=False)


   .. py:method:: unsub_event(e_type: GraphState | str, func)


   .. py:method:: reset()

      Resets the all the events.



.. py:class:: GraphTime

   A class that wraps all time related information for a graph player.
   (fps, delta_time, time, etc)

   This class only makes sense if the graph has frame nodes.


   .. py:property:: frames
      The frame-rate this player will attempt to follow.


   .. py:property:: frame_count
      Frame count since time has started. Incremented at the start of each frame


   .. py:property:: time
      Time (seconds) since the player has started.


   .. py:property:: delta_time
      Interval (seconds) between the current frame and the last.


   .. py:method:: frame_dur()

      Frame duration the player will attempt to uphold.



   .. py:method:: avg_fps() -> float

      The average frames per second since the start of time.



   .. py:method:: current_fps() -> float

      The current frames per second



   .. py:method:: reset()


.. py:class:: GraphPlayer(frames: int = 5)

   Bases: :py:obj:`abc.ABC`


   A graph player is a class that handles the processing and evaluating
   of a flow of nodes like it would a python program.


   .. py:property:: flow
      :type: cognixcore.flow.Flow

      The flow for this player.


   .. py:property:: graph_time
      :type: GraphTime

      Time information for this player


   .. py:property:: delta_time
      :type: float

      Convenience method for returning delta-time


   .. py:property:: graph_events
      :type: GraphEvents

      Events for this graph


   .. py:method:: set_frames(value: int)


   .. py:property:: state
      The state of the player.


   .. py:method:: play()
      :abstractmethod:


      Plays or evaluates the graph.



   .. py:method:: pause()
      :abstractmethod:


      Pauses the graph if it had any real-time elements (FrameNodes).



   .. py:method:: resume()
      :abstractmethod:


      Resumes the graph if it was paused.



   .. py:method:: stop()
      :abstractmethod:


      Stops the graph.



.. py:class:: FlowPlayer(frames: int = 30)

   Bases: :py:obj:`GraphPlayer`


   The default implementation of a Graph Player in CogniX


   .. py:property:: flow
      The flow for this player.


   .. py:method:: play()

      Plays or evaluates the graph.



   .. py:method:: pause()

      Pauses the graph if it had any real-time elements (FrameNodes).



   .. py:method:: resume()

      Resumes the graph if it was paused.



   .. py:method:: stop()

      Stops the graph.



