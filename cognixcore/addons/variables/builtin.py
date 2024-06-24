"""
Defines built-in variable types and their metadata as :class:`cognixcore.IdentifiableGroups`. The built in types
include Python primitives, namely :class:`str`, :class:`bytes`, :class:`int`, :class:`float`, and :class:`complex`. 
"""

from ...serializers import (
    TypeSerializer, 
    BasicSerializer,
    ComplexSerializer,
    FractionSerializer,
)
from ._core import VarType
from ...base import Identifiable, IdentifiableGroups
from types import MappingProxyType
from fractions import Fraction

__built_in_types: dict[type, VarType] = {}
built_in_types = MappingProxyType(__built_in_types)
"""A mapping from type to variable type."""

variable_groups = IdentifiableGroups[VarType]()
"""The variable groups holding the built-in variables."""

base_package = 'builtin'
numbers_package = f'{base_package}.numbers'
# collection_package = f'{base_package}.collections'

def __var_type(val_type: type, pkg: str, serializer: TypeSerializer, name=None):
    vt_name = name if name else val_type.__name__
    var_type = VarType.create(val_type, vt_name, pkg, serializer)
    __built_in_types[var_type.identifier] = var_type
    
    var_identifiable = Identifiable(var_type.name, var_type.package, info=var_type)
    variable_groups.add(var_identifiable)
    
def __base_var_type(val_type: type, pkg: str, name=None):
    serializer = BasicSerializer(val_type)
    __var_type(val_type, pkg, serializer, name)

# CORE
__base_var_type(str, base_package)
__base_var_type(bytes, base_package)

# NUMBERS
__base_var_type(int, numbers_package)
__base_var_type(float, numbers_package)
__var_type(complex, numbers_package, ComplexSerializer())
__var_type(Fraction, numbers_package, FractionSerializer())

# TODO reason for collections, they might be needed, might not, don't really know   

