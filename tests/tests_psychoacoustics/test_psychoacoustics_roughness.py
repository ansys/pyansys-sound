from unittest.mock import patch

from ansys.dpf.core import Field, FieldsContainer
import numpy as np
import pytest

from ansys.dpf.sound.psychoacoustics import Roughness
from ansys.dpf.sound.pydpf_sound import PyDpfSoundException, PyDpfSoundWarning
from ansys.dpf.sound.signal_utilities import LoadWav

EXP_ROUGHNESS_1 = 0.5495809316635132
EXP_ROUGHNESS_2 = 0.20937225222587585
EXP_SPECIFIC_ROUGHNESS_1_0 = 0.0018477396806702018
EXP_SPECIFIC_ROUGHNESS_1_9 = 0.0060088788159191618
EXP_SPECIFIC_ROUGHNESS_1_40 = 0.062388259917497635
EXP_SPECIFIC_ROUGHNESS_2_15 = 0.03811583295464516
EXP_SPECIFIC_ROUGHNESS_2_17 = 0.18448638916015625
EXP_SPECIFIC_ROUGHNESS_2_40 = 0.0
EXP_BARK_0 = 0.5
EXP_BARK_9 = 5.0
EXP_BARK_40 = 20.5
EXP_FREQ_0 = 56.417020507724274
EXP_FREQ_9 = 498.9473684210526
EXP_FREQ_40 = 6875.975124656844


@pytest.mark.dependency()
def test_roughness_instantiation(dpf_sound_test_server):
    roughness_computer = Roughness()
    assert roughness_computer != None


