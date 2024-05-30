import pytest

from ansys.sound.core.spectrogram_processing import SpectrogramProcessingParent


@pytest.mark.dependency()
def test_spectrogram_processing_parent_instanciate():
    pyansys_sound = SpectrogramProcessingParent()
    assert pyansys_sound != None
