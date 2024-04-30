from unittest.mock import patch

from ansys.dpf.core import Field, FieldsContainer, Operator, GenericDataContainer
import numpy as np
import pytest

from ansys.dpf.sound.pydpf_sound import PyDpfSoundException, PyDpfSoundWarning
from ansys.dpf.sound.signal_utilities import LoadWav
from ansys.dpf.sound.xtract.xtract_denoiser import XtractDenoiser


def test_xtract_denoiser_instantiation(dpf_sound_test_server):
    xtract_denoiser = XtractDenoiser()
    assert xtract_denoiser != None

def test_xtract_denoiser_initialization_FieldsContainers():
    # Test initialization with default values
    xtract = XtractDenoiser()
    assert xtract.input_signal is None
    assert xtract.input_parameters is None

    # Test initialization with custom values
    input_signal = FieldsContainer()
    input_parameters = GenericDataContainer()
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
    input_parameters = GenericDataContainer()
    xtract = XtractDenoiser(
        input_signal=input_signal,
        input_parameters=input_parameters,
    )
    assert xtract.input_signal == input_signal
    assert xtract.input_parameters == input_parameters
    assert xtract.output_denoised_signals is None
    assert xtract.output_noise_signals is None    

def test_xtract_denoiser_process_except1(dpf_sound_test_server):
    """
    Test no signal.
    """
    xtract_denoiser = XtractDenoiser(None, GenericDataContainer())
    with pytest.raises(PyDpfSoundException) as excinfo:
        xtract_denoiser.process()
    assert excinfo.value.args[0] == "Input signal is not set."

def test_xtract_denoiser_process_except2(dpf_sound_test_server):
    """
    Test no parameters.
    """
    xtract_denoiser = XtractDenoiser(Field(), None)
    with pytest.raises(PyDpfSoundException) as excinfo:
        xtract_denoiser.process()
    assert excinfo.value.args[0] == "Input parameters are not set." 


def test_xtract_process(dpf_sound_test_server):
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute_in_container)
    wav_bird_plus_idle.process()
    wav_white_noise = LoadWav(pytest.data_path_white_noise_in_container)
    wav_white_noise.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]
    wav_white_noise = wav_white_noise.get_output()[0]


    noise_levels = GenericDataContainer("noise_levels", wav_white_noise)  # CQU debug - what is this? values for Field?

    xtract_denoiser = XtractDenoiser(bird_plus_idle_sig, noise_levels)
    xtract_denoiser.process()

    assert xtract_denoiser.output_denoised_signals is not None

def test_xtract_denoiser_get_output():
    # Test the get_output method
    xtract = XtractDenoiser()
    # Add your test logic here
    assert False

def test_xtract_denoiser_get_output_as_nparray():
    # Test the get_output_as_nparray method
    xtract = XtractDenoiser()
    # Add your test logic here
    assert False

def test_xtract_denoiser_plot_output():
    # Test the plot_output method
    xtract = XtractDenoiser()
    # Add your test logic here
    assert False