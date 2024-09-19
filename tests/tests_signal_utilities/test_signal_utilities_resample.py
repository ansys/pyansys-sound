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

import numpy as np
import pytest
from ansys.dpf.core import Field, FieldsContainer

from ansys.sound.core._pyansys_sound import (PyAnsysSoundException,
                                             PyAnsysSoundWarning)
from ansys.sound.core.signal_utilities import LoadWav, Resample


def test_resample_instantiation(dpf_sound_test_server):
    resampler = Resample()
    assert resampler != None


def test_resample_process(dpf_sound_test_server):
    resampler = Resample()
    wav_loader = LoadWav(pytest.data_path_flute_in_container)

    # Error 1
    with pytest.raises(PyAnsysSoundException) as excinfo:
        resampler.process()
    assert str(excinfo.value) == "No signal to resample. Use the 'Resample.set_signal()' method."

    wav_loader.process()
    fc = wav_loader.get_output()

    # Testing input fields container (no error expected)
    resampler.signal = fc
    resampler.process()

    # Testing input field (no error expected)
    resampler.signal = fc[0]
    resampler.process()


def test_resample_get_output(dpf_sound_test_server):
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc_signal = wav_loader.get_output()
    resampler = Resample(signal=fc_signal, new_sampling_frequency=88100.0)

    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. \
                        Use the 'Resample.process\\(\\)' method.",
    ):
        fc_out = resampler.get_output()

    resampler.process()
    fc_out = resampler.get_output()

    assert len(fc_out) == 1

    resampler.signal = fc_signal[0]
    resampler.process()
    f_out = resampler.get_output()

    assert len(f_out.data) == 311743
    assert f_out.data[1000] == 2.9065033686492825e-06
    assert f_out.data[3456] == -0.0007385587086901069
    assert f_out.data[30000] == 0.02302781119942665
    assert f_out.data[60000] == -0.4175410866737366


def test_resample_get_output_as_np_array(dpf_sound_test_server):
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc_signal = wav_loader.get_output()
    resampler = Resample(signal=fc_signal[0], new_sampling_frequency=88100.0)
    resampler.process()
    out_arr = resampler.get_output_as_nparray()

    assert len(out_arr) == 311743
    assert out_arr[1000] == 2.9065033686492825e-06
    assert out_arr[3456] == -0.0007385587086901069
    assert out_arr[30000] == 0.02302781119942665
    assert out_arr[60000] == -0.4175410866737366

    resampler.signal = fc_signal
    resampler.process()
    out_arr = resampler.get_output_as_nparray()

    assert len(out_arr) == 311743
    assert out_arr[1000] == 2.9065033686492825e-06
    assert out_arr[3456] == -0.0007385587086901069
    assert out_arr[30000] == 0.02302781119942665
    assert out_arr[60000] == -0.4175410866737366


def test_resample_set_get_signal(dpf_sound_test_server):
    resampler = Resample()
    fc = FieldsContainer()
    fc.labels = ["channel"]
    f = Field()
    f.data = 42 * np.ones(3)
    fc.add_field({"channel": 0}, f)
    fc.name = "testField"
    resampler.signal = fc
    fc_from_get = resampler.signal

    assert fc_from_get.name == "testField"
    assert len(fc_from_get) == 1
    assert fc_from_get[0].data[0, 2] == 42


def test_resample_set_get_sampling_frequency(dpf_sound_test_server):
    resampler = Resample()

    # Error
    with pytest.raises(PyAnsysSoundException) as excinfo:
        resampler.new_sampling_frequency = -12.0
    assert str(excinfo.value) == "Sampling frequency must be greater than 0.0."

    resampler.new_sampling_frequency = 1234.0
    assert resampler.new_sampling_frequency == 1234.0


@patch("matplotlib.pyplot.show")
def test_resample_plot(mock_show, dpf_sound_test_server):
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc_signal = wav_loader.get_output()
    resampler = Resample(signal=fc_signal, new_sampling_frequency=88100.0)
    resampler.process()
    resampler.plot()

    resampler.signal = fc_signal[0]
    resampler.process()
    resampler.plot()
