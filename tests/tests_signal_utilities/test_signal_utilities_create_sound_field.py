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

import numpy as np
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ansys.sound.core.signal_utilities import CreateSoundField


def test_create_sound_field_instantiation(dpf_sound_test_server):
    sound_field_creator = CreateSoundField()
    assert sound_field_creator != None


def test_create_sound_field_process(dpf_sound_test_server):
    sound_field_creator = CreateSoundField()

    # Error 1
    with pytest.raises(PyAnsysSoundException) as excinfo:
        sound_field_creator.process()
    assert str(excinfo.value) == "No data to use. Use the 'CreateSoundField.set_data()' method."

    # No error
    arr = np.ones(100)
    sound_field_creator.data = arr
    sound_field_creator.process()


def test_create_sound_field_get_output(dpf_sound_test_server):
    sound_field_creator = CreateSoundField(data=np.ones(100))

    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the 'CreateSoundField.process()' method.",
    ):
        f_out = sound_field_creator.get_output()

    sound_field_creator.process()
    f_out = sound_field_creator.get_output()

    assert len(f_out) == 100
    assert f_out.data[0] == 1.0
    assert f_out.data[50] == 1.0
    assert f_out.data[99] == 1.0


def test_create_sound_field_get_output_as_np_array(dpf_sound_test_server):
    sound_field_creator = CreateSoundField(data=np.ones(100))
    sound_field_creator.process()
    out_arr = sound_field_creator.get_output_as_nparray()

    assert len(out_arr) == 100
    assert out_arr[0] == 1.0
    assert out_arr[50] == 1.0
    assert out_arr[99] == 1.0


def test_create_sound_field_set_get_data(dpf_sound_test_server):
    sound_field_creator = CreateSoundField()
    sound_field_creator.data = np.ones(100)
    data = sound_field_creator.data
    assert len(data) == 100
    assert data[0] == 1.0
    assert data[50] == 1.0
    assert data[99] == 1.0


def test_create_sound_field_set_get_sampling_frequency(dpf_sound_test_server):
    sound_field_creator = CreateSoundField()

    # Error 1
    with pytest.raises(PyAnsysSoundException) as excinfo:
        sound_field_creator.sampling_frequency = -1234.0
    assert str(excinfo.value) == "Sampling frequency must be greater than or equal to 0.0."

    sound_field_creator.sampling_frequency = 1234.0
    assert sound_field_creator.sampling_frequency == 1234.0


def test_create_sound_field_set_get_unit(dpf_sound_test_server):
    sound_field_creator = CreateSoundField()

    sound_field_creator.unit = "MyUnit"
    assert sound_field_creator.unit == "MyUnit"
