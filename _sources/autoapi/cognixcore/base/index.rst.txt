cognixcore.base
===============

.. py:module:: cognixcore.base

.. autoapi-nested-parse::

   This module defines the :class:`Base` class for most internal components,
   implementing features such as a unique ID, a system for save and load,
   and a very minimal event system.



Attributes
----------

.. autoapisummary::

   cognixcore.base.EP
   cognixcore.base.InfoType


Classes
-------

.. autoapisummary::

   cognixcore.base.TypeMeta
   cognixcore.base.TypeSerializer
   cognixcore.base.BasicSerializer
   cognixcore.base.IDCtr
   cognixcore.base.Event
   cognixcore.base.NoArgsEvent
   cognixcore.base.Base
   cognixcore.base.Identifiable
   cognixcore.base.IHaveIdentifiable
   cognixcore.base.IdentifiableGroups


Functions
---------

.. autoapisummary::

   cognixcore.base.find_identifiable


Module Contents
---------------

.. py:class:: TypeMeta

   Metadata regarding a type. Useful if we want to build packages.


   .. py:attribute:: package
      :type:  str


   .. py:attribute:: type_id
      :type:  str


   .. py:method:: identifier()


.. py:class:: TypeSerializer

   Bases: :py:obj:`abc.ABC`


   Serializes/Deserializes an object into JSON compatible form.


   .. py:method:: serialize(obj)
      :abstractmethod:


      Serializes the object



   .. py:method:: deserialize(data)
      :abstractmethod:


      Deserializes the object from the data



   .. py:method:: default()
      :abstractmethod:


      Retrieves a default value for this type



.. py:class:: BasicSerializer(default_obj_type: type)

   Bases: :py:obj:`TypeSerializer`


   This default implementation simply returns the object as is. Useful
   for types that are already JSON compatible.


   .. py:method:: serialize(obj)

      Serializes the object



   .. py:method:: deserialize(data)

      Deserializes the object from the data



   .. py:method:: default()

      Retrieves a default value for this type



.. py:class:: IDCtr

   A simple ascending integer ID counter.
   Guarantees uniqueness during lifetime or the program (not only of the Session).
   This approach is preferred over UUIDs because UUIDs need a networking context
   and require according system support which might not be available everywhere.


   .. py:method:: count()

      Increases the counter and returns the new count. Starting value is 0



   .. py:method:: set_count(cnt)


.. py:data:: EP

   A Parameter Spec for the :class:`Event` class. For Generic purposes.

.. py:class:: Event

   Bases: :py:obj:`Generic`\ [\ :py:obj:`EP`\ ]


   Implements a generalization of the observer pattern, with additional
   priority support. The lower the value, the earlier the callback
   is called. The default priority is 0.

   Negative priorities internally to ensure
   precedence of internal observers over all user-defined ones.


   .. py:method:: clear()


   .. py:method:: sub(callback: Callable[EP, None], nice=0, one_off=False)

      Registers a callback function. The callback must accept compatible arguments.
      The optional :code:`nice` parameter can be used to set the priority of the
      callback. The lower the priority, the earlier the callback is called.
      :code:`nice` can range from -5 to 10. The :code:`one_off` parameter indicates
      that the callback will be removed once it has been invoked.

      Negative priorities indicate internal functions. Users should not set these.



   .. py:method:: unsub(callback: Callable[EP, None])

      De-registers a callback function. The function must have been added previously.



   .. py:method:: emit(*args: EP, **kwargs: EP)

      Emits an event by calling all registered callback functions with parameters
      given by :code:`args`.



.. py:class:: NoArgsEvent

   Bases: :py:obj:`Event`\ [\ [\ ]\ ]


   Just wraps the Event[[]] for syntactic sugar. Not usefull in any other way.


