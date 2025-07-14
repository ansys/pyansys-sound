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
import pathlib

from ansys.sound.core.examples_helpers import (
    download_accel_with_rpm_2_wav,
    download_accel_with_rpm_3_wav,
    download_accel_with_rpm_wav,
    download_aircraft10kHz_wav,
    download_aircraft_wav,
    download_fan_wav,
    download_flute_psd,
    download_flute_wav,
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
from ansys.sound.core.examples_helpers.download import EXAMPLES_PATH


def test_download_flute_psd():
    download_flute_psd()[0]
    p = str(EXAMPLES_PATH) + "/flute_psd.txt"
    assert pathlib.Path(p).exists() == True
    assert os.path.getsize(p) == 118119


def test_download_flute_wav():
    download_flute_wav()[0]
    p = str(EXAMPLES_PATH) + "/flute.wav"
    assert pathlib.Path(p).exists() == True
    assert os.path.getsize(p) == 312297


def test_download_accel_with_rpm_wav():
    download_accel_with_rpm_wav()[0]
    p = str(EXAMPLES_PATH) + "/accel_with_rpm.wav"
    assert pathlib.Path(p).exists() == True
    assert os.path.getsize(p) == 3639982

    p = str(EXAMPLES_PATH) + "/accel_with_rpm_2.wav"
    download_accel_with_rpm_2_wav()[0]
    assert pathlib.Path(p).exists() == True
    assert os.path.getsize(p) == 3639982

    p = str(EXAMPLES_PATH) + "/accel_with_rpm_3.wav"
    download_accel_with_rpm_3_wav()[0]
    assert pathlib.Path(p).exists() == True
    assert os.path.getsize(p) == 3639982


def test_download_xtract_demo_signal_wav():
    download_xtract_demo_signal_1_wav()[0]
    p = str(EXAMPLES_PATH) + "/xtract_demo_signal_1.wav"
    assert pathlib.Path(p).exists() == True
    assert os.path.getsize(p) == 882363

    p = str(EXAMPLES_PATH) + "/xtract_demo_signal_2.wav"
    download_xtract_demo_signal_2_wav()[0]
    assert pathlib.Path(p).exists() == True
    assert os.path.getsize(p) == 882363


def test_download_fan_wav():
    download_fan_wav()[0]
    p = str(EXAMPLES_PATH) + "/Fan.wav"
    assert pathlib.Path(p).exists() == True
    assert os.path.getsize(p) == 500195


def test_download_aircraft_wav():
    download_aircraft_wav()[0]
    p = str(EXAMPLES_PATH) + "/Aircraft.wav"
    assert pathlib.Path(p).exists() == True
    assert os.path.getsize(p) == 2299160


def test_download_sound_composer_project_whatif():
    download_sound_composer_project_whatif()[0]
    p = str(EXAMPLES_PATH) + "/SoundComposer-WhatIfScenario-Motor-Gear-HVAC-Noise.scn"
    assert pathlib.Path(p).exists() == True
    assert os.path.getsize(p) == 1313147


def test_download_aircraft10kHz_wav():
    download_aircraft10kHz_wav()[0]
    p = str(EXAMPLES_PATH) + "/Aircraft_FS10kHz.wav"
    assert pathlib.Path(p).exists() == True
    assert os.path.getsize(p) == 521565


def test_download_turbo_whistling_wav():
    download_turbo_whistling_wav()[0]
    p = str(EXAMPLES_PATH) + "/Turbo_whistling.wav"
    assert pathlib.Path(p).exists() == True
    assert os.path.getsize(p) == 521565


def test_download_sound_composer_source_eMotor():
    download_sound_composer_source_eMotor()[0]
    p = str(EXAMPLES_PATH) + "/eMotor - FEM - orders levels (harmonics source).txt"
    assert pathlib.Path(p).exists() == True
    assert os.path.getsize(p) == 3153


def test_download_sound_composer_sourcecontrol_eMotor():
    download_sound_composer_source_control_eMotor()[0]
    p = str(EXAMPLES_PATH) + "/eMotor - rpm evolution.txt"
    assert pathlib.Path(p).exists() == True
    assert os.path.getsize(p) == 48


def test_download_sound_composer_FRF_eMotor():
    download_sound_composer_FRF_eMotor()[0]
    p = str(EXAMPLES_PATH) + "/FRF - eMotor transfer.txt"
    assert pathlib.Path(p).exists() == True
    assert os.path.getsize(p) == 612509


def test_download_sound_composer_source_WindRoadNoise():
    download_sound_composer_source_WindRoadNoise()[0]
    p = str(EXAMPLES_PATH) + "/Wind and Road noise - spectrum vs vehicle speed (BBN source).txt"
    assert pathlib.Path(p).exists() == True
    assert os.path.getsize(p) == 147261


def test_download_sound_composer_sourcecontrol_WindRoadNoise():
    download_sound_composer_source_control_WindRoadNoise()[0]
    p = str(EXAMPLES_PATH) + "/WindRoadNoise - vehicle speed.txt"
    assert pathlib.Path(p).exists() == True
    assert os.path.getsize(p) == 80
