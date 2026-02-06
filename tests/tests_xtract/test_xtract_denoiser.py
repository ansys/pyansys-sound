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
from ansys.sound.core.xtract.xtract_denoiser import XtractDenoiser
from ansys.sound.core.xtract.xtract_denoiser_parameters import XtractDenoiserParameters


def test_xtract_denoiser_instantiation():
    """Test XtractDenoiser instantiation."""
    xtract_denoiser = XtractDenoiser()
    assert xtract_denoiser != None


def test_xtract_denoiser_initialization():
    """Test XtractDenoiser initialization."""
    # Test initialization with default values
    xtract = XtractDenoiser()
    assert xtract.input_signal is None
    assert xtract.input_parameters is None

    # Test initialization with custom values
    input_signal = Field()
    input_parameters = XtractDenoiserParameters()
    xtract = XtractDenoiser(
        input_signal=input_signal,
        input_parameters=input_parameters,
    )
    assert xtract.input_signal == input_signal
    assert xtract.input_parameters == input_parameters
    assert xtract.output_denoised_signals is None
    assert xtract.output_noise_signals is None


def test_xtract_denoiser_process_except1():
    """Test no signal."""
    xtract_denoiser = XtractDenoiser(None, XtractDenoiserParameters())
    with pytest.raises(PyAnsysSoundException, match="Input signal is not set."):
        xtract_denoiser.process()
        assert xtract_denoiser._output == (None, None)


def test_xtract_denoiser_process_except2():
    """Test no parameters."""
    xtract_denoiser = XtractDenoiser(Field(), None)
    with pytest.raises(PyAnsysSoundException, match="Input parameters are not set."):
        xtract_denoiser.process()
        assert xtract_denoiser._output == (None, None)


def test_xtract_denoiser_process():
    """Test the process method."""
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    # Setting Denoiser parameters
    params_denoiser = XtractDenoiserParameters()
    params_denoiser.noise_psd = params_denoiser.create_noise_psd_from_white_noise_level(
        -6.0 + 94.0, 44100.0, 50
    )
    xtract_denoiser = XtractDenoiser(bird_plus_idle_sig, params_denoiser)
    xtract_denoiser.process()

    assert xtract_denoiser.output_denoised_signals is not None
    assert xtract_denoiser.output_noise_signals is not None

    assert type(xtract_denoiser.output_denoised_signals) == Field
    assert type(xtract_denoiser.output_noise_signals) == Field

    # Type of the denoiser. np.array
    assert xtract_denoiser.get_output_as_nparray() is not None
    assert type(xtract_denoiser.get_output_as_nparray()[0]) == np.ndarray
    assert type(xtract_denoiser.get_output_as_nparray()[1]) == np.ndarray

    # Get the denoised signal
    assert xtract_denoiser.get_output_as_nparray()[0][0] == pytest.approx(-4.048184330747483e-15)
    assert xtract_denoiser.get_output_as_nparray()[0][99] == pytest.approx(-3.329021806551297e-15)

    assert xtract_denoiser.get_output_as_nparray()[0].shape == (156048,)

    if pytest.SOUND_VERSION_GREATER_THAN_OR_EQUAL_TO_2026R1:
        # bug fix in DPF Sound 2026 R1 ID#1247009
        assert np.min(xtract_denoiser.get_output_as_nparray()[0]) == pytest.approx(
            -0.7059202790260315
        )
        assert np.max(xtract_denoiser.get_output_as_nparray()[0]) == pytest.approx(
            0.8131743669509888
        )
    else:  # DPF Sound <= 2025 R2
        assert np.min(xtract_denoiser.get_output_as_nparray()[0]) == pytest.approx(
            -0.6995288133621216
        )
        assert np.max(xtract_denoiser.get_output_as_nparray()[0]) == pytest.approx(
            0.8091265559196472
        )

    # Get the noise signal
    assert xtract_denoiser.get_output_as_nparray()[1][0] == pytest.approx(-4.048184330747483e-15)
    assert xtract_denoiser.get_output_as_nparray()[1][99] == pytest.approx(-3.329021806551297e-15)


def test_xtract_denoiser_get_output_warns():
    """Test get_output method's warning if output is not processed yet."""
    xtract_denoiser = XtractDenoiser()

    with pytest.warns(PyAnsysSoundWarning, match="Output is not processed yet."):
        output = xtract_denoiser.get_output()
        assert output == (None, None)


