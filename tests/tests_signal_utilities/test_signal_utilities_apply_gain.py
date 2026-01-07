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

from ansys.dpf.core import Field, FieldsContainer
import numpy as np
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ansys.sound.core.signal_utilities import ApplyGain, LoadWav


def test_apply_gain_instantiation():
    gain_applier = ApplyGain()
    assert gain_applier != None


def test_apply_gain_process():
    gain_applier = ApplyGain()
    wav_loader = LoadWav(pytest.data_path_flute_in_container)

    # Error 1
    with pytest.raises(PyAnsysSoundException) as excinfo:
        gain_applier.process()
    assert (
        str(excinfo.value) == "No signal to apply gain on. Use the 'ApplyGain.set_signal()' method."
    )

    wav_loader.process()
    fc = wav_loader.get_output()

    # Testing input fields container (no error expected)
    gain_applier.signal = fc
    gain_applier.process()

    # Testing input field (no error expected)
    gain_applier.signal = fc[0]
    gain_applier.process()


def test_apply_gain_get_output():
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc_signal = wav_loader.get_output()
    gain_applier = ApplyGain(signal=fc_signal, gain=12.0, gain_in_db=True)

    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the 'ApplyGain.process\\(\\)' method.",
    ):
        fc_out = gain_applier.get_output()

    gain_applier.process()
    fc_out = gain_applier.get_output()

    assert len(fc_out) == 1

    gain_applier.signal = fc_signal[0]
    gain_applier.process()
    f_out = gain_applier.get_output()

    assert len(f_out.data) == 156048
    assert f_out.data[1000] == 0.00024298533389810473
    assert f_out.data[3456] == -0.005102692171931267
    assert f_out.data[30000] == 0.29461970925331116
    assert f_out.data[60000] == -0.09051203727722168


def test_apply_gain_get_output_as_np_array():
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc_signal = wav_loader.get_output()
    gain_applier = ApplyGain(signal=fc_signal[0], gain=12.0, gain_in_db=True)
    gain_applier.process()
    out_arr = gain_applier.get_output_as_nparray()

    assert len(out_arr) == 156048
    assert out_arr[1000] == 0.00024298533389810473
    assert out_arr[3456] == -0.005102692171931267
    assert out_arr[30000] == 0.29461970925331116
    assert out_arr[60000] == -0.09051203727722168

    gain_applier.signal = fc_signal
    gain_applier.process()
    out_arr = gain_applier.get_output_as_nparray()

    assert len(out_arr) == 156048
    assert out_arr[1000] == 0.00024298533389810473
    assert out_arr[3456] == -0.005102692171931267
    assert out_arr[30000] == 0.29461970925331116
    assert out_arr[60000] == -0.09051203727722168


def test_apply_gain_set_get_signal():
    gain_applier = ApplyGain()
    fc = FieldsContainer()
    fc.labels = ["channel"]
    f = Field()
    f.data = 42 * np.ones(3)
    fc.add_field({"channel": 0}, f)
    fc.name = "testField"
    gain_applier.signal = fc
    fc_from_get = gain_applier.signal

    assert fc_from_get.name == "testField"
    assert len(fc_from_get) == 1
    assert fc_from_get[0].data[0, 2] == 42


def test_apply_gain_set_get_gain():
    gain_applier = ApplyGain()

    gain_applier.gain = 1234.0
    assert gain_applier.gain == 1234.0


def test_apply_gain_set_get_gain_in_db():
    gain_applier = ApplyGain()

    # Error 1
    with pytest.raises(PyAnsysSoundException) as excinfo:
        gain_applier.gain_in_db = 1234.0
    assert (
        str(excinfo.value) == "'new_gain_in_db' must be a Boolean value. Specify 'True' or 'False'."
    )

    gain_applier.gain_in_db = False
    assert gain_applier.gain_in_db == False
