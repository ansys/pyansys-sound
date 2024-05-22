from unittest.mock import patch

from ansys.dpf.core import Field, FieldsContainer, GenericDataContainer
import numpy as np
import pytest

from ansys.dpf.sound.pydpf_sound import PyDpfSoundException, PyDpfSoundWarning
from ansys.dpf.sound.signal_utilities import LoadWav
from ansys.dpf.sound.xtract.xtract_tonal import XtractTonal


def test_xtract_tonal_instantiation(dpf_sound_test_server):
    xtract_tonal = XtractTonal()
    assert xtract_tonal != None


def test_xtract_tonal_initialization_FieldsContainer(dpf_sound_test_server):
    # Test initialization with default values
    xtract_tonal = XtractTonal()
    assert xtract_tonal.input_signal is None
    assert xtract_tonal.input_parameters is None
    assert xtract_tonal.output_tonal_signals is None
    assert xtract_tonal.output_non_tonal_signals is None

    # Test initialization with custom values
    input_signal = FieldsContainer()
    input_parameters = GenericDataContainer()
    xtract_tonal = XtractTonal(
        input_signal=input_signal,
        input_parameters=input_parameters,
    )
    assert xtract_tonal.input_signal == input_signal
    assert xtract_tonal.input_parameters == input_parameters
    assert xtract_tonal.output_tonal_signals is None
    assert xtract_tonal.output_non_tonal_signals is None


def test_xtract_tonal_initialization_Field(dpf_sound_test_server):
    # Test initialization with default values
    xtract_tonal = XtractTonal()
    assert xtract_tonal.input_signal is None
    assert xtract_tonal.input_parameters is None
    assert xtract_tonal.output_tonal_signals is None
    assert xtract_tonal.output_non_tonal_signals is None

    # Test initialization with custom values
    input_signal = Field()
    input_parameters = GenericDataContainer()
    xtract_tonal = XtractTonal(
        input_signal=input_signal,
        input_parameters=input_parameters,
    )
    assert xtract_tonal.input_signal == input_signal
    assert xtract_tonal.input_parameters == input_parameters
    assert xtract_tonal.output_tonal_signals is None
    assert xtract_tonal.output_non_tonal_signals is None


def test_xtract_tonal_process_except1(dpf_sound_test_server):
    xtract_tonal = XtractTonal(None, GenericDataContainer())
    with pytest.raises(PyDpfSoundException) as excinfo:
        xtract_tonal.process()
    assert str(excinfo.value) == "No input signal for tonal analysis."


def test_xtract_tonal_process_except2(dpf_sound_test_server):
    xtract_tonal = XtractTonal(Field(), None)
    with pytest.raises(PyDpfSoundException) as excinfo:
        xtract_tonal.process()
    assert str(excinfo.value) == "Input parameters are not set."


def test_xtract_tonal_process(dpf_sound_test_server):
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute_in_container)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    # Setting tonal parameters
    params_tonal = GenericDataContainer()
    params_tonal.set_property("class_name", "Xtract_tonal_parameters")
    params_tonal.set_property("regularity", 1.0)
    params_tonal.set_property("maximum_slope", 750.0)
    params_tonal.set_property("minimum_duration", 1.0)
    params_tonal.set_property("intertonal_gap", 20.0)
    params_tonal.set_property("local_emergence", 15.0)
    params_tonal.set_property("fft_size", 8192)

    xtract_tonal = XtractTonal(bird_plus_idle_sig, params_tonal)
    xtract_tonal.process()

    assert xtract_tonal.output_tonal_signals is not None
    assert xtract_tonal.output_non_tonal_signals is not None

    assert type(xtract_tonal.output_tonal_signals) == Field
    assert type(xtract_tonal.output_non_tonal_signals) == Field

    # Type of output tonal signals. np.array
    assert xtract_tonal.get_output_as_nparray() is not None
    assert type(xtract_tonal.get_output_as_nparray()[0]) == np.ndarray
    assert type(xtract_tonal.get_output_as_nparray()[1]) == np.ndarray

    assert xtract_tonal.get_output_as_nparray()[0].shape == (156048,)
    assert np.min(xtract_tonal.get_output_as_nparray()[0]) == pytest.approx(-0.6828306913375854)
    assert np.max(xtract_tonal.get_output_as_nparray()[0]) == pytest.approx(0.794617772102356)

    assert xtract_tonal.get_output_as_nparray()[0][0] == pytest.approx(3.6770161386812106e-06)
    assert xtract_tonal.get_output_as_nparray()[0][1] == pytest.approx(1.8551201037553255e-06)

    assert xtract_tonal.get_output_as_nparray()[1].shape == (156048,)
    assert xtract_tonal.get_output_as_nparray()[1][0] == pytest.approx(-3.6770161386812106e-06)
    assert xtract_tonal.get_output_as_nparray()[1][99] == pytest.approx(1.8362156879447866e-06)


