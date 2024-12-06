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

from ansys.dpf.core import upload_file_in_tmp_folder
import pytest

from ansys.sound.core.server_helpers import connect_to_or_start_server


def pytest_configure():

    # TODO comment
    server = connect_to_or_start_server(use_license_context=True)

    # # Get the current directory of the conftest.py file
    base_dir = os.path.dirname(__file__)

    # Construct the paths of the different test files after uploading them on the server
    pytest.data_path_flute_in_container = upload_file_in_tmp_folder(
        os.path.join(base_dir, "data", "flute.wav"), server=server
    )
    pytest.data_path_flute2_in_container = upload_file_in_tmp_folder(
        os.path.join(base_dir, "data", "flute2.wav"), server=server
    )
    pytest.data_path_flute_nonUnitaryCalib_in_container = upload_file_in_tmp_folder(
        os.path.join(base_dir, "data", "flute_nonUnitaryCalib.wav"), server=server
    )
    pytest.data_path_sharp_noise_in_container = upload_file_in_tmp_folder(
        os.path.join(base_dir, "data", "sharp_noise.wav"), server=server
    )
    pytest.data_path_sharper_noise_in_container = upload_file_in_tmp_folder(
        os.path.join(base_dir, "data", "sharper_noise.wav"), server=server
    )
    pytest.data_path_rough_noise_in_container = upload_file_in_tmp_folder(
        os.path.join(base_dir, "data", "rough_noise.wav"), server=server
    )
    pytest.data_path_rough_tone_in_container = upload_file_in_tmp_folder(
        os.path.join(base_dir, "data", "rough_tone.wav"), server=server
    )
    pytest.data_path_fluctuating_noise_in_container = upload_file_in_tmp_folder(
        os.path.join(base_dir, "data", "fluctuating_noise.wav"), server=server
    )
    pytest.data_path_fluctuating_tone_in_container = upload_file_in_tmp_folder(
        os.path.join(base_dir, "data", "fluctuating_tone.wav"), server=server
    )
    pytest.data_path_white_noise_in_container = upload_file_in_tmp_folder(
        os.path.join(base_dir, "data", "white_noise.wav"), server=server
    )
    pytest.data_path_accel_with_rpm_in_container = upload_file_in_tmp_folder(
        os.path.join(base_dir, "data", "accel_with_rpm.wav"), server=server
    )
    pytest.data_path_flute_psd_in_container = upload_file_in_tmp_folder(
        os.path.join(base_dir, "data", "flute_psd.txt"), server=server
    )
    pytest.data_path_swl_project_file_in_container = upload_file_in_tmp_folder(
        os.path.join(base_dir, "data", "SoundPowerLevelProject_hemisphere_2025R1_20243008.spw"),
        server=server,
    )
    pytest.data_path_swl_project_file_with_calibration_in_container = upload_file_in_tmp_folder(
        os.path.join(
            base_dir,
            "data",
            "SoundPowerLevelProject_hemisphere_signalsWithCalibration_2025R1_20240919.spw",
        ),
        server=server,
    )
    pytest.data_path_sound_composer_spectrum_source_in_container = upload_file_in_tmp_folder(
        os.path.join(
            base_dir, "data", "AnsysSound_Spectrum_v3_-_nominal_-_dBSPLperHz_2024R2_20241121.txt"
        ),
        server=server,
    )

    pytest.data_path_flute_nonUnitaryCalib_as_txt_in_container = upload_file_in_tmp_folder(
        os.path.join(base_dir, "data", "flute_nonUnitaryCalib_as_text_2024R2_20241125.txt"),
        server=server,
    )

    pytest.data_path_rpm_profile_as_wav_in_container = upload_file_in_tmp_folder(
        os.path.join(base_dir, "data", "RPM_profile_2024R2_20241126.wav"), server=server
    )
    pytest.data_path_rpm_profile_as_txt_in_container = upload_file_in_tmp_folder(
        os.path.join(base_dir, "data", "RPM_profile_2024R2_20241126.txt"), server=server
    )
    pytest.temporary_folder = os.path.dirname(pytest.data_path_flute_in_container)