def test_xtract_denoiser_get_output_as_nparray_warns():
    """Test get_output's warning propagation to get_output_as_nparray."""
    xtract_denoiser = XtractDenoiser()

    with pytest.warns(PyAnsysSoundWarning, match="Output is not processed yet."):
        denoised, noise = xtract_denoiser.get_output_as_nparray()
        assert len(denoised) == 0
        assert len(noise) == 0


def test_xtract_denoiser_get_output():
    """Test the get_output method."""
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    # Setting Denoiser parameters
    params_denoiser = XtractDenoiserParameters()
    params_denoiser.noise_psd = params_denoiser.create_noise_psd_from_white_noise_level(
        -6.0 + 94.0, 44100.0, 50
    )
    xtract_denoiser = XtractDenoiser(bird_plus_idle_sig, params_denoiser)
    xtract_denoiser.process()

    xtract_denoiser = XtractDenoiser(bird_plus_idle_sig, params_denoiser)
    xtract_denoiser.process()

    denoised_signal, noise_signal = xtract_denoiser.get_output()

    # Type of the denoiser. Field
    assert type(denoised_signal) == Field
    assert type(noise_signal) == Field

    # Verify numerical app. of the denoiser.
    # Get the denoised signal
    assert denoised_signal.data[0] == pytest.approx(-4.048184330747483e-15)
    assert denoised_signal.data[99] == pytest.approx(-3.329021806551297e-15)

    # Get the noise signal
    assert noise_signal.data[0] == pytest.approx(-4.048184330747483e-15)
    assert noise_signal.data[99] == pytest.approx(-3.329021806551297e-15)


def test_xtract_denoiser_get_output_as_nparray():
    """Test the get_output_as_nparray method."""
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    # Setting Denoiser parameters
    params_denoiser = XtractDenoiserParameters()
    params_denoiser.noise_psd = params_denoiser.create_noise_psd_from_white_noise_level(
        -6.0 + 94.0, 44100.0, 50
    )
    xtract_denoiser = XtractDenoiser(bird_plus_idle_sig, params_denoiser)
    xtract_denoiser.process()

    denoised_signal, noise_signal = xtract_denoiser.get_output_as_nparray()

    # Output types
    assert type(denoised_signal) == np.ndarray
    assert type(noise_signal) == np.ndarray

    # Output values
    assert denoised_signal[0] == pytest.approx(-4.048184330747483e-15)
    assert denoised_signal[99] == pytest.approx(-3.329021806551297e-15)

    assert denoised_signal.shape == (156048,)

    if pytest.SOUND_VERSION_GREATER_THAN_OR_EQUAL_TO_2026R1:
        # bug fix in DPF Sound 2026 R1 ID#1247009
        assert np.min(denoised_signal) == pytest.approx(-0.7059202790260315)
        assert np.max(denoised_signal) == pytest.approx(0.8131743669509888)

    else:  # DPF Sound <= 2025 R2
        assert np.min(denoised_signal) == pytest.approx(-0.6995288133621216)
        assert np.max(denoised_signal) == pytest.approx(0.8091265559196472)

    # Test the noise signal
    assert noise_signal[0] == pytest.approx(-4.048184330747483e-15)
    assert noise_signal[99] == pytest.approx(-3.329021806551297e-15)


def test_xtract_denoiser_setters():
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    # Setting Denoiser parameters
    params_denoiser = XtractDenoiserParameters()
    params_denoiser.noise_psd = params_denoiser.create_noise_psd_from_white_noise_level(
        -6.0 + 94.0, 44100.0, 50
    )
    xtract_denoiser = XtractDenoiser()

    xtract_denoiser.input_signal = bird_plus_idle_sig
    assert type(xtract_denoiser.input_signal) == Field

    xtract_denoiser.input_parameters = params_denoiser
    assert type(xtract_denoiser.input_parameters) == XtractDenoiserParameters


@patch("matplotlib.pyplot.show")
def test_xtract_denoiser_plot_output(mock_show):
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    # Setting Denoiser parameters
    params_denoiser = XtractDenoiserParameters()
    params_denoiser.noise_psd = params_denoiser.create_noise_psd_from_white_noise_level(
        -6.0 + 94.0, 44100.0, 50
    )

    xtract_denoiser = XtractDenoiser(bird_plus_idle_sig, params_denoiser)
    xtract_denoiser.process()

    xtract_denoiser.plot()
