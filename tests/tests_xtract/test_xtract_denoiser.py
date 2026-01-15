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

from ansys.dpf.core import Field, FieldsContainer
import numpy as np
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ansys.sound.core.signal_utilities import LoadWav
from ansys.sound.core.xtract.xtract_denoiser import XtractDenoiser
from ansys.sound.core.xtract.xtract_denoiser_parameters import XtractDenoiserParameters


def test_xtract_denoiser_instantiation():
    xtract_denoiser = XtractDenoiser()
    assert xtract_denoiser != None


def test_xtract_denoiser_initialization_FieldsContainers():
    # Test initialization with default values
    xtract = XtractDenoiser()
    assert xtract.input_signal is None
    assert xtract.input_parameters is None

    # Test initialization with custom values
    input_signal = FieldsContainer()
    input_parameters = XtractDenoiserParameters()
    xtract = XtractDenoiser(
        input_signal=input_signal,
        input_parameters=input_parameters,
    )
    assert xtract.input_signal == input_signal
    assert xtract.input_parameters == input_parameters
    assert xtract.output_denoised_signals is None
    assert xtract.output_noise_signals is None


def test_xtract_denoiser_initialization_Field():
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
    """
    Test no signal.
    """
    xtract_denoiser = XtractDenoiser(None, XtractDenoiserParameters())
    with pytest.raises(PyAnsysSoundException) as excinfo:
        xtract_denoiser.process()
    assert excinfo.value.args[0] == "Input signal is not set."


def test_xtract_denoiser_process_except2():
    """
    Test no parameters.
    """
    xtract_denoiser = XtractDenoiser(Field(), None)
    with pytest.raises(PyAnsysSoundException) as excinfo:
        xtract_denoiser.process()
    assert excinfo.value.args[0] == "Input parameters are not set."


def test_xtract_denoiser_process():
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

    if pytest.SERVERS_VERSION_GREATER_THAN_OR_EQUAL_TO_11_0:
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
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    # Setting Denoiser parameters
    params_denoiser = XtractDenoiserParameters()
    params_denoiser.noise_psd = params_denoiser.create_noise_psd_from_white_noise_level(
        -6.0 + 94.0, 44100.0, 50
    )
    xtract_denoiser = XtractDenoiser(bird_plus_idle_sig, params_denoiser)

    with pytest.warns(PyAnsysSoundWarning) as record:
        xtract_denoiser.get_output()
    assert record[0].message.args[0] == "Output is not processed yet."


def test_xtract_denoiser_get_output_np_array_warns():
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    # Setting Denoiser parameters
    params_denoiser = XtractDenoiserParameters()
    params_denoiser.noise_psd = params_denoiser.create_noise_psd_from_white_noise_level(
        -6.0 + 94.0, 44100.0, 50
    )
    xtract_denoiser = XtractDenoiser(bird_plus_idle_sig, params_denoiser)

    with pytest.warns(PyAnsysSoundWarning) as record:
        xtract_denoiser.get_output_as_nparray()
    assert record[0].message.args[0] == "Output is not processed yet."


def test_xtract_denoiser_get_output():
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

    # Type of the denoiser. Field
    assert xtract_denoiser.get_output() is not None
    assert type(xtract_denoiser.get_output()[0]) == Field
    assert type(xtract_denoiser.get_output()[1]) == Field

    # Verify numerical app. of the denoiser.
    # Get the denoised signal
    assert xtract_denoiser.get_output()[0].data[0] == pytest.approx(-4.048184330747483e-15)
    assert xtract_denoiser.get_output()[0].data[99] == pytest.approx(-3.329021806551297e-15)

    # Get the noise signal
    assert xtract_denoiser.get_output()[1].data[0] == pytest.approx(-4.048184330747483e-15)
    assert xtract_denoiser.get_output()[1].data[99] == pytest.approx(-3.329021806551297e-15)


def test_xtract_denoiser_get_output_noprocess():
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
    output1, output2 = xtract_denoiser.get_output()
    # note: check warnings on the console to see the warning message
    assert output1 is None
    assert output2 is None