.. py:class:: Base

   Base class for all abstract components. It provides:

   Functionality for ID counting:
       - an automatic :code:`GLOBAL_ID` unique during the lifetime of the program
       - a :code:`PREV_GLOBAL_ID` for re-identification after save & load,
         automatically set in :code:`load()`

   Serialization:
       - the :code:`data()` method gets reimplemented by subclasses to serialize
       - the :code:`load()` method gets reimplemented by subclasses to deserialize
       - the static attribute :code:`Base.complete_data_function` can be set to
         a function which extends the serialization process by supplementing the
         data dict with additional information, which is useful in many
         contexts, e.g. a frontend does not need to implement separate save & load
         functions for its GUI components


   .. py:method:: obj_from_prev_id(prev_id: int)
      :classmethod:


      returns the object with the given previous id



   .. py:attribute:: complete_data_function


   .. py:method:: complete_data(data: dict)
      :staticmethod:


      Invokes the customizable :code:`complete_data_function` function
      on the dict returned by :code:`data`. This does not happen automatically
      on :code:`data()` because it is not always necessary (and might only be
      necessary once, not for each component individually).



   .. py:attribute:: version
      :type:  str
      :value: None



   .. py:method:: data() -> dict

      Convert the object to a JSON compatible dict.
      Reserved field names are 'GID' and 'version'.



   .. py:method:: load(data: dict)

      Recreate the object state from the data dict returned by :code:`data()`.

      Convention: don't call this method in the constructor, invoke it manually
      from outside, if other components can depend on it (and be notified of its
      creation).
      Reason: If another component `X` depends on this one (and
      gets notified when this one is created), `X` should be notified *before*
      it gets notified of creation or loading of subcomponents created during
      this load. (E.g. add-ons need to know the flow before nodes are loaded.)



.. py:data:: InfoType

   TypeVar for specifying an Identifiable's info, if it exists

.. py:class:: Identifiable(id_name: str, id_prefix: str | None = None, legacy_ids: list[str] = [], info: InfoType | None = None)

   Bases: :py:obj:`Generic`\ [\ :py:obj:`InfoType`\ ]


   A **container** that provides metadata useful for grouping.


   .. py:method:: __str__() -> str

      Return str(self).



   .. py:property:: id
      :type: str

      The id of this identifiable. A combination of the prefix (if used) and the name.


   .. py:property:: name
      :type: str

      The name of this identifiable.


   .. py:property:: prefix
      :type: str | None

      The prefix of this identifable


   .. py:property:: info
      The info of an identifiable


.. py:class:: IHaveIdentifiable

   If an object has identifiable information, it must conform to this contract


   .. py:property:: identifiable
      :type: Identifiable



.. py:function:: find_identifiable(id: str, to_search: collections.abc.Iterable[Identifiable[InfoType]])

   Searches for a :class:`Identifiable` with a given id.


.. py:class:: IdentifiableGroups(ids: collections.abc.Iterable[Identifiable[InfoType]] = [])

   Bases: :py:obj:`Generic`\ [\ :py:obj:`InfoType`\ ]


   Groups identifiables by their prefix and name. Identifiables with no prefix are groupped under 'global'

   Also holds structures for getting an identifiable by its name.


   .. py:attribute:: NO_PREFIX_ROOT
      :value: 'global'



   .. py:method:: __str__() -> str

      Return str(self).



   .. py:property:: id_set
      :type: set[Identifiable[InfoType]]

      A set containing all the Identifiables


   .. py:property:: id_map
      :type: collections.abc.Mapping[str, Identifiable[InfoType]]

      identifiable}

      :type: A map with layout {id


   .. py:property:: groups
      :type: collections.abc.Mapping[str, collections.abc.Mapping[str, Identifiable[InfoType]]]

      The identifiable groupped by their prefixes


   .. py:method:: rename(new_name: str, old_name: str, group: str)


   .. py:method:: add(id: Identifiable[InfoType]) -> bool

      Adds an identifiable to its group. Creates the group if it doesn't exist



   .. py:method:: remove(id: Identifiable[InfoType])

      Removes an identifiable from its group. Deletes the group if it's empty



   .. py:method:: group(group_id: str) -> None | collections.abc.Mapping[str, Identifiable[InfoType]]

      Retrieves a specific group. group_id must exist as a valid group.



   .. py:method:: group_infos(group_id: str) -> set[Self]


   .. py:method:: remove_group(group_id: str, emit_id_removed=False) -> bool

      Removes a group. group_id must exist as a valid group



   .. py:method:: groups_from_path(path: str)

      Retrieves all groups whose prefix contains the path

      Useful for "imitating" sub-groups



   .. py:method:: remove_groups_from_path(path: str)

      Removes all groups whos prefix contains the path

      Useful for "imitating" sub-groups



