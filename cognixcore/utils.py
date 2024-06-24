"""A collection of useful functions and definitions used by different components."""

import base64
import json
import pickle
import sys
import importlib.util
import importlib.metadata as importlib_metadata

from os.path import dirname, abspath, join, basename
from packaging.version import Version, parse as _parse_version
from types import ModuleType
from typing import Callable, Any
from inspect import getmembers, isclass
from collections.abc import Iterable, Sequence, Mapping

from .base import Identifiable

def pkg_version() -> str:
    return importlib_metadata.version('cognixcore')


def pkg_path(subpath: str = None):
    """
    Returns the path to the installed package root directory, optionally with a relative sub-path appended.
    Notice that this returns the path to the cognixcore package (cognixcore/cognixcore/) not the repository (cognixcore/).
    """

    p = dirname(__file__)
    if subpath is not None:
        p = join(p, subpath)
    return abspath(p)


def serialize(data) -> str:
    return base64.b64encode(pickle.dumps(data)).decode('ascii')


def deserialize(data):
    return pickle.loads(base64.b64decode(data))


def print_err(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def json_print(d: dict):
    # I just need this all the time
    print(json.dumps(d, indent=4))


def get_mod_classes(mod: str | ModuleType, to_fill: list | None = None, filter: Callable[[Any], bool] = None):
    """
    Returns a list of classes defined in the current file.
    
    The filter paramater is a function that takes the object and returns if it should be included.
    """
    
    current_module = mod if isinstance(mod, ModuleType) else sys.modules[mod]

    classes = to_fill if to_fill else []
    for _, obj in getmembers(current_module):
        if not (isclass(obj) and obj.__module__ == current_module.__name__):
            continue
        if filter and not filter(obj):
            continue
        classes.append(obj)

    return classes


def has_abstractmethods(cls):
    """Returns whether an object has abstract methods"""
    return hasattr(cls, '__abstractmethods__') and len(getattr(cls, '__abstractmethods__')) != 0


    