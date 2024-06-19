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

import pathlib

from ansys.sound.core.examples_helpers import (
    download_accel_with_rpm_2_wav,
    download_accel_with_rpm_3_wav,
    download_accel_with_rpm_wav,
    download_flute_2_wav,
    download_flute_psd,
    download_flute_wav,
    download_xtract_demo_signal_1_wav,
    download_xtract_demo_signal_2_wav,
    get_absolute_path_for_accel_with_rpm_wav,
    get_absolute_path_for_fluctuating_noise_wav,
    get_absolute_path_for_fluctuating_tone_wav,
    get_absolute_path_for_flute2_wav,
    get_absolute_path_for_flute_wav,
    get_absolute_path_for_rough_noise_wav,
    get_absolute_path_for_rough_tone_wav,
    get_absolute_path_for_sharp_noise_wav,
    get_absolute_path_for_sharper_noise_wav,
    get_absolute_path_for_xtract_demo_signal_1_wav,
    get_absolute_path_for_xtract_demo_signal_2_wav,
)
from ansys.sound.core.examples_helpers.download import EXAMPLES_PATH


def test_data_path_xtract_demo_signal_1_wav():
    p = get_absolute_path_for_xtract_demo_signal_1_wav()
    assert p == "C:\\data\\xtract_demo_signal_1.wav"


def test_data_path_xtract_demo_signal_2_wav():
    p = get_absolute_path_for_xtract_demo_signal_2_wav()
    assert p == "C:\\data\\xtract_demo_signal_2.wav"


def test_data_path_flute_wav():
    p = get_absolute_path_for_flute_wav()
    assert p == "C:\\data\\flute.wav"


def test_data_path_flute2_wav():
    p = get_absolute_path_for_flute2_wav()
    assert p == "C:\\data\\flute2.wav"


def test_data_path_accel_with_rpm_wav():
    p = get_absolute_path_for_accel_with_rpm_wav()
    assert p == "C:\\data\\accel_with_rpm.wav"


def test_data_path_sharp_noise_wav():
    p = get_absolute_path_for_sharp_noise_wav()
    assert p == "C:\\data\\sharp_noise.wav"


def test_data_path_sharper_noise_wav():
    p = get_absolute_path_for_sharper_noise_wav()
    assert p == "C:\\data\\sharper_noise.wav"


def test_data_path_rough_noise_wav():
    p = get_absolute_path_for_rough_noise_wav()
    assert p == "C:\\data\\rough_noise.wav"


def test_data_path_rough_tone_wav():
    p = get_absolute_path_for_rough_tone_wav()
    assert p == "C:\\data\\rough_tone.wav"


def test_data_path_fluctuating_noise_wav():
    p = get_absolute_path_for_fluctuating_noise_wav()
    assert p == "C:\\data\\fluctuating_noise.wav"


def test_data_path_fluctuating_tone_wav():
    p = get_absolute_path_for_fluctuating_tone_wav()
    assert p == "C:\\data\\fluctuating_tone.wav"


def test_download_flute_psd():
    download_flute_psd()[0]
    p = str(EXAMPLES_PATH) + "/flute_psd.txt"
    assert pathlib.Path(p).exists() == True


def test_download_flute_wav():
    download_flute_wav()[0]
    p = str(EXAMPLES_PATH) + "/flute.wav"
    assert pathlib.Path(p).exists() == True
    p = str(EXAMPLES_PATH) + "/flute2.wav"
    download_flute_2_wav()[0]
    assert pathlib.Path(p).exists() == True


def test_download_accel_with_rpm_wav():
    download_accel_with_rpm_wav()[0]
    p = str(EXAMPLES_PATH) + "/accel_with_rpm.wav"
    assert pathlib.Path(p).exists() == True
    p = str(EXAMPLES_PATH) + "/accel_with_rpm_2.wav"
    download_accel_with_rpm_2_wav()[0]
    assert pathlib.Path(p).exists() == True
    p = str(EXAMPLES_PATH) + "/accel_with_rpm_3.wav"
    download_accel_with_rpm_3_wav()[0]
    assert pathlib.Path(p).exists() == True


def test_download_xtract_demo_signal_wav():
    download_xtract_demo_signal_1_wav()[0]
    p = str(EXAMPLES_PATH) + "/xtract_demo_signal_1.wav"
    assert pathlib.Path(p).exists() == True
    p = str(EXAMPLES_PATH) + "/xtract_demo_signal_2.wav"
    download_xtract_demo_signal_2_wav()[0]
    assert pathlib.Path(p).exists() == True
