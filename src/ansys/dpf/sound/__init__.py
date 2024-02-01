"""
pydpf-sound.

Library
"""

import importlib.metadata as importlib_metadata

__version__ = importlib_metadata.version(__name__.replace(".", "-"))

from . import examples_helpers, server_helpers

__all__ = "server_helpers, example_helpers"
