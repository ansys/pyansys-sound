"""Utilities for managing the PyAnsys Sound example files.

Helper functions for managing the PyAnsys Sound example files.
"""

import os

import platformdirs

from ._get_example_files import (
    get_absolute_path_for_accel_with_rpm_wav,
    get_absolute_path_for_fluctuating_noise_wav,
    get_absolute_path_for_fluctuating_tone_wav,
    get_absolute_path_for_flute2_wav,
    get_absolute_path_for_flute_psd_txt,
    get_absolute_path_for_flute_wav,
    get_absolute_path_for_rough_noise_wav,
    get_absolute_path_for_rough_tone_wav,
    get_absolute_path_for_sharp_noise_wav,
    get_absolute_path_for_sharper_noise_wav,
    get_absolute_path_for_xtract_demo_signal_1_wav,
    get_absolute_path_for_xtract_demo_signal_2_wav,
)

# Setup data directory
USER_DATA_PATH = platformdirs.user_data_dir(appname="ansys_sound_core", appauthor="Ansys")
if not os.path.exists(USER_DATA_PATH):  # pragma: no cover
    os.makedirs(USER_DATA_PATH)

EXAMPLES_PATH = os.path.join(USER_DATA_PATH, "examples")

from .download import download_flute_psd

__all__ = (
    "get_absolute_path_for_accel_with_rpm_wav",
    "get_absolute_path_for_flute2_wav",
    "get_absolute_path_for_flute_wav",
    "get_absolute_path_for_sharp_noise_wav",
    "get_absolute_path_for_sharper_noise_wav",
    "get_absolute_path_for_rough_noise_wav",
    "get_absolute_path_for_rough_tone_wav",
    "get_absolute_path_for_fluctuating_noise_wav",
    "get_absolute_path_for_fluctuating_tone_wav",
    "get_absolute_path_for_xtract_demo_signal_1_wav",
    "get_absolute_path_for_xtract_demo_signal_2_wav",
    "get_absolute_path_for_flute_psd_txt",
    "download_flute_psd",
)
