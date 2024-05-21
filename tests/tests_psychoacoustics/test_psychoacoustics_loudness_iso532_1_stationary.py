from unittest.mock import patch

from ansys.dpf.core import Field, FieldsContainer
import numpy as np
import pytest

from ansys.dpf.sound.psychoacoustics import Loudness_ISO532_1_stationary
from ansys.dpf.sound.pydpf_sound import PyDpfSoundException, PyDpfSoundWarning
from ansys.dpf.sound.signal_utilities import LoadWav


@pytest.mark.dependency()
def test_loudness_iso532_1_stationary_instantiation(dpf_sound_test_server):
    loudness_computer = Loudness_ISO532_1_stationary()
    assert loudness_computer != None


@pytest.mark.dependency(depends=["test_loudness_iso532_1_stationary_instantiation"])
def test_loudness_iso532_1_stationary_process(dpf_sound_test_server):
    loudness_computer = Loudness_ISO532_1_stationary()

    # No signal -> error
    with pytest.raises(
        PyDpfSoundException,
        match="No signal for loudness computation. Use Loudness_ISO532_1_stationary.signal.",
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
    loudness_computer = Loudness_ISO532_1_stationary()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Loudness not calculated yet -> warning
    with pytest.warns(
        PyDpfSoundWarning,
        match="Output has not been processed yet, use Loudness_ISO532_1_stationary.process().",
    ):
        output = loudness_computer.get_output()
    assert output == None

    # Set signal
    loudness_computer.signal = fc
    # Compute
    loudness_computer.process()

    (loudness_sone, loudness_level_phon, specific_loudness) = loudness_computer.get_output()
    assert loudness_sone != None
    assert loudness_level_phon != None
    assert specific_loudness != None


@pytest.mark.dependency(depends=["test_loudness_iso532_1_stationary_process"])
def test_loudness_iso532_1_stationary_get_loudness_sone(dpf_sound_test_server):
    loudness_computer = Loudness_ISO532_1_stationary()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Loudness not calculated yet -> warning
    with pytest.warns(
        PyDpfSoundWarning,
        match="Output has not been processed yet, use Loudness_ISO532_1_stationary.process().",
    ):
        output = loudness_computer.get_loudness_sone()
    assert output == None

    # Set signal as a field
    loudness_computer.signal = fc[0]
    # Compute
    loudness_computer.process()

    # Request second channel's loudness while signal is a field (mono) -> error
    with pytest.raises(
        PyDpfSoundException, match="Specified channel index \\(1\\) does not exist."
    ):
        loudness_sone = loudness_computer.get_loudness_sone(1)

    loudness_sone = loudness_computer.get_loudness_sone(0)
    assert loudness_sone == 39.58000183105469

    # Set signal as a fields container
    loudness_computer.signal = fc
    # Compute
    loudness_computer.process()

    loudness_sone = loudness_computer.get_loudness_sone(0)
    assert loudness_sone == 39.58000183105469

    wav_loader = LoadWav(pytest.data_path_flute2_in_container)
    wav_loader.process()

    # Store the second signal with the first one.
    fc_two_signals = fc
    fc_two_signals.add_field({"channel_number": 1}, wav_loader.get_output()[0])

    # Compute
    loudness_computer.process()

    loudness_sone = loudness_computer.get_loudness_sone(0)
    assert loudness_sone == 39.58000183105469
    loudness_sone = loudness_computer.get_loudness_sone(1)
    assert loudness_sone == 16.18000030517578


@pytest.mark.dependency(depends=["test_loudness_iso532_1_stationary_process"])
def test_loudness_iso532_1_stationary_get_loudness_level_phon(dpf_sound_test_server):
    loudness_computer = Loudness_ISO532_1_stationary()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Loudness not calculated yet -> warning
    with pytest.warns(
        PyDpfSoundWarning,
        match="Output has not been processed yet, use Loudness_ISO532_1_stationary.process().",
    ):
        output = loudness_computer.get_loudness_level_phon()
    assert output == None

    # Set signal
    loudness_computer.signal = fc
    # Compute
    loudness_computer.process()

    loudness_level_phon = loudness_computer.get_loudness_level_phon()
    assert loudness_level_phon == 93.0669937133789


@pytest.mark.dependency(depends=["test_loudness_iso532_1_stationary_process"])
def test_loudness_iso532_1_stationary_get_specific_loudness(dpf_sound_test_server):
    loudness_computer = Loudness_ISO532_1_stationary()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Loudness not calculated yet -> warning
    with pytest.warns(
        PyDpfSoundWarning,
        match="Output has not been processed yet, use Loudness_ISO532_1_stationary.process().",
    ):
        output = loudness_computer.get_specific_loudness()
    assert output == None

    # Set signal
    loudness_computer.signal = fc
    # Compute
    loudness_computer.process()

    specific_loudness = loudness_computer.get_specific_loudness()
    assert len(specific_loudness) == 240
    assert specific_loudness[0] == 0
    assert specific_loudness[9] == 0.15664348006248474
    assert specific_loudness[40] == 1.3235466480255127

    wav_loader = LoadWav(pytest.data_path_flute2_in_container)
    wav_loader.process()

    # Store the second signal with the first one.
    fc_two_signals = fc
    fc_two_signals.add_field({"channel_number": 1}, wav_loader.get_output()[0])

    # Compute
    loudness_computer.process()

    specific_loudness = loudness_computer.get_specific_loudness(1)
    assert len(specific_loudness) == 240
    assert specific_loudness[0] == 0
    assert specific_loudness[9] == 0.008895192295312881
    assert specific_loudness[40] == 0.4043666124343872


@pytest.mark.dependency(depends=["test_loudness_iso532_1_stationary_process"])
def test_loudness_iso532_1_stationary_get_bark_band_indexes(dpf_sound_test_server):
    loudness_computer = Loudness_ISO532_1_stationary()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Loudness not calculated yet -> warning
    with pytest.warns(
        PyDpfSoundWarning,
        match="Output has not been processed yet, use Loudness_ISO532_1_stationary.process().",
    ):
        output = loudness_computer.get_bark_band_indexes()
    assert output == None

    # Set signal as a fields container
    loudness_computer.signal = fc
    # Compute
    loudness_computer.process()

    bark_band_indexes = loudness_computer.get_bark_band_indexes()
    assert len(bark_band_indexes) == 240
    assert bark_band_indexes[0] == 0.10000000149011612
    assert bark_band_indexes[9] == 1.0000000149011612
    assert bark_band_indexes[40] == 4.100000061094761

    # Set signal as a field
    loudness_computer.signal = fc[0]
    # Compute
    loudness_computer.process()

    bark_band_indexes = loudness_computer.get_bark_band_indexes()
    assert len(bark_band_indexes) == 240
    assert bark_band_indexes[0] == 0.10000000149011612
    assert bark_band_indexes[9] == 1.0000000149011612
    assert bark_band_indexes[40] == 4.100000061094761


@pytest.mark.dependency(depends=["test_loudness_iso532_1_stationary_get_bark_band_indexes"])
def test_loudness_iso532_1_stationary_get_bark_band_frequencies(dpf_sound_test_server):
    loudness_computer = Loudness_ISO532_1_stationary()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    loudness_computer.signal = fc
    # Compute
    loudness_computer.process()

    bark_band_frequencies = loudness_computer.get_bark_band_frequencies()
    assert len(bark_band_frequencies) == 240
    assert bark_band_frequencies[0] == 21.33995930840456
    assert bark_band_frequencies[9] == 102.08707043772274
    assert bark_band_frequencies[40] == 400.79351405718324


@pytest.mark.dependency(depends=["test_loudness_iso532_1_stationary_process"])
def test_loudness_iso532_1_stationary_get_output_as_nparray_from_fields_container(
    dpf_sound_test_server,
):
    loudness_computer = Loudness_ISO532_1_stationary()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Loudness not calculated yet -> warning
    with pytest.warns(
        PyDpfSoundWarning,
        match="Output has not been processed yet, use Loudness_ISO532_1_stationary.process().",
    ):
        output = loudness_computer.get_output_as_nparray()
    assert output == None

    # Set signal
    loudness_computer.signal = fc
    # Compute
    loudness_computer.process()

    (
        loudness_sone,
        loudness_level_phon,
        specific_loudness,
    ) = loudness_computer.get_output_as_nparray()
    assert len(loudness_sone) == 1
    assert loudness_sone[0] == 39.58000183105469
    assert len(loudness_level_phon) == 1
    assert loudness_level_phon[0] == 93.0669937133789
    assert len(specific_loudness) == 240
    assert specific_loudness[0] == 0
    assert specific_loudness[9] == 0.15664348006248474
    assert specific_loudness[40] == 1.3235466480255127


@pytest.mark.dependency(depends=["test_loudness_iso532_1_stationary_process"])
def test_loudness_iso532_1_stationary_get_output_as_nparray_from_field(dpf_sound_test_server):
    loudness_computer = Loudness_ISO532_1_stationary()
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
    assert len(loudness_sone) == 1
    assert loudness_sone[0] == 39.58000183105469
    assert len(loudness_level_phon) == 1
    assert loudness_level_phon[0] == 93.0669937133789
    assert len(specific_loudness) == 240
    assert specific_loudness[0] == 0
    assert specific_loudness[9] == 0.15664348006248474
    assert specific_loudness[40] == 1.3235466480255127


@patch("matplotlib.pyplot.show")
@pytest.mark.dependency(depends=["test_loudness_iso532_1_stationary_process"])
def test_loudness_iso532_1_stationary_plot_from_fields_container(mock_show, dpf_sound_test_server):
    loudness_computer = Loudness_ISO532_1_stationary()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    loudness_computer.signal = fc

    # Loudness not computed yet -> error
    with pytest.raises(
        PyDpfSoundException,
        match="Output has not been processed yet, use Loudness_ISO532_1_stationary.process().",
    ):
        loudness_computer.plot()

    # Compute
    loudness_computer.process()

    # Plot
    loudness_computer.plot()

    # Add a second signal in the fields container
    wav_loader = LoadWav(pytest.data_path_flute2_in_container)
    wav_loader.process()
    fc.add_field({"channel_number": 1}, wav_loader.get_output()[0])

    # Compute
    loudness_computer.process()

    # Plot
    loudness_computer.plot()


@patch("matplotlib.pyplot.show")
@pytest.mark.dependency(depends=["test_loudness_iso532_1_stationary_process"])
def test_loudness_iso532_1_stationary_plot_from_field(mock_show, dpf_sound_test_server):
    loudness_computer = Loudness_ISO532_1_stationary()
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
    loudness_computer = Loudness_ISO532_1_stationary()
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
