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

from ansys.dpf.core import Field, FieldsContainer
import numpy as np
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ansys.sound.core.signal_utilities import LoadWav
from ansys.sound.core.spectrogram_processing import Istft, Stft

EXP_SIZE = 156048

if pytest.SOUND_VERSION_GREATER_THAN_OR_EQUAL_TO_2026R1:
    # Third-party update (IPP) in DPF Sound 2026 R1
    EXP_100 = 8.265356715025929e-13
    EXP_2000 = -0.001495360629633069
    EXP_30000 = 0.0740051418542862
else:  # DPF Sound <= 2025 R2
    EXP_100 = -3.790271482090324e-12
    EXP_2000 = -0.0014953609788790345
    EXP_30000 = 0.0740051195025444


def test_istft_instantiation():
    stft = Istft()
    assert stft != None


def test_istft_process():
    wav_loader = LoadWav(pytest.data_path_flute)
    wav_loader.process()
    stft = Stft(signal=wav_loader.get_output()[0])
    stft.process()
    istft = Istft()

    # Error 1
    with pytest.raises(PyAnsysSoundException) as excinfo:
        istft.process()
    assert str(excinfo.value) == "No STFT input found for ISTFT computation. Use 'Istft.stft'."

    # Testing input fields container (no error expected)
    istft.stft = stft.get_output()
    try:
        istft.process()
    except:
        # Should not fail
        assert False


def test_istft_get_output():
    wav_loader = LoadWav(pytest.data_path_flute)
    wav_loader.process()
    stft = Stft(signal=wav_loader.get_output()[0])
    stft.process()
    istft = Istft(stft=stft.get_output())

    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. \
                        Use the 'Istft.process\\(\\)' method.",
    ):
        fc_out = istft.get_output()

    istft.process()
    f_out = istft.get_output()

    assert len(f_out) == EXP_SIZE
    assert f_out.data[100] == EXP_100
    assert f_out.data[2000] == EXP_2000
    assert f_out.data[30000] == EXP_30000


def test_istft_get_output_as_np_array():
    wav_loader = LoadWav(pytest.data_path_flute)
    wav_loader.process()
    stft = Stft(signal=wav_loader.get_output()[0])
    stft.process()
    istft = Istft(stft=stft.get_output())

    istft.process()
    arr = istft.get_output_as_nparray()

    assert len(arr) == EXP_SIZE
    assert arr[100] == EXP_100
    assert arr[2000] == EXP_2000
    assert arr[30000] == EXP_30000


def test_istft_set_get_signal():
    # Test 1 with error
    istft = Istft()
    fc = FieldsContainer()
    fc.labels = ["channel"]
    f = Field()
    f.data = 42 * np.ones(3)
    fc.add_field({"channel": 0}, f)

    # Error
    with pytest.raises(PyAnsysSoundException) as excinfo:
        istft.stft = 456
    assert str(excinfo.value) == "Input must be a DPF fields container."

    with pytest.raises(PyAnsysSoundException) as excinfo:
        istft.stft = fc
    assert (
        str(excinfo.value) == "STFT is in the wrong format. Make sure that it has been computed "
        "with the 'Stft' class."
    )

    # Test 2 - No Error
    wav_loader = LoadWav(pytest.data_path_flute)
    wav_loader.process()
    stft = Stft(signal=wav_loader.get_output()[0])
    stft.process()
    istft.stft = stft.get_output()

    out_stft = istft.stft

    assert out_stft.has_label("time")
    assert out_stft.has_label("channel_number")
    assert out_stft.has_label("complex")


@patch("matplotlib.pyplot.show")
def test_istft_plot(mock_show):
    wav_loader = LoadWav(pytest.data_path_flute)
    wav_loader.process()
    stft = Stft(signal=wav_loader.get_output()[0])
    stft.process()
    istft = Istft(stft=stft.get_output())
    with pytest.raises(
        PyAnsysSoundException,
        match="Output is not processed yet. Use the `Istft.process\\(\\)` method.",
    ):
        istft.plot()
    istft.process()
    istft.plot()
