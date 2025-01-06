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

from unittest.mock import patch

from ansys.dpf.core import Field, FieldsContainer
import numpy as np
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ansys.sound.core.signal_utilities import LoadWav
from ansys.sound.core.xtract.xtract_tonal import XtractTonal
from ansys.sound.core.xtract.xtract_tonal_parameters import XtractTonalParameters


def test_xtract_tonal_instantiation():
    xtract_tonal = XtractTonal()
    assert xtract_tonal != None


def test_xtract_tonal_initialization_FieldsContainer():
    # Test initialization with default values
    xtract_tonal = XtractTonal()
    assert xtract_tonal.input_signal is None
    assert xtract_tonal.input_parameters is None
    assert xtract_tonal.output_tonal_signals is None
    assert xtract_tonal.output_non_tonal_signals is None

    # Test initialization with custom values
    input_signal = FieldsContainer()
    input_parameters = XtractTonalParameters()
    xtract_tonal = XtractTonal(
        input_signal=input_signal,
        input_parameters=input_parameters,
    )
    assert xtract_tonal.input_signal == input_signal
    assert xtract_tonal.input_parameters == input_parameters
    assert xtract_tonal.output_tonal_signals is None
    assert xtract_tonal.output_non_tonal_signals is None


def test_xtract_tonal_initialization_Field():
    # Test initialization with default values
    xtract_tonal = XtractTonal()
    assert xtract_tonal.input_signal is None
    assert xtract_tonal.input_parameters is None
    assert xtract_tonal.output_tonal_signals is None
    assert xtract_tonal.output_non_tonal_signals is None

    # Test initialization with custom values
    input_signal = Field()
    input_parameters = XtractTonalParameters()
    xtract_tonal = XtractTonal(
        input_signal=input_signal,
        input_parameters=input_parameters,
    )
    assert xtract_tonal.input_signal == input_signal
    assert xtract_tonal.input_parameters == input_parameters
    assert xtract_tonal.output_tonal_signals is None
    assert xtract_tonal.output_non_tonal_signals is None


def test_xtract_tonal_process_except1():
    xtract_tonal = XtractTonal(None, XtractTonalParameters())
    with pytest.raises(PyAnsysSoundException) as excinfo:
        xtract_tonal.process()
    assert str(excinfo.value) == "No input signal found for tonal analysis."


def test_xtract_tonal_process_except2():
    xtract_tonal = XtractTonal(Field(), None)
    with pytest.raises(PyAnsysSoundException) as excinfo:
        xtract_tonal.process()
    assert str(excinfo.value) == "Input parameters are not set."


def test_xtract_tonal_process():
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute_in_container)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    # Setting tonal parameters
    params_tonal = XtractTonalParameters()
    params_tonal.regularity = 1.0
    params_tonal.maximum_slope = 750.0
    params_tonal.minimum_duration = 1.0
    params_tonal.intertonal_gap = 20.0
    params_tonal.local_emergence = 15.0
    params_tonal.fft_size = 8192

    xtract_tonal = XtractTonal(bird_plus_idle_sig, params_tonal)
    xtract_tonal.process()

    assert xtract_tonal.output_tonal_signals is not None
    assert xtract_tonal.output_non_tonal_signals is not None

    assert type(xtract_tonal.output_tonal_signals) == Field
    assert type(xtract_tonal.output_non_tonal_signals) == Field

    # Type of output tonal signals. np.array
    assert xtract_tonal.get_output_as_nparray() is not None
    assert type(xtract_tonal.get_output_as_nparray()[0]) == np.ndarray
    assert type(xtract_tonal.get_output_as_nparray()[1]) == np.ndarray

    assert xtract_tonal.get_output_as_nparray()[0].shape == (156048,)
    assert np.min(xtract_tonal.get_output_as_nparray()[0]) == pytest.approx(-0.6828306913375854)
    assert np.max(xtract_tonal.get_output_as_nparray()[0]) == pytest.approx(0.794617772102356)

    assert xtract_tonal.get_output_as_nparray()[0][0] == pytest.approx(3.6770161386812106e-06)
    assert xtract_tonal.get_output_as_nparray()[0][1] == pytest.approx(1.8551201037553255e-06)

    assert xtract_tonal.get_output_as_nparray()[1].shape == (156048,)
    assert xtract_tonal.get_output_as_nparray()[1][0] == pytest.approx(-3.6770161386812106e-06)
    assert xtract_tonal.get_output_as_nparray()[1][99] == pytest.approx(1.8362156879447866e-06)


def test_xtract_tonal_get_output_warns():
    xtract_tonal = XtractTonal()
    with pytest.warns(PyAnsysSoundWarning) as record:
        xtract_tonal.get_output()
    assert "Output is not processed yet." in record[0].message.args[0]


