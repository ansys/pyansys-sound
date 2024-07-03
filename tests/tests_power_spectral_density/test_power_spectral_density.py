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

from ansys.dpf.core import Field
import numpy as np
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ansys.sound.core.signal_utilities import LoadWav
from ansys.sound.core.spectral_processing import PowerSpectralDensity


def test_power_spectral_density_instantiation(dpf_sound_test_server):
    """Test PowerSpectralDensity instantiation."""
    # Test instantiation
    psd = PowerSpectralDensity(Field())
    assert psd.input_signal is not None
    assert psd.window_type == "HANN"
    assert psd.window_length == 2048
    assert psd.fft_size == 2048
    assert psd.overlap == 1536


def test_power_spectral_density_setters(dpf_sound_test_server):
    """Test PowerSpectralDensity setters."""
    # Test setters
    psd = PowerSpectralDensity(Field())
    input_signal = LoadWav(pytest.data_path_flute_in_container)
    psd.input_signal = input_signal
    assert psd.input_signal is not None
    assert psd.input_signal == input_signal

    psd.window_type = "HAMMING"
    assert psd.window_type == "HAMMING"

    psd.window_length = 1024
    assert psd.window_length == 1024

    psd.fft_size = 1024
    assert psd.fft_size == 1024

    psd.overlap = 512
    assert psd.overlap == 512


def test_warning(dpf_sound_test_server):
    """Test PowerSpectralDensity warning."""
    with pytest.warns(PyAnsysSoundWarning) as record:
        psd = PowerSpectralDensity(Field())
        psd.get_output()
    assert record[0].message.args[0] == "No output is available."


def test_exception(dpf_sound_test_server):
    """Test PowerSpectralDensity exception."""
    with pytest.raises(PyAnsysSoundException) as record:
        psd = PowerSpectralDensity(Field())
        psd.input_signal = None
        psd.process()
    assert record.value.args[0] == "Input signal is not set"


def test_noprocess_get_output_as_nparray(dpf_sound_test_server):
    """Test PowerSpectralDensity get_output_as_nparray without process."""
    psd = PowerSpectralDensity(Field())
    psd_values, psd_frequencies = psd.get_output_as_nparray()

    assert type(psd_values) == np.ndarray
    assert type(psd_frequencies) == np.ndarray

    assert len(psd_values) == 0
    assert len(psd_frequencies) == 0


def test_power_spectral_density_noprocess(dpf_sound_test_server):
    """Test PowerSpectralDensity without process."""
    # Test without process
    psd = PowerSpectralDensity(Field())
    with pytest.warns(PyAnsysSoundWarning) as record:
        psd.get_output()
    assert record[0].message.args[0] == "No output is available."


def test_power_spectral_density_process(dpf_sound_test_server):
    # Test process with input signal
    op_load_wav = LoadWav(pytest.data_path_flute_in_container)
    op_load_wav.process()
    input_signal = op_load_wav.get_output()[0]

    psd = PowerSpectralDensity(input_signal)
    psd.process()

    assert psd.get_output() is not None


def test_power_spectral_density_get_output(dpf_sound_test_server):
    """Test PowerSpectralDensity get_output."""
    # Test get_output
    op_load_wav = LoadWav(pytest.data_path_flute_in_container)
    op_load_wav.process()
    input_signal = op_load_wav.get_output()[0]

    psd = PowerSpectralDensity(input_signal)
    psd.process()

    output = psd.get_output()
    assert output is not None

    # Check psd values
    assert output.data[0] == pytest.approx(1.25080765e-10)
    assert output.data[11] == pytest.approx(2.03282834e-05)
    assert output.data[12] == pytest.approx(0.000139945812)
    assert output.data[24] == pytest.approx(0.0008081714622676373)
    assert output.data[26] == pytest.approx(1.1030235327780247e-05)
    assert output.data[36] == pytest.approx(0.00037289742613211274)
    assert output.data[37] == pytest.approx(0.00042272001155652106)
    assert output.data[209] == pytest.approx(5.506178180070265e-09)

    # Check frequencies
    assert output.time_freq_support.time_frequencies.data[0] == pytest.approx(0.0)
    assert output.time_freq_support.time_frequencies.data[1] == pytest.approx(21.533203125000000)
    assert output.time_freq_support.time_frequencies.data[1023] == pytest.approx(22028.466796875000)
    assert output.time_freq_support.time_frequencies.data[1024] == pytest.approx(22050.000000000000)


def test_power_spectral_density_get_output_as_nparray(dpf_sound_test_server):
    """Test PowerSpectralDensity get_output_as_nparray."""
    op_load_wav = LoadWav(pytest.data_path_flute_in_container)
    op_load_wav.process()
    input_signal = op_load_wav.get_output()[0]

    psd = PowerSpectralDensity(input_signal)
    psd.process()

    psd_values, psd_frequencies = psd.get_output_as_nparray()

    assert psd_values[0] == pytest.approx(1.25080765e-10)
    assert psd_frequencies[1] == pytest.approx(21.533203125000000)


