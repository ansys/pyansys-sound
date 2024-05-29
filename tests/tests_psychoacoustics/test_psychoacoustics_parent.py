import numpy as np
import pytest

from ansys.dpf.sound.psychoacoustics import PsychoacousticsParent
from ansys.dpf.sound.pydpf_sound import PyDpfSoundException


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
            bark_band_indexes=np.array(-1)
        )

    # Check output for some valid indexes
    bark_band_indexes = np.array(0, 0.1, 1, 6, 8.5, 15.3, 24)
    bark_band_frequencies = psychoacoustics_parent._convert_bark_to_hertz(
        bark_band_indexes=bark_band_indexes
    )
    assert type(bark_band_frequencies) == np.ndarray
    assert len(bark_band_frequencies) == len(bark_band_indexes)
    assert bark_band_frequencies[0] == pytest.approx(12.764378478664192)
    assert bark_band_frequencies[1] == pytest.approx(21.33995918005147)
    assert bark_band_frequencies[4] == pytest.approx(975.1181102362203)
    assert bark_band_frequencies[6] == pytest.approx(15334.573030003306)
