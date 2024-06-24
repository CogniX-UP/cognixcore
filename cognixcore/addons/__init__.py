"""
Defines an add-on system to extend congixcore's functionalities.
The :class:`cognixcore.addons.variables.VarsAddon` and :class:`cognixcore.addons.logging.LoggingAddon`
addons are built-in. Additional add-ons can be implemented and registered in the :class:`cognixcore.session.Session`.

An add-on
    - has a unique name and a version
    - is session-local, not flow-local but can implement per-Flow functionality
    - manages its own state (in particular :code:`get_state()` and :code:`set_state()`)
    - can store additional node-specific data in the node's :code:`data` dict when it's serialized
    - will be accessible through the nodes API: :code:`self.get_addon('your_addon')` in your nodes

Add-on access is blocked during loading (deserialization), so nodes should not access any
add-ons during the execution of :code:`Node.__init__` or :code:`Node.set_data`.
This prevents inconsistent states. Nodes are loaded first, then the add-ons. 
Therefore, the add-on should be sufficiently isolated and self-contained.

To define a custom add-on:
    - create a class :code:`YourAddon(cognixcore.addons.base.AddOn)` that defines your add-on's functionality
    - register your addon directory in the Session: :code:`session.register_addon_dir(YourAddon | YourAddon())`
"""

from ._base import AddOn, AddonType