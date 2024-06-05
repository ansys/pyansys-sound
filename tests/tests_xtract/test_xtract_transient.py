from unittest.mock import patch

from ansys.dpf.core import Field, FieldsContainer, GenericDataContainer
import numpy as np
import pytest

from ansys.sound.core.pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ansys.sound.core.signal_utilities import LoadWav
from ansys.sound.core.xtract.xtract_transient import XtractTransient
from ansys.sound.core.xtract.xtract_transient_parameters import XtractTransientParameters


def test_xtract_transient_instantiation(dpf_sound_test_server):
    xtract_transient = XtractTransient()
    assert xtract_transient != None


def test_xtract_transient_initialization_FieldsContainer(dpf_sound_test_server):
    # Test initialization with default values
    xtract_transient = XtractTransient()
    assert xtract_transient.input_signal is None
    assert xtract_transient.input_parameters is None
    assert xtract_transient.output_transient_signals is None
    assert xtract_transient.output_non_transient_signals is None

    # Test initialization with custom values
    input_signal = FieldsContainer()
    input_parameters = XtractTransientParameters()
    xtract_transient = XtractTransient(
        input_signal=input_signal,
        input_parameters=input_parameters,
    )
    assert xtract_transient.input_signal == input_signal
    assert xtract_transient.input_parameters == input_parameters
    assert xtract_transient.output_transient_signals is None
    assert xtract_transient.output_non_transient_signals is None


def test_xtract_transient_initialization_Field():
    # Test initialization with default values
    xtract_transient = XtractTransient()
    assert xtract_transient.input_signal is None
    assert xtract_transient.input_parameters is None
    assert xtract_transient.output_transient_signals is None
    assert xtract_transient.output_non_transient_signals is None

    # Test initialization with custom values
    input_signal = Field()
    input_parameters = XtractTransientParameters()
    xtract_transient = XtractTransient(
        input_signal=input_signal,
        input_parameters=input_parameters,
    )
    assert xtract_transient.input_signal == input_signal
    assert xtract_transient.input_parameters == input_parameters
    assert xtract_transient.output_transient_signals is None
    assert xtract_transient.output_non_transient_signals is None


def test_xtract_transient_except1(dpf_sound_test_server):
    xtract_transient = XtractTransient(None, XtractTransientParameters())
    with pytest.raises(PyAnsysSoundException) as excinfo:
        xtract_transient.process()
    assert str(excinfo.value) == "Input signal is not set."


def test_xtract_transient_except2(dpf_sound_test_server):
    xtract_transient = XtractTransient(Field(), None)
    with pytest.raises(PyAnsysSoundException) as excinfo:
        xtract_transient.process()
    assert str(excinfo.value) == "Input parameters are not set."


def test_xtract_transient_process(dpf_sound_test_server):
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute_in_container)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    # Setting transient parameters
    params_transient = XtractTransientParameters()
    params_transient.lower_threshold = 1.0
    params_transient.upper_threshold = 100.0

    xtract_transient = XtractTransient(bird_plus_idle_sig, params_transient)
    xtract_transient.process()

    assert xtract_transient.output_transient_signals is not None
    assert xtract_transient.output_non_transient_signals is not None

    assert type(xtract_transient.output_transient_signals) == Field
    assert type(xtract_transient.output_non_transient_signals) == Field

    # Type of output transient signals. It should be a Field
    # transient
    assert type(xtract_transient.get_output()[0]) == Field
    assert type(xtract_transient.get_output()[1]) == Field

    assert xtract_transient.get_output()[0].data[0] == pytest.approx(0.0)
    assert xtract_transient.get_output()[0].data[99] == pytest.approx(0.0)
    assert np.min(xtract_transient.get_output()[0].data) == pytest.approx(-0.70742798)
    assert np.max(xtract_transient.get_output()[0].data) == pytest.approx(0.87719721)
    # non transient
    assert xtract_transient.get_output()[1].data[0] == pytest.approx(0.0)
    assert xtract_transient.get_output()[1].data[99] == pytest.approx(0.0)
    assert np.min(xtract_transient.get_output()[1].data) == pytest.approx(-1.78813934e-07)
    assert np.max(xtract_transient.get_output()[1].data) == pytest.approx(1.78813934e-07)


