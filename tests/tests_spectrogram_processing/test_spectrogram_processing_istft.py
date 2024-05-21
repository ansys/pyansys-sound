from ansys.dpf.core import Field, FieldsContainer
import numpy as np
import pytest

from ansys.dpf.sound.pydpf_sound import PyDpfSoundException, PyDpfSoundWarning
from ansys.dpf.sound.signal_utilities import LoadWav
from ansys.dpf.sound.spectrogram_processing import Istft, Stft


@pytest.mark.dependency()
def test_istft_instantiation(dpf_sound_test_server):
    stft = Istft()
    assert stft != None


@pytest.mark.dependency(depends=["test_istft_instantiation"])
def test_istft_process(dpf_sound_test_server):
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    stft = Stft(signal=wav_loader.get_output())
    stft.process()
    istft = Istft()

    # Error 1
    with pytest.raises(PyDpfSoundException) as excinfo:
        istft.process()
    assert str(excinfo.value) == "No stft for ISTFT. Use Istft.stft."

    # Testing input fields container (no error expected)
    istft.stft = stft.get_output()
    try:
        istft.process()
    except:
        # Should not fail
        assert False


@pytest.mark.dependency(depends=["test_istft_process"])
def test_istft_get_output(dpf_sound_test_server):
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    stft = Stft(signal=wav_loader.get_output())
    stft.process()
    istft = Istft(stft=stft.get_output())

    with pytest.warns(
        PyDpfSoundWarning, match="Output has not been yet processed, use Istft.process()."
    ):
        fc_out = istft.get_output()

    istft.process()
    f_out = istft.get_output()

    assert len(f_out) == 156048
    assert f_out.data[100] == -3.790271482090324e-12
    assert f_out.data[2000] == -0.0014953609788790345
    assert f_out.data[30000] == 0.0740051195025444


@pytest.mark.dependency(depends=["test_istft_process"])
def test_istft_get_output_as_np_array(dpf_sound_test_server):
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    stft = Stft(signal=wav_loader.get_output())
    stft.process()
    istft = Istft(stft=stft.get_output())

    istft.process()
    arr = istft.get_output_as_nparray()

    assert len(arr) == 156048
    assert arr[100] == -3.790271482090324e-12
    assert arr[2000] == -0.0014953609788790345
    assert arr[30000] == 0.0740051195025444


@pytest.mark.dependency(depends=["test_istft_instantiation"])
def test_istft_set_get_signal(dpf_sound_test_server):
    # Test 1 with error
    istft = Istft()
    fc = FieldsContainer()
    fc.labels = ["channel"]
    f = Field()
    f.data = 42 * np.ones(3)
    fc.add_field({"channel": 0}, f)

    # Error
    with pytest.raises(PyDpfSoundException) as excinfo:
        istft.stft = 456
    assert str(excinfo.value) == "Input must be a Fields container."

    with pytest.raises(PyDpfSoundException) as excinfo:
        istft.stft = fc
    assert (
        str(excinfo.value)
        == "STFT is in the wrong format, make sure it has been computed with the Stft class."
    )

    # Test 2 - No Error
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    stft = Stft(signal=wav_loader.get_output())
    stft.process()
    istft.stft = stft.get_output()

    out_stft = istft.stft

    assert out_stft.has_label("time")
    assert out_stft.has_label("channel_number")
    assert out_stft.has_label("complex")


@pytest.mark.dependency(depends=["test_istft_process"])
def test_istft_plot(dpf_sound_test_server):
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    stft = Stft(signal=wav_loader.get_output())
    stft.process()
    istft = Istft(stft=stft.get_output())
    istft.process()
    # istft.plot()
