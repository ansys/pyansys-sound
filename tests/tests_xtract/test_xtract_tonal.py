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
from ansys.sound.core.xtract.xtract_tonal import XtractTonal
from ansys.sound.core.xtract.xtract_tonal_parameters import XtractTonalParameters

EXP_SIZE = 156048
EXP_0_MIN = -0.6828306913375854
EXP_0_MAX = 0.794617772102356
EXP_0_0 = 3.6770161386812106e-06
if pytest.SOUND_VERSION_GREATER_THAN_OR_EQUAL_TO_2026R1:
    # Third-party update (IPP) slightly changed the output values (ID #884424)
    EXP_0_1 = 1.855125219663023e-06
else:
    EXP_0_1 = 1.8551201037553255e-06
EXP_0_99 = -1.8362156879447866e-06
EXP_1_0 = -3.6770161386812106e-06
EXP_1_99 = 1.8362156879447866e-06


def test_xtract_tonal_instantiation():
    """Test instantiation of XtractTonal."""
    xtract_tonal = XtractTonal()
    assert xtract_tonal != None


def test_xtract_tonal_initialization():
    """Test initialization of XtractTonal."""
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
    """Test method process's exception for missing signal."""
    xtract_tonal = XtractTonal(None, XtractTonalParameters())
    with pytest.raises(PyAnsysSoundException, match="No input signal found for tonal analysis."):
        xtract_tonal.process()
        assert xtract_tonal._output is (None, None)


def test_xtract_tonal_process_except2():
    """Test method process's exception for missing parameters."""
    xtract_tonal = XtractTonal(Field(), None)
    with pytest.raises(PyAnsysSoundException, match="Input parameters are not set."):
        xtract_tonal.process()
        assert xtract_tonal._output is (None, None)


def test_xtract_tonal_process():
    """Test method process."""
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute)
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
    assert xtract_tonal._output is not (None, None)


def test_xtract_tonal_get_output_warns():
    """Test method get_output's warning for unprocessed output."""
    xtract_tonal = XtractTonal()
    with pytest.warns(PyAnsysSoundWarning, match="Output is not processed yet."):
        output = xtract_tonal.get_output()
        assert output == (None, None)


def test_xtract_tonal_get_output_as_nparray_warns():
    """Test get_output's warning propagation to get_output_as_nparray."""
    xtract_tonal = XtractTonal()
    with pytest.warns(PyAnsysSoundWarning, match="Output is not processed yet."):
        tonal, non_tonal = xtract_tonal.get_output_as_nparray()
        assert len(tonal) == 0
        assert len(non_tonal) == 0


def test_xtract_tonal_get_output():
    """Test method get_output."""
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute)
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

    tonal_signal, non_tonal_signal = xtract_tonal.get_output()

    assert type(tonal_signal) == Field
    assert type(non_tonal_signal) == Field

    assert tonal_signal.data[0] == pytest.approx(EXP_0_0)
    assert tonal_signal.data[1] == pytest.approx(EXP_0_1)

    assert non_tonal_signal.data[0] == pytest.approx(EXP_1_0)
    assert non_tonal_signal.data[99] == pytest.approx(EXP_1_99)


def test_xtract_tonal_get_output_as_nparray():
    """Test method get_output_as_nparray."""
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute)
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

    tonal_signal, non_tonal_signal = xtract_tonal.get_output_as_nparray()

    assert type(tonal_signal) == np.ndarray
    assert type(non_tonal_signal) == np.ndarray

    assert tonal_signal.shape == (156048,)
    assert np.min(tonal_signal) == pytest.approx(EXP_0_MIN)
    assert np.max(tonal_signal) == pytest.approx(EXP_0_MAX)

    assert tonal_signal[0] == pytest.approx(EXP_0_0)
    assert tonal_signal[1] == pytest.approx(EXP_0_1)

    assert non_tonal_signal.shape == (156048,)
    assert non_tonal_signal[0] == pytest.approx(EXP_1_0)
    assert non_tonal_signal[99] == pytest.approx(EXP_1_99)


def test_extract_tonal_setters():
    """Test setters for input signal and parameters."""
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute)
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

    xtract_tonal = XtractTonal()

    xtract_tonal.input_signal = bird_plus_idle_sig
    assert type(xtract_tonal.input_signal) == Field

    xtract_tonal.input_parameters = params_tonal
    assert type(xtract_tonal.input_parameters) == XtractTonalParameters


@patch("matplotlib.pyplot.show")
def test_xtract_tonal_plot_output(mock_show):
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute)
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
