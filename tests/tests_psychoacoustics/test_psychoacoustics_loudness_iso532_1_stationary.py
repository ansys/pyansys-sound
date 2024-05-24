from unittest.mock import patch

from ansys.dpf.core import Field, FieldsContainer
import numpy as np
import pytest

from ansys.dpf.sound.psychoacoustics import LoudnessISO532_1_Stationary
from ansys.dpf.sound.pydpf_sound import PyDpfSoundException, PyDpfSoundWarning
from ansys.dpf.sound.signal_utilities import LoadWav


@pytest.mark.dependency()
def test_loudness_iso532_1_stationary_instantiation(dpf_sound_test_server):
    loudness_computer = LoudnessISO532_1_Stationary()
    assert loudness_computer != None


@pytest.mark.dependency(depends=["test_loudness_iso532_1_stationary_instantiation"])
def test_loudness_iso532_1_stationary_process(dpf_sound_test_server):
    loudness_computer = LoudnessISO532_1_Stationary()

    # No signal -> error
    with pytest.raises(
        PyDpfSoundException,
        match="No signal for loudness computation. Use LoudnessISO532_1_Stationary.signal.",
    ):
        loudness_computer.process()

    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal as field container
    loudness_computer.signal = fc
    # Compute: no error
    loudness_computer.process()

    # Set signal as field
    loudness_computer.signal = fc[0]
    # Compute: no error
    loudness_computer.process()


@pytest.mark.dependency(depends=["test_loudness_iso532_1_stationary_process"])
def test_loudness_iso532_1_stationary_get_output(dpf_sound_test_server):
    loudness_computer = LoudnessISO532_1_Stationary()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    loudness_computer.signal = fc

    # Loudness not calculated yet -> warning
    with pytest.warns(
        PyDpfSoundWarning,
        match="Output has not been processed yet, use LoudnessISO532_1_Stationary.process().",
    ):
        output = loudness_computer.get_output()
    assert output == None

    # Compute
    loudness_computer.process()

    (loudness_sone, loudness_level_phon, specific_loudness) = loudness_computer.get_output()
    assert type(loudness_sone) == FieldsContainer
    assert loudness_sone != None
    assert type(loudness_level_phon) == FieldsContainer
    assert loudness_level_phon != None
    assert type(specific_loudness) == FieldsContainer
    assert specific_loudness != None


@pytest.mark.dependency(depends=["test_loudness_iso532_1_stationary_process"])
def test_loudness_iso532_1_stationary_get_loudness_sone(dpf_sound_test_server):
    loudness_computer = LoudnessISO532_1_Stationary()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal as a field
    loudness_computer.signal = fc[0]

    # Loudness not calculated yet -> warning
    with pytest.warns(
        PyDpfSoundWarning,
        match="Output has not been processed yet, use LoudnessISO532_1_Stationary.process().",
    ):
        output = loudness_computer.get_loudness_sone()
    assert output == None

    # Compute
    loudness_computer.process()

    # Request second channel's loudness while signal is a field (mono) -> error
    with pytest.raises(
        PyDpfSoundException, match="Specified channel index \\(1\\) does not exist."
    ):
        loudness_sone = loudness_computer.get_loudness_sone(1)

    loudness_sone = loudness_computer.get_loudness_sone(0)
    assert type(loudness_sone) == np.float64
    assert loudness_sone == pytest.approx(39.58000183105469)

    # Set signal as a fields container
    loudness_computer.signal = fc
    # Compute
    loudness_computer.process()

    loudness_sone = loudness_computer.get_loudness_sone(0)
    assert type(loudness_sone) == np.float64
    assert loudness_sone == pytest.approx(39.58000183105469)

    # Add a second signal in the fields container
    # Note: No need to re-assign the signal property, as fc is simply an alias for it
    wav_loader = LoadWav(pytest.data_path_flute2_in_container)
    wav_loader.process()
    fc.add_field({"channel_number": 1}, wav_loader.get_output()[0])

    # Compute again
    loudness_computer.process()

    loudness_sone = loudness_computer.get_loudness_sone(0)
    assert type(loudness_sone) == np.float64
    assert loudness_sone == pytest.approx(39.58000183105469)
    loudness_sone = loudness_computer.get_loudness_sone(1)
    assert type(loudness_sone) == np.float64
    assert loudness_sone == pytest.approx(16.18000030517578)