def test_xtract_tonal_get_output_as_nparray_warns():
    xtract_tonal = XtractTonal()
    with pytest.warns(PyAnsysSoundWarning) as record:
        xtract_tonal.get_output_as_nparray()
    assert "Output is not processed yet." in record[0].message.args[0]


def test_xtract_tonal_get_output():
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute_in_container)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    # Setting tonal parameters
    params_tonal = XtractTonalParameters()
    params_tonal.regularity = 1.0
    params_tonal.maximum_slope = 750.0
    params_tonal.minimum_duration = 1.0
    params_tonal.intertonal_gap = 20.0
    params_tonal.local_emergence = 15.0
    params_tonal.fft_size = 8192

    xtract_tonal = XtractTonal(bird_plus_idle_sig, params_tonal)
    xtract_tonal.process()

    assert xtract_tonal.output_tonal_signals is not None
    assert xtract_tonal.output_non_tonal_signals is not None

    assert type(xtract_tonal.output_tonal_signals) == Field
    assert type(xtract_tonal.output_non_tonal_signals) == Field

    # Type of output tonal signals. As Field
    assert xtract_tonal.get_output()[0].data[0] == pytest.approx(3.6770161386812106e-06)
    assert xtract_tonal.get_output()[0].data[1] == pytest.approx(1.8551201037553255e-06)

    assert xtract_tonal.get_output()[1].data[0] == pytest.approx(-3.6770161386812106e-06)
    assert xtract_tonal.get_output()[1].data[99] == pytest.approx(1.8362156879447866e-06)


def test_xtract_tonal_get_output_noprocess():
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute_in_container)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    # Setting tonal parameters
    params_tonal = XtractTonalParameters()
    params_tonal.regularity = 1.0
    params_tonal.maximum_slope = 750.0
    params_tonal.minimum_duration = 1.0
    params_tonal.intertonal_gap = 20.0
    params_tonal.local_emergence = 15.0
    params_tonal.fft_size = 8192

    xtract_tonal = XtractTonal(bird_plus_idle_sig, params_tonal)
    output1, output2 = xtract_tonal.get_output()

    assert output1 is None
    assert output2 is None


def test_xtract_tonal_get_output_fc():
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute_in_container)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    # Setting tonal parameters
    params_tonal = XtractTonalParameters()
    params_tonal.regularity = 1.0
    params_tonal.maximum_slope = 750.0
    params_tonal.minimum_duration = 1.0
    params_tonal.intertonal_gap = 20.0
    params_tonal.local_emergence = 15.0
    params_tonal.fft_size = 8192

    fc_bird_plus_idle = FieldsContainer()
    fc_bird_plus_idle.labels = ["channel"]
    fc_bird_plus_idle.add_field({"channel": 0}, bird_plus_idle_sig)
    fc_bird_plus_idle.add_field({"channel": 1}, bird_plus_idle_sig)

    xtract_tonal = XtractTonal(fc_bird_plus_idle, params_tonal)
    xtract_tonal.process()

    assert xtract_tonal.get_output() is not None
    assert type(xtract_tonal.get_output()[0]) == FieldsContainer
    assert type(xtract_tonal.get_output()[1]) == FieldsContainer

    # Verify numerical app. of the denoiser.
    # Get the denoised signal - signal1
    assert xtract_tonal.get_output()[0][0].data[0] == pytest.approx(3.6770161386812106e-06)
    assert xtract_tonal.get_output()[0][0].data[99] == pytest.approx(-1.8362156879447866e-06)

    # Get the denoised signal - signal2
    assert xtract_tonal.get_output()[0][1].data[0] == pytest.approx(3.6770161386812106e-06)
    assert xtract_tonal.get_output()[0][1].data[99] == pytest.approx(-1.8362156879447866e-06)

    # Get the noise signal - signal1
    assert xtract_tonal.get_output()[1][0].data[0] == pytest.approx(-3.6770161386812106e-06)
    assert xtract_tonal.get_output()[1][0].data[99] == pytest.approx(1.8362156879447866e-06)
    # Get the noise signal - signal2
    assert xtract_tonal.get_output()[1][0].data[0] == pytest.approx(-3.6770161386812106e-06)
    assert xtract_tonal.get_output()[1][0].data[99] == pytest.approx(1.8362156879447866e-06)


