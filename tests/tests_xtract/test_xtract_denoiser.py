from unittest.mock import patch

from ansys.dpf.core import Field, FieldsContainer, GenericDataContainer, Operator
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

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    ## Creating noise profile with Xtract helper (white noise power)
    op_create_noise_from_white_noise = Operator("create_noise_profile_from_white_noise_power")

    op_create_noise_from_white_noise.connect(0, -6.0)
    op_create_noise_from_white_noise.connect(1, 44100.0)
    op_create_noise_from_white_noise.connect(2, 50)

    op_create_noise_from_white_noise.run()
    l_noise_profile = op_create_noise_from_white_noise.get_output(0, "field")

    # Setting Denoiser parameters
    params_denoiser = GenericDataContainer()
    params_denoiser.set_property("class_name", "Xtract_denoiser_parameters")
    params_denoiser.set_property("noise_levels", l_noise_profile)

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
    assert np.min(xtract_denoiser.get_output_as_nparray()[0]) == pytest.approx(-0.6995288133621216)
    assert np.max(xtract_denoiser.get_output_as_nparray()[0]) == pytest.approx(0.8091265559196472)

    # Get the noise signal
    assert xtract_denoiser.get_output_as_nparray()[1][0] == pytest.approx(-4.048184330747483e-15)
    assert xtract_denoiser.get_output_as_nparray()[1][99] == pytest.approx(-3.329021806551297e-15)


def test_xtract_denoiser_get_output_warns(dpf_sound_test_server):
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute_in_container)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    ## Creating noise profile with Xtract helper (white noise power)
    op_create_noise_from_white_noise = Operator("create_noise_profile_from_white_noise_power")

    op_create_noise_from_white_noise.connect(0, -6.0)
    op_create_noise_from_white_noise.connect(1, 44100.0)
    op_create_noise_from_white_noise.connect(2, 50)

    op_create_noise_from_white_noise.run()
    l_noise_profile = op_create_noise_from_white_noise.get_output(0, "field")

    # Setting Denoiser parameters
    params_denoiser = GenericDataContainer()
    params_denoiser.set_property("class_name", "Xtract_denoiser_parameters")
    params_denoiser.set_property("noise_levels", l_noise_profile)

    xtract_denoiser = XtractDenoiser(bird_plus_idle_sig, params_denoiser)

    with pytest.warns(PyDpfSoundWarning) as record:
        xtract_denoiser.get_output()
    assert record[0].message.args[0] == "Output has not been processed yet."


def test_xtract_denoiser_get_output_np_array_warns(dpf_sound_test_server):
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute_in_container)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    ## Creating noise profile with Xtract helper (white noise power)
    op_create_noise_from_white_noise = Operator("create_noise_profile_from_white_noise_power")

    op_create_noise_from_white_noise.connect(0, -6.0)
    op_create_noise_from_white_noise.connect(1, 44100.0)
    op_create_noise_from_white_noise.connect(2, 50)

    op_create_noise_from_white_noise.run()
    l_noise_profile = op_create_noise_from_white_noise.get_output(0, "field")

    # Setting Denoiser parameters
    params_denoiser = GenericDataContainer()
    params_denoiser.set_property("class_name", "Xtract_denoiser_parameters")
    params_denoiser.set_property("noise_levels", l_noise_profile)

    xtract_denoiser = XtractDenoiser(bird_plus_idle_sig, params_denoiser)

    with pytest.warns(PyDpfSoundWarning) as record:
        xtract_denoiser.get_output_as_nparray()
    assert record[0].message.args[0] == "Output has not been processed yet."


def test_xtract_denoiser_get_output(dpf_sound_test_server):
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute_in_container)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    ## Creating noise profile with Xtract helper (white noise power)
    op_create_noise_from_white_noise = Operator("create_noise_profile_from_white_noise_power")

    op_create_noise_from_white_noise.connect(0, -6.0)
    op_create_noise_from_white_noise.connect(1, 44100.0)
    op_create_noise_from_white_noise.connect(2, 50)

    op_create_noise_from_white_noise.run()
    l_noise_profile = op_create_noise_from_white_noise.get_output(0, "field")

    # Setting Denoiser parameters
    params_denoiser = GenericDataContainer()
    params_denoiser.set_property("class_name", "Xtract_denoiser_parameters")
    params_denoiser.set_property("noise_levels", l_noise_profile)

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


