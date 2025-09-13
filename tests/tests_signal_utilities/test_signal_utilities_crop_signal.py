from ansys.dpf.core import Field, FieldsContainer
import numpy as np
import pytest

from ansys.dpf.sound.pydpf_sound import PyDpfSoundException, PyDpfSoundWarning
from ansys.dpf.sound.signal_utilities import CropSignal, LoadWav


@pytest.mark.dependency()
def test_crop_signal_instantiation(dpf_sound_test_server):
    signal_cropper = CropSignal()
    assert signal_cropper != None


@pytest.mark.dependency(depends=["test_crop_signal_instantiation"])
def test_crop_signal_process(dpf_sound_test_server):
    signal_cropper = CropSignal(start_time=0.0, end_time=1.0)
    wav_loader = LoadWav(pytest.data_path_flute_in_container)

    # Error 1
    with pytest.raises(PyDpfSoundException) as excinfo:
        signal_cropper.process()
    assert str(excinfo.value) == "No signal to crop. Use CropSignal.set_signal()."

    wav_loader.process()
    fc = wav_loader.get_output()

    # Testing input fields container (no error expected)
    signal_cropper.signal = fc
    signal_cropper.process()

    # Testing input field (no error expected)
    signal_cropper.signal = fc[0]
    signal_cropper.process()


@pytest.mark.dependency(depends=["test_crop_signal_process"])
def test_crop_signal_get_output(dpf_sound_test_server):
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc_signal = wav_loader.get_output()
    signal_cropper = CropSignal(signal=fc_signal, start_time=0.0, end_time=1.0)

    with pytest.warns(
        PyDpfSoundWarning, match="Output has not been yet processed, use CropSignal.process()."
    ):
        fc_out = signal_cropper.get_output()

    signal_cropper.process()
    fc_out = signal_cropper.get_output()

    assert len(fc_out) == 1

    signal_cropper.signal = fc_signal[0]
    signal_cropper.process()
    f_out = signal_cropper.get_output()
    data = f_out.data
    # Checking data size and some random samples
    assert len(data) == 44101
    assert data[10] == 0.0
    assert data[1000] == 6.103515625e-05
    assert data[10000] == 0.0308837890625
    assert data[44000] == 0.47772216796875


@pytest.mark.dependency(depends=["test_crop_signal_process"])
def test_crop_signal_get_output_as_np_array(dpf_sound_test_server):
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc_signal = wav_loader.get_output()
    signal_cropper = CropSignal(signal=fc_signal, start_time=0.0, end_time=1.0)

    with pytest.warns(
        PyDpfSoundWarning, match="Output has not been yet processed, use CropSignal.process()."
    ):
        fc_out = signal_cropper.get_output()

    signal_cropper.process()
    data = signal_cropper.get_output_as_nparray()

    assert len(data) == 44101
    assert data[10] == 0.0
    assert data[1000] == 6.103515625e-05
    assert data[10000] == 0.0308837890625
    assert data[44000] == 0.47772216796875

    signal_cropper.signal = fc_signal[0]
    signal_cropper.process()
    data = signal_cropper.get_output_as_nparray()
    # Checking data size and some random samples
    assert len(data) == 44101
    assert data[10] == 0.0
    assert data[1000] == 6.103515625e-05
    assert data[10000] == 0.0308837890625
    assert data[44000] == 0.47772216796875


@pytest.mark.dependency(depends=["test_crop_signal_instantiation"])
def test_crop_signal_set_get_signal(dpf_sound_test_server):
    signal_cropper = CropSignal()
    fc = FieldsContainer()
    fc.labels = ["channel"]
    f = Field()
    f.data = 42 * np.ones(3)
    fc.add_field({"channel": 0}, f)
    fc.name = "testField"
    signal_cropper.signal = fc
    fc_from_get = signal_cropper.signal

    assert fc_from_get.name == "testField"
    assert len(fc_from_get) == 1
    assert fc_from_get[0].data[0, 2] == 42


@pytest.mark.dependency(depends=["test_crop_signal_instantiation"])
def test_crop_signal_set_get_start_end_times(dpf_sound_test_server):
    signal_cropper = CropSignal()

    # Error
    with pytest.raises(PyDpfSoundException) as excinfo:
        signal_cropper.start_time = -12.0
    assert str(excinfo.value) == "Start time must be greater than or equal to 0.0."

    # Error
    with pytest.raises(PyDpfSoundException) as excinfo:
        signal_cropper.end_time = -12.0
    assert str(excinfo.value) == "End time must be greater than or equal to 0.0."

    signal_cropper.start_time = 1.0

    # Error
    with pytest.raises(PyDpfSoundException) as excinfo:
        signal_cropper.end_time = 0.5
    assert str(excinfo.value) == "End time must be greater than or equal to the start time."

    signal_cropper.end_time = 1234.0

    start_time = signal_cropper.start_time
    end_time = signal_cropper.end_time
    assert start_time == 1.0
    assert end_time == 1234.0
