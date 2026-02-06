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
from ansys.sound.core.xtract.xtract import Xtract
from ansys.sound.core.xtract.xtract_denoiser_parameters import XtractDenoiserParameters
from ansys.sound.core.xtract.xtract_tonal_parameters import XtractTonalParameters
from ansys.sound.core.xtract.xtract_transient_parameters import XtractTransientParameters


def test_xtract_instantiation():
    """Test instantiation of Xtract."""
    xtract = Xtract()
    assert type(xtract) == Xtract


def test_xtract_initialization():
    """Test initialization of Xtract."""
    # Test initialization with default values
    xtract = Xtract()
    assert xtract.input_signal is None
    assert xtract.parameters_denoiser is None
    assert xtract.parameters_tonal is None
    assert xtract.parameters_transient is None
    assert xtract.output_noise_signal is None
    assert xtract.output_tonal_signal is None
    assert xtract.output_transient_signal is None
    assert xtract.output_remainder_signal is None

    # Test initialization with custom values
    input_signal = Field()
    parameters_denoiser = XtractDenoiserParameters()
    parameters_tonal = XtractTonalParameters()
    parameters_transient = XtractTransientParameters()
    xtract = Xtract(
        input_signal=input_signal,
        parameters_denoiser=parameters_denoiser,
        parameters_tonal=parameters_tonal,
        parameters_transient=parameters_transient,
    )
    assert xtract.input_signal == input_signal
    assert type(xtract.input_signal) == Field
    assert xtract.parameters_denoiser == parameters_denoiser
    assert xtract.parameters_tonal == parameters_tonal
    assert xtract.parameters_transient == parameters_transient
    assert xtract.output_noise_signal is None
    assert xtract.output_tonal_signal is None
    assert xtract.output_transient_signal is None
    assert xtract.output_remainder_signal is None


def test_xtract_except1():
    """Test method process's exceptions for missing parameters."""
    xtract = Xtract(Field(), None, XtractTonalParameters(), XtractTransientParameters())
    with pytest.raises(
        PyAnsysSoundException,
        match="Input parameters for the denoiser extraction are not set.",
    ):
        xtract.process()
        assert xtract._output == (None, None, None, None)

    xtract = Xtract(Field(), XtractDenoiserParameters(), None, XtractTransientParameters())
    with pytest.raises(
        PyAnsysSoundException,
        match="Input parameters for the tonal extraction are not set.",
    ):
        xtract.process()
        assert xtract._output == (None, None, None, None)

    xtract = Xtract(Field(), XtractDenoiserParameters(), XtractTonalParameters(), None)
    with pytest.raises(
        PyAnsysSoundException,
        match="Input parameters for the transient extraction are not set.",
    ):
        xtract.process()
        assert xtract._output == (None, None, None, None)


def test_xtract_except2():
    """Test method process's exception for missing signal."""
    xtract = Xtract(
        None,
        XtractDenoiserParameters(),
        XtractTonalParameters(),
        XtractTransientParameters(),
    )
    with pytest.raises(PyAnsysSoundException, match="Input signal is not set."):
        xtract.process()
        assert xtract._output == (None, None, None, None)


def test_xtract_process():
    """Test the process method."""
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    ## Creating noise profile with Xtract helper (white noise level)
    params_denoiser = XtractDenoiserParameters()
    params_denoiser.noise_psd = params_denoiser.create_noise_psd_from_white_noise_level(
        -6.0 + 94.0, 44100.0, 50
    )

    # Setting tonal parameters
    params_tonal = XtractTonalParameters()
    params_tonal.regularity = 1.0
    params_tonal.maximum_slope = 750.0
    params_tonal.minimum_duration = 1.0
    params_tonal.intertonal_gap = 20.0
    params_tonal.local_emergence = 15.0
    params_tonal.fft_size = 8192

    # Setting transient parameters
    params_transient = XtractTransientParameters()
    params_transient.lower_threshold = 1.0
    params_transient.upper_threshold = 100.0

    xtract = Xtract(bird_plus_idle_sig, params_denoiser, params_tonal, params_transient)
    xtract.process()

    ## Collecting outputs as Field
    noise, tonal, transient, remainder = xtract.get_output()

    assert noise is not None
    assert tonal is not None
    assert transient is not None
    assert remainder is not None

    assert type(noise) == Field
    assert type(tonal) == Field
    assert type(transient) == Field
    assert type(remainder) == Field