@pytest.mark.dependency(depends=["test_loudness_iso532_1_stationary_process"])
def test_loudness_iso532_1_stationary_get_loudness_level_phon(dpf_sound_test_server):
    loudness_computer = LoudnessISO532_1_Stationary()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    loudness_computer.signal = fc

    # Loudness not calculated yet -> warning
    with pytest.warns(
        PyDpfSoundWarning,
        match="Output has not been processed yet, use LoudnessISO532_1_Stationary.process().",
    ):
        output = loudness_computer.get_loudness_level_phon()
    assert output == None

    # Compute
    loudness_computer.process()

    loudness_level_phon = loudness_computer.get_loudness_level_phon()
    assert type(loudness_level_phon) == np.float64
    assert loudness_level_phon == pytest.approx(93.0669937133789)


@pytest.mark.dependency(depends=["test_loudness_iso532_1_stationary_process"])
def test_loudness_iso532_1_stationary_get_specific_loudness(dpf_sound_test_server):
    loudness_computer = LoudnessISO532_1_Stationary()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    loudness_computer.signal = fc

    # Loudness not calculated yet -> warning
    with pytest.warns(
        PyDpfSoundWarning,
        match="Output has not been processed yet, use LoudnessISO532_1_Stationary.process().",
    ):
        output = loudness_computer.get_specific_loudness()
    assert output == None

    # Compute
    loudness_computer.process()

    specific_loudness = loudness_computer.get_specific_loudness()
    assert type(specific_loudness) == np.ndarray
    assert len(specific_loudness) == 240
    assert specific_loudness[0] == pytest.approx(0.0)
    assert specific_loudness[9] == pytest.approx(0.15664348006248474)
    assert specific_loudness[40] == pytest.approx(1.3235466480255127)

    # Add a second signal in the fields container
    # Note: No need to re-assign the signal property, as fc is simply an alias for it
    wav_loader = LoadWav(pytest.data_path_flute2_in_container)
    wav_loader.process()
    fc.add_field({"channel_number": 1}, wav_loader.get_output()[0])

    # Compute again
    loudness_computer.process()

    specific_loudness = loudness_computer.get_specific_loudness(1)
    assert type(specific_loudness) == np.ndarray
    assert len(specific_loudness) == 240
    assert specific_loudness[0] == pytest.approx(0.0)
    assert specific_loudness[9] == pytest.approx(0.008895192295312881)
    assert specific_loudness[40] == pytest.approx(0.4043666124343872)


@pytest.mark.dependency(depends=["test_loudness_iso532_1_stationary_process"])
def test_loudness_iso532_1_stationary_get_bark_band_indexes(dpf_sound_test_server):
    loudness_computer = LoudnessISO532_1_Stationary()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal as a fields container
    loudness_computer.signal = fc

    # Loudness not calculated yet -> warning
    with pytest.warns(
        PyDpfSoundWarning,
        match="Output has not been processed yet, use LoudnessISO532_1_Stationary.process().",
    ):
        output = loudness_computer.get_bark_band_indexes()
    assert output == None

    # Compute
    loudness_computer.process()

    bark_band_indexes = loudness_computer.get_bark_band_indexes()
    assert type(bark_band_indexes) == np.ndarray
    assert len(bark_band_indexes) == 240
    assert bark_band_indexes[0] == pytest.approx(0.10000000149011612)
    assert bark_band_indexes[9] == pytest.approx(1.0000000149011612)
    assert bark_band_indexes[40] == pytest.approx(4.100000061094761)

    # Set signal as a field
    loudness_computer.signal = fc[0]
    # Compute
    loudness_computer.process()

    bark_band_indexes = loudness_computer.get_bark_band_indexes()
    assert type(bark_band_indexes) == np.ndarray
    assert len(bark_band_indexes) == 240
    assert bark_band_indexes[0] == pytest.approx(0.10000000149011612)
    assert bark_band_indexes[9] == pytest.approx(1.0000000149011612)
    assert bark_band_indexes[40] == pytest.approx(4.100000061094761)


@pytest.mark.dependency(depends=["test_loudness_iso532_1_stationary_get_bark_band_indexes"])
def test_loudness_iso532_1_stationary_get_bark_band_frequencies(dpf_sound_test_server):
    loudness_computer = LoudnessISO532_1_Stationary()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    loudness_computer.signal = fc
    # Compute
    loudness_computer.process()

    bark_band_frequencies = loudness_computer.get_bark_band_frequencies()
    assert type(bark_band_frequencies) == np.ndarray
    assert len(bark_band_frequencies) == 240
    assert bark_band_frequencies[0] == pytest.approx(21.33995930840456)
    assert bark_band_frequencies[9] == pytest.approx(102.08707043772274)
    assert bark_band_frequencies[40] == pytest.approx(400.79351405718324)