def test_xtract_tonal_get_output_as_nparray():
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute_in_container)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    # Setting tonal parameters
    params_tonal = XtractTonalParameters()
    params_tonal.regularity = 1.0
    params_tonal.maximum_slope = 750.0
    params_tonal.minimum_duration = 1.0
    params_tonal.intertonal_gap = 20.0
    params_tonal.local_emergence = 15.0
    params_tonal.fft_size = 8192

    xtract_tonal = XtractTonal(bird_plus_idle_sig, params_tonal)
    xtract_tonal.process()

    assert xtract_tonal.get_output_as_nparray() is not None
    assert type(xtract_tonal.get_output_as_nparray()[0]) == np.ndarray
    assert type(xtract_tonal.get_output_as_nparray()[1]) == np.ndarray

    assert xtract_tonal.get_output_as_nparray()[0].shape == (156048,)
    assert np.min(xtract_tonal.get_output_as_nparray()[0]) == pytest.approx(-0.6828306913375854)
    assert np.max(xtract_tonal.get_output_as_nparray()[0]) == pytest.approx(0.794617772102356)

    assert xtract_tonal.get_output_as_nparray()[0][0] == pytest.approx(3.6770161386812106e-06)
    assert xtract_tonal.get_output_as_nparray()[0][1] == pytest.approx(1.8551201037553255e-06)

    assert xtract_tonal.get_output_as_nparray()[1].shape == (156048,)
    assert xtract_tonal.get_output_as_nparray()[1][0] == pytest.approx(-3.6770161386812106e-06)
    assert xtract_tonal.get_output_as_nparray()[1][99] == pytest.approx(1.8362156879447866e-06)


def test_xtract_tonal_get_output_fc_as_nparray():
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute_in_container)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    # Setting tonal parameters
    params_tonal = XtractTonalParameters()
    params_tonal.regularity = 1.0
    params_tonal.maximum_slope = 750.0
    params_tonal.minimum_duration = 1.0
    params_tonal.intertonal_gap = 20.0
    params_tonal.local_emergence = 15.0
    params_tonal.fft_size = 8192

    fc_bird_plus_idle = FieldsContainer()
    fc_bird_plus_idle.labels = ["channel"]
    fc_bird_plus_idle.add_field({"channel": 0}, bird_plus_idle_sig)
    fc_bird_plus_idle.add_field({"channel": 1}, bird_plus_idle_sig)

    xtract_tonal = XtractTonal(fc_bird_plus_idle, params_tonal)
    xtract_tonal.process()

    # Type of output tonal signals. np.array
    assert type(xtract_tonal.get_output_as_nparray()[0]) == np.ndarray
    assert type(xtract_tonal.get_output_as_nparray()[1]) == np.ndarray


def test_extract_tonal_setters():
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute_in_container)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    # Setting tonal parameters
    params_tonal = XtractTonalParameters()
    params_tonal.regularity = 1.0
    params_tonal.maximum_slope = 750.0
    params_tonal.minimum_duration = 1.0
    params_tonal.intertonal_gap = 20.0
    params_tonal.local_emergence = 15.0
    params_tonal.fft_size = 8192

    xtract_tonal = XtractTonal(bird_plus_idle_sig, params_tonal)

    assert xtract_tonal.input_signal is not None
    xtract_tonal.input_signal = None
    assert xtract_tonal.input_signal is None

    assert xtract_tonal.input_parameters is not None
    xtract_tonal.input_parameters = None
    assert xtract_tonal.input_parameters is None


@patch("matplotlib.pyplot.show")
def test_xtract_tonal_plot_output(mock_show):
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute_in_container)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    # Setting tonal parameters
    params_tonal = XtractTonalParameters()
    params_tonal.regularity = 1.0
    params_tonal.maximum_slope = 750.0
    params_tonal.minimum_duration = 1.0
    params_tonal.intertonal_gap = 20.0
    params_tonal.local_emergence = 15.0
    params_tonal.fft_size = 8192

    xtract_tonal = XtractTonal(bird_plus_idle_sig, params_tonal)
    xtract_tonal.process()

    xtract_tonal.plot()


@patch("matplotlib.pyplot.show")
def test_xtract_tonal_plot_output_fc(mock_show):
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute_in_container)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    # Setting tonal parameters
    params_tonal = XtractTonalParameters()
    params_tonal.regularity = 1.0
    params_tonal.maximum_slope = 750.0
    params_tonal.minimum_duration = 1.0
    params_tonal.intertonal_gap = 20.0
    params_tonal.local_emergence = 15.0
    params_tonal.fft_size = 8192

    fc_bird_plus_idle = FieldsContainer()
    fc_bird_plus_idle.labels = ["channel"]
    fc_bird_plus_idle.add_field({"channel": 0}, bird_plus_idle_sig)
    fc_bird_plus_idle.add_field({"channel": 1}, bird_plus_idle_sig)

    xtract_tonal = XtractTonal(fc_bird_plus_idle, params_tonal)
    xtract_tonal.process()

    xtract_tonal.plot()
