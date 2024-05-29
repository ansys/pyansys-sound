"""Utilities for managing the DPF Sound example files.

Helper functions for managing the DPF Sound example files.
"""

from ._get_example_files import (
    get_absolute_path_for_flute2_wav,
    get_absolute_path_for_flute_psd_txt,
    get_absolute_path_for_flute_wav,
)

__all__ = (
    "get_absolute_path_for_flute_wav",
    "get_absolute_path_for_flute2_wav",
    "get_absolute_path_for_flute_psd_txt",
)
