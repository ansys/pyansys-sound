"""
PyAnsys Sound core package.
"""

# Version
# ------------------------------------------------------------------------------

import importlib.metadata as importlib_metadata

__version__ = importlib_metadata.version(__name__.replace(".", "-"))
"""PyAnsys Sound version."""

from . import examples_helpers, server_helpers, signal_utilities

__all__ = ("examples_helpers", "server_helpers", "signal_utilities")
