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

import pytest

from ansys.sound.core.server_helpers import connect_to_or_start_server


def pytest_configure():

    # We're using here a PyAnsys Sound function to connect to the server based on whether we're in
    # a docker or local configuration.
    # There are tests for the function connect_to_or_start_server that are independent from the
    # configuration. That's why we authorize the use of this function here.
    server = connect_to_or_start_server(use_license_context=True)

    ## Get the current directory of the conftest.py file
    base_dir = os.path.join(os.path.dirname(__file__), "data")

    def upload_file_in_tmp_folder_tmp(file_path, server):
        return file_path

    ## Construct the paths of the different test files after uploading them on the server.
    # Audio samples
    pytest.data_path_flute_in_container = upload_file_in_tmp_folder_tmp(
        os.path.join(base_dir, "flute.wav"), server=server
    )
    pytest.data_path_flute_nonUnitaryCalib_in_container = upload_file_in_tmp_folder_tmp(
        os.path.join(base_dir, "flute_nonUnitaryCalib.wav"), server=server
    )
    pytest.data_path_flute_nonUnitaryCalib_as_txt_in_container = upload_file_in_tmp_folder_tmp(
        os.path.join(base_dir, "flute_nonUnitaryCalib_as_text_2024R2_20241125.txt"),
        server=server,
    )
    pytest.data_path_sharp_noise_in_container = upload_file_in_tmp_folder_tmp(
        os.path.join(base_dir, "sharp_noise.wav"), server=server
    )
    pytest.data_path_sharper_noise_in_container = upload_file_in_tmp_folder_tmp(
        os.path.join(base_dir, "sharper_noise.wav"), server=server
    )
    pytest.data_path_rough_noise_in_container = upload_file_in_tmp_folder_tmp(
        os.path.join(base_dir, "rough_noise.wav"), server=server
    )
    pytest.data_path_rough_tone_in_container = upload_file_in_tmp_folder_tmp(
        os.path.join(base_dir, "rough_tone.wav"), server=server
    )
    pytest.data_path_fluctuating_noise_in_container = upload_file_in_tmp_folder_tmp(
        os.path.join(base_dir, "fluctuating_noise.wav"), server=server
    )
    pytest.data_path_white_noise_in_container = upload_file_in_tmp_folder_tmp(
        os.path.join(base_dir, "white_noise.wav"), server=server
    )
    pytest.data_path_aircraft_nonUnitaryCalib_in_container = upload_file_in_tmp_folder_tmp(
        os.path.join(base_dir, "Aircraft-App2_nonUnitaryCalib.wav"), server=server
    )
    pytest.data_path_Acceleration_stereo_nonUnitaryCalib = upload_file_in_tmp_folder_tmp(
        os.path.join(base_dir, "Acceleration_stereo_nonUnitaryCalib.wav"),
        server=server,
    )
    pytest.data_path_accel_with_rpm_in_container = upload_file_in_tmp_folder_tmp(
        os.path.join(base_dir, "accel_with_rpm.wav"), server=server
    )
    pytest.data_path_Acceleration_with_Tacho_nonUnitaryCalib = upload_file_in_tmp_folder_tmp(
        os.path.join(base_dir, "Acceleration_with_Tacho_nonUnitaryCalib.wav"),
        server=server,
    )

    # RPM profiles
    pytest.data_path_rpm_profile_as_wav_in_container = upload_file_in_tmp_folder_tmp(
        os.path.join(base_dir, "RPM_profile_2024R2_20241126.wav"), server=server
    )
    pytest.data_path_rpm_profile_as_txt_in_container = upload_file_in_tmp_folder_tmp(
        os.path.join(base_dir, "RPM_profile_2024R2_20241126.txt"), server=server
    )

    # Sound power level projects
    pytest.data_path_swl_project_file_in_container = upload_file_in_tmp_folder_tmp(
        os.path.join(base_dir, "SoundPowerLevelProject_hemisphere_2025R1_20243008.spw"),
        server=server,
    )
    pytest.data_path_swl_project_file_with_calibration_in_container = upload_file_in_tmp_folder_tmp(
        os.path.join(
            base_dir,
            "SoundPowerLevelProject_hemisphere_signalsWithCalibration_2025R1_20240919.spw",
        ),
        server=server,
    )

    # Sound composer files (including spectrum, harmonics, etc. data files)
    pytest.data_path_sound_composer_spectrum_source_in_container = upload_file_in_tmp_folder_tmp(
        os.path.join(base_dir, "AnsysSound_Spectrum_v3_-_nominal_-_dBSPLperHz_2024R2_20241121.txt"),
        server=server,
    )
    pytest.data_path_sound_composer_harmonics_source_2p_in_container = (
        upload_file_in_tmp_folder_tmp(
            os.path.join(
                base_dir, "AnsysSound_Orders_MultipleParameters dBSPL_2024R2_20241205.txt"
            ),
            server=server,
        )
    )
    pytest.data_path_sound_composer_harmonics_source_2p_many_values_in_container = (
        upload_file_in_tmp_folder_tmp(
            os.path.join(
                base_dir,
                "AnsysSound_Orders_MultipleParameters dBSPL_many_values_2024R2_20241205.txt",
            ),
            server=server,
        )
    )
    pytest.data_path_sound_composer_harmonics_source_in_container = upload_file_in_tmp_folder_tmp(
        os.path.join(base_dir, "AnsysSound_Orders dBSPL v1_2024R2_20241203.txt"), server=server
    )
    pytest.data_path_sound_composer_harmonics_source_10rpm_40orders_in_container = (
        upload_file_in_tmp_folder_tmp(
            os.path.join(
                base_dir, "AnsysSound_Orders dBSPL v1_10_rpm_values_40_orders_2024R2_20241203.txt"
            ),
            server=server,
        )
    )
    pytest.data_path_sound_composer_harmonics_source_2p_inverted_controls_in_container = (
        upload_file_in_tmp_folder_tmp(
            os.path.join(
                base_dir,
                "AnsysSound_Orders_MultipleParameters dBSPL - InvertedContols_2024R2_20241205.txt",
            ),
            server=server,
        )
    )
    pytest.data_path_sound_composer_harmonics_source_2p_from_accel_in_container = (
        upload_file_in_tmp_folder_tmp(
            os.path.join(
                base_dir,
                "AnsysSound_Orders_MultipleParameters_FromAccelWithTacho_2024R2_20241205.txt",
            ),
            server=server,
        )
    )
    pytest.data_path_sound_composer_harmonics_source_Pa_in_container = (
        upload_file_in_tmp_folder_tmp(
            os.path.join(base_dir, "AnsysSound_Orders Pa v1_2024R2_20241203.txt"), server=server
        )
    )
    pytest.data_path_sound_composer_harmonics_source_wrong_type_in_container = (
        upload_file_in_tmp_folder_tmp(
            os.path.join(base_dir, "AnsysSound_Orders V2_2024R2_20241203.txt"), server=server
        )
    )
    pytest.data_path_sound_composer_harmonics_source_xml_in_container = (
        upload_file_in_tmp_folder_tmp(
            os.path.join(base_dir, "VRX_Waterfall_2024R2_20241203.xml"), server=server
        )
    )
    pytest.data_path_sound_composer_bbn_source_in_container = upload_file_in_tmp_folder_tmp(
        os.path.join(base_dir, "AnsysSound_BBN dBSPL OCTAVE Constants.txt"), server=server
    )
    pytest.data_path_sound_composer_bbn_source_40_values_in_container = (
        upload_file_in_tmp_folder_tmp(
            os.path.join(
                base_dir, "AnsysSound_BBN dBSPLperHz NARROWBAND v2_40values_2024R2_20241128.txt"
            ),
            server=server,
        )
    )
    pytest.data_path_sound_composer_bbn_source_2p_in_container = upload_file_in_tmp_folder_tmp(
        os.path.join(
            base_dir, "AnsysSound_BBN_MultipleParameters Pa2PerHz Narrowband v2_2024R2_20240418.txt"
        ),
        server=server,
    )
    pytest.data_path_sound_composer_bbn_source_2p_octave_in_container = (
        upload_file_in_tmp_folder_tmp(
            os.path.join(
                base_dir, "AnsysSound_BBN_MultipleParameters dBSPL Octave v2_2024R2_20240418.txt"
            ),
            server=server,
        )
    )
    pytest.data_path_sound_composer_project_in_container = upload_file_in_tmp_folder_tmp(
        os.path.join(base_dir, "20250130_SoundComposerProjectForDpfSoundTesting_valid.scn"),
        server=server,
    )

    # FRF files
    pytest.data_path_filter_frf = upload_file_in_tmp_folder_tmp(
        os.path.join(base_dir, "AnsysSound_FRF_2024R2_20241206.txt"), server=server
    )
    pytest.data_path_filter_frf_wrong_header = upload_file_in_tmp_folder_tmp(
        os.path.join(base_dir, "AnsysSound_FRF_bad_2024R2_20241206.txt"), server=server
    )

    # PSD file
    # This path is different from the other files': we need a local path
    # and not a server path because we will use a native python
    # `open()` to read this file and not a DPF operator
    pytest.data_path_flute_psd_locally = os.path.join(base_dir, "flute_psd.txt")

    ## The temporary folder is the folder in the server where the files are stored.
    pytest.temporary_folder = os.path.dirname(pytest.data_path_flute_in_container)
