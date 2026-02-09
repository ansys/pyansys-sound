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

from ansys.dpf.core import Field
import numpy as np
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ansys.sound.core.signal_utilities import LoadWav, ZeroPad


def test_zero_pad_instantiation():
    zero_pad = ZeroPad()
    assert zero_pad != None


def test_zero_pad_process():
    zero_pad = ZeroPad()
    wav_loader = LoadWav(pytest.data_path_flute)

    # Error 1
    with pytest.raises(PyAnsysSoundException) as excinfo:
        zero_pad.process()
    assert str(excinfo.value) == "No signal found to zero pad. \
                    Use the 'ZeroPad.set_signal()' method."

    wav_loader.process()
    signal = wav_loader.get_output()

    zero_pad.signal = signal[0]
    zero_pad.process()


def test_zero_pad_get_output():
    wav_loader = LoadWav(pytest.data_path_flute)
    wav_loader.process()
    signal = wav_loader.get_output()
    zero_pad = ZeroPad(signal=signal[0], duration_zeros=12.0)

    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. \
                        Use the 'ZeroPad.process\\(\\)' method.",
    ):
        _ = zero_pad.get_output()

    zero_pad.process()
    output = zero_pad.get_output()

    assert len(output.data) == 685248
    assert output.data[1000] == 6.103515625e-05
    assert output.data[3456] == -0.00128173828125
    assert output.data[30000] == 0.074005126953125
    assert output.data[60000] == -0.022735595703125
    assert output.data[156048] == 0.0
    assert output.data[600000] == 0.0


def test_zero_pad_get_output_as_np_array():
    wav_loader = LoadWav(pytest.data_path_flute)
    wav_loader.process()
    signal = wav_loader.get_output()
    zero_pad = ZeroPad(signal=signal[0], duration_zeros=12.0)
    zero_pad.process()
    out_arr = zero_pad.get_output_as_nparray()

    assert len(out_arr) == 685248
    assert out_arr[1000] == 6.103515625e-05
    assert out_arr[3456] == -0.00128173828125
    assert out_arr[30000] == 0.074005126953125
    assert out_arr[60000] == -0.022735595703125
    assert out_arr[156048] == 0.0
    assert out_arr[600000] == 0.0


def test_zero_pad_set_get_signal():
    zero_pad = ZeroPad()
    signal = Field()
    signal.data = 42 * np.ones(3)
    zero_pad.signal = signal
    signal_from_getter = zero_pad.signal

    assert signal_from_getter.data[0, 2] == 42


def test_zero_pad_set_signal_exception():
    """Test exception for signal setter."""
    zero_pad = ZeroPad()

    with pytest.raises(PyAnsysSoundException, match="Signal must be specified as a DPF field."):
        zero_pad.signal = "WrongType"

    assert zero_pad.signal is None


def test_zero_pad_set_get_duration_zeros():
    zero_pad = ZeroPad()

    # Error
    with pytest.raises(PyAnsysSoundException) as excinfo:
        zero_pad.duration_zeros = -12.0
    assert str(excinfo.value) == "Zero duration must be greater than 0.0."
    zero_pad.duration_zeros = 1234.0
    assert zero_pad.duration_zeros == 1234.0