def test_xtract_denoiser_get_output_fc():
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

    fc_bird_plus_idle = FieldsContainer()
    fc_bird_plus_idle.labels = ["channel"]
    fc_bird_plus_idle.add_field({"channel": 0}, bird_plus_idle_sig)
    fc_bird_plus_idle.add_field({"channel": 1}, bird_plus_idle_sig)

    # Test 1 - param denoiser with only one noise profile
    xtract_denoiser = XtractDenoiser(fc_bird_plus_idle, params_denoiser)
    xtract_denoiser.process()

    # Type of the denoiser. Field
    assert xtract_denoiser.get_output() is not None
    assert type(xtract_denoiser.get_output()[0]) == FieldsContainer
    assert type(xtract_denoiser.get_output()[1]) == FieldsContainer

    # Verify numerical app. of the denoiser.
    # Get the denoised signal - signal1
    assert xtract_denoiser.get_output()[0][0].data[0] == pytest.approx(-4.048184330747483e-15)
    assert xtract_denoiser.get_output()[0][0].data[99] == pytest.approx(-3.329021806551297e-15)

    # Get the denoised signal - signal2
    assert xtract_denoiser.get_output()[0][1].data[0] == pytest.approx(-4.048184330747483e-15)
    assert xtract_denoiser.get_output()[0][1].data[99] == pytest.approx(-3.329021806551297e-15)

    # Get the noise signal - signal1
    assert xtract_denoiser.get_output()[1][0].data[0] == pytest.approx(-4.048184330747483e-15)
    assert xtract_denoiser.get_output()[1][0].data[99] == pytest.approx(-3.329021806551297e-15)
    # Get the noise signal - signal2
    assert xtract_denoiser.get_output()[1][0].data[0] == pytest.approx(-4.048184330747483e-15)
    assert xtract_denoiser.get_output()[1][0].data[99] == pytest.approx(-3.329021806551297e-15)


def test_xtract_denoiser_get_output_as_nparray():
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

    # Type of the denoiser. np.array
    assert xtract_denoiser.get_output_as_nparray() is not None
    assert type(xtract_denoiser.get_output_as_nparray()[0]) == np.ndarray
    assert type(xtract_denoiser.get_output_as_nparray()[1]) == np.ndarray

    # Get the denoised signal
    assert xtract_denoiser.get_output_as_nparray()[0][0] == pytest.approx(-4.048184330747483e-15)
    assert xtract_denoiser.get_output_as_nparray()[0][99] == pytest.approx(-3.329021806551297e-15)

    assert xtract_denoiser.get_output_as_nparray()[0].shape == (156048,)

    if pytest.SERVERS_VERSION_GREATER_THAN_OR_EQUAL_TO_11_0:
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


def test_xtract_denoiser_get_output_fc_as_nparray():
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

    fc_bird_plus_idle = FieldsContainer()
    fc_bird_plus_idle.labels = ["channel"]
    fc_bird_plus_idle.add_field({"channel": 0}, bird_plus_idle_sig)
    fc_bird_plus_idle.add_field({"channel": 1}, bird_plus_idle_sig)

    # Test 1 - param denoiser with only one noise profile
    xtract_denoiser = XtractDenoiser(fc_bird_plus_idle, params_denoiser)
    xtract_denoiser.process()

    # Type of the denoiser. np.array
    assert type(xtract_denoiser.get_output_as_nparray()[0]) == np.ndarray
    assert type(xtract_denoiser.get_output_as_nparray()[1]) == np.ndarray


def test_xtract_denoiser_setters():
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

    assert xtract_denoiser.input_signal is not None
    xtract_denoiser.input_signal = None
    assert xtract_denoiser.input_signal is None

    assert xtract_denoiser.input_parameters is not None
    xtract_denoiser.input_parameters = None
    assert xtract_denoiser.input_parameters is None


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

    xtract_denoiser = XtractDenoiser(bird_plus_idle_sig, params_denoiser)
    xtract_denoiser.process()

    xtract_denoiser.plot()


@patch("matplotlib.pyplot.show")
def test_xtract_denoiser_plot_output_fc(mock_show):
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

    fc_bird_plus_idle = FieldsContainer()
    fc_bird_plus_idle.labels = ["channel"]
    fc_bird_plus_idle.add_field({"channel": 0}, bird_plus_idle_sig)
    fc_bird_plus_idle.add_field({"channel": 1}, bird_plus_idle_sig)

    # Test 1 - param denoiser with only one noise profile
    xtract_denoiser = XtractDenoiser(fc_bird_plus_idle, params_denoiser)
    xtract_denoiser.process()

    xtract_denoiser.plot()