def test_get_PSD_as_square_linear(dpf_sound_test_server):
    """Test PowerSpectralDensity get_PSD_as_square_linear."""
    # Test get_PSD_as_square_linear
    op_load_wav = LoadWav(pytest.data_path_flute_in_container)
    op_load_wav.process()
    input_signal = op_load_wav.get_output()[0]

    psd = PowerSpectralDensity(input_signal)
    psd.process()

    output = psd.get_PSD_as_square_linear()
    assert output is not None

    # Check psd values
    assert output.data[0] == pytest.approx(1.25080765e-10)
    assert output.data[11] == pytest.approx(2.03282834e-05)
    assert output.data[12] == pytest.approx(0.000139945812)
    assert output.data[24] == pytest.approx(0.0008081714622676373)
    assert output.data[26] == pytest.approx(1.1030235327780247e-05)
    assert output.data[36] == pytest.approx(0.00037289742613211274)
    assert output.data[37] == pytest.approx(0.00042272001155652106)
    assert output.data[209] == pytest.approx(5.506178180070265e-09)

    # Check frequencies
    assert output.time_freq_support.time_frequencies.data[0] == pytest.approx(0.0)
    assert output.time_freq_support.time_frequencies.data[1] == pytest.approx(21.533203125000000)
    assert output.time_freq_support.time_frequencies.data[1023] == pytest.approx(22028.466796875000)
    assert output.time_freq_support.time_frequencies.data[1024] == pytest.approx(22050.000000000000)


def test_get_PSD_as_square_linear_as_nparray(dpf_sound_test_server):
    """Test PowerSpectralDensity get_PSD_as_square_linear_as_nparray."""
    op_load_wav = LoadWav(pytest.data_path_flute_in_container)
    op_load_wav.process()
    input_signal = op_load_wav.get_output()[0]

    psd = PowerSpectralDensity(input_signal)
    psd.process()

    psd_values, psd_frequencies = psd.get_PSD_as_square_linear_as_nparray()

    assert psd_values[0] == pytest.approx(1.25080765e-10)
    assert psd_frequencies[1] == pytest.approx(21.533203125000000)


def test_get_PSD_as_dB(dpf_sound_test_server):
    op_load_wav = LoadWav(pytest.data_path_flute_in_container)
    op_load_wav.process()
    input_signal = op_load_wav.get_output()[0]

    psd = PowerSpectralDensity(input_signal)
    psd.process()

    output = psd.get_PSD_as_dB()
    assert output is not None

    # Check psd values (dB)
    assert output.data[0] == pytest.approx(-99.02809470595948)
    assert output.data[11] == pytest.approx(-46.91898865309873)
    assert output.data[12] == pytest.approx(-38.54039776267062)
    assert output.data[24] == pytest.approx(-30.924964892045686)
    assert output.data[26] == pytest.approx(-49.574152218783794)

    # Check frequencies
    assert output.time_freq_support.time_frequencies.data[0] == pytest.approx(0.0)
    assert output.time_freq_support.time_frequencies.data[1] == pytest.approx(21.533203125000000)
    assert output.time_freq_support.time_frequencies.data[1023] == pytest.approx(22028.466796875000)
    assert output.time_freq_support.time_frequencies.data[1024] == pytest.approx(22050.000000000000)


def test_get_PSD_as_dB_as_nparray(dpf_sound_test_server):
    op_load_wav = LoadWav(pytest.data_path_flute_in_container)
    op_load_wav.process()
    input_signal = op_load_wav.get_output()[0]

    psd = PowerSpectralDensity(input_signal)
    psd.process()

    psd_values = psd.get_PSD_as_dB_as_nparray()

    # Check psd values (dB)
    assert psd_values[0] == pytest.approx(-99.02809470595948)
    assert psd_values[11] == pytest.approx(-46.91898865309873)
    assert psd_values[12] == pytest.approx(-38.54039776267062)
    assert psd_values[24] == pytest.approx(-30.924964892045686)
    assert psd_values[26] == pytest.approx(-49.574152218783794)


def test_get_frequencies(dpf_sound_test_server):
    op_load_wav = LoadWav(pytest.data_path_flute_in_container)
    op_load_wav.process()
    input_signal = op_load_wav.get_output()[0]

    psd = PowerSpectralDensity(input_signal)
    psd.process()
    frequencies = psd.get_frequencies()

    # Check frequencies
    assert frequencies[0] == pytest.approx(0.0)
    assert frequencies[1] == pytest.approx(21.533203125000000)
    assert frequencies[1023] == pytest.approx(22028.466796875000)
    assert frequencies[1024] == pytest.approx(22050.000000000000)


@patch("matplotlib.pyplot.show")
def test_power_spectral_density_plot(mock_show, dpf_sound_test_server):
    """Test PowerSpectralDensity plot."""
    op_load_wav = LoadWav(pytest.data_path_flute_in_container)
    op_load_wav.process()
    input_signal = op_load_wav.get_output()[0]

    psd = PowerSpectralDensity(input_signal)
    psd.process()
    psd.plot()