def test_xtract_tonal_get_output_warns(dpf_sound_test_server):
    xtract_tonal = XtractTonal()
    with pytest.warns(PyDpfSoundWarning) as record:
        xtract_tonal.get_output()
    assert "Output tonal or non tonal signals are not set" in record[0].message.args[0]


def test_xtract_tonal_get_output_as_nparray_warns(dpf_sound_test_server):
    xtract_tonal = XtractTonal()
    with pytest.warns(PyDpfSoundWarning) as record:
        xtract_tonal.get_output_as_nparray()
    assert "Output tonal or non tonal signals are not set" in record[0].message.args[0]


def test_xtract_tonal_get_output(dpf_sound_test_server):
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute_in_container)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    # Setting tonal parameters
    params_tonal = GenericDataContainer()
    params_tonal.set_property("class_name", "Xtract_tonal_parameters")
    params_tonal.set_property("regularity", 1.0)
    params_tonal.set_property("maximum_slope", 750.0)
    params_tonal.set_property("minimum_duration", 1.0)
    params_tonal.set_property("intertonal_gap", 20.0)
    params_tonal.set_property("local_emergence", 15.0)
    params_tonal.set_property("fft_size", 8192)

    xtract_tonal = XtractTonal(bird_plus_idle_sig, params_tonal)
    xtract_tonal.process()

    assert xtract_tonal.output_tonal_signals is not None
    assert xtract_tonal.output_non_tonal_signals is not None

    assert type(xtract_tonal.output_tonal_signals) == Field
    assert type(xtract_tonal.output_non_tonal_signals) == Field

    # Type of output tonal signals. As Field
    assert xtract_tonal.get_output()[0].data[0] == pytest.approx(3.6770161386812106e-06)
    assert xtract_tonal.get_output()[0].data[1] == pytest.approx(1.8551201037553255e-06)

    assert xtract_tonal.get_output()[1].data[0] == pytest.approx(-3.6770161386812106e-06)
    assert xtract_tonal.get_output()[1].data[99] == pytest.approx(1.8362156879447866e-06)


def test_xtract_tonal_get_output_noprocess(dpf_sound_test_server):
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute_in_container)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    # Setting tonal parameters
    params_tonal = GenericDataContainer()
    params_tonal.set_property("class_name", "Xtract_tonal_parameters")
    params_tonal.set_property("regularity", 1.0)
    params_tonal.set_property("maximum_slope", 750.0)
    params_tonal.set_property("minimum_duration", 1.0)
    params_tonal.set_property("intertonal_gap", 20.0)
    params_tonal.set_property("local_emergence", 15.0)
    params_tonal.set_property("fft_size", 8192)

    xtract_tonal = XtractTonal(bird_plus_idle_sig, params_tonal)
    output1, output2 = xtract_tonal.get_output()

    assert output1 is None
    assert output2 is None


