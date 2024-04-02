from ansys.dpf.core import Field, FieldsContainer
import numpy as np
import pytest

from ansys.dpf.sound.signal_utilities import ApplyGain, LoadWav


@pytest.mark.dependency()
def test_apply_gain_instantiation(dpf_sound_test_server):
    gain_applier = ApplyGain()
    assert gain_applier != None


@pytest.mark.dependency(depends=["test_apply_gain_instantiation"])
def test_apply_gain_process(dpf_sound_test_server):
    gain_applier = ApplyGain()
    wav_loader = LoadWav(pytest.data_path_flute_in_container)

    # Error 1
    with pytest.raises(RuntimeError) as excinfo:
        gain_applier.process()
    assert str(excinfo.value) == "No signal on which to apply gain. Use ApplyGain.set_signal()."

    wav_loader.process()
    fc = wav_loader.get_output()

    # Testing input fields container (no error expected)
    gain_applier.set_signal(fc)
    gain_applier.process()

    # Testing input field (no error expected)
    gain_applier.set_signal(fc[0])
    gain_applier.process()


@pytest.mark.dependency(depends=["test_apply_gain_process"])
def test_apply_gain_get_output(dpf_sound_test_server):
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc_signal = wav_loader.get_output()
    gain_applier = ApplyGain(signal=fc_signal, gain=12.0, gain_in_db=True)

    with pytest.warns(
        UserWarning, match="Output has not been yet processed, use ApplyGain.process()."
    ):
        fc_out = gain_applier.get_output()

    gain_applier.process()
    fc_out = gain_applier.get_output()

    assert len(fc_out) == 1

    gain_applier.set_signal(fc_signal[0])
    gain_applier.process()
    f_out = gain_applier.get_output()

    print(f_out.data[1000])
    print(f_out.data[3456])
    print(f_out.data[30000])
    print(f_out.data[60000])

    assert len(f_out.data) == 156048
    assert f_out.data[1000] == 0.00024298533389810473
    assert f_out.data[3456] == -0.005102692171931267
    assert f_out.data[30000] == 0.29461970925331116
    assert f_out.data[60000] == -0.09051203727722168


@pytest.mark.dependency(depends=["test_apply_gain_process"])
def test_apply_gain_get_output_as_np_array(dpf_sound_test_server):
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc_signal = wav_loader.get_output()
    gain_applier = ApplyGain(signal=fc_signal[0], gain=12.0, gain_in_db=True)
    gain_applier.process()
    out_arr = gain_applier.get_output_as_nparray()

    assert len(out_arr) == 156048
    assert out_arr[1000] == 0.00024298533389810473
    assert out_arr[3456] == -0.005102692171931267
    assert out_arr[30000] == 0.29461970925331116
    assert out_arr[60000] == -0.09051203727722168

    gain_applier.set_signal(fc_signal)
    gain_applier.process()
    out_arr = gain_applier.get_output_as_nparray()

    assert len(out_arr) == 156048
    assert out_arr[1000] == 0.00024298533389810473
    assert out_arr[3456] == -0.005102692171931267
    assert out_arr[30000] == 0.29461970925331116
    assert out_arr[60000] == -0.09051203727722168


@pytest.mark.dependency(depends=["test_apply_gain_instantiation"])
def test_apply_gain_set_get_signal(dpf_sound_test_server):
    gain_applier = ApplyGain()
    fc = FieldsContainer()
    fc.labels = ["channel"]
    f = Field()
    f.data = 42 * np.ones(3)
    fc.add_field({"channel": 0}, f)
    fc.name = "testField"
    gain_applier.set_signal(fc)
    fc_from_get = gain_applier.get_signal()

    assert fc_from_get.name == "testField"
    assert len(fc_from_get) == 1
    assert fc_from_get[0].data[0, 2] == 42


@pytest.mark.dependency(depends=["test_apply_gain_instantiation"])
def test_apply_gain_set_get_gain(dpf_sound_test_server):
    gain_applier = ApplyGain()

    gain_applier.set_gain(1234.0)
    assert gain_applier.get_gain() == 1234.0


@pytest.mark.dependency(depends=["test_apply_gain_instantiation"])
def test_apply_gain_set_get_gain_in_db(dpf_sound_test_server):
    gain_applier = ApplyGain()

    # Error 1
    with pytest.raises(RuntimeError) as excinfo:
        gain_applier.set_gain_in_db(1234.0)
    assert str(excinfo.value) == "new_gain_in_db must be a boolean value, either True or False."

    gain_applier.set_gain_in_db(False)
    assert gain_applier.get_gain_in_db() == False
