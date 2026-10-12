# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

"""Functions to download example data from the PyAnsys Sound examples repository.

This module provides functions to download example data files used in PyAnsys Sound.

When implementing a new PyAnsys Sound example that requires new example data file(s), a new
download function must be added to this module.

Note: the example data files must be submitted to the PyAnsys Sound examples repository, through a
pull request, for the implemented download function to work. You can create the pull request by
following this link:
https://github.com/ansys/example-data/upload/main/pyansys-sound.
"""

import os

from ansys.tools.common.example_download import download_manager
import platformdirs

# Setup data directory
USER_DATA_PATH = platformdirs.user_data_dir(appname="pyansys", appauthor="Ansys")
EXAMPLES_PATH = os.path.join(USER_DATA_PATH, "examples")


def _download_file(filename):
    """Download a file from the PyAnsys Sound examples repository to the local example files folder.

    The specified file is retrieved from the PyAnsys Sound examples repository at the URL
    https://github.com/ansys/example-data/raw/main/pyansys-sound/

    Parameters
    ----------
    filename : str
        File name in the local examples folder.

    Returns
    -------
    Local path of the downloaded example file.
    """
    return download_manager.download_file(
        filename, "pyansys-sound", EXAMPLES_PATH, force=True, timeout=10.0
    )


def download_flute_psd():
    """Download the `flute_psd.txt` file with the PSD corresponding to `flute.wav`.

    Returns
    -------
    str
        Local path for the `flute_psd.txt` file.
    """
    return _download_file("flute_psd.txt")


def download_flute_wav():
    """Download the ``flute.wav`` file.

    Returns
    -------
    str
        Path for the ``flute.wav`` file.
    """
    return _download_file("flute.wav")


def download_accel_with_rpm_wav():
    """Download the ``accel_with_rpm.wav`` file.

    Returns
    -------
    str
        Path for the ``accel_with_rpm.wav`` file.
    """
    return _download_file("accel_with_rpm.wav")


def download_accel_with_rpm_2_wav():
    """Download the ``accel_with_rpm_2.wav`` file.

    Returns
    -------
    str
        Path for the ``accel_with_rpm_2.wav`` file.
    """
    return _download_file("accel_with_rpm_2.wav")


def download_accel_with_rpm_3_wav():
    """Download the ``accel_with_rpm_3.wav`` file.

    Returns
    -------
    str
        Path for the ``accel_with_rpm_3.wav`` file.
    """
    return _download_file("accel_with_rpm_3.wav")


def download_xtract_demo_signal_1_wav():
    """Download the ``xtract_demo_signal_1.wav`` file.

    Returns
    -------
    str
        Path for the ``xtract_demo_signal_1.wav`` file.
    """
    return _download_file("xtract_demo_signal_1.wav")


def download_xtract_demo_signal_2_wav():
    """Download the ``xtract_demo_signal_2.wav`` file.

    Returns
    -------
    str
        Path for the ``xtract_demo_signal_2.wav`` file.
    """
    return _download_file("xtract_demo_signal_2.wav")


def download_fan_wav():
    """Download the ``Fan.wav`` file.

    Returns
    -------
    str
        Path for the ``Fan.wav`` file.
    """
    return _download_file("Fan.wav")


def download_aircraft_wav():
    """Download the ``Aircraft.wav`` file.

    Returns
    -------
    str
        Path for the ``Aircraft.wav`` file.
    """
    return _download_file("Aircraft.wav")


def download_aircraft10kHz_wav():
    """Download the ``Aircraft.wav`` file.

    Returns
    -------
    str
        Path for the ``Aircraft_FS10kHz.wav`` file.
    """
    return _download_file("Aircraft_FS10kHz.wav")


def download_turbo_whistling_wav():
    """Download the ``Turbo_Whistling.wav`` file.

    Returns
    -------
    str
        Path for the ``Turbo_Whistling.wav`` file.
    """
    return _download_file("Turbo_Whistling.wav")


