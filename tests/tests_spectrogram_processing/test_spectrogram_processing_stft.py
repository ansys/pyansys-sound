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

from unittest.mock import patch

from ansys.dpf.core import Field, FieldsContainer
import numpy as np
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ansys.sound.core.signal_utilities import LoadWav
from ansys.sound.core.spectrogram_processing import Stft


def test_stft_instantiation():
    stft = Stft()
    assert stft != None


def test_stft_process():
    stft = Stft()
    wav_loader = LoadWav(pytest.data_path_flute_in_container)

    # Error 1
    with pytest.raises(PyAnsysSoundException) as excinfo:
        stft.process()
    assert str(excinfo.value) == "No signal found for STFT. Use 'Stft.signal'."

    wav_loader.process()
    fc = wav_loader.get_output()

    # Testing input fields container (no error expected)
    stft.signal = fc
    try:
        stft.process()
    except:
        # Should not fail
        assert False


def test_stft_get_output():
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc_signal = wav_loader.get_output()
    stft = Stft(signal=fc_signal)

    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. \
                    Use the 'Stft.process\\(\\)' method.",
    ):
        fc_out = stft.get_output()

    stft.process()
    fc_out = stft.get_output()

    assert len(fc_out) == 310
    assert len(fc_out[100].data) == stft.fft_size
    assert fc_out[100].data[0] == -0.11434437334537506
    assert fc_out[200].data[0] == -0.09117653965950012
    assert fc_out[300].data[0] == -0.019828863441944122


def test_stft_get_output_as_np_array():
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc_signal = wav_loader.get_output()
    stft = Stft(signal=fc_signal)

    stft.process()
    arr = stft.get_output_as_nparray()

    assert np.shape(arr) == (stft.fft_size, 155)

    assert type(arr[100, 0]) == np.complex128
    assert arr[100, 50] == (-1.0736324787139893 - 1.4027032852172852j)
    assert arr[200, 50] == (0.511505126953125 + 0.3143689036369324j)
    assert arr[300, 50] == (-0.03049434721469879 - 0.49174121022224426j)


def test_stft_set_get_signal():
    stft = Stft()
    fc = FieldsContainer()
    fc.labels = ["channel"]
    f = Field()
    f.data = 42 * np.ones(3)
    fc.add_field({"channel": 0}, f)
    fc.name = "testField"
    stft.signal = fc
    f = stft.signal

    assert len(f) == 3
    assert f.data[0, 2] == 42

    stft.signal = fc[0]
    fc_from_get = stft.signal

    assert len(f) == 3
    assert f.data[0, 2] == 42

    fc.add_field({"channel": 1}, fc[0])

    # Error
    with pytest.raises(PyAnsysSoundException) as excinfo:
        stft.signal = fc
    assert (
        str(excinfo.value)
        == "Input as a DPF fields container can only have one field (mono signal)."
    )


def test_stft_set_get_fft_size():
    stft = Stft()

    # Error
    with pytest.raises(PyAnsysSoundException) as excinfo:
        stft.fft_size = -12.0
    assert str(excinfo.value) == "FFT size must be greater than 0.0."

    stft.fft_size = 1234.0
    assert stft.fft_size == 1234.0


def test_stft_set_get_window_overlap():
    stft = Stft()

    # Error
    with pytest.raises(PyAnsysSoundException) as excinfo:
        stft.window_overlap = -12.0
    assert str(excinfo.value) == "Window overlap must be between 0.0 and 1.0."

    stft.window_overlap = 0.5
    assert stft.window_overlap == 0.5


def test_stft_set_get_window_type():
    stft = Stft()

    # Error
    with pytest.raises(PyAnsysSoundException) as excinfo:
        stft.window_type = "InvalidWindow"
    assert (
        str(excinfo.value)
        == "Window type is invalid. Options are 'BARTLETT', 'BLACKMAN', 'BLACKMANHARRIS', "
        "'HAMMING', 'HANN', 'KAISER', and 'RECTANGULAR'."
    )

    stft.window_type = "KAISER"
    assert stft.window_type == "KAISER"


@patch("matplotlib.pyplot.show")
def test_stft_plot(mock_show):
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc_signal = wav_loader.get_output()
    stft = Stft(signal=fc_signal)
    stft.process()
    stft.plot()
