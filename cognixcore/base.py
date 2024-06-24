"""
This module defines the :class:`Base` class for most internal components,
implementing features such as a unique ID, a system for save and load,
and a very minimal event system.
"""
from typing import Self
from bisect import insort
from collections.abc import Iterable, Set, Mapping
from typing import Generic, TypeVar, ParamSpec, Callable, Any
from types import MappingProxyType
from dataclasses import dataclass
from abc import ABC, abstractmethod
from beartype.door import is_bearable

@dataclass
class TypeMeta:
    """Metadata regarding a type. Useful if we want to build packages."""
    package: str
    type_id: str
    
    def identifier(self):
        return f"{self.package}.{self.type_id}"
    
class TypeSerializer(ABC):
    """
    Serializes/Deserializes an object into JSON compatible form.
    """
    
    @abstractmethod
    def serialize(self, obj):
        """Serializes the object"""
        pass
    
    @abstractmethod
    def deserialize(self, data):
        """Deserializes the object from the data"""
        pass
    
    @abstractmethod
    def default(self):
        """Retrieves a default value for this type"""
        pass

class BasicSerializer(TypeSerializer):
    """
    This default implementation simply returns the object as is. Useful
    for types that are already JSON compatible.
    """
    
    def __init__(self, default_obj_type: type):
        self.default_obj_type = default_obj_type
        self._type = default_obj_type
    
    def serialize(self, obj):
        if not is_bearable(obj, self._type):
            raise ValueError(f"{obj} is not of type {self._type}. Cannot serialize.")
        return obj

    def deserialize(self, data):
        if not is_bearable(data, self._type):
            raise ValueError(f"{data} is not of type {self._type}. Cannot deserialize.")
        return data
    
    def default(self):
        return self.default_obj_type()
    
class IDCtr:
    """
    A simple ascending integer ID counter.
    Guarantees uniqueness during lifetime or the program (not only of the Session).
    This approach is preferred over UUIDs because UUIDs need a networking context
    and require according system support which might not be available everywhere.
    """

    def __init__(self):
        self.ctr = -1

    def count(self):
        """Increases the counter and returns the new count. Starting value is 0"""
        self.ctr += 1
        return self.ctr

    def set_count(self, cnt):
        if cnt < self.ctr:
            raise Exception("Decreasing ID counters is illegal")
        else:
            self.ctr = cnt

EP = ParamSpec('EP')
"""A Parameter Spec for the :class:`Event` class. For Generic purposes."""

class Event(Generic[EP]):
    """
    Implements a generalization of the observer pattern, with additional
    priority support. The lower the value, the earlier the callback
    is called. The default priority is 0.
    
    Negative priorities internally to ensure
    precedence of internal observers over all user-defined ones.
    """

    def __init__(self):
        self._slots: dict[int, set] = {}
        self._ordered_slot_pos = []
        self._slot_priorities = {}
        self._one_offs = set()

    def clear(self):
        self._slots: dict[int, set] = {}
        self._ordered_slot_pos = []
        self._slot_priorities = {}
        
    def sub(self, callback: Callable[EP, None], nice=0, one_off=False):
        """
        Registers a callback function. The callback must accept compatible arguments.
        The optional :code:`nice` parameter can be used to set the priority of the
        callback. The lower the priority, the earlier the callback is called.
        :code:`nice` can range from -5 to 10. The :code:`one_off` parameter indicates
        that the callback will be removed once it has been invoked.
        
        Negative priorities indicate internal functions. Users should not set these.
        """
        assert -5 <= nice <= 10
        assert self._slot_priorities.get(callback) is None

        cb_set = self._slots.get(nice)
        if cb_set is None:
            cb_set = self._slots[nice] = set()
            insort(self._ordered_slot_pos, nice)
            
        cb_set.add(callback)
        if one_off:
            self._one_offs.add(callback)
        self._slot_priorities[callback] = nice

    def unsub(self, callback: Callable[EP, None]):
        """
        De-registers a callback function. The function must have been added previously.
        """
        self.__unsub(callback, True)
    
    def __unsub(self, callback: Callable[EP, None], check_one_off: bool):
        """
        De-registers a function that was added. If :code:`check_one_off`, attempts to remove
        it as a one_off function. This is an internal function.
        """
        nice = self._slot_priorities[callback]
        cb_set = self._slots[nice]
        cb_set.remove(callback)
        del self._slot_priorities[callback]

        if len(cb_set) == 0:
            del self._slots[nice]
            self._ordered_slot_pos.remove(nice)
        
        if check_one_off and callback in self._one_offs:
            self._one_offs.remove(callback)

    def emit(self, *args: EP.args, **kwargs: EP.kwargs):
        """
        Emits an event by calling all registered callback functions with parameters
        given by :code:`args`.
        """

        # we're using the ordered list to run through the events
        for nice in self._ordered_slot_pos:
            for cb in self._slots[nice]:
                cb(*args)
        
        for one_off_func in self._one_offs:
            self.__unsub(one_off_func, False)
        
        self._one_offs.clear()


