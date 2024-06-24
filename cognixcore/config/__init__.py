"""
Defines the :class:`NodeConfig` interface class. Implement this
class for creating a specific configuration base type. The default implementation
for this, using the `Traits <https://docs.enthought.com/traitsui/>`_ library, is :class:`cognixcore.config.traits.NodeTraitsConfig`
"""

from ._abc import NodeConfig