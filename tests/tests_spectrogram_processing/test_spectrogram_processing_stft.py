from ansys.dpf.core import Field, FieldsContainer
import numpy as np
import pytest

from ansys.dpf.sound.pydpf_sound import PyDpfSoundException
from ansys.dpf.sound.spectrogram_processing import Stft


@pytest.mark.dependency()
def test_stft_instantiation(dpf_sound_test_server):
    stft = Stft()
    assert stft != None


# @pytest.mark.dependency(depends=["test_stft_instantiation"])
# def test_stft_process(dpf_sound_test_server):
#     resampler = Resample()
#     wav_loader = LoadWav(pytest.data_path_flute_in_container)

#     # Error 1
#     with pytest.raises(PyDpfSoundException) as excinfo:
#         resampler.process()
#     assert str(excinfo.value) == "No signal to resample. Use Resample.set_signal()."

#     wav_loader.process()
#     fc = wav_loader.get_output()

#     # Testing input fields container (no error expected)
#     resampler.signal = fc
#     resampler.process()

#     # Testing input field (no error expected)
#     resampler.signal = fc[0]
#     resampler.process()


# @pytest.mark.dependency(depends=["test_stft_process"])
# def test_stft_get_output(dpf_sound_test_server):
#     wav_loader = LoadWav(pytest.data_path_flute_in_container)
#     wav_loader.process()
#     fc_signal = wav_loader.get_output()
#     resampler = Resample(signal=fc_signal, new_sampling_frequency=88100.0)

#     with pytest.warns(
#         PyDpfSoundWarning, match="Output has not been yet processed, use Resample.process()."
#     ):
#         fc_out = resampler.get_output()

#     resampler.process()
#     fc_out = resampler.get_output()

#     assert len(fc_out) == 1

#     resampler.signal = fc_signal[0]
#     resampler.process()
#     f_out = resampler.get_output()

#     assert len(f_out.data) == 311743
#     assert f_out.data[1000] == 2.9065033686492825e-06
#     assert f_out.data[3456] == -0.0007385587086901069
#     assert f_out.data[30000] == 0.02302781119942665
#     assert f_out.data[60000] == -0.4175410866737366


# @pytest.mark.dependency(depends=["test_stft_process"])
# def test_stft_get_output_as_np_array(dpf_sound_test_server):
#     wav_loader = LoadWav(pytest.data_path_flute_in_container)
#     wav_loader.process()
#     fc_signal = wav_loader.get_output()
#     resampler = Resample(signal=fc_signal[0], new_sampling_frequency=88100.0)
#     resampler.process()
#     out_arr = resampler.get_output_as_nparray()

#     assert len(out_arr) == 311743
#     assert out_arr[1000] == 2.9065033686492825e-06
#     assert out_arr[3456] == -0.0007385587086901069
#     assert out_arr[30000] == 0.02302781119942665
#     assert out_arr[60000] == -0.4175410866737366

#     resampler.signal = fc_signal
#     resampler.process()
#     out_arr = resampler.get_output_as_nparray()

#     assert len(out_arr) == 311743
#     assert out_arr[1000] == 2.9065033686492825e-06
#     assert out_arr[3456] == -0.0007385587086901069
#     assert out_arr[30000] == 0.02302781119942665
#     assert out_arr[60000] == -0.4175410866737366


@pytest.mark.dependency(depends=["test_stft_instantiation"])
def test_stft_set_get_signal(dpf_sound_test_server):
    stft = Stft()
    fc = FieldsContainer()
    fc.labels = ["channel"]
    f = Field()
    f.data = 42 * np.ones(3)
    fc.add_field({"channel": 0}, f)
    fc.name = "testField"
    stft.signal = fc
    fc_from_get = stft.signal

    assert fc_from_get.name == "testField"
    assert len(fc_from_get) == 1
    assert fc_from_get[0].data[0, 2] == 42


@pytest.mark.dependency(depends=["test_stft_instantiation"])
def test_stft_set_get_fft_size(dpf_sound_test_server):
    stft = Stft()

    # Error
    with pytest.raises(PyDpfSoundException) as excinfo:
        stft.fft_size = -12.0
    assert str(excinfo.value) == "Fft size must be greater than 0.0."

    stft.fft_size = 1234.0
    assert stft.fft_size == 1234.0


@pytest.mark.dependency(depends=["test_stft_instantiation"])
def test_stft_set_get_window_overlap(dpf_sound_test_server):
    stft = Stft()

    # Error
    with pytest.raises(PyDpfSoundException) as excinfo:
        stft.window_overlap = -12.0
    assert str(excinfo.value) == "Window overlap must be between 0.0 and 1.0."

    stft.window_overlap = 0.5
    assert stft.window_overlap == 0.5


@pytest.mark.dependency(depends=["test_stft_instantiation"])
def test_stft_set_get_window_type(dpf_sound_test_server):
    stft = Stft()

    # Error
    with pytest.raises(PyDpfSoundException) as excinfo:
        stft.window_type = "InvalidWindow"
    assert (
        str(excinfo.value)
        == "Invalid window type, accepted values are 'BLACKMANHARRIS', 'HANN','BLACKMAN', \
                    'HAMMING', 'KAISER', 'BARTLETT', 'RECTANGULAR'."
    )

    stft.window_type = "KAISER"
    assert stft.window_type == "KAISER"


# @patch("matplotlib.pyplot.show")
# @pytest.mark.dependency(depends=["test_stft_process"])
# def test_stft_plot(mock_show, dpf_sound_test_server):
#     wav_loader = LoadWav(pytest.data_path_flute_in_container)
#     wav_loader.process()
#     fc_signal = wav_loader.get_output()
#     resampler = Resample(signal=fc_signal, new_sampling_frequency=88100.0)
#     resampler.process()
#     resampler.plot()

#     resampler.signal = fc_signal[0]
#     resampler.process()
#     resampler.plot()
