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

from ansys.dpf.core import Field, FieldsContainer
import numpy as np
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ansys.sound.core.signal_utilities import CropSignal, LoadWav


def test_crop_signal_instantiation():
    signal_cropper = CropSignal()
    assert signal_cropper != None


def test_crop_signal_process():
    signal_cropper = CropSignal(start_time=0.0, end_time=1.0)
    wav_loader = LoadWav(pytest.data_path_flute_in_container)

    # Error 1
    with pytest.raises(PyAnsysSoundException) as excinfo:
        signal_cropper.process()
    assert (
        str(excinfo.value)
        == "No signal found to crop. \
                Use the 'CropSignal.set_signal()' method."
    )

    wav_loader.process()
    fc = wav_loader.get_output()

    # Testing input fields container (no error expected)
    signal_cropper.signal = fc
    signal_cropper.process()

    # # Testing input field (no error expected)
    # signal_cropper.signal = fc[0]
    # signal_cropper.process()


def test_crop_signal_get_output():
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc_signal = wav_loader.get_output()
    signal_cropper = CropSignal(signal=fc_signal, start_time=0.0, end_time=1.0)

    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. \
                        Use the 'CropSignal.process\\(\\)' method.",
    ):
        fc_out = signal_cropper.get_output()

    signal_cropper.process()
    fc_out = signal_cropper.get_output()

    assert len(fc_out) == 1

    # signal_cropper.signal = fc_signal[0]
    # signal_cropper.process()
    # f_out = signal_cropper.get_output()
    data = fc_out[0].data
    # Checking data size and some random samples
    assert len(data) == 44101
    assert data[10] == 0.0
    assert data[1000] == 6.103515625e-05
    assert data[10000] == 0.0308837890625
    assert data[44000] == 0.47772216796875


def test_crop_signal_get_output_as_np_array():
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc_signal = wav_loader.get_output()
    signal_cropper = CropSignal(signal=fc_signal, start_time=0.0, end_time=1.0)

    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. \
                        Use the 'CropSignal.process\\(\\)' method.",
    ):
        fc_out = signal_cropper.get_output()

    signal_cropper.process()
    data = signal_cropper.get_output_as_nparray()

    assert len(data) == 44101
    assert data[10] == 0.0
    assert data[1000] == 6.103515625e-05
    assert data[10000] == 0.0308837890625
    assert data[44000] == 0.47772216796875

    # signal_cropper.signal = fc_signal[0]
    # signal_cropper.process()
    # data = signal_cropper.get_output_as_nparray()
    # # Checking data size and some random samples
    # assert len(data) == 44101
    # assert data[10] == 0.0
    # assert data[1000] == 6.103515625e-05
    # assert data[10000] == 0.0308837890625
    # assert data[44000] == 0.47772216796875


def test_crop_signal_set_get_signal():
    signal_cropper = CropSignal()
    fc = FieldsContainer()
    fc.labels = ["channel"]
    f = Field()
    f.data = 42 * np.ones(3)
    fc.add_field({"channel": 0}, f)
    fc.name = "testField"
    signal_cropper.signal = fc
    fc_from_get = signal_cropper.signal

    assert fc_from_get.name == "testField"
    assert len(fc_from_get) == 1
    assert fc_from_get[0].data[0, 2] == 42


def test_crop_signal_set_get_start_end_times():
    signal_cropper = CropSignal()

    # Error
    with pytest.raises(PyAnsysSoundException) as excinfo:
        signal_cropper.start_time = -12.0
    assert str(excinfo.value) == "Start time must be greater than or equal to 0.0."

    # Error
    with pytest.raises(PyAnsysSoundException) as excinfo:
        signal_cropper.end_time = -12.0
    assert str(excinfo.value) == "End time must be greater than or equal to 0.0."

    signal_cropper.start_time = 1.0

    # Error
    with pytest.raises(PyAnsysSoundException) as excinfo:
        signal_cropper.end_time = 0.5
    assert str(excinfo.value) == "End time must be greater than or equal to the start time."

    signal_cropper.end_time = 1234.0

    start_time = signal_cropper.start_time
    end_time = signal_cropper.end_time
    assert start_time == 1.0
    assert end_time == 1234.0
