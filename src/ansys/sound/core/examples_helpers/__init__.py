# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Utilities for managing the PyAnsys Sound example files.

Helper functions for managing the PyAnsys Sound example files.
"""

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
from .download import (
    download_accel_with_rpm_2_wav,
    download_accel_with_rpm_3_wav,
    download_accel_with_rpm_wav,
    download_flute_2_wav,
    download_flute_psd,
    download_flute_wav,
    download_xtract_demo_signal_1_wav,
    download_xtract_demo_signal_2_wav,
)

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
    "download_flute_wav",
    "download_flute_2_wav",
    "download_accel_with_rpm_wav",
    "download_accel_with_rpm_2_wav",
    "download_accel_with_rpm_3_wav",
    "download_xtract_demo_signal_1_wav",
    "download_xtract_demo_signal_2_wav",
)