def test_xtract_tonal_get_output_fc(dpf_sound_test_server):
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute_in_container)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    # Setting tonal parameters
    params_tonal = GenericDataContainer()
    params_tonal.set_property("class_name", "Xtract_tonal_parameters")
    params_tonal.set_property("regularity", 1.0)
    params_tonal.set_property("maximum_slope", 750.0)
    params_tonal.set_property("minimum_duration", 1.0)
    params_tonal.set_property("intertonal_gap", 20.0)
    params_tonal.set_property("local_emergence", 15.0)
    params_tonal.set_property("fft_size", 8192)

    fc_bird_plus_idle = FieldsContainer()
    fc_bird_plus_idle.labels = ["channel"]
    fc_bird_plus_idle.add_field({"channel": 0}, bird_plus_idle_sig)
    fc_bird_plus_idle.add_field({"channel": 1}, bird_plus_idle_sig)

    xtract_tonal = XtractTonal(fc_bird_plus_idle, params_tonal)
    xtract_tonal.process()

    assert xtract_tonal.get_output() is not None
    assert type(xtract_tonal.get_output()[0]) == FieldsContainer
    assert type(xtract_tonal.get_output()[1]) == FieldsContainer

    # Verify numerical app. of the denoiser.
    # Get the denoised signal - signal1
    assert xtract_tonal.get_output()[0][0].data[0] == pytest.approx(3.6770161386812106e-06)
    assert xtract_tonal.get_output()[0][0].data[99] == pytest.approx(-1.8362156879447866e-06)

    # Get the denoised signal - signal2
    assert xtract_tonal.get_output()[0][1].data[0] == pytest.approx(3.6770161386812106e-06)
    assert xtract_tonal.get_output()[0][1].data[99] == pytest.approx(-1.8362156879447866e-06)

    # Get the noise signal - signal1
    assert xtract_tonal.get_output()[1][0].data[0] == pytest.approx(-3.6770161386812106e-06)
    assert xtract_tonal.get_output()[1][0].data[99] == pytest.approx(1.8362156879447866e-06)
    # Get the noise signal - signal2
    assert xtract_tonal.get_output()[1][0].data[0] == pytest.approx(-3.6770161386812106e-06)
    assert xtract_tonal.get_output()[1][0].data[99] == pytest.approx(1.8362156879447866e-06)


def test_xtract_tonal_get_output_as_nparray(dpf_sound_test_server):
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute_in_container)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    # Setting tonal parameters
    params_tonal = GenericDataContainer()
    params_tonal.set_property("class_name", "Xtract_tonal_parameters")
    params_tonal.set_property("regularity", 1.0)
    params_tonal.set_property("maximum_slope", 750.0)
    params_tonal.set_property("minimum_duration", 1.0)
    params_tonal.set_property("intertonal_gap", 20.0)
    params_tonal.set_property("local_emergence", 15.0)
    params_tonal.set_property("fft_size", 8192)

    xtract_tonal = XtractTonal(bird_plus_idle_sig, params_tonal)
    xtract_tonal.process()

    assert xtract_tonal.get_output_as_nparray() is not None
    assert type(xtract_tonal.get_output_as_nparray()[0]) == np.ndarray
    assert type(xtract_tonal.get_output_as_nparray()[1]) == np.ndarray

    assert xtract_tonal.get_output_as_nparray()[0].shape == (156048,)
    assert np.min(xtract_tonal.get_output_as_nparray()[0]) == pytest.approx(-0.6828306913375854)
    assert np.max(xtract_tonal.get_output_as_nparray()[0]) == pytest.approx(0.794617772102356)

    assert xtract_tonal.get_output_as_nparray()[0][0] == pytest.approx(3.6770161386812106e-06)
    assert xtract_tonal.get_output_as_nparray()[0][1] == pytest.approx(1.8551201037553255e-06)

    assert xtract_tonal.get_output_as_nparray()[1].shape == (156048,)
    assert xtract_tonal.get_output_as_nparray()[1][0] == pytest.approx(-3.6770161386812106e-06)
    assert xtract_tonal.get_output_as_nparray()[1][99] == pytest.approx(1.8362156879447866e-06)


