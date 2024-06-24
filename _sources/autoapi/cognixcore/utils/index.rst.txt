cognixcore.utils
================

.. py:module:: cognixcore.utils

.. autoapi-nested-parse::

   A collection of useful functions and definitions used by different components.



Functions
---------

.. autoapisummary::

   cognixcore.utils.pkg_version
   cognixcore.utils.pkg_path
   cognixcore.utils.serialize
   cognixcore.utils.deserialize
   cognixcore.utils.print_err
   cognixcore.utils.json_print
   cognixcore.utils.get_mod_classes
   cognixcore.utils.has_abstractmethods


Module Contents
---------------

.. py:function:: pkg_version() -> str

.. py:function:: pkg_path(subpath: str = None)

   Returns the path to the installed package root directory, optionally with a relative sub-path appended.
   Notice that this returns the path to the cognixcore package (cognixcore/cognixcore/) not the repository (cognixcore/).


.. py:function:: serialize(data) -> str

.. py:function:: deserialize(data)

.. py:function:: print_err(*args, **kwargs)

.. py:function:: json_print(d: dict)

.. py:function:: get_mod_classes(mod: str | types.ModuleType, to_fill: list | None = None, filter: Callable[[Any], bool] = None)

   Returns a list of classes defined in the current file.

   The filter paramater is a function that takes the object and returns if it should be included.


.. py:function:: has_abstractmethods(cls)

   Returns whether an object has abstract methods


