from unittest.mock import patch

from ansys.dpf.core import Field, FieldsContainer
import numpy as np
import pytest

from ansys.dpf.sound.pydpf_sound import PyDpfSoundException, PyDpfSoundWarning
from ansys.dpf.sound.signal_utilities import LoadWav
from ansys.dpf.sound.spectrogram_processing import Stft


@pytest.mark.dependency()
def test_stft_instantiation(dpf_sound_test_server):
    stft = Stft()
    assert stft != None


@pytest.mark.dependency(depends=["test_stft_instantiation"])
def test_stft_process(dpf_sound_test_server):
    stft = Stft()
    wav_loader = LoadWav(pytest.data_path_flute_in_container)

    # Error 1
    with pytest.raises(PyDpfSoundException) as excinfo:
        stft.process()
    assert str(excinfo.value) == "No signal for STFT. Use Stft.set_signal()."

    wav_loader.process()
    fc = wav_loader.get_output()

    # Testing input fields container (no error expected)
    stft.signal = fc
    try:
        stft.process()
    except:
        # Should not fail
        assert False


@pytest.mark.dependency(depends=["test_stft_process"])
def test_stft_get_output(dpf_sound_test_server):
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc_signal = wav_loader.get_output()
    stft = Stft(signal=fc_signal)

    with pytest.warns(
        PyDpfSoundWarning, match="Output has not been yet processed, use Stft.process()."
    ):
        fc_out = stft.get_output()

    stft.process()
    fc_out = stft.get_output()

    assert len(fc_out) == 310
    assert len(fc_out[100].data) == stft.fft_size
    assert fc_out[100].data[0] == -0.11434437334537506
    assert fc_out[200].data[0] == -0.09117653965950012
    assert fc_out[300].data[0] == -0.019828863441944122


@pytest.mark.dependency(depends=["test_stft_process"])
def test_stft_get_output_as_np_array(dpf_sound_test_server):
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc_signal = wav_loader.get_output()
    stft = Stft(signal=fc_signal)

    stft.process()
    arr = stft.get_output_as_nparray()

    print(np.shape(arr))
    assert np.shape(arr) == (stft.fft_size, 156)

    print(type(arr[100, 0]))
    print((arr[100, 0]))
    print((arr[200, 0]))
    print((arr[300, 0]))
    assert type(arr[100, 0]) == np.complex128
    assert arr[100, 0] == (-1.0736324787139893 - 1.4027032852172852j)
    assert arr[200, 0] == (0.511505126953125 + 0.3143689036369324j)
    assert arr[300, 0] == (-0.03049434721469879 - 0.49174121022224426j)


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
    f = stft.signal

    assert len(f) == 3
    assert f.data[0, 2] == 42

    stft.signal = fc[0]
    fc_from_get = stft.signal

    assert len(f) == 3
    assert f.data[0, 2] == 42

    fc.add_field({"channel": 1}, fc[0])

    # Error
    with pytest.raises(PyDpfSoundException) as excinfo:
        stft.signal = fc
    assert str(excinfo.value) == "Input as FieldsContainer can only have one Field (mono signal)."


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
        == "Invalid window type, accepted values are 'HANNING', 'BLACKMANHARRIS', 'HANN', \
                    'BLACKMAN','HAMMING', 'KAISER', 'BARTLETT', 'RECTANGULAR'."
    )

    stft.window_type = "KAISER"
    assert stft.window_type == "KAISER"


@patch("matplotlib.pyplot.show")
@pytest.mark.dependency(depends=["test_stft_process"])
def test_stft_plot(mock_show, dpf_sound_test_server):
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc_signal = wav_loader.get_output()
    stft = Stft(signal=fc_signal)
    stft.process()
    stft.plot()
