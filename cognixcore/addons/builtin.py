"""Gathers all the built-in Addons in a tuple"""

from .logging import LoggingAddon
from .variables._core import VarsAddon
 

built_in_addons = (LoggingAddon, VarsAddon)