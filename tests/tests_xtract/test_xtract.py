from unittest.mock import patch

from ansys.dpf.core import Field, FieldsContainer, GenericDataContainer
from ansys.dpf.sound.pydpf_sound import PyDpfSoundException, PyDpfSoundWarning
from ansys.dpf.sound.signal_utilities import LoadWav
import numpy as np
import pytest

from ansys.dpf.sound.xtract.xtract import Xtract
from ansys.dpf.sound.xtract.xtract_denoiser_parameters import XtractDenoiserParameters
from ansys.dpf.sound.xtract.xtract_tonal_parameters import XtractTonalParameters
from ansys.dpf.sound.xtract.xtract_transient_parameters import XtractTransientParameters


def test_xtract_instantiation(dpf_sound_test_server):
    xtract = Xtract()
    assert xtract != None


def test_xtract_initialization(dpf_sound_test_server):
    # Test initialization with default values
    xtract = Xtract()
    assert xtract.input_signal is None

    # Test initialization with custom values
    input_signal = FieldsContainer()
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
    assert xtract.parameters_denoiser == parameters_denoiser
    assert xtract.parameters_tonal == parameters_tonal
    assert xtract.parameters_transient == parameters_transient


def test_xtract_initialization_FieldsContainer(dpf_sound_test_server):
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
    input_signal = FieldsContainer()
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
    assert type(xtract.input_signal) == FieldsContainer
    assert xtract.parameters_denoiser == parameters_denoiser
    assert xtract.parameters_tonal == parameters_tonal
    assert xtract.parameters_transient == parameters_transient
    assert xtract.output_noise_signal is None
    assert xtract.output_tonal_signal is None
    assert xtract.output_transient_signal is None
    assert xtract.output_remainder_signal is None


def test_xtract_initialization_Field(dpf_sound_test_server):
    # Test initialization with default values
    xtract = Xtract()

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


def test_xtract_except1(dpf_sound_test_server):
    xtract = Xtract(Field(), None, GenericDataContainer(), GenericDataContainer())
    with pytest.raises(PyDpfSoundException) as excinfo:
        xtract.process()
    assert str(excinfo.value) == "Input parameters denoiser are not set."

    xtract = Xtract(Field(), GenericDataContainer(), None, GenericDataContainer())
    with pytest.raises(PyDpfSoundException) as excinfo:
        xtract.process()
    assert str(excinfo.value) == "Input parameters tonal are not set."

    xtract = Xtract(Field(), GenericDataContainer(), GenericDataContainer(), None)
    with pytest.raises(PyDpfSoundException) as excinfo:
        xtract.process()
    assert str(excinfo.value) == "Input parameters transient are not set."


def test_xtract_except2(dpf_sound_test_server):
    xtract = Xtract(None, GenericDataContainer(), GenericDataContainer(), GenericDataContainer())
    with pytest.raises(PyDpfSoundException) as excinfo:
        xtract.process()
    assert str(excinfo.value) == "Input signal is not set."


