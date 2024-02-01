"""
pydpf-sound.

Library
"""

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata

__version__ = importlib_metadata.version(__name__.replace(".", "-"))

from . import server_helpers

__all__ = "server_helpers"
