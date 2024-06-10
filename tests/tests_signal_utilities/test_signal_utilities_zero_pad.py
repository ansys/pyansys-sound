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

from ansys.dpf.core import Field, FieldsContainer
import numpy as np
import pytest

from ansys.sound.core.pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ansys.sound.core.signal_utilities import LoadWav, ZeroPad


def test_zero_pad_instantiation(dpf_sound_test_server):
    zero_pad = ZeroPad()
    assert zero_pad != None


def test_zero_pad_process(dpf_sound_test_server):
    zero_pad = ZeroPad()
    wav_loader = LoadWav(pytest.data_path_flute_in_container)

    # Error 1
    with pytest.raises(PyAnsysSoundException) as excinfo:
        zero_pad.process()
    assert str(excinfo.value) == "No signal to zero-pad. Use ZeroPad.set_signal()."

    wav_loader.process()
    fc = wav_loader.get_output()

    # Testing input fields container (no error expected)
    zero_pad.signal = fc
    zero_pad.process()

    # Testing input field (no error expected)
    zero_pad.signal = fc[0]
    zero_pad.process()


def test_zero_pad_get_output(dpf_sound_test_server):
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc_signal = wav_loader.get_output()
    zero_pad = ZeroPad(signal=fc_signal, duration_zeros=12.0)

    with pytest.warns(
        PyAnsysSoundWarning, match="Output has not been yet processed, use ZeroPad.process()."
    ):
        fc_out = zero_pad.get_output()

    zero_pad.process()
    fc_out = zero_pad.get_output()

    assert len(fc_out) == 1

    zero_pad.signal = fc_signal[0]
    zero_pad.process()
    f_out = zero_pad.get_output()

    assert len(f_out.data) == 685248
    assert f_out.data[1000] == 6.103515625e-05
    assert f_out.data[3456] == -0.00128173828125
    assert f_out.data[30000] == 0.074005126953125
    assert f_out.data[60000] == -0.022735595703125
    assert f_out.data[156048] == 0.0
    assert f_out.data[600000] == 0.0


def test_zero_pad_get_output_as_np_array(dpf_sound_test_server):
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc_signal = wav_loader.get_output()
    zero_pad = ZeroPad(signal=fc_signal[0], duration_zeros=12.0)
    zero_pad.process()
    out_arr = zero_pad.get_output_as_nparray()

    assert len(out_arr) == 685248
    assert out_arr[1000] == 6.103515625e-05
    assert out_arr[3456] == -0.00128173828125
    assert out_arr[30000] == 0.074005126953125
    assert out_arr[60000] == -0.022735595703125
    assert out_arr[156048] == 0.0
    assert out_arr[600000] == 0.0

    zero_pad.signal = fc_signal
    zero_pad.process()
    out_arr = zero_pad.get_output_as_nparray()

    assert len(out_arr) == 685248
    assert out_arr[1000] == 6.103515625e-05
    assert out_arr[3456] == -0.00128173828125
    assert out_arr[30000] == 0.074005126953125
    assert out_arr[60000] == -0.022735595703125
    assert out_arr[156048] == 0.0
    assert out_arr[600000] == 0.0


def test_zero_pad_set_get_signal(dpf_sound_test_server):
    zero_pad = ZeroPad()
    fc = FieldsContainer()
    fc.labels = ["channel"]
    f = Field()
    f.data = 42 * np.ones(3)
    fc.add_field({"channel": 0}, f)
    fc.name = "testField"
    zero_pad.signal = fc
    fc_from_get = zero_pad.signal

    assert fc_from_get.name == "testField"
    assert len(fc_from_get) == 1
    assert fc_from_get[0].data[0, 2] == 42


def test_zero_pad_set_get_duration_zeros(dpf_sound_test_server):
    zero_pad = ZeroPad()

    # Error
    with pytest.raises(PyAnsysSoundException) as excinfo:
        zero_pad.duration_zeros = -12.0
    assert str(excinfo.value) == "Zero duration must be strictly greater than 0.0."
    zero_pad.duration_zeros = 1234.0
    assert zero_pad.duration_zeros == 1234.0
