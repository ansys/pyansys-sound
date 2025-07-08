# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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

from ansys.dpf import core
from ansys.dpf.core import upload_file_in_tmp_folder
from ansys.dpf.core.check_version import get_server_version, meets_version
import pytest

from ansys.sound.core.server_helpers import connect_to_or_start_server


def pytest_configure(config):

    # We're using here a PyAnsys Sound function to connect to the server based on whether we're in
    # a docker or local configuration.
    # There are tests for the function connect_to_or_start_server that are independent from the
    # configuration. That's why we authorize the use of this function here.
    server, lic_context = connect_to_or_start_server(use_license_context=True)

    # Store the server and licensing context into the pytest object, to make these attributes
    # available in the tests, everywhere we import pytest
    config.dpf_server = server
    config.dpf_lic_context = lic_context

    # Define global variables for server version checks: store it in the pytest object
    # to make it global and available in all tests.
    # Note: 11.0 corresponds to Ansys 2026 R1
    pytest.SERVERS_VERSION_GREATER_THAN_OR_EQUAL_TO_11_0 = meets_version(
        get_server_version(server), "11.0"
    )
    # 10.0 corresponds to Ansys 2025 R2
    pytest.SERVERS_VERSION_GREATER_THAN_OR_EQUAL_TO_10_0 = meets_version(
        get_server_version(server), "10.0"
    )

    # Use the conftest.py file's directory to set the base directory for the test data files.
    base_dir = os.path.join(os.path.dirname(__file__), "data")

    def get_test_file_path(filename, base_dir, server) -> str:
        # Set the local path to the test file.
        local_path = os.path.join(base_dir, filename)

        if server.has_client():
            # If the server is a gRPC server, we need to upload the file to the server's temporary
            # folder
            return upload_file_in_tmp_folder(local_path, server=server)
        # Otherwise, that is, if the server is an in-process server, we return the local path
        return local_path

    ## Construct the paths of the different test files after uploading them on the server.
    # Audio samples
    pytest.data_path_flute_in_container = get_test_file_path("flute.wav", base_dir, server=server)
    pytest.data_path_flute_nonUnitaryCalib_in_container = get_test_file_path(
        "flute_nonUnitaryCalib.wav", base_dir, server=server
    )
    pytest.data_path_flute_nonUnitaryCalib_as_txt_in_container = get_test_file_path(
        "flute_nonUnitaryCalib_as_text_2024R2_20241125.txt",
        base_dir,
        server=server,
    )
    pytest.data_path_sharp_noise_in_container = get_test_file_path(
        "sharp_noise.wav", base_dir, server=server
    )
    pytest.data_path_sharper_noise_in_container = get_test_file_path(
        "sharper_noise.wav", base_dir, server=server
    )
    pytest.data_path_rough_noise_in_container = get_test_file_path(
        "rough_noise.wav", base_dir, server=server
    )
    pytest.data_path_rough_tone_in_container = get_test_file_path(
        "rough_tone.wav", base_dir, server=server
    )
    pytest.data_path_fluctuating_noise_in_container = get_test_file_path(
        "fluctuating_noise.wav", base_dir, server=server
    )
    pytest.data_path_white_noise_in_container = get_test_file_path(
        "white_noise.wav", base_dir, server=server
    )
    pytest.data_path_aircraft_nonUnitaryCalib_in_container = get_test_file_path(
        "Aircraft-App2_nonUnitaryCalib.wav", base_dir, server=server
    )
    pytest.data_path_Acceleration_stereo_nonUnitaryCalib = get_test_file_path(
        "Acceleration_stereo_nonUnitaryCalib.wav",
        base_dir,
        server=server,
    )
    pytest.data_path_accel_with_rpm_in_container = get_test_file_path(
        "accel_with_rpm.wav", base_dir, server=server
    )
    pytest.data_path_Acceleration_with_Tacho_nonUnitaryCalib = get_test_file_path(
        "Acceleration_with_Tacho_nonUnitaryCalib.wav",
        base_dir,
        server=server,
    )

    # RPM profiles
    pytest.data_path_rpm_profile_as_wav_in_container = get_test_file_path(
        "RPM_profile_2024R2_20241126.wav", base_dir, server=server
    )
    pytest.data_path_rpm_profile_as_txt_in_container = get_test_file_path(
        "RPM_profile_2024R2_20241126.txt", base_dir, server=server
    )

    # Sound power level projects
    pytest.data_path_swl_project_file_in_container = get_test_file_path(
        "SoundPowerLevelProject_hemisphere_2025R1_20243008.spw",
        base_dir,
        server=server,
    )
    pytest.data_path_swl_project_file_with_calibration_in_container = get_test_file_path(
        "SoundPowerLevelProject_hemisphere_signalsWithCalibration_2025R1_20240919.spw",
        base_dir,
        server=server,
    )

    # Sound composer files (including spectrum, harmonics, etc. data files)
    pytest.data_path_sound_composer_spectrum_source_in_container = get_test_file_path(
        "AnsysSound_Spectrum_v3_-_nominal_-_dBSPLperHz_2024R2_20241121.txt",
        base_dir,
        server=server,
    )
    pytest.data_path_sound_composer_harmonics_source_2p_in_container = get_test_file_path(
        "AnsysSound_Orders_MultipleParameters dBSPL_2024R2_20241205.txt",
        base_dir,
        server=server,
    )
    pytest.data_path_sound_composer_harmonics_source_2p_many_values_in_container = (
        get_test_file_path(
            "AnsysSound_Orders_MultipleParameters dBSPL_many_values_2024R2_20241205.txt",
            base_dir,
            server=server,
        )
    )
    pytest.data_path_sound_composer_harmonics_source_in_container = get_test_file_path(
        "AnsysSound_Orders dBSPL v1_2024R2_20241203.txt", base_dir, server=server
    )
    pytest.data_path_sound_composer_harmonics_source_10rpm_40orders_in_container = (
        get_test_file_path(
            "AnsysSound_Orders dBSPL v1_10_rpm_values_40_orders_2024R2_20241203.txt",
            base_dir,
            server=server,
        )
    )
    pytest.data_path_sound_composer_harmonics_source_2p_inverted_controls_in_container = (
        get_test_file_path(
            "AnsysSound_Orders_MultipleParameters dBSPL - InvertedContols_2024R2_20241205.txt",
            base_dir,
            server=server,
        )
    )
    pytest.data_path_sound_composer_harmonics_source_2p_from_accel_in_container = (
        get_test_file_path(
            "AnsysSound_Orders_MultipleParameters_FromAccelWithTacho_2024R2_20241205.txt",
            base_dir,
            server=server,
        )
    )
    pytest.data_path_sound_composer_harmonics_source_Pa_in_container = get_test_file_path(
        "AnsysSound_Orders Pa v1_2024R2_20241203.txt", base_dir, server=server
    )
    pytest.data_path_sound_composer_harmonics_source_wrong_type_in_container = get_test_file_path(
        "AnsysSound_Orders V2_2024R2_20241203.txt", base_dir, server=server
    )
    pytest.data_path_sound_composer_harmonics_source_xml_in_container = get_test_file_path(
        "VRX_Waterfall_2024R2_20241203.xml", base_dir, server=server
    )
    pytest.data_path_sound_composer_bbn_source_in_container = get_test_file_path(
        "AnsysSound_BBN dBSPL OCTAVE Constants.txt", base_dir, server=server
    )
    pytest.data_path_sound_composer_bbn_source_40_values_in_container = get_test_file_path(
        "AnsysSound_BBN dBSPLperHz NARROWBAND v2_40values_2024R2_20241128.txt",
        base_dir,
        server=server,
    )
    pytest.data_path_sound_composer_bbn_source_2p_in_container = get_test_file_path(
        "AnsysSound_BBN_MultipleParameters Pa2PerHz Narrowband v2_2024R2_20240418.txt",
        base_dir,
        server=server,
    )
    pytest.data_path_sound_composer_bbn_source_2p_octave_in_container = get_test_file_path(
        "AnsysSound_BBN_MultipleParameters dBSPL Octave v2_2024R2_20240418.txt",
        base_dir,
        server=server,
    )
    pytest.data_path_sound_composer_project_in_container = get_test_file_path(
        "20250130_SoundComposerProjectForDpfSoundTesting_valid.scn",
        base_dir,
        server=server,
    )

    # FRF files
    pytest.data_path_filter_frf = get_test_file_path(
        "AnsysSound_FRF_2024R2_20241206.txt", base_dir, server=server
    )
    pytest.data_path_filter_frf_wrong_header = get_test_file_path(
        "AnsysSound_FRF_bad_2024R2_20241206.txt", base_dir, server=server
    )

    # PSD file
    # This path is different from the other files': we need a local path
    # and not a server path because we will use a native python
    # `open()` to read this file and not a DPF operator
    pytest.data_path_flute_psd_locally = os.path.join(base_dir, "flute_psd.txt")

    ## The temporary folder is the folder in the server where the files are stored.
    pytest.temporary_folder = os.path.dirname(pytest.data_path_flute_in_container)