def download_sound_composer_project_whatif():
    """Download the ``SoundComposer-WhatIfScenario-Motor-Gear-HVAC-Noise.scn`` file.

    This file is a Sound Composer project file.

    Returns
    -------
    str
        Path for the ``SoundComposer-WhatIfScenario-Motor-Gear-HVAC-Noise.scn`` file.
    """
    return _download_file("SoundComposer-WhatIfScenario-Motor-Gear-HVAC-Noise.scn")


def download_sound_composer_source_eMotor():
    """Download the ``eMotor - FEM - orders levels (harmonics source).txt`` file.

    This file is a Sound Composer source of an eMotor.

    Returns
    -------
    str
        Path for the ``eMotor - FEM - orders levels (harmonics source).txt`` file.
    """
    return _download_file("eMotor - FEM - orders levels (harmonics source).txt")


def download_sound_composer_source_control_eMotor():
    """Download the ``eMotor - rpm evolution.txt`` file.

    This file is an eMotor source control, from 250 to 5000 rpm, in 8 seconds.

    Returns
    -------
    str
        Path for the ``eMotor - rpm evolution.txt`` file.
    """
    return _download_file(
        "eMotor - rpm evolution.txt",
    )


def download_sound_composer_FRF_eMotor():
    """Download the ``FRF - eMotor transfer.txt`` file.

    This file is a Frequency Response Function that represents the transfer of the eMotor noise
    to the receiver, to use in Sound Composer track.

    Returns
    -------
    str
        Path for the ``FRF - eMotor transfer.txt`` file.
    """
    return _download_file(
        "FRF - eMotor transfer.txt",
    )


def download_sound_composer_source_WindRoadNoise():
    """Download the ``Wind and Road noise - spectrum vs vehicle speed (BBN source).txt`` file.

    This file is the definition of a source of type broadband noise, which models the wind
    and road noise of a vehicle as a function of the speed. This source is defined between 10 and
    100 km/h, in 10 km/h steps. To be used in Sound Composer track.

    Returns
    -------
    str
        Path for the ``Wind and Road noise - spectrum vs vehicle speed (BBN source).txt`` file.
    """
    return _download_file("Wind and Road noise - spectrum vs vehicle speed (BBN source).txt")


def download_sound_composer_source_control_WindRoadNoise():
    """Download the ``WindRoadNoise - vehicle speed.txt`` file.

    This file is a wind and noise source control, evolving from 10 to 100 kph, in 8 seconds.


    Returns
    -------
    str
        Path for the ``WindRoadNoise - vehicle speed.txt`` file.
    """
    return _download_file("WindRoadNoise - vehicle speed.txt")


def download_HVAC_test_wav():
    """Download the ``HVAC_test.wav`` file.

    This file is a stationary automotive HVAC noise.

    Returns
    -------
    str
        Path for the ``HVAC_test.wav`` file.
    """
    return _download_file("HVAC_test.wav")


def download_all_carHVAC_wav() -> str:
    """Download all the ``carHVAC<i>.wav`` files.

    This function downloads 20 WAV files named ``carHVAC1.wav`` to ``carHVAC20.wav``.

    Returns
    -------
    str
        Path where the ``carHVAC<i>.wav`` files are located.
    """
    for i in range(20):
        filepath = _download_file(
            f"carHVAC{i+1}.wav",
        )
    return os.path.dirname(filepath)


def download_JLT_CE_data_csv():
    """Download the ``JLT_CE_data.csv`` file.

    Returns
    -------
    str
        Local path for the ``JLT_CE_data.csv`` file.
    """
    return _download_file("JLT_CE_data.csv")


def download_uff_sample_4_channels_type58b():
    """Download the ``4_channels_type58b.uff`` file.

    This function downloads a UFF/UNV file containing 4 data blocks of type 58b
    (binary time data, evenly spaced in time).

    Returns
    -------
    str
        Local path for the ``4_channels_type58b.uff`` file.
    """
    return _download_file("4_channels_type58b.uff")


def download_rpm_acceleration_deceleration():
    """Download the ``rpm_acceleration-deceleration.txt`` file.

    This file contains RPM data for acceleration and deceleration scenarios.

    Returns
    -------
    str
        Path for the ``rpm_acceleration-deceleration.txt`` file.
    """
    return _download_file("rpm_acceleration-deceleration.txt")
