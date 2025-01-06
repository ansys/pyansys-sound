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

from unittest.mock import patch

import numpy as np
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ansys.sound.core.signal_utilities import LoadWav


def test_load_wav_instantiation():
    wav_loader = LoadWav()
    assert wav_loader != None


def test_load_wav_process():
    # Should not return an error
    wav_loader_good = LoadWav(pytest.data_path_flute_in_container)
    wav_loader_good.process()

    # Should return an error
    wav_loader_bad = LoadWav()

    with pytest.raises(PyAnsysSoundException) as excinfo:
        wav_loader_bad.process()
    assert (
        str(excinfo.value) == "Path for loading WAV file is not specified. Use 'LoadWav.set_path'."
    )


def test_load_wav_get_output():
    wav_loader = LoadWav(pytest.data_path_flute_in_container)

    # Loading a wav signal using LoadWav class
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. \
                        Use the 'LoadWav.process\\(\\)' method.",
    ):
        fc = wav_loader.get_output()

    wav_loader.process()
    fc = wav_loader.get_output()

    # Extracting data
    data = fc[0].data

    # Checking data size and some random samples
    assert len(data) == 156048
    assert data[10] == 0.0
    assert data[1000] == 6.103515625e-05
    assert data[10000] == 0.0308837890625
    assert data[136047] == -0.084686279296875


def test_load_wav_get_output_as_nparray():
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()

    # Loading a wav signal using LoadWav
    np_arr = wav_loader.get_output_as_nparray()

    # Checking data size and some random samples
    assert len(np_arr) == 156048
    assert np_arr[10] == 0.0
    assert np_arr[1000] == 6.103515625e-05
    assert np_arr[10000] == 0.0308837890625
    assert np_arr[136047] == -0.084686279296875

    # Tests with a stereo signal
    wav_loader_stereo = LoadWav(pytest.data_path_white_noise_in_container)
    wav_loader_stereo.process()

    # Loading a wav signal using LoadWav
    np_arr = wav_loader_stereo.get_output_as_nparray()

    assert np.shape(np_arr) == (2, 480000)
    assert np_arr[1][1000] == 0.0169677734375
    assert np_arr[1][10000] == -0.27001953125
    assert np_arr[1][100000] == -0.0509033203125


def test_load_wav_get_set_path():
    wav_loader = LoadWav()
    wav_loader.path_to_wav = pytest.data_path_flute_in_container
    assert wav_loader.path_to_wav == pytest.data_path_flute_in_container


@patch("matplotlib.pyplot.show")
def test_load_wav_plot(mock_show):
    wav_loader = LoadWav(pytest.data_path_white_noise_in_container)
    wav_loader.process()
    wav_loader.plot()
