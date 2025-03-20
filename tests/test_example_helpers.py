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
    download_flute_psd,
    download_flute_wav,
    download_xtract_demo_signal_1_wav,
    download_xtract_demo_signal_2_wav,
    download_fan_wav,
    download_aircraft_wav,
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