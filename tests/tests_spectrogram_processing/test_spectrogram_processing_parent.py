from ansys.sound.core.spectrogram_processing import SpectrogramProcessingParent


def test_spectrogram_processing_parent_instanciate():
    pyansys_sound = SpectrogramProcessingParent()
    assert pyansys_sound != None