class NoArgsEvent(Event[[]]):
    """Just wraps the Event[[]] for syntactic sugar. Not usefull in any other way."""
    pass


class Base:
    """
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
    """

    # static attributes

    _global_id_ctr = IDCtr()

    # TODO: this produces a memory leak, because the objects are never removed
    #  from the dict. It shouldn't be a problem as long as PREF_GLOBAL_ID is
    #  only used for loading, but I'd be happy to avoid this if possible
    _prev_id_objs = {}

    @classmethod
    def obj_from_prev_id(cls, prev_id: int):
        """returns the object with the given previous id"""
        return cls._prev_id_objs.get(prev_id)

    complete_data_function = lambda data: data

    @staticmethod
    def complete_data(data: dict):
        """
        Invokes the customizable :code:`complete_data_function` function
        on the dict returned by :code:`data`. This does not happen automatically
        on :code:`data()` because it is not always necessary (and might only be
        necessary once, not for each component individually).
        """
        return Base.complete_data_function(data)


    # optional version which, if set, will be stored in :code:`data()`
    version: str = None

    # non-static

    def __init__(self):
        self.global_id = self._global_id_ctr.count()

        # the following attributes are set in :code:`load()`
        self.prev_global_id = None
        self.prev_version = None

    def data(self) -> dict:
        """
        Convert the object to a JSON compatible dict.
        Reserved field names are 'GID' and 'version'.
        """
        return {
            'GID': self.global_id,

            # version optional
            **({'version': self.version}
               if self.version is not None
               else {})
        }

    def load(self, data: dict):
        """
        Recreate the object state from the data dict returned by :code:`data()`.

        Convention: don't call this method in the constructor, invoke it manually
        from outside, if other components can depend on it (and be notified of its
        creation).
        Reason: If another component `X` depends on this one (and
        gets notified when this one is created), `X` should be notified *before*
        it gets notified of creation or loading of subcomponents created during
        this load. (E.g. add-ons need to know the flow before nodes are loaded.)
        """

        if data is not None:
            self.prev_global_id = data['GID']
            self._prev_id_objs[self.prev_global_id] = self
            self.prev_version = data.get('version')

InfoType = TypeVar('InfoType')
"""TypeVar for specifying an Identifiable's info, if it exists""" 

class Identifiable(Generic[InfoType]):
    """
    A **container** that provides metadata useful for grouping.
    """
    
    def __init__(
        self,
        id_name: str,
        id_prefix: str | None = None,
        legacy_ids: list[str] = [],
        info: InfoType | None = None
    ):
        self._id_prefix = id_prefix
        self._id_name = id_name
        self.legacy_ids = legacy_ids
        
        prefix = f'{self._id_prefix}.' if self._id_prefix else ''
        self._id = f'{prefix}{self.name}'
        
        self._info = info
    
    def __str__(self) -> str:
        return f"prexix: {self._id_prefix} name: {self._id_name} info: {self.info}"
    
    @property
    def id(self) -> str:
        """The id of this identifiable. A combination of the prefix (if used) and the name."""
        return self._id

    @property
    def name(self) -> str:
        """The name of this identifiable."""
        return self._id_name
    
    @property
    def prefix(self) -> str | None:
        """The prefix of this identifable"""
        return self._id_prefix
    
    @property
    def info(self):
        """The info of an identifiable"""
        return self._info

class IHaveIdentifiable:
    """If an object has identifiable information, it must conform to this contract"""
    
    @property
    def identifiable(self) -> Identifiable:
        raise NotImplemented("The identifiable method must be implemented") 

def find_identifiable(id: str, to_search: Iterable[Identifiable[InfoType]]):
    """Searches for a :class:`Identifiable` with a given id."""
    
    for nc in to_search:
        if nc.id == id:
            return nc
    else:  # couldn't find a identifiable with this identifier => search in legacy_ids
        for nc in to_search:
            if id in nc.legacy_ids:
                return nc
        else:
            raise Exception(
                f'could not find Identifiable class with id: \'{id}\'. '
                f'if you changed your node\'s class name, make sure to add the old '
                f'identifier to the legacy_ids list attribute to provide '
                f'backwards compatibility.'
            )
            