def test_xtract_denoiser_get_output_noprocess(dpf_sound_test_server):
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute_in_container)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    ## Creating noise profile with Xtract helper (white noise power)
    op_create_noise_from_white_noise = Operator("create_noise_profile_from_white_noise_power")

    op_create_noise_from_white_noise.connect(0, -6.0)
    op_create_noise_from_white_noise.connect(1, 44100.0)
    op_create_noise_from_white_noise.connect(2, 50)

    op_create_noise_from_white_noise.run()
    l_noise_profile = op_create_noise_from_white_noise.get_output(0, "field")

    # Setting Denoiser parameters
    params_denoiser = GenericDataContainer()
    params_denoiser.set_property("class_name", "Xtract_denoiser_parameters")
    params_denoiser.set_property("noise_levels", l_noise_profile)

    xtract_denoiser = XtractDenoiser(bird_plus_idle_sig, params_denoiser)
    output1, output2 = xtract_denoiser.get_output()
    # note: check warnings on the console to see the warning message
    assert output1 is None
    assert output2 is None


def test_xtract_denoiser_get_output_fc(dpf_sound_test_server):
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute_in_container)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    ## Creating noise profile with Xtract helper (white noise power)
    op_create_noise_from_white_noise = Operator("create_noise_profile_from_white_noise_power")

    op_create_noise_from_white_noise.connect(0, -6.0)
    op_create_noise_from_white_noise.connect(1, 44100.0)
    op_create_noise_from_white_noise.connect(2, 50)

    op_create_noise_from_white_noise.run()
    l_noise_profile = op_create_noise_from_white_noise.get_output(0, "field")

    # Setting Denoiser parameters
    params_denoiser = GenericDataContainer()
    params_denoiser.set_property("class_name", "Xtract_denoiser_parameters")
    params_denoiser.set_property("noise_levels", l_noise_profile)

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


def test_xtract_denoiser_get_output_as_nparray(dpf_sound_test_server):
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute_in_container)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    ## Creating noise profile with Xtract helper (white noise power)
    op_create_noise_from_white_noise = Operator("create_noise_profile_from_white_noise_power")

    op_create_noise_from_white_noise.connect(0, -6.0)
    op_create_noise_from_white_noise.connect(1, 44100.0)
    op_create_noise_from_white_noise.connect(2, 50)

    op_create_noise_from_white_noise.run()
    l_noise_profile = op_create_noise_from_white_noise.get_output(0, "field")

    # Setting Denoiser parameters
    params_denoiser = GenericDataContainer()
    params_denoiser.set_property("class_name", "Xtract_denoiser_parameters")
    params_denoiser.set_property("noise_levels", l_noise_profile)

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
    assert np.min(xtract_denoiser.get_output_as_nparray()[0]) == pytest.approx(-0.6995288133621216)
    assert np.max(xtract_denoiser.get_output_as_nparray()[0]) == pytest.approx(0.8091265559196472)

    # Get the noise signal
    assert xtract_denoiser.get_output_as_nparray()[1][0] == pytest.approx(-4.048184330747483e-15)
    assert xtract_denoiser.get_output_as_nparray()[1][99] == pytest.approx(-3.329021806551297e-15)


def test_xtract_denoiser_get_output_fc_as_nparray(dpf_sound_test_server):
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute_in_container)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    ## Creating noise profile with Xtract helper (white noise power)
    op_create_noise_from_white_noise = Operator("create_noise_profile_from_white_noise_power")

    op_create_noise_from_white_noise.connect(0, -6.0)
    op_create_noise_from_white_noise.connect(1, 44100.0)
    op_create_noise_from_white_noise.connect(2, 50)

    op_create_noise_from_white_noise.run()
    l_noise_profile = op_create_noise_from_white_noise.get_output(0, "field")

    # Setting Denoiser parameters
    params_denoiser = GenericDataContainer()
    params_denoiser.set_property("class_name", "Xtract_denoiser_parameters")
    params_denoiser.set_property("noise_levels", l_noise_profile)

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