def test_xtract_tonal_get_output_fc_as_nparray(dpf_sound_test_server):
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute_in_container)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    # Setting tonal parameters
    params_tonal = GenericDataContainer()
    params_tonal.set_property("class_name", "Xtract_tonal_parameters")
    params_tonal.set_property("regularity", 1.0)
    params_tonal.set_property("maximum_slope", 750.0)
    params_tonal.set_property("minimum_duration", 1.0)
    params_tonal.set_property("intertonal_gap", 20.0)
    params_tonal.set_property("local_emergence", 15.0)
    params_tonal.set_property("fft_size", 8192)

    fc_bird_plus_idle = FieldsContainer()
    fc_bird_plus_idle.labels = ["channel"]
    fc_bird_plus_idle.add_field({"channel": 0}, bird_plus_idle_sig)
    fc_bird_plus_idle.add_field({"channel": 1}, bird_plus_idle_sig)

    xtract_tonal = XtractTonal(fc_bird_plus_idle, params_tonal)
    xtract_tonal.process()

    # Type of output tonal signals. np.array
    assert type(xtract_tonal.get_output_as_nparray()[0]) == np.ndarray
    assert type(xtract_tonal.get_output_as_nparray()[1]) == np.ndarray


def test_extract_tonal_setters(dpf_sound_test_server):
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute_in_container)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    # Setting tonal parameters
    params_tonal = GenericDataContainer()
    params_tonal.set_property("class_name", "Xtract_tonal_parameters")
    params_tonal.set_property("regularity", 1.0)
    params_tonal.set_property("maximum_slope", 750.0)
    params_tonal.set_property("minimum_duration", 1.0)
    params_tonal.set_property("intertonal_gap", 20.0)
    params_tonal.set_property("local_emergence", 15.0)
    params_tonal.set_property("fft_size", 8192)

    xtract_tonal = XtractTonal(bird_plus_idle_sig, params_tonal)

    assert xtract_tonal.input_signal is not None
    xtract_tonal.input_signal = None
    assert xtract_tonal.input_signal is None

    assert xtract_tonal.input_parameters is not None
    xtract_tonal.input_parameters = None
    assert xtract_tonal.input_parameters is None


@patch("matplotlib.pyplot.show")
def test_xtract_tonal_plot_output(mock_show, dpf_sound_test_server):
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute_in_container)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    # Setting tonal parameters
    params_tonal = GenericDataContainer()
    params_tonal.set_property("class_name", "Xtract_tonal_parameters")
    params_tonal.set_property("regularity", 1.0)
    params_tonal.set_property("maximum_slope", 750.0)
    params_tonal.set_property("minimum_duration", 1.0)
    params_tonal.set_property("intertonal_gap", 20.0)
    params_tonal.set_property("local_emergence", 15.0)
    params_tonal.set_property("fft_size", 8192)

    xtract_tonal = XtractTonal(bird_plus_idle_sig, params_tonal)
    xtract_tonal.process()

    xtract_tonal.plot()


@patch("matplotlib.pyplot.show")
def test_xtract_tonal_plot_output_fc(mock_show, dpf_sound_test_server):
    wav_bird_plus_idle = LoadWav(pytest.data_path_flute_in_container)
    wav_bird_plus_idle.process()

    bird_plus_idle_sig = wav_bird_plus_idle.get_output()[0]

    # Setting tonal parameters
    params_tonal = GenericDataContainer()
    params_tonal.set_property("class_name", "Xtract_tonal_parameters")
    params_tonal.set_property("regularity", 1.0)
    params_tonal.set_property("maximum_slope", 750.0)
    params_tonal.set_property("minimum_duration", 1.0)
    params_tonal.set_property("intertonal_gap", 20.0)
    params_tonal.set_property("local_emergence", 15.0)
    params_tonal.set_property("fft_size", 8192)

    fc_bird_plus_idle = FieldsContainer()
    fc_bird_plus_idle.labels = ["channel"]
    fc_bird_plus_idle.add_field({"channel": 0}, bird_plus_idle_sig)
    fc_bird_plus_idle.add_field({"channel": 1}, bird_plus_idle_sig)

    xtract_tonal = XtractTonal(fc_bird_plus_idle, params_tonal)
    xtract_tonal.process()

    xtract_tonal.plot()
