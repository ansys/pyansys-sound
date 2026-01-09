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

from unittest.mock import patch

import numpy as np
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ansys.sound.core.signal_utilities import LoadWav


def test_load_wav_instantiation():
    """Test the instantiation of LoadWav class."""
    wav_loader = LoadWav()
    assert isinstance(wav_loader, LoadWav)


def test_load_wav_process():
    """Test the process method of LoadWav class."""
    # Should not return an error
    wav_loader_good = LoadWav(pytest.data_path_flute)
    wav_loader_good.process()

    # Should return an error
    wav_loader_bad = LoadWav()

    with pytest.raises(
        PyAnsysSoundException,
        match="Path for loading WAV file is not specified. Use `LoadWav.path_to_wav`.",
    ):
        wav_loader_bad.process()


def test_load_wav_get_output():
    """Test the get_output method of LoadWav class."""
    wav_loader = LoadWav(pytest.data_path_flute)

    # Loading a wav signal using LoadWav class
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the `LoadWav.process\\(\\)` method.",
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
    """Test the get_output_as_nparray method of LoadWav class."""
    wav_loader = LoadWav(pytest.data_path_flute)
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
    wav_loader_stereo = LoadWav(pytest.data_path_white_noise)
    wav_loader_stereo.process()

    # Loading a wav signal using LoadWav
    np_arr = wav_loader_stereo.get_output_as_nparray()

    assert np.shape(np_arr) == (2, 480000)
    assert np_arr[1][1000] == 0.0169677734375
    assert np_arr[1][10000] == -0.27001953125
    assert np_arr[1][100000] == -0.0509033203125


def test_load_wav_get_set_path():
    """Test the path setter of LoadWav class."""
    wav_loader = LoadWav()
    wav_loader.path_to_wav = pytest.data_path_flute
    assert wav_loader.path_to_wav == pytest.data_path_flute


@pytest.mark.skipif(
    not pytest.SERVERS_VERSION_GREATER_THAN_OR_EQUAL_TO_11_0,
    reason="Sampling frequency and format outputs require DPF server version 11.0 or higher.",
)
def test_load_wav_get_sampling_frequency():
    """Test getting the sampling frequency output of LoadWav class."""
    wav_loader = LoadWav(pytest.data_path_flute)

    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the `LoadWav.process\\(\\)` method.",
    ):
        fs = wav_loader.get_sampling_frequency()
    assert fs is None

    wav_loader.process()
    fs = wav_loader.get_sampling_frequency()

    assert fs == pytest.approx(44100.0)


@pytest.mark.skipif(
    not pytest.SERVERS_VERSION_GREATER_THAN_OR_EQUAL_TO_11_0,
    reason="Sampling frequency and format outputs require DPF server version 11.0 or higher.",
)
def test_load_wav_get_format():
    """Test getting the format output of LoadWav class."""
    wav_loader = LoadWav(pytest.data_path_flute)

    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the `LoadWav.process\\(\\)` method.",
    ):
        fmt = wav_loader.get_format()
    assert fmt is None

    wav_loader.process()
    fmt = wav_loader.get_format()
    assert fmt == "int16"

    wav_loader.path_to_wav = pytest.data_path_flute_int8
    wav_loader.process()
    fmt = wav_loader.get_format()
    assert fmt == "int8"

    wav_loader.path_to_wav = pytest.data_path_flute_int24
    wav_loader.process()
    fmt = wav_loader.get_format()
    assert fmt == "int24"

    wav_loader.path_to_wav = pytest.data_path_flute_int32
    wav_loader.process()
    fmt = wav_loader.get_format()
    assert fmt == "int32"

    wav_loader.path_to_wav = pytest.data_path_flute_float32
    wav_loader.process()
    fmt = wav_loader.get_format()
    assert fmt == "float32"


@patch("matplotlib.pyplot.show")
def test_load_wav_plot(mock_show):
    """Test the plot method of LoadWav class."""
    wav_loader = LoadWav(pytest.data_path_white_noise)
    with pytest.raises(
        PyAnsysSoundException,
        match="Output is not processed yet. Use the `LoadWav.process\\(\\)` method.",
    ):
        wav_loader.plot()
    wav_loader.process()
    wav_loader.plot()
