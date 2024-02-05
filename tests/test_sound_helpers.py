import pytest

from ansys.dpf.sound.sound_helpers import load_wav_signal, write_wav_signal


@pytest.mark.dependency()
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


@pytest.mark.dependency(depends=["test_load_wav_file"])
def test_write_wav_file(dpf_sound_test_server):
    input_path = pytest.data_path_flute_in_container

    # Loading a wav signal using load_wav_signal
    fc_original_signal = load_wav_signal(input_path)

    # Writing the signal in memory
    output_path = input_path[:-4] + "_modified.wav"
    write_wav_signal(output_path, fc_original_signal, "int16")

    # Re loading again
    fc_reloaded_signal = load_wav_signal(output_path)

    # Checking that the written signal has the same properties has the original one
    assert len(fc_reloaded_signal[0].data) == len(fc_original_signal[0].data)
    assert fc_reloaded_signal[0].data[10] == fc_original_signal[0].data[10]
    assert fc_reloaded_signal[0].data[1000] == fc_original_signal[0].data[1000]
    assert fc_reloaded_signal[0].data[10000] == fc_original_signal[0].data[10000]
    assert fc_reloaded_signal[0].data[136047] == fc_original_signal[0].data[136047]