def test_xtract_transient_get_output_warns(dpf_sound_test_server):
    xtract_transient = XtractTransient()
    with pytest.warns(PyAnsysSoundWarning) as record:
        xtract_transient.get_output()
    assert "Output has not been processed yet." in record[0].message.args[0]


def test_xtract_transient_get_output_as_np_array_warns(dpf_sound_test_server):
    xtract_transient = XtractTransient()
    with pytest.warns(PyAnsysSoundWarning) as record:
        xtract_transient.get_output_as_nparray()
    assert "Output has not been processed yet." in record[0].message.args[0]


def test_xtract_transient_get_output(dpf_sound_test_server):
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute_in_container)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    # Setting transient parameters
    params_transient = XtractTransientParameters()
    params_transient.lower_threshold = 1.0
    params_transient.upper_threshold = 100.0

    xtract_transient = XtractTransient(bird_plus_idle_sig, params_transient)
    xtract_transient.process()

    # Type of output transient signals. It should be a Field
    # transient
    assert type(xtract_transient.get_output()[0]) == Field
    assert type(xtract_transient.get_output()[1]) == Field

    assert xtract_transient.get_output()[0].data[0] == pytest.approx(0.0)
    assert xtract_transient.get_output()[0].data[99] == pytest.approx(0.0)
    assert np.min(xtract_transient.get_output()[0].data) == pytest.approx(-0.70742798)
    assert np.max(xtract_transient.get_output()[0].data) == pytest.approx(0.87719721)
    # non transient
    assert xtract_transient.get_output()[1].data[0] == pytest.approx(0.0)
    assert xtract_transient.get_output()[1].data[99] == pytest.approx(0.0)
    assert np.min(xtract_transient.get_output()[1].data) == pytest.approx(-1.78813934e-07)
    assert np.max(xtract_transient.get_output()[1].data) == pytest.approx(1.78813934e-07)


def test_xtract_transient_get_output_noprocess(dpf_sound_test_server):
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute_in_container)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    # Setting transient parameters
    params_transient = GenericDataContainer()
    params_transient.set_property("class_name", "Xtract_transient_parameters")
    params_transient.set_property("lower_threshold", 1.0)
    params_transient.set_property("upper_threshold", 100.0)

    xtract_transient = XtractTransient(bird_plus_idle_sig, params_transient)
    output_transient_signals, output_non_transient_signals = xtract_transient.get_output()

    assert output_transient_signals is None
    assert output_non_transient_signals is None


def test_xtract_transient_get_output_fc(dpf_sound_test_server):
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute_in_container)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    # Setting transient parameters
    params_transient = XtractTransientParameters()
    params_transient.lower_threshold = 1.0
    params_transient.upper_threshold = 100.0

    fc_bird_plus_idle = FieldsContainer()
    fc_bird_plus_idle.labels = ["channel"]
    fc_bird_plus_idle.add_field({"channel": 0}, bird_plus_idle_sig)
    fc_bird_plus_idle.add_field({"channel": 1}, bird_plus_idle_sig)

    xtract_transient = XtractTransient(fc_bird_plus_idle, params_transient)
    xtract_transient.process()

    assert xtract_transient.get_output() is not None
    assert type(xtract_transient.get_output()[0]) == FieldsContainer
    assert type(xtract_transient.get_output()[1]) == FieldsContainer

    # Verify the output of the transient analysis
    assert xtract_transient.get_output()[0][0].data[0] == pytest.approx(0.0)
    assert xtract_transient.get_output()[0][0].data[99] == pytest.approx(0.0)
    # Verify the output of the non transient analysis
    assert xtract_transient.get_output()[1][0].data[0] == pytest.approx(0.0)
    assert xtract_transient.get_output()[1][0].data[99] == pytest.approx(0.0)


def test_xtract_transient_get_output_as_nparray(dpf_sound_test_server):
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute_in_container)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    # Setting transient parameters
    params_transient = GenericDataContainer()
    params_transient.set_property("class_name", "Xtract_transient_parameters")
    params_transient.set_property("lower_threshold", 1.0)
    params_transient.set_property("upper_threshold", 100.0)

    xtract_transient = XtractTransient(bird_plus_idle_sig, params_transient)
    xtract_transient.process()

    # Type of output transient signals. np.array
    assert xtract_transient.get_output_as_nparray() is not None
    assert type(xtract_transient.get_output_as_nparray()[0]) == np.ndarray
    assert type(xtract_transient.get_output_as_nparray()[1]) == np.ndarray

    assert xtract_transient.get_output_as_nparray()[0].shape == (156048,)


