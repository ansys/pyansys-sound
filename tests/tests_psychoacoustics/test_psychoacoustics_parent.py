from ansys.dpf.sound.psychoacoustics.loudness_iso_532_1_stationary import (
    LoudnessISO532_1_Stationary,
)
from ansys.dpf.sound.pydpf_sound import PyDpfSoundException, PyDpfSoundWarning
from ansys.dpf.sound.signal_utilities.load_wav import LoadWav
import numpy as np
import pytest

from ansys.dpf.sound.psychoacoustics import PsychoacousticsParent


def test_psychoacoustics_parent_instantiation(dpf_sound_test_server):
    psychoacoustics_parent = PsychoacousticsParent()
    assert psychoacoustics_parent != None


def test_psychoacoustics_convert_bark_to_hertz(dpf_sound_test_server):
    psychoacoustics_parent = PsychoacousticsParent()

    # Invalid Bark band index -> error
    with pytest.raises(
        PyDpfSoundException, match="Specified Bark band indexes must be between 0.0 and 24.0 Bark."
    ):
        bark_band_frequencies = psychoacoustics_parent._convert_bark_to_hertz(
            bark_band_indexes=np.array([-1])
        )

    # Check output for some valid indexes
    bark_band_indexes = np.array([0, 0.1, 1, 6, 8.5, 15.3, 24])
    bark_band_frequencies = psychoacoustics_parent._convert_bark_to_hertz(
        bark_band_indexes=bark_band_indexes
    )
    assert type(bark_band_frequencies) == np.ndarray
    assert len(bark_band_frequencies) == len(bark_band_indexes)
    assert bark_band_frequencies[0] == pytest.approx(12.764378478664192)
    assert bark_band_frequencies[1] == pytest.approx(21.33995918005147)
    assert bark_band_frequencies[4] == pytest.approx(975.1181102362203)
    assert bark_band_frequencies[6] == pytest.approx(15334.573030003306)


def test_psychoacoustics_parent_check_channel_index(dpf_sound_test_server):
    # We need to instantiate either of the child classes (loudness here), otherwise we cannot
    # achieve complete test coverage of the method.
    loudness = LoudnessISO532_1_Stationary()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal as a field
    loudness.signal = fc[0]

    # Nothing computed -> false
    with pytest.warns(
        PyDpfSoundWarning,
        match="Output has not been processed yet, use LoudnessISO532_1_Stationary.process().",
    ):
        valid_status = loudness._check_channel_index(0)
    assert valid_status == False

    loudness.process()

    # Check unexisting channel (field case)
    with pytest.raises(
        PyDpfSoundException, match="Specified channel index \\(1\\) does not exist."
    ):
        loudness._check_channel_index(1)

    # Set signal as a fields container
    loudness.signal = fc
    loudness.process()

    # Check unexisting channel (fields container case)
    with pytest.raises(
        PyDpfSoundException, match="Specified channel index \\(1\\) does not exist."
    ):
        loudness._check_channel_index(1)

    # Check existing channel (0)
    assert loudness._check_channel_index(0) == True
