from unittest.mock import patch

from ansys.dpf.core import Field
import numpy as np
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ansys.sound.core.signal_utilities import LoadWav
from ansys.sound.core.power_spectral_density import PowerSpectralDensity


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


def test_power_spectral_density_noprocess(dpf_sound_test_server):
    """Test PowerSpectralDensity without process."""
    # Test without process
    psd = PowerSpectralDensity(Field())
    with pytest.raises(PyAnsysSoundException):
        psd.output


def test_power_spectral_density_process(dpf_sound_test_server):
    """Test PowerSpectralDensity process."""
    # Test process
    psd = PowerSpectralDensity(Field())
    with pytest.raises(PyAnsysSoundException):
        psd.process()

    # Test process with input signal
    input_signal = LoadWav(pytest.data_path_flute_in_container)
    psd.input_signal = input_signal
    psd.process()
    assert psd.output is not None


def test_power_spectral_density_get_output(dpf_sound_test_server):
    """Test PowerSpectralDensity get_output."""
    # Test get_output
    psd = PowerSpectralDensity(Field())
    with pytest.raises(PyAnsysSoundException):
        psd.get_output()

    # Test get_output with input signal
    input_signal = LoadWav(pytest.data_path_flute_in_container)
    psd.input_signal = input_signal
    psd.process()
    output = psd.get_output()
    assert output is not None


def test_power_spectral_density_get_output_as_nparray(dpf_sound_test_server):
    """Test PowerSpectralDensity get_output_as_nparray."""
    # Test get_output_as_nparray
    psd = PowerSpectralDensity(Field())
    with pytest.raises(PyAnsysSoundException):
        psd.get_output_as_nparray()

    # Test get_output_as_nparray with input signal
    input_signal = LoadWav(pytest.data_path_flute_in_container)
    psd.input_signal = input_signal
    psd.process()
    output = psd.get_output_as_nparray()
    assert output is not None


@patch("matplotlib.pyplot.show")
def test_power_spectral_density_plot(mock_show, dpf_sound_test_server):
    """Test PowerSpectralDensity plot."""
    # Test plot
    psd = PowerSpectralDensity(Field())
    with pytest.raises(PyAnsysSoundException):
        psd.plot()

    # Test plot with input signal
    input_signal = LoadWav(pytest.data_path_flute_in_container)
    psd.input_signal = input_signal
    psd.process()
    psd.plot()
    mock_show.assert_called()