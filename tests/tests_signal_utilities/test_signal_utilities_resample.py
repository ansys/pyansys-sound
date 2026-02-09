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

from ansys.dpf.core import Field
import numpy as np
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ansys.sound.core.signal_utilities import LoadWav, Resample

EXP_SIZE = 311743

if pytest.SOUND_VERSION_GREATER_THAN_OR_EQUAL_TO_2026R1:
    # Third-party update (IPP) in DPF Sound 2026 R1
    EXP_1000 = 2.9065022317809053e-06
    EXP_3456 = -0.000738558592274785
    EXP_30000 = 0.02302781119942665
    EXP_60000 = -0.4175410866737366
else:  # DPF Sound <= 2025 R2
    EXP_1000 = 2.9065033686492825e-06
    EXP_3456 = -0.0007385587086901069
    EXP_30000 = 0.02302781119942665
    EXP_60000 = -0.4175410866737366


def test_resample_instantiation():
    resampler = Resample()
    assert resampler != None


def test_resample_process():
    resampler = Resample()
    wav_loader = LoadWav(pytest.data_path_flute)

    # Error 1
    with pytest.raises(PyAnsysSoundException) as excinfo:
        resampler.process()
    assert str(excinfo.value) == "No signal to resample. Use the 'Resample.set_signal()' method."

    wav_loader.process()
    signal = wav_loader.get_output()

    resampler.signal = signal[0]
    resampler.process()
    assert resampler._output is not None


def test_resample_get_output():
    wav_loader = LoadWav(pytest.data_path_flute)
    wav_loader.process()
    signal = wav_loader.get_output()
    resampler = Resample(signal=signal[0], new_sampling_frequency=88100.0)

    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. \
                        Use the 'Resample.process\\(\\)' method.",
    ):
        _ = resampler.get_output()

    resampler.process()
    output = resampler.get_output()

    assert len(output.data) == EXP_SIZE
    assert output.data[1000] == EXP_1000
    assert output.data[3456] == EXP_3456
    assert output.data[30000] == EXP_30000
    assert output.data[60000] == EXP_60000


def test_resample_get_output_as_np_array():
    wav_loader = LoadWav(pytest.data_path_flute)
    wav_loader.process()
    signal = wav_loader.get_output()
    resampler = Resample(signal=signal[0], new_sampling_frequency=88100.0)
    resampler.process()
    out_arr = resampler.get_output_as_nparray()

    assert len(out_arr) == EXP_SIZE
    assert out_arr[1000] == EXP_1000
    assert out_arr[3456] == EXP_3456
    assert out_arr[30000] == EXP_30000
    assert out_arr[60000] == EXP_60000


def test_resample_set_get_signal():
    resampler = Resample()
    signal = Field()
    signal.data = 42 * np.ones(3)
    resampler.signal = signal
    signal_from_getter = resampler.signal

    assert signal_from_getter.data[0, 2] == 42


def test_resample_set_signal_exception():
    """Test exception for signal setter."""
    resampler = Resample()

    with pytest.raises(PyAnsysSoundException, match="Signal must be specified as a DPF field."):
        resampler.signal = "WrongType"

    assert resampler.signal is None


def test_resample_set_get_sampling_frequency():
    resampler = Resample()

    # Error
    with pytest.raises(PyAnsysSoundException) as excinfo:
        resampler.new_sampling_frequency = -12.0
    assert str(excinfo.value) == "Sampling frequency must be greater than 0.0."

    resampler.new_sampling_frequency = 1234.0
    assert resampler.new_sampling_frequency == 1234.0


@patch("matplotlib.pyplot.show")
def test_resample_plot(mock_show):
    wav_loader = LoadWav(pytest.data_path_flute)
    wav_loader.process()
    signal = wav_loader.get_output()
    resampler = Resample(signal=signal[0], new_sampling_frequency=88100.0)
    resampler.process()
    resampler.plot()
