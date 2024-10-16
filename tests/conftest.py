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

import os

from ansys.dpf.core import (
    AvailableServerContexts,
    LicenseContextManager,
    connect_to_server,
    load_library,
)
import pytest

CONTAINER_SERVER_PORT = 6780
STR_DPF_SOUND = "dpf_sound.dll"
STR_DPF_SOUND_DLL = "dpf_sound.dll"


def pytest_configure():
    pytest.data_path_flute_in_container = "C:\\data\\flute.wav"
    pytest.data_path_flute2_in_container = "C:\\data\\flute2.wav"
    pytest.data_path_sharp_noise_in_container = "C:\\data\\sharp_noise.wav"
    pytest.data_path_sharper_noise_in_container = "C:\\data\\sharper_noise.wav"
    pytest.data_path_rough_noise_in_container = "C:\\data\\rough_noise.wav"
    pytest.data_path_rough_tone_in_container = "C:\\data\\rough_tone.wav"
    pytest.data_path_fluctuating_noise_in_container = "C:\\data\\fluctuating_noise.wav"
    pytest.data_path_fluctuating_tone_in_container = "C:\\data\\fluctuating_tone.wav"
    pytest.data_path_white_noise_in_container = "C:\\data\\white_noise.wav"
    pytest.data_path_accel_with_rpm_in_container = "C:\\data\\accel_with_rpm.wav"
    pytest.data_path_flute_psd_in_container = "C:\\data\\flute_psd.txt"
    pytest.data_path_swl_project_file_in_container = (
        "C:\\data\\SoundPowerLevelProject_hemisphere_2025R1_20243008.spw"
    )
    pytest.data_path_swl_project_file_with_calibration_in_container = (
        "C:\\data\\SoundPowerLevelProject_hemisphere_signalsWithCalibration_2025R1_20240919.spw"
    )


@pytest.fixture(scope="session")
def dpf_sound_test_server():
    port_in_env = os.environ.get("ANSRV_DPF_SOUND_PORT")
    if port_in_env is not None:
        port = int(port_in_env)
    else:
        port = CONTAINER_SERVER_PORT

    # Connecting to server
    server = connect_to_server(port=port, context=AvailableServerContexts.premium)

    # Initializing licence context manager, will make tests faster by avoiding licenses checkouts
    licence_context_manager = LicenseContextManager(increment_name="avrxp_snd_level1")

    # Loading DPF Sound
    load_library(STR_DPF_SOUND_DLL, STR_DPF_SOUND)
    yield server