@pytest.mark.dependency(depends=["test_roughness_instantiation"])
def test_roughness_process(dpf_sound_test_server):
    roughness_computer = Roughness()

    # No signal -> error
    with pytest.raises(
        PyDpfSoundException,
        match="No signal for roughness computation. Use Roughness.signal.",
    ):
        roughness_computer.process()

    # Get a signal
    wav_loader = LoadWav(pytest.data_path_rough_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal as field container
    roughness_computer.signal = fc
    # Compute: no error
    roughness_computer.process()

    # Set signal as field
    roughness_computer.signal = fc[0]
    # Compute: no error
    roughness_computer.process()


@pytest.mark.dependency(depends=["test_roughness_process"])
def test_roughness_get_output(dpf_sound_test_server):
    roughness_computer = Roughness()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_rough_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Roughness not calculated yet -> warning
    with pytest.warns(
        PyDpfSoundWarning,
        match="Output has not been processed yet, use Roughness.process().",
    ):
        output = roughness_computer.get_output()
    assert output == None

    # Set signal
    roughness_computer.signal = fc

    # Compute
    roughness_computer.process()

    (roughness, specific_roughness) = roughness_computer.get_output()
    assert type(roughness) == FieldsContainer
    assert roughness != None
    assert type(specific_roughness) == FieldsContainer
    assert specific_roughness != None


@pytest.mark.dependency(depends=["test_roughness_process"])
def test_roughness_get_roughness(dpf_sound_test_server):
    roughness_computer = Roughness()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_rough_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Roughness not calculated yet -> warning
    with pytest.warns(
        PyDpfSoundWarning,
        match="Output has not been processed yet, use Roughness.process().",
    ):
        output = roughness_computer.get_roughness()
    assert output == None

    # Set signal as a field
    roughness_computer.signal = fc[0]

    # Compute
    roughness_computer.process()

    # Request second channel's roughness while signal is a field (mono) -> error
    with pytest.raises(
        PyDpfSoundException, match="Specified channel index \\(1\\) does not exist."
    ):
        roughness = roughness_computer.get_roughness(1)

    roughness = roughness_computer.get_roughness(0)
    assert type(roughness) == np.float64
    assert roughness == pytest.approx(EXP_ROUGHNESS_1)

    # Set signal as a fields container
    roughness_computer.signal = fc

    # Compute
    roughness_computer.process()

    # Request second channel's roughness while signal is mono -> error
    with pytest.raises(
        PyDpfSoundException, match="Specified channel index \\(1\\) does not exist."
    ):
        roughness = roughness_computer.get_roughness(1)

    roughness = roughness_computer.get_roughness(0)
    assert type(roughness) == np.float64
    assert roughness == pytest.approx(EXP_ROUGHNESS_1)

    # Add a second signal in the fields container
    # Note: No need to re-assign the signal property, as fc is simply an alias for it
    wav_loader = LoadWav(pytest.data_path_rough_tone_in_container)
    wav_loader.process()
    fc.add_field({"channel_number": 1}, wav_loader.get_output()[0])

    # Compute again
    roughness_computer.process()

    roughness = roughness_computer.get_roughness(1)
    assert type(roughness) == np.float64
    assert roughness == pytest.approx(EXP_ROUGHNESS_2)


@pytest.mark.dependency(depends=["test_roughness_process"])
def test_roughness_get_specific_roughness(dpf_sound_test_server):
    roughness_computer = Roughness()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_rough_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Roughness not calculated yet -> warning
    with pytest.warns(
        PyDpfSoundWarning,
        match="Output has not been processed yet, use Roughness.process().",
    ):
        output = roughness_computer.get_specific_roughness()
    assert output == None

    # Set signal
    roughness_computer.signal = fc

    # Compute
    roughness_computer.process()

    specific_roughness = roughness_computer.get_specific_roughness()
    assert type(specific_roughness) == np.ndarray
    assert len(specific_roughness) == 47
    assert specific_roughness[0] == pytest.approx(EXP_SPECIFIC_ROUGHNESS_1_0)
    assert specific_roughness[9] == pytest.approx(EXP_SPECIFIC_ROUGHNESS_1_9)
    assert specific_roughness[40] == pytest.approx(EXP_SPECIFIC_ROUGHNESS_1_40)

    # Add a second signal in the fields container
    # Note: No need to re-assign the signal property, as fc is simply an alias for it
    wav_loader = LoadWav(pytest.data_path_rough_tone_in_container)
    wav_loader.process()
    fc.add_field({"channel_number": 1}, wav_loader.get_output()[0])

    # Compute again
    roughness_computer.process()

    specific_roughness = roughness_computer.get_specific_roughness(1)
    assert type(specific_roughness) == np.ndarray
    assert len(specific_roughness) == 47
    assert specific_roughness[15] == pytest.approx(EXP_SPECIFIC_ROUGHNESS_2_15)
    assert specific_roughness[17] == pytest.approx(EXP_SPECIFIC_ROUGHNESS_2_17)
    assert specific_roughness[40] == pytest.approx(EXP_SPECIFIC_ROUGHNESS_2_40)


@pytest.mark.dependency(depends=["test_roughness_process"])
def test_roughness_get_bark_band_indexes(dpf_sound_test_server):
    roughness_computer = Roughness()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_rough_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Roughness not calculated yet -> warning
    with pytest.warns(
        PyDpfSoundWarning,
        match="Output has not been processed yet, use Roughness.process().",
    ):
        output = roughness_computer.get_bark_band_indexes()
    assert output == None

    # Set signal as a fields container
    roughness_computer.signal = fc

    # Compute
    roughness_computer.process()

    bark_band_indexes = roughness_computer.get_bark_band_indexes()
    assert type(bark_band_indexes) == np.ndarray
    assert len(bark_band_indexes) == 47
    assert bark_band_indexes[0] == pytest.approx(EXP_BARK_0)
    assert bark_band_indexes[9] == pytest.approx(EXP_BARK_9)
    assert bark_band_indexes[40] == pytest.approx(EXP_BARK_40)

    # Set signal as a field
    roughness_computer.signal = fc[0]

    # Compute
    roughness_computer.process()

    bark_band_indexes = roughness_computer.get_bark_band_indexes()
    assert type(bark_band_indexes) == np.ndarray
    assert len(bark_band_indexes) == 47
    assert bark_band_indexes[0] == pytest.approx(EXP_BARK_0)
    assert bark_band_indexes[9] == pytest.approx(EXP_BARK_9)
    assert bark_band_indexes[40] == pytest.approx(EXP_BARK_40)


@pytest.mark.dependency(depends=["test_roughness_get_bark_band_indexes"])
def test_roughness_get_bark_band_frequencies(dpf_sound_test_server):
    roughness_computer = Roughness()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_rough_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    roughness_computer.signal = fc

    # Compute
    roughness_computer.process()

    bark_band_frequencies = roughness_computer.get_bark_band_frequencies()
    assert type(bark_band_frequencies) == np.ndarray
    assert len(bark_band_frequencies) == 47
    assert bark_band_frequencies[0] == pytest.approx(EXP_FREQ_0)
    assert bark_band_frequencies[9] == pytest.approx(EXP_FREQ_9)
    assert bark_band_frequencies[40] == pytest.approx(EXP_FREQ_40)


@pytest.mark.dependency(depends=["test_roughness_process"])
def test_roughness_get_output_as_nparray_from_fields_container(dpf_sound_test_server):
    roughness_computer = Roughness()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_rough_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Roughness not calculated yet -> warning
    with pytest.warns(
        PyDpfSoundWarning,
        match="Output has not been processed yet, use Roughness.process().",
    ):
        output = roughness_computer.get_output_as_nparray()
    assert output == None

    # Set signal
    roughness_computer.signal = fc

    # Compute
    roughness_computer.process()

    (roughness, specific_roughness) = roughness_computer.get_output_as_nparray()
    assert type(roughness) == np.ndarray
    assert len(roughness) == 1
    assert roughness[0] == pytest.approx(EXP_ROUGHNESS_1)
    assert type(specific_roughness) == np.ndarray
    assert len(specific_roughness) == 47
    assert specific_roughness[0] == pytest.approx(EXP_SPECIFIC_ROUGHNESS_1_0)
    assert specific_roughness[9] == pytest.approx(EXP_SPECIFIC_ROUGHNESS_1_9)
    assert specific_roughness[40] == pytest.approx(EXP_SPECIFIC_ROUGHNESS_1_40)


@pytest.mark.dependency(depends=["test_roughness_process"])
def test_roughness_get_output_as_nparray_from_field(dpf_sound_test_server):
    roughness_computer = Roughness()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_rough_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    roughness_computer.signal = fc[0]

    # Compute
    roughness_computer.process()

    (roughness, specific_roughness) = roughness_computer.get_output_as_nparray()
    assert type(roughness) == np.ndarray
    assert len(roughness) == 1
    assert roughness[0] == pytest.approx(EXP_ROUGHNESS_1)
    assert type(specific_roughness) == np.ndarray
    assert len(specific_roughness) == 47
    assert specific_roughness[0] == pytest.approx(EXP_SPECIFIC_ROUGHNESS_1_0)
    assert specific_roughness[9] == pytest.approx(EXP_SPECIFIC_ROUGHNESS_1_9)
    assert specific_roughness[40] == pytest.approx(EXP_SPECIFIC_ROUGHNESS_1_40)


@patch("matplotlib.pyplot.show")
@pytest.mark.dependency(depends=["test_roughness_process"])
def test_roughness_plot_from_fields_container(mock_show, dpf_sound_test_server):
    roughness_computer = Roughness()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_rough_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    roughness_computer.signal = fc

    # Roughness not computed yet -> error
    with pytest.raises(
        PyDpfSoundException,
        match="Output has not been processed yet, use Roughness.process().",
    ):
        roughness_computer.plot()

    # Compute
    roughness_computer.process()

    # Plot
    roughness_computer.plot()

    # Add a second signal in the fields container
    # Note: No need to re-assign the signal property, as fc is simply an alias for it
    wav_loader = LoadWav(pytest.data_path_rough_tone_in_container)
    wav_loader.process()
    fc.add_field({"channel_number": 1}, wav_loader.get_output()[0])

    # Compute
    roughness_computer.process()

    # Plot
    roughness_computer.plot()


@patch("matplotlib.pyplot.show")
@pytest.mark.dependency(depends=["test_roughness_process"])
def test_roughness_plot_from_field(mock_show, dpf_sound_test_server):
    roughness_computer = Roughness()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_rough_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    roughness_computer.signal = fc[0]

    # Compute
    roughness_computer.process()

    # Plot
    roughness_computer.plot()


@pytest.mark.dependency(depends=["test_roughness_instantiation"])
def test_roughness_set_get_signal(dpf_sound_test_server):
    roughness_computer = Roughness()
    fc = FieldsContainer()
    fc.labels = ["channel"]
    f = Field()
    f.data = 42 * np.ones(3)
    fc.add_field({"channel": 0}, f)
    fc.name = "testField"
    roughness_computer.signal = fc
    fc_from_get = roughness_computer.signal

    assert fc_from_get.name == "testField"
    assert len(fc_from_get) == 1
    assert fc_from_get[0].data[0, 2] == 42