def test_xtract_get_output_warns():
    """Test the get_output method's warning for unprocessed output."""
    xtract = Xtract()

    with pytest.warns(PyAnsysSoundWarning, match="Output is not processed yet."):
        output = xtract.get_output()
        assert output == (None, None, None, None)


def test_xtract_get_output_as_np_array_warns():
    """Test get_output's warning propagation to get_output_as_nparray."""
    xtract = Xtract()

    with pytest.warns(PyAnsysSoundWarning, match="Output is not processed yet."):
        noise, tonal, transient, remainder = xtract.get_output_as_nparray()
        assert len(noise) == 0
        assert len(tonal) == 0
        assert len(transient) == 0
        assert len(remainder) == 0


def test_xtract_get_output():
    """Test the get_output method."""
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    ## Creating noise profile with Xtract helper (white noise level)
    params_denoiser = XtractDenoiserParameters()
    params_denoiser.noise_psd = params_denoiser.create_noise_psd_from_white_noise_level(
        -6.0 + 94.0, 44100.0, 50
    )

    # Setting tonal parameters
    params_tonal = XtractTonalParameters()
    params_tonal.regularity = 1.0
    params_tonal.maximum_slope = 750.0
    params_tonal.minimum_duration = 1.0
    params_tonal.intertonal_gap = 20.0
    params_tonal.local_emergence = 15.0
    params_tonal.fft_size = 8192

    # Setting transient parameters
    params_transient = XtractTransientParameters()
    params_transient.lower_threshold = 1.0
    params_transient.upper_threshold = 100.0

    xtract = Xtract(bird_plus_idle_sig, params_denoiser, params_tonal, params_transient)
    xtract.process()

    ## Collecting outputs as Field
    noise, tonal, transient, remainder = xtract.get_output()

    # Check numerical values
    if pytest.SOUND_VERSION_GREATER_THAN_OR_EQUAL_TO_2026R1:
        # bug fix in DPF Sound 2026 R1 ID#1247009
        assert np.min(noise.data) == pytest.approx(-0.2724415361881256)
        assert np.max(noise.data) == pytest.approx(0.30289316177368164)

        assert np.min(tonal.data) == pytest.approx(-0.6827592849731445)
        assert np.max(tonal.data) == pytest.approx(0.8007676005363464)

        assert np.min(transient.data) == pytest.approx(-0.20742443203926086)
        assert np.max(transient.data) == pytest.approx(0.2130335420370102)

        assert np.min(remainder.data) == pytest.approx(-7.95791721e-07)
        assert np.max(remainder.data) == pytest.approx(7.01886734e-07)

    else:  # DPF Sound <= 2025 R2
        assert np.min(noise.data) == pytest.approx(-0.2635681)
        assert np.max(noise.data) == pytest.approx(0.30395156)

        assert np.min(tonal.data) == pytest.approx(-0.67513376)
        assert np.max(tonal.data) == pytest.approx(0.79357791)

        assert np.min(transient.data) == pytest.approx(-0.20801553)
        assert np.max(transient.data) == pytest.approx(0.21244156)

        assert np.min(remainder.data) == pytest.approx(-7.95791721e-07)
        assert np.max(remainder.data) == pytest.approx(7.01886734e-07)


