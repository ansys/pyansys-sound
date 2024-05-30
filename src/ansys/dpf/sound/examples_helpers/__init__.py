"""Utilities for managing the DPF Sound example files.

Helper functions for managing the DPF Sound example files.
"""

from ._get_example_files import (
    get_absolute_path_for_accel_with_rpm_wav,
    get_absolute_path_for_fluctuating_noise_wav,
    get_absolute_path_for_fluctuating_tone_wav,
    get_absolute_path_for_flute2_wav,
    get_absolute_path_for_flute_wav,
    get_absolute_path_for_rough_noise_wav,
    get_absolute_path_for_rough_tone_wav,
    get_absolute_path_for_sharp_noise_wav,
    get_absolute_path_for_sharper_noise_wav,
)

__all__ = (
    "get_absolute_path_for_flute_wav",
    "get_absolute_path_for_flute2_wav",
    "get_absolute_path_for_accel_with_rpm_wav",
    "get_absolute_path_for_sharp_noise_wav",
    "get_absolute_path_for_sharper_noise_wav",
    "get_absolute_path_for_rough_noise_wav",
    "get_absolute_path_for_rough_tone_wav",
    "get_absolute_path_for_fluctuating_noise_wav",
    "get_absolute_path_for_fluctuating_tone_wav",
)