def test_xtract_process(dpf_sound_test_server):
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute_in_container)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    ## Creating noise profile with Xtract helper (white noise level)
    params_denoiser = XtractDenoiserParameters()
    params_denoiser.noise_psd = params_denoiser.create_noise_psd_from_white_noise_level(
        -6.0, 44100.0, 50
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


def test_xtract_get_output_warns(dpf_sound_test_server):
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute_in_container)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    ## Creating noise profile with Xtract helper (white noise level)
    params_denoiser = XtractDenoiserParameters()
    params_denoiser.noise_psd = params_denoiser.create_noise_psd_from_white_noise_level(
        -6.0, 44100.0, 50
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

    with pytest.warns(PyDpfSoundWarning) as record:
        xtract.get_output()
    assert record[0].message.args[0] == "No output available."


def test_xtract_get_output_as_np_array_warns(dpf_sound_test_server):
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute_in_container)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    ## Creating noise profile with Xtract helper (white noise level)
    params_denoiser = XtractDenoiserParameters()
    params_denoiser.noise_psd = params_denoiser.create_noise_psd_from_white_noise_level(
        -6.0, 44100.0, 50
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

    with pytest.warns(PyDpfSoundWarning) as record:
        xtract.get_output_as_nparray()
    assert record[0].message.args[0] == "No output available."


def test_xtract_get_output(dpf_sound_test_server):
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute_in_container)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    ## Creating noise profile with Xtract helper (white noise level)
    params_denoiser = XtractDenoiserParameters()
    params_denoiser.noise_psd = params_denoiser.create_noise_psd_from_white_noise_level(
        -6.0, 44100.0, 50
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

    # Check numerical apps.
    assert np.min(noise.data) == pytest.approx(-0.2635681)
    assert np.max(noise.data) == pytest.approx(0.30395156)

    assert np.min(tonal.data) == pytest.approx(-0.67513376)
    assert np.max(tonal.data) == pytest.approx(0.79357791)

    assert np.min(transient.data) == pytest.approx(-0.20801553)
    assert np.max(transient.data) == pytest.approx(0.21244156)

    assert np.min(remainder.data) == pytest.approx(-7.95791721e-07)
    assert np.max(remainder.data) == pytest.approx(7.01886734e-07)


def test_xtract_get_output_noprocess(dpf_sound_test_server):
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute_in_container)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    ## Creating noise profile with Xtract helper (white noise level)
    params_denoiser = XtractDenoiserParameters()
    params_denoiser.noise_psd = params_denoiser.create_noise_psd_from_white_noise_level(
        -6.0, 44100.0, 50
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

    assert xtract.output_noise_signal is None
    assert xtract.output_tonal_signal is None
    assert xtract.output_transient_signal is None
    assert xtract.output_remainder_signal is None


def test_xtract_get_output_fc(dpf_sound_test_server):
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute_in_container)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    fc_bird_plus_idle = FieldsContainer()
    fc_bird_plus_idle.labels = ["channel"]
    fc_bird_plus_idle.add_field({"channel": 0}, bird_plus_idle_sig)
    fc_bird_plus_idle.add_field({"channel": 1}, bird_plus_idle_sig)

    ## Creating noise profile with Xtract helper (white noise level)
    params_denoiser = XtractDenoiserParameters()
    params_denoiser.noise_psd = params_denoiser.create_noise_psd_from_white_noise_level(
        -6.0, 44100.0, 50
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

    xtract = Xtract(fc_bird_plus_idle, params_denoiser, params_tonal, params_transient)
    xtract.process()
    # Get out_put as FieldContainer
    fc_noise, fc_tonal, fc_transient, fc_remainder = xtract.get_output()

    assert fc_noise is not None
    assert fc_tonal is not None
    assert fc_transient is not None
    assert fc_remainder is not None

    assert type(fc_noise) == FieldsContainer
    assert type(fc_tonal) == FieldsContainer
    assert type(fc_transient) == FieldsContainer
    assert type(fc_remainder) == FieldsContainer

    assert len(fc_noise) == 2
    assert len(fc_tonal) == 2
    assert len(fc_transient) == 2
    assert len(fc_remainder) == 2

    # Check numerical apps.
    assert np.min(fc_noise[0].data) == pytest.approx(-0.2635681)
    assert np.min(fc_tonal[0].data) == pytest.approx(-0.67513376)
    assert np.min(fc_transient[0].data) == pytest.approx(-0.20801553)
    assert np.min(fc_remainder[0].data) == pytest.approx(-7.95791721e-07)

    assert np.min(fc_noise[1].data) == pytest.approx(-0.2635681)
    assert np.min(fc_tonal[1].data) == pytest.approx(-0.67513376)
    assert np.min(fc_transient[1].data) == pytest.approx(-0.20801553)
    assert np.min(fc_remainder[1].data) == pytest.approx(-7.95791721e-07)

    assert np.max(fc_noise[0].data) == pytest.approx(0.30395156)
    assert np.max(fc_tonal[0].data) == pytest.approx(0.79357791)
    assert np.max(fc_transient[0].data) == pytest.approx(0.21244156)
    assert np.max(fc_remainder[0].data) == pytest.approx(7.01886734e-07)

    assert np.max(fc_noise[1].data) == pytest.approx(0.30395156)
    assert np.max(fc_tonal[1].data) == pytest.approx(0.79357791)
    assert np.max(fc_transient[1].data) == pytest.approx(0.21244156)
    assert np.max(fc_remainder[1].data) == pytest.approx(7.01886734e-07)


def test_xtract_get_output_as_nparray(dpf_sound_test_server):
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute_in_container)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    ## Creating noise profile with Xtract helper (white noise level)
    params_denoiser = XtractDenoiserParameters()
    params_denoiser.noise_psd = params_denoiser.create_noise_psd_from_white_noise_level(
        -6.0, 44100.0, 50
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
    np_noise, np_tonal, np_transient, np_remainder = xtract.get_output_as_nparray()

    assert np_noise is not None
    assert np_tonal is not None
    assert np_transient is not None
    assert np_remainder is not None

    assert type(np_noise) == np.ndarray
    assert type(np_tonal) == np.ndarray
    assert type(np_transient) == np.ndarray
    assert type(np_remainder) == np.ndarray

    # Check numerical apps.
    assert np.min(np_noise) == pytest.approx(-0.2635681)
    assert np.max(np_noise) == pytest.approx(0.30395156)

    assert np.min(np_tonal) == pytest.approx(-0.67513376)
    assert np.max(np_tonal) == pytest.approx(0.79357791)

    assert np.min(np_transient) == pytest.approx(-0.20801553)
    assert np.max(np_transient) == pytest.approx(0.21244156)

    assert np.min(np_remainder) == pytest.approx(-7.95791721e-07)
    assert np.max(np_remainder) == pytest.approx(7.01886734e-07)


def test_xtract_get_output_fc_as_nparray(dpf_sound_test_server):
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute_in_container)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    fc_bird_plus_idle = FieldsContainer()
    fc_bird_plus_idle.labels = ["channel"]
    fc_bird_plus_idle.add_field({"channel": 0}, bird_plus_idle_sig)
    fc_bird_plus_idle.add_field({"channel": 1}, bird_plus_idle_sig)

    ## Creating noise profile with Xtract helper (white noise level)
    params_denoiser = XtractDenoiserParameters()
    params_denoiser.noise_psd = params_denoiser.create_noise_psd_from_white_noise_level(
        -6.0, 44100.0, 50
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

    xtract = Xtract(fc_bird_plus_idle, params_denoiser, params_tonal, params_transient)
    xtract.process()
    # Get out_put as FieldContainer
    np_fc_noise, np_fc_tonal, np_fc_transient, np_fc_remainder = xtract.get_output_as_nparray()

    assert np_fc_noise is not None
    assert np_fc_tonal is not None
    assert np_fc_transient is not None
    assert np_fc_remainder is not None

    assert type(np_fc_noise) == np.ndarray
    assert type(np_fc_tonal) == np.ndarray
    assert type(np_fc_transient) == np.ndarray
    assert type(np_fc_remainder) == np.ndarray

    assert np_fc_noise.shape == (2, 156048)
    assert np_fc_tonal.shape == (2, 156048)
    assert np_fc_transient.shape == (2, 156048)
    assert np_fc_remainder.shape == (2, 156048)

    assert np_fc_noise[0] is not None
    assert np_fc_tonal[0] is not None
    assert np_fc_transient[0] is not None
    assert np_fc_remainder[0] is not None

    assert np_fc_noise[1] is not None
    assert np_fc_tonal[1] is not None
    assert np_fc_transient[1] is not None
    assert np_fc_remainder[1] is not None

    # Check numerical apps.
    assert np.min(np_fc_noise[0][:]) == pytest.approx(-0.2635681)
    assert np.min(np_fc_tonal[0][:]) == pytest.approx(-0.6751337647438049)
    assert np.min(np_fc_transient[0][:]) == pytest.approx(-0.20801553)
    assert np.min(np_fc_remainder[0][:]) == pytest.approx(-7.957917205203557e-07)

    assert np.min(np_fc_noise[1][:]) == pytest.approx(-0.2635681)
    assert np.min(np_fc_tonal[1][:]) == pytest.approx(-0.67513376)
    assert np.min(np_fc_transient[1][:]) == pytest.approx(-0.20801553)
    assert np.min(np_fc_remainder[1][:]) == pytest.approx(-7.95791721e-07)

    assert np.max(np_fc_noise[0][:]) == pytest.approx(0.30395156)
    assert np.max(np_fc_tonal[0][:]) == pytest.approx(0.79357791)
    assert np.max(np_fc_transient[0][:]) == pytest.approx(0.21244156)
    assert np.max(np_fc_remainder[0][:]) == pytest.approx(7.01886734e-07)

    assert np.max(np_fc_noise[1][:]) == pytest.approx(0.30395156)
    assert np.max(np_fc_tonal[1][:]) == pytest.approx(0.79357791)
    assert np.max(np_fc_transient[1][:]) == pytest.approx(0.21244156)
    assert np.max(np_fc_remainder[1][:]) == pytest.approx(7.01886734e-07)


def test_xtract_setters(dpf_sound_test_server):
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute_in_container)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    ## Creating noise profile with Xtract helper (white noise level)
    params_denoiser = XtractDenoiserParameters()
    params_denoiser.noise_psd = params_denoiser.create_noise_psd_from_white_noise_level(
        -6.0, 44100.0, 50
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

    assert xtract.input_signal is not None
    xtract.input_signal = None
    assert xtract.input_signal is None

    assert xtract.parameters_denoiser is not None
    xtract.parameters_denoiser = None
    assert xtract.parameters_denoiser is None

    assert xtract.parameters_tonal is not None
    xtract.parameters_tonal = None
    assert xtract.parameters_tonal is None

    assert xtract.parameters_transient is not None
    xtract.parameters_transient = None
    assert xtract.parameters_transient is None


@patch("matplotlib.pyplot.show")
def test_xtract_plot_output(mock_show, dpf_sound_test_server):
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute_in_container)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    ## Creating noise profile with Xtract helper (white noise level)
    params_denoiser = XtractDenoiserParameters()
    params_denoiser.noise_psd = params_denoiser.create_noise_psd_from_white_noise_level(
        -6.0, 44100.0, 50
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


@patch("matplotlib.pyplot.show")
def test_xtract_plot_output_fc(mock_show, dpf_sound_test_server):
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute_in_container)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    fc_bird_plus_idle = FieldsContainer()
    fc_bird_plus_idle.labels = ["channel"]
    fc_bird_plus_idle.add_field({"channel": 0}, bird_plus_idle_sig)
    fc_bird_plus_idle.add_field({"channel": 1}, bird_plus_idle_sig)

    ## Creating noise profile with Xtract helper (white noise level)
    params_denoiser = XtractDenoiserParameters()
    params_denoiser.noise_psd = params_denoiser.create_noise_psd_from_white_noise_level(
        -6.0, 44100.0, 50
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

    xtract = Xtract(fc_bird_plus_idle, params_denoiser, params_tonal, params_transient)
    xtract.process()

    xtract.plot()
