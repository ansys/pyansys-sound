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
from ansys.sound.core.signal_utilities import LoadWav
from ansys.sound.core.xtract.xtract_transient import XtractTransient
from ansys.sound.core.xtract.xtract_transient_parameters import XtractTransientParameters


def test_xtract_transient_instantiation():
    """Test instantiation of XtractTransient."""
    xtract_transient = XtractTransient()
    assert xtract_transient != None


def test_xtract_transient_initialization():
    """Test initialization of XtractTransient."""
    # Test initialization with default values
    xtract_transient = XtractTransient()
    assert xtract_transient.input_signal is None
    assert xtract_transient.input_parameters is None
    assert xtract_transient.output_transient_signals is None
    assert xtract_transient.output_non_transient_signals is None

    # Test initialization with custom values
    input_signal = Field()
    input_parameters = XtractTransientParameters()
    xtract_transient = XtractTransient(
        input_signal=input_signal,
        input_parameters=input_parameters,
    )
    assert xtract_transient.input_signal == input_signal
    assert xtract_transient.input_parameters == input_parameters
    assert xtract_transient.output_transient_signals is None
    assert xtract_transient.output_non_transient_signals is None


def test_xtract_transient_except1():
    """Test method process's exception when input signal is not set."""
    xtract_transient = XtractTransient(None, XtractTransientParameters())
    with pytest.raises(PyAnsysSoundException, match="Input signal is not set."):
        xtract_transient.process()
        assert xtract_transient._output == (None, None)


def test_xtract_transient_except2():
    """Test method process's exception when input parameters are not set."""
    xtract_transient = XtractTransient(Field(), None)
    with pytest.raises(PyAnsysSoundException, match="Input parameters are not set."):
        xtract_transient.process()
        assert xtract_transient._output == (None, None)


def test_xtract_transient_process():
    """Test the process method of XtractTransient."""
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    # Setting transient parameters
    params_transient = XtractTransientParameters()
    params_transient.lower_threshold = 1.0
    params_transient.upper_threshold = 100.0

    xtract_transient = XtractTransient(bird_plus_idle_sig, params_transient)
    xtract_transient.process()

    assert xtract_transient.output_transient_signals is not None
    assert xtract_transient.output_non_transient_signals is not None
    assert xtract_transient._output is not None


def test_xtract_transient_get_output_warns():
    """Test method get_output's warning when output is not processed yet."""
    xtract_transient = XtractTransient()
    with pytest.warns(PyAnsysSoundWarning, match="Output is not processed yet."):
        output = xtract_transient.get_output()
        assert output == (None, None)


def test_xtract_transient_get_output_as_np_array_warns():
    """Test get_output's warning propagation to get_output_as_nparray."""
    xtract_transient = XtractTransient()
    with pytest.warns(PyAnsysSoundWarning, match="Output is not processed yet."):
        transient, non_transient = xtract_transient.get_output_as_nparray()
        assert len(transient) == 0
        assert len(non_transient) == 0


def test_xtract_transient_get_output():
    """Test method get_output."""
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    # Setting transient parameters
    params_transient = XtractTransientParameters()
    params_transient.lower_threshold = 1.0
    params_transient.upper_threshold = 100.0

    xtract_transient = XtractTransient(bird_plus_idle_sig, params_transient)
    xtract_transient.process()

    transient_signal, non_transient_signal = xtract_transient.get_output()

    # Type checks
    assert type(transient_signal) == Field
    assert type(non_transient_signal) == Field

    # Check transient signal values
    assert transient_signal.data[0] == pytest.approx(0.0)
    assert transient_signal.data[99] == pytest.approx(0.0)
    assert np.min(transient_signal.data) == pytest.approx(-0.70742798)
    assert np.max(transient_signal.data) == pytest.approx(0.87719721)

    # Check non transient signal values
    assert non_transient_signal.data[0] == pytest.approx(0.0)
    assert non_transient_signal.data[99] == pytest.approx(0.0)
    assert np.min(non_transient_signal.data) == pytest.approx(-1.78813934e-07)
    assert np.max(non_transient_signal.data) == pytest.approx(1.78813934e-07)


def test_xtract_transient_get_output_as_nparray():
    """Test method get_output_as_nparray."""
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    # Setting transient parameters
    params_transient = XtractTransientParameters()
    params_transient.lower_threshold = 1.0
    params_transient.upper_threshold = 100.0

    xtract_transient = XtractTransient(bird_plus_idle_sig, params_transient)
    xtract_transient.process()

    transient_signal, non_transient_signal = xtract_transient.get_output_as_nparray()

    # Type checks
    assert type(transient_signal) == np.ndarray
    assert type(non_transient_signal) == np.ndarray

    # Check signal values
    assert transient_signal.shape == (156048,)
    np.min(transient_signal) == pytest.approx(-0.707427978515625)
    np.max(transient_signal) == pytest.approx(0.8771972060203552)
    np.min(non_transient_signal) == pytest.approx(-1.7881393432617188e-07)
    np.max(non_transient_signal) == pytest.approx(-1.7881393432617188e-07)


def test_xtract_transient_setters():
    """Test setters for input signal and parameters."""
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    # Setting transient parameters
    params_transient = XtractTransientParameters()
    params_transient.lower_threshold = 1.0
    params_transient.upper_threshold = 100.0

    xtract_transient = XtractTransient()

    xtract_transient.input_signal = bird_plus_idle_sig
    assert type(xtract_transient.input_signal) == Field

    xtract_transient.input_parameters = params_transient
    assert type(xtract_transient.input_parameters) == XtractTransientParameters


@patch("matplotlib.pyplot.show")
def test_xtract_transient_plot_output(mock_show):
    """Test the plot method of XtractTransient."""
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    # Setting transient parameters
    params_transient = XtractTransientParameters()
    params_transient.lower_threshold = 1.0
    params_transient.upper_threshold = 100.0

    xtract_transient = XtractTransient(bird_plus_idle_sig, params_transient)
    xtract_transient.process()

    xtract_transient.plot()