def test_xtract_transient_get_output_as_nparray(dpf_sound_test_server):
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute_in_container)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    # Setting transient parameters
    params_transient = XtractTransientParameters()
    params_transient.lower_threshold = 1.0
    params_transient.upper_threshold = 100.0

    xtract_transient = XtractTransient(bird_plus_idle_sig, params_transient)
    xtract_transient.process()

    # Type of output transient signals. np.array
    assert xtract_transient.get_output_as_nparray() is not None
    assert type(xtract_transient.get_output_as_nparray()[0]) == np.ndarray
    assert type(xtract_transient.get_output_as_nparray()[1]) == np.ndarray

    assert xtract_transient.get_output_as_nparray()[0].shape == (156048,)
    np.min(xtract_transient.get_output_as_nparray()[0]) == pytest.approx(-0.707427978515625)
    np.max(xtract_transient.get_output_as_nparray()[0]) == pytest.approx(0.8771972060203552)
    np.min(xtract_transient.get_output_as_nparray()[1]) == pytest.approx(-1.7881393432617188e-07)
    np.max(xtract_transient.get_output_as_nparray()[1]) == pytest.approx(-1.7881393432617188e-07)


def test_xtract_transient_get_output_fc_as_nparray(dpf_sound_test_server):
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute_in_container)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    # Setting transient parameters
    params_transient = XtractTransientParameters()
    params_transient.lower_threshold = 1.0
    params_transient.upper_threshold = 100.0

    fc_bird_plus_idle = FieldsContainer()
    fc_bird_plus_idle.labels = ["channel"]
    fc_bird_plus_idle.add_field({"channel": 0}, bird_plus_idle_sig)
    fc_bird_plus_idle.add_field({"channel": 1}, bird_plus_idle_sig)

    xtract_transient = XtractTransient(fc_bird_plus_idle, params_transient)
    xtract_transient.process()

    assert type(xtract_transient.get_output_as_nparray()[0]) == np.ndarray
    assert type(xtract_transient.get_output_as_nparray()[1]) == np.ndarray


def test_xtract_transient_setters(dpf_sound_test_server):
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute_in_container)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    # Setting transient parameters
    params_transient = XtractTransientParameters()
    params_transient.lower_threshold = 1.0
    params_transient.upper_threshold = 100.0

    xtract_transient = XtractTransient(bird_plus_idle_sig, params_transient)

    assert xtract_transient.input_signal is not None
    xtract_transient.input_signal = None
    assert xtract_transient.input_signal is None

    assert xtract_transient.input_parameters is not None
    xtract_transient.input_parameters = None
    assert xtract_transient.input_parameters is None


@patch("matplotlib.pyplot.show")
def test_xtract_transient_plot_output(mock_show, dpf_sound_test_server):
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute_in_container)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    # Setting transient parameters
    params_transient = XtractTransientParameters()
    params_transient.lower_threshold = 1.0
    params_transient.upper_threshold = 100.0

    xtract_transient = XtractTransient(bird_plus_idle_sig, params_transient)
    xtract_transient.process()

    xtract_transient.plot()


@patch("matplotlib.pyplot.show")
def test_xtract_transient_plot_output_fc(mock_show, dpf_sound_test_server):
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute_in_container)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    # Setting transient parameters
    params_transient = XtractTransientParameters()
    params_transient.lower_threshold = 1.0
    params_transient.upper_threshold = 100.0

    fc_bird_plus_idle = FieldsContainer()
    fc_bird_plus_idle.labels = ["channel"]
    fc_bird_plus_idle.add_field({"channel": 0}, bird_plus_idle_sig)
    fc_bird_plus_idle.add_field({"channel": 1}, bird_plus_idle_sig)

    xtract_transient = XtractTransient(fc_bird_plus_idle, params_transient)
    xtract_transient.process()

    xtract_transient.plot()
