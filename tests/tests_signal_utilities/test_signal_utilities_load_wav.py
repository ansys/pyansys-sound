import numpy as np
import pytest

from ansys.dpf.sound.signal_utilities import LoadWav


@pytest.mark.dependency()
def test_load_wav_instantiation(dpf_sound_test_server):
    wav_loader = LoadWav()
    assert wav_loader != None


@pytest.mark.dependency(depends=["test_load_wav_instantiation"])
def test_load_wav_compute(dpf_sound_test_server):
    # Should not return an error
    wav_loader_good = LoadWav(pytest.data_path_flute_in_container)
    wav_loader_good.compute()

    # Should return an error
    wav_loader_bad = LoadWav()

    with pytest.raises(RuntimeError) as excinfo:
        wav_loader_bad.compute()
    assert str(excinfo.value) == "Path for loading wav file is not specified. Use LoadWav.set_path."


@pytest.mark.dependency(depends=["test_load_wav_compute"])
def test_load_wav_get_output(dpf_sound_test_server):
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.compute()

    # Loading a wav signal using load_wav_signal
    fc = wav_loader.get_output()

    # Extracting data
    data = fc[0].data

    # Checking data size and some random samples
    assert len(data) == 156048
    assert data[10] == 0.0
    assert data[1000] == 6.103515625e-05
    assert data[10000] == 0.0308837890625
    assert data[136047] == -0.084686279296875


@pytest.mark.dependency(depends=["test_load_wav_compute"])
def test_load_wav_get_output_as_nparray(dpf_sound_test_server):
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.compute()

    # Loading a wav signal using load_wav_signal
    np_arr = wav_loader.get_output_as_nparray()

    # Checking data size and some random samples
    assert len(np_arr) == 156048
    assert np_arr[10] == 0.0
    assert np_arr[1000] == 6.103515625e-05
    assert np_arr[10000] == 0.0308837890625
    assert np_arr[136047] == -0.084686279296875

    # Tests with a stereo signal
    wav_loader_stereo = LoadWav(pytest.data_path_white_noise_in_container)
    wav_loader_stereo.compute()

    # Loading a wav signal using load_wav_signal
    np_arr = wav_loader_stereo.get_output_as_nparray()

    assert np.shape(np_arr) == (480000, 2)
    assert np_arr[1000][1] == 0.0169677734375
    assert np_arr[10000][1] == -0.27001953125
    assert np_arr[100000][1] == -0.0509033203125


@pytest.mark.dependency(depends=["test_load_wav_instantiation"])
def test_load_wav_get_set_path(dpf_sound_test_server):
    wav_loader = LoadWav()
    wav_loader.set_path(pytest.data_path_flute_in_container)
    assert wav_loader.get_path() == pytest.data_path_flute_in_container
