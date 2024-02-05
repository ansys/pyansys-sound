import pytest

from ansys.dpf.sound.sound_helpers import load_wav_signal


def test_load_wav_file(dpf_sound_test_server):
    # Loading a wav signal using load_wav_signal
    fc = load_wav_signal(pytest.data_path_flute_in_container)

    # Extracting data
    data = fc[0].data

    # Checking data size and some random samples
    assert len(data) == 156048
    assert data[10] == 0.0
    assert data[1000] == 6.103515625e-05
    assert data[10000] == 0.0308837890625
    assert data[136047] == -0.084686279296875
