import pytest

from ansys.dpf.sound.spectrogram_processing import SpectrogramProcessingParent


@pytest.mark.dependency()
def test_spectrogram_processing_parent_instanciate():
    pydpf_sound = SpectrogramProcessingParent()
    assert pydpf_sound != None