def test_xtract_denoiser_setters(dpf_sound_test_server):
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute_in_container)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    ## Creating noise profile with Xtract helper (white noise power)
    op_create_noise_from_white_noise = Operator("create_noise_profile_from_white_noise_power")

    op_create_noise_from_white_noise.connect(0, -6.0)
    op_create_noise_from_white_noise.connect(1, 44100.0)
    op_create_noise_from_white_noise.connect(2, 50)

    op_create_noise_from_white_noise.run()
    l_noise_profile = op_create_noise_from_white_noise.get_output(0, "field")

    # Setting Denoiser parameters
    params_denoiser = GenericDataContainer()
    params_denoiser.set_property("class_name", "Xtract_denoiser_parameters")
    params_denoiser.set_property("noise_levels", l_noise_profile)

    xtract_denoiser = XtractDenoiser(bird_plus_idle_sig, params_denoiser)

    assert xtract_denoiser.input_signal is not None
    xtract_denoiser.input_signal = None
    assert xtract_denoiser.input_signal is None

    assert xtract_denoiser.input_parameters is not None
    xtract_denoiser.input_parameters = None
    assert xtract_denoiser.input_parameters is None


@patch("matplotlib.pyplot.show")
def test_xtract_denoiser_plot_output(mock_show, dpf_sound_test_server):
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute_in_container)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    ## Creating noise profile with Xtract helper (white noise power)
    op_create_noise_from_white_noise = Operator("create_noise_profile_from_white_noise_power")

    op_create_noise_from_white_noise.connect(0, -6.0)
    op_create_noise_from_white_noise.connect(1, 44100.0)
    op_create_noise_from_white_noise.connect(2, 50)

    op_create_noise_from_white_noise.run()
    l_noise_profile = op_create_noise_from_white_noise.get_output(0, "field")

    # Setting Denoiser parameters
    params_denoiser = GenericDataContainer()
    params_denoiser.set_property("class_name", "Xtract_denoiser_parameters")
    params_denoiser.set_property("noise_levels", l_noise_profile)

    xtract_denoiser = XtractDenoiser(bird_plus_idle_sig, params_denoiser)
    xtract_denoiser.process()

    xtract_denoiser.plot()


@patch("matplotlib.pyplot.show")
def test_xtract_denoiser_plot_output_fc(mock_show, dpf_sound_test_server):
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute_in_container)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    ## Creating noise profile with Xtract helper (white noise power)
    op_create_noise_from_white_noise = Operator("create_noise_profile_from_white_noise_power")

    op_create_noise_from_white_noise.connect(0, -6.0)
    op_create_noise_from_white_noise.connect(1, 44100.0)
    op_create_noise_from_white_noise.connect(2, 50)

    op_create_noise_from_white_noise.run()
    l_noise_profile = op_create_noise_from_white_noise.get_output(0, "field")

    # Setting Denoiser parameters
    params_denoiser = GenericDataContainer()
    params_denoiser.set_property("class_name", "Xtract_denoiser_parameters")
    params_denoiser.set_property("noise_levels", l_noise_profile)

    fc_bird_plus_idle = FieldsContainer()
    fc_bird_plus_idle.labels = ["channel"]
    fc_bird_plus_idle.add_field({"channel": 0}, bird_plus_idle_sig)
    fc_bird_plus_idle.add_field({"channel": 1}, bird_plus_idle_sig)

    # Test 1 - param denoiser with only one noise profile
    xtract_denoiser = XtractDenoiser(fc_bird_plus_idle, params_denoiser)
    xtract_denoiser.process()

    xtract_denoiser.plot()