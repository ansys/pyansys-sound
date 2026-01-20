# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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

from .download import (
    download_accel_with_rpm_2_wav,
    download_accel_with_rpm_3_wav,
    download_accel_with_rpm_wav,
    download_aircraft10kHz_wav,
    download_aircraft_wav,
    download_all_carHVAC_wav,
    download_fan_wav,
    download_flute_psd,
    download_flute_wav,
    download_HVAC_test_wav,
    download_JLT_CE_data_csv,
    download_sound_composer_FRF_eMotor,
    download_sound_composer_project_whatif,
    download_sound_composer_source_control_eMotor,
    download_sound_composer_source_control_WindRoadNoise,
    download_sound_composer_source_eMotor,
    download_sound_composer_source_WindRoadNoise,
    download_turbo_whistling_wav,
    download_xtract_demo_signal_1_wav,
    download_xtract_demo_signal_2_wav,
)

__all__ = (
    "download_flute_psd",
    "download_flute_wav",
    "download_accel_with_rpm_wav",
    "download_accel_with_rpm_2_wav",
    "download_accel_with_rpm_3_wav",
    "download_JLT_CE_data_csv",
    "download_all_carHVAC_wav",
    "download_HVAC_test_wav",
    "download_xtract_demo_signal_1_wav",
    "download_xtract_demo_signal_2_wav",
    "download_fan_wav",
    "download_turbo_whistling_wav",
    "download_aircraft_wav",
    "download_aircraft10kHz_wav",
    "download_sound_composer_project_whatif",
    "download_sound_composer_source_eMotor",
    "download_sound_composer_source_control_eMotor",
    "download_sound_composer_FRF_eMotor",
    "download_sound_composer_source_WindRoadNoise",
    "download_sound_composer_source_control_WindRoadNoise",
)
