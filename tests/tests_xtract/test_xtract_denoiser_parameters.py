from ansys.dpf.core import Field
import numpy as np
import pytest

from ansys.sound.core.pyansys_sound import PyDpfSoundException
from ansys.sound.core.signal_utilities import LoadWav
from ansys.sound.core.xtract.xtract_denoiser_parameters import XtractDenoiserParameters


def test_xtract_denoiser_parameters_instantiation(dpf_sound_test_server):
    xtract_denoiser_parameters = XtractDenoiserParameters()
    assert xtract_denoiser_parameters != None


def test_xtract_denoiser_parameters_getter_setter_upper_threshold(dpf_sound_test_server):
    xtract_denoiser_parameters = XtractDenoiserParameters()

    # Invalid value
    with pytest.raises(PyDpfSoundException) as excinfo:
        xtract_denoiser_parameters.noise_psd = None
    assert str(excinfo.value) == "Noise PSD must be a non-empty Field."

    xtract_denoiser_parameters.noise_psd = Field()

    assert type(xtract_denoiser_parameters.noise_psd) == Field


def test_xtract_denoiser_parameters_getter_generic_data_container(dpf_sound_test_server):
    xtract_denoiser_parameters = XtractDenoiserParameters()

    gdc = xtract_denoiser_parameters.get_parameters_as_generic_data_container()
    assert gdc is not None


def test_xtract_denoiser_parameters_generate_noise_psd_from_white_noise_level(
    dpf_sound_test_server,
):
    xtract_denoiser_parameters = XtractDenoiserParameters()

    noise_psd = xtract_denoiser_parameters.create_noise_psd_from_white_noise_level(
        white_noise_level=(40.0), sampling_frequency=44100.0, window_length=50
    )

    noise = noise_psd.data

    s = np.sum(noise)
    assert s == pytest.approx(464.853)


def test_xtract_denoiser_parameters_generate_noise_psd_from_automatic_estimation(
    dpf_sound_test_server,
):
    wav_loader = LoadWav(pytest.data_path_white_noise_in_container)
    wav_loader.process()
    fc_signal = wav_loader.get_output()
    xtract_denoiser_parameters = XtractDenoiserParameters()

    noise_psd = xtract_denoiser_parameters.create_noise_psd_from_automatic_estimation(fc_signal[0])

    noise = noise_psd.data

    s = np.sum(noise)
    assert s == pytest.approx(0.005321223133933017)


def test_xtract_denoiser_parameters_generate_noise_psd_from_noise_samples(
    dpf_sound_test_server,
):
    wav_loader = LoadWav(pytest.data_path_white_noise_in_container)
    wav_loader.process()
    fc_signal = wav_loader.get_output()
    xtract_denoiser_parameters = XtractDenoiserParameters()

    noise_psd = xtract_denoiser_parameters.create_noise_psd_from_noise_samples(
        fc_signal[0], 44100.0
    )

    noise = noise_psd.data

    s = np.sum(noise)
    assert s == pytest.approx(0.0025502318834469406)