@pytest.mark.dependency(depends=["test_loudness_iso532_1_stationary_process"])
def test_loudness_iso532_1_stationary_get_output_as_nparray_from_fields_container(
    dpf_sound_test_server,
):
    loudness_computer = LoudnessISO532_1_Stationary()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    loudness_computer.signal = fc

    # Loudness not calculated yet -> warning
    with pytest.warns(
        PyDpfSoundWarning,
        match="Output has not been processed yet, use LoudnessISO532_1_Stationary.process().",
    ):
        output = loudness_computer.get_output_as_nparray()
    assert output == None

    # Compute
    loudness_computer.process()

    (
        loudness_sone,
        loudness_level_phon,
        specific_loudness,
    ) = loudness_computer.get_output_as_nparray()
    assert type(loudness_sone) == np.ndarray
    assert len(loudness_sone) == 1
    assert loudness_sone[0] == pytest.approx(39.58000183105469)
    assert type(loudness_level_phon) == np.ndarray
    assert len(loudness_level_phon) == 1
    assert loudness_level_phon[0] == pytest.approx(93.0669937133789)
    assert type(specific_loudness) == np.ndarray
    assert len(specific_loudness) == 240
    assert specific_loudness[0] == pytest.approx(0.0)
    assert specific_loudness[9] == pytest.approx(0.15664348006248474)
    assert specific_loudness[40] == pytest.approx(1.3235466480255127)


@pytest.mark.dependency(depends=["test_loudness_iso532_1_stationary_process"])
def test_loudness_iso532_1_stationary_get_output_as_nparray_from_field(dpf_sound_test_server):
    loudness_computer = LoudnessISO532_1_Stationary()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    loudness_computer.signal = fc[0]
    # Compute
    loudness_computer.process()

    (
        loudness_sone,
        loudness_level_phon,
        specific_loudness,
    ) = loudness_computer.get_output_as_nparray()
    assert type(loudness_sone) == np.ndarray
    assert len(loudness_sone) == 1
    assert loudness_sone[0] == pytest.approx(39.58000183105469)
    assert type(loudness_level_phon) == np.ndarray
    assert len(loudness_level_phon) == 1
    assert loudness_level_phon[0] == pytest.approx(93.0669937133789)
    assert type(specific_loudness) == np.ndarray
    assert len(specific_loudness) == 240
    assert specific_loudness[0] == pytest.approx(0.0)
    assert specific_loudness[9] == pytest.approx(0.15664348006248474)
    assert specific_loudness[40] == pytest.approx(1.3235466480255127)


@patch("matplotlib.pyplot.show")
@pytest.mark.dependency(depends=["test_loudness_iso532_1_stationary_process"])
def test_loudness_iso532_1_stationary_plot_from_fields_container(mock_show, dpf_sound_test_server):
    loudness_computer = LoudnessISO532_1_Stationary()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    loudness_computer.signal = fc

    # Loudness not computed yet -> error
    with pytest.raises(
        PyDpfSoundException,
        match="Output has not been processed yet, use LoudnessISO532_1_Stationary.process().",
    ):
        loudness_computer.plot()

    # Compute
    loudness_computer.process()

    # Plot
    loudness_computer.plot()

    # Add a second signal in the fields container
    # Note: No need to re-assign the signal property, as fc is simply an alias for it
    wav_loader = LoadWav(pytest.data_path_flute2_in_container)
    wav_loader.process()
    fc.add_field({"channel_number": 1}, wav_loader.get_output()[0])

    # Compute again
    loudness_computer.process()

    # Plot
    loudness_computer.plot()


@patch("matplotlib.pyplot.show")
@pytest.mark.dependency(depends=["test_loudness_iso532_1_stationary_process"])
def test_loudness_iso532_1_stationary_plot_from_field(mock_show, dpf_sound_test_server):
    loudness_computer = LoudnessISO532_1_Stationary()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    loudness_computer.signal = fc[0]
    # Compute
    loudness_computer.process()

    # Plot
    loudness_computer.plot()


@pytest.mark.dependency(depends=["test_loudness_iso532_1_stationary_instantiation"])
def test_loudness_iso532_1_stationary_set_get_signal(dpf_sound_test_server):
    loudness_computer = LoudnessISO532_1_Stationary()
    fc = FieldsContainer()
    fc.labels = ["channel"]
    f = Field()
    f.data = 42 * np.ones(3)
    fc.add_field({"channel": 0}, f)
    fc.name = "testField"
    loudness_computer.signal = fc
    fc_from_get = loudness_computer.signal

    assert fc_from_get.name == "testField"
    assert len(fc_from_get) == 1
    assert fc_from_get[0].data[0, 2] == 42
