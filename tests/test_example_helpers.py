from ansys.dpf.sound.examples_helpers import get_absolute_path_for_flute_wav


def test_data_path_flute_wav():
    p = get_absolute_path_for_flute_wav()
    assert p == "C:\\data\\flute.wav"