def test_xtract_get_output_as_nparray():
    """Test the get_output_as_nparray method."""
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    ## Creating noise profile with Xtract helper (white noise level)
    params_denoiser = XtractDenoiserParameters()
    params_denoiser.noise_psd = params_denoiser.create_noise_psd_from_white_noise_level(
        -6.0 + 94.0, 44100.0, 50
    )

    # Setting tonal parameters
    params_tonal = XtractTonalParameters()
    params_tonal.regularity = 1.0
    params_tonal.maximum_slope = 750.0
    params_tonal.minimum_duration = 1.0
    params_tonal.intertonal_gap = 20.0
    params_tonal.local_emergence = 15.0
    params_tonal.fft_size = 8192

    # Setting transient parameters
    params_transient = XtractTransientParameters()
    params_transient.lower_threshold = 1.0
    params_transient.upper_threshold = 100.0

    xtract = Xtract(bird_plus_idle_sig, params_denoiser, params_tonal, params_transient)
    xtract.process()

    ## Collecting outputs as Field
    noise, tonal, transient, remainder = xtract.get_output_as_nparray()

    assert noise is not None
    assert tonal is not None
    assert transient is not None
    assert remainder is not None

    assert type(noise) == np.ndarray
    assert type(tonal) == np.ndarray
    assert type(transient) == np.ndarray
    assert type(remainder) == np.ndarray

    # Check numerical values
    if pytest.SOUND_VERSION_GREATER_THAN_OR_EQUAL_TO_2026R1:
        # bug fix in DPF Sound 2026 R1 ID#1247009
        assert np.min(noise) == pytest.approx(-0.2724415361881256)
        assert np.max(noise) == pytest.approx(0.30289316177368164)

        assert np.min(tonal) == pytest.approx(-0.6827592849731445)
        assert np.max(tonal) == pytest.approx(0.8007676005363464)

        assert np.min(transient) == pytest.approx(-0.20742443203926086)
        assert np.max(transient) == pytest.approx(0.2130335420370102)

        assert np.min(remainder) == pytest.approx(-7.95791721e-07)
        assert np.max(remainder) == pytest.approx(7.01886734e-07)

    else:  # DPF Sound <= 2025 R2
        assert np.min(noise) == pytest.approx(-0.2635681)
        assert np.max(noise) == pytest.approx(0.30395156)

        assert np.min(tonal) == pytest.approx(-0.67513376)
        assert np.max(tonal) == pytest.approx(0.79357791)

        assert np.min(transient) == pytest.approx(-0.20801553)
        assert np.max(transient) == pytest.approx(0.21244156)

        assert np.min(remainder) == pytest.approx(-7.95791721e-07)
        assert np.max(remainder) == pytest.approx(7.01886734e-07)


def test_xtract_setters():
    """Test setters for input signal and parameters."""
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    ## Creating noise profile with Xtract helper (white noise level)
    params_denoiser = XtractDenoiserParameters()
    params_denoiser.noise_psd = params_denoiser.create_noise_psd_from_white_noise_level(
        -6.0 + 94.0, 44100.0, 50
    )

    # Setting tonal parameters
    params_tonal = XtractTonalParameters()
    params_tonal.regularity = 1.0
    params_tonal.maximum_slope = 750.0
    params_tonal.minimum_duration = 1.0
    params_tonal.intertonal_gap = 20.0
    params_tonal.local_emergence = 15.0
    params_tonal.fft_size = 8192

    # Setting transient parameters
    params_transient = XtractTransientParameters()
    params_transient.lower_threshold = 1.0
    params_transient.upper_threshold = 100.0

    xtract = Xtract()

    xtract.input_signal = bird_plus_idle_sig
    assert type(xtract.input_signal) == Field

    xtract.parameters_denoiser = params_denoiser
    assert type(xtract.parameters_denoiser) == XtractDenoiserParameters

    xtract.parameters_tonal = params_tonal
    assert type(xtract.parameters_tonal) == XtractTonalParameters

    xtract.parameters_transient = params_transient
    assert type(xtract.parameters_transient) == XtractTransientParameters


@patch("matplotlib.pyplot.show")
def test_xtract_plot_output(mock_show):
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    ## Creating noise profile with Xtract helper (white noise level)
    params_denoiser = XtractDenoiserParameters()
    params_denoiser.noise_psd = params_denoiser.create_noise_psd_from_white_noise_level(
        -6.0 + 94.0, 44100.0, 50
    )

    # Setting tonal parameters
    params_tonal = XtractTonalParameters()
    params_tonal.regularity = 1.0
    params_tonal.maximum_slope = 750.0
    params_tonal.minimum_duration = 1.0
    params_tonal.intertonal_gap = 20.0
    params_tonal.local_emergence = 15.0
    params_tonal.fft_size = 8192

    # Setting transient parameters
    params_transient = XtractTransientParameters()
    params_transient.lower_threshold = 1.0
    params_transient.upper_threshold = 100.0

    xtract = Xtract(bird_plus_idle_sig, params_denoiser, params_tonal, params_transient)
    xtract.process()

    xtract.plot()