class IdentifiableGroups(Generic[InfoType]):
    """
    Groups identifiables by their prefix and name. Identifiables with no prefix are groupped under 'global'
    
    Also holds structures for getting an identifiable by its name.
    """
    NO_PREFIX_ROOT = 'global'
    
    def __init__(self, ids: Iterable[Identifiable[InfoType]] = []):
        
        self.__id_set = set[Identifiable[InfoType]]()
        
        self.__id_dict = dict[str, Identifiable[InfoType]]()
        self.__id_dict_proxy = MappingProxyType(self.__id_dict)
        
        self.__id_groups: dict[str, dict[str, Identifiable[InfoType]]] = {
            'global': {}
        }
        self._groups_proxy = MappingProxyType(self.__id_groups)
        
        # init
        for item in ids:
            if not item.prefix:
                group = self.__id_groups['global']
            else:
                if not item.prefix in self.__id_groups:
                    self.__id_groups[item.prefix] = group = {}
                else:
                    group = self.__id_groups[item.prefix]
        
            group[item.name] = item
        
        self.infos = {id.info for id in self.__id_set}
        # events
        self.group_added = Event[str]()
        self.group_removed = Event[str]()
        self.id_added = Event[Identifiable[InfoType]]()
        self.id_removed = Event[Identifiable[InfoType]]()
    
    
    def __str__(self) -> str:
        return self.__id_groups.__str__()
    
    @property
    def id_set(self) -> set[Identifiable[InfoType]]:
        """A set containing all the Identifiables"""
        return self.__id_set
    
    @property
    def id_map(self) -> Mapping[str, Identifiable[InfoType]]:
        """A map with layout {id: identifiable}"""
        return self.__id_dict_proxy
    
    @property
    def groups(self) -> Mapping[str, Mapping[str, Identifiable[InfoType]]]:
        """The identifiable groupped by their prefixes"""
        return self._groups_proxy
    
    def rename(self, new_name: str, old_name: str, group: str):
        id = self.groups[group][old_name]
        self.remove(id)
        
        id._id_name = new_name
        self.add(id)
        
    def add(self, id: Identifiable[InfoType]) -> bool:
        """Adds an identifiable to its group. Creates the group if it doesn't exist"""
        
        if id.id in self.__id_dict:
            return False
        
        if not id.prefix:
            group = self.__id_groups['global']
        elif id.prefix in self.__id_groups:
            group = self.__id_groups[id.prefix]
        else:
            self.__id_groups[id.prefix] = group = {}
            self.group_added.emit(id.prefix)
        
        group[id.name] = id
        self.infos.add(id.info)
        
        self.__id_set.add(id)
        self.__id_dict[id.id] = id
        self.id_added.emit(id)
        
        return True
    
    def remove(self, id: Identifiable[InfoType]):
        """Removes an identifiable from its group. Deletes the group if it's empty"""
        
        id_in_dict = self.__id_dict.get(id.id)
        if not id_in_dict:
            return False
        
        if not id.prefix:
            del self.__id_groups['global'][id.name]
        else:
            del self.__id_groups[id.prefix][id.name]
            if not self.__id_groups[id.prefix]:
                del self.__id_groups[id.prefix]
                
                self.group_removed.emit(id.prefix)
        
        self.__id_set.remove(id_in_dict)
        del self.__id_dict[id.id]
        
        self.infos.remove(id.info)
        
        self.id_removed.emit(id_in_dict)
          
    def group(self, group_id: str) -> None | Mapping[str, Identifiable[InfoType]]:
        """Retrieves a specific group. group_id must exist as a valid group."""
        
        if not group_id in self.__id_groups:
            return None
        return MappingProxyType(self.__id_groups[group_id])

    def group_infos(self, group_id: str) -> set[Self]:
        group = self.group(group_id)
        return {identifiable.info for identifiable in group.values()}
    
    def remove_group(self, group_id: str, emit_id_removed=False) -> bool:
        """Removes a group. group_id must exist as a valid group"""
        
        group = self.__id_groups.get(group_id)
        if not group:
            return False
        
        for id in group.values():
            self.__id_set.remove(id)
            self.infos.remove(id.info)
            del self.__id_dict[id.id]
            if emit_id_removed:
                self.id_removed.emit(id)
        
        del self.__id_groups[group_id]
        self.group_removed.emit(group_id)
        return True
    
    def groups_from_path(self, path: str):
        """
        Retrieves all groups whose prefix contains the path
        
        Useful for "imitating" sub-groups
        """
        
        return {
            id: group 
            for id, group in self.__id_dict.items()
            if path.startswith(id)
        }
    
    def remove_groups_from_path(self, path: str):
        """
        Removes all groups whos prefix contains the path
        
        Useful for "imitating" sub-groups
        """
        
        to_remove = self.groups_from_path(path)
        for id in to_remove.keys():
            self.remove_group(id)    
        
        
        

    
    
