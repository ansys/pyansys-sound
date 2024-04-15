from ansys.dpf.core import Field, FieldsContainer
import numpy as np
import pytest

from ansys.dpf.sound.signal_utilities import LoadWav, ZeroPad


@pytest.mark.dependency()
def test_zero_pad_instantiation(dpf_sound_test_server):
    zero_pad = ZeroPad()
    assert zero_pad != None


@pytest.mark.dependency(depends=["test_zero_pad_instantiation"])
def test_zero_pad_process(dpf_sound_test_server):
    zero_pad = ZeroPad()
    wav_loader = LoadWav(pytest.data_path_flute_in_container)

    # Error 1
    with pytest.raises(RuntimeError) as excinfo:
        zero_pad.process()
    assert str(excinfo.value) == "No signal to zero-pad. Use ZeroPad.set_signal()."

    wav_loader.process()
    fc = wav_loader.get_output()

    # Testing input fields container (no error expected)
    zero_pad.signal = fc
    zero_pad.process()

    # Testing input field (no error expected)
    zero_pad.signal = fc[0]
    zero_pad.process()


@pytest.mark.dependency(depends=["test_zero_pad_process"])
def test_zero_pad_get_output(dpf_sound_test_server):
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc_signal = wav_loader.get_output()
    zero_pad = ZeroPad(signal=fc_signal, duration_zeros=12.0)

    with pytest.warns(
        UserWarning, match="Output has not been yet processed, use ZeroPad.process()."
    ):
        fc_out = zero_pad.get_output()

    zero_pad.process()
    fc_out = zero_pad.get_output()

    assert len(fc_out) == 1

    zero_pad.signal = fc_signal[0]
    zero_pad.process()
    f_out = zero_pad.get_output()

    assert len(f_out.data) == 685248
    assert f_out.data[1000] == 6.103515625e-05
    assert f_out.data[3456] == -0.00128173828125
    assert f_out.data[30000] == 0.074005126953125
    assert f_out.data[60000] == -0.022735595703125
    assert f_out.data[156048] == 0.0
    assert f_out.data[600000] == 0.0


@pytest.mark.dependency(depends=["test_zero_pad_process"])
def test_zero_pad_get_output_as_np_array(dpf_sound_test_server):
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc_signal = wav_loader.get_output()
    zero_pad = ZeroPad(signal=fc_signal[0], duration_zeros=12.0)
    zero_pad.process()
    out_arr = zero_pad.get_output_as_nparray()

    assert len(out_arr) == 685248
    assert out_arr[1000] == 6.103515625e-05
    assert out_arr[3456] == -0.00128173828125
    assert out_arr[30000] == 0.074005126953125
    assert out_arr[60000] == -0.022735595703125
    assert out_arr[156048] == 0.0
    assert out_arr[600000] == 0.0

    zero_pad.signal = fc_signal
    zero_pad.process()
    out_arr = zero_pad.get_output_as_nparray()

    assert len(out_arr) == 685248
    assert out_arr[1000] == 6.103515625e-05
    assert out_arr[3456] == -0.00128173828125
    assert out_arr[30000] == 0.074005126953125
    assert out_arr[60000] == -0.022735595703125
    assert out_arr[156048] == 0.0
    assert out_arr[600000] == 0.0


@pytest.mark.dependency(depends=["test_zero_pad_instantiation"])
def test_zero_pad_set_get_signal(dpf_sound_test_server):
    zero_pad = ZeroPad()
    fc = FieldsContainer()
    fc.labels = ["channel"]
    f = Field()
    f.data = 42 * np.ones(3)
    fc.add_field({"channel": 0}, f)
    fc.name = "testField"
    zero_pad.signal = fc
    fc_from_get = zero_pad.signal

    assert fc_from_get.name == "testField"
    assert len(fc_from_get) == 1
    assert fc_from_get[0].data[0, 2] == 42


@pytest.mark.dependency(depends=["test_zero_pad_process"])
def test_zero_pad_set_get_duration_zeros(dpf_sound_test_server):
    zero_pad = ZeroPad()

    # Error
    with pytest.raises(RuntimeError) as excinfo:
        zero_pad.duration_zeros - 12.0
    assert str(excinfo.value) == "Zero duration must be strictly greater than 0.0."
    zero_pad.duration_zeros = 1234.0
    assert zero_pad.duration_zeros == 1234.0
