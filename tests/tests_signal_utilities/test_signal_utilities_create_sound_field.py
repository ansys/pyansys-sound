import numpy as np
import pytest

from ansys.dpf.sound.signal_utilities import CreateSoundField


@pytest.mark.dependency()
def test_create_sound_field_instantiation(dpf_sound_test_server):
    sound_field_creator = CreateSoundField()
    assert sound_field_creator != None


@pytest.mark.dependency(depends=["test_create_sound_field_instantiation"])
def test_create_sound_field_process(dpf_sound_test_server):
    sound_field_creator = CreateSoundField()

    # Error 1
    with pytest.raises(RuntimeError) as excinfo:
        sound_field_creator.process()
    assert str(excinfo.value) == "No data to use. Use CreateSoundField.set_data()."

    # No error
    arr = np.ones(100)
    sound_field_creator.set_data(arr)
    sound_field_creator.process()


@pytest.mark.dependency(depends=["test_create_sound_field_process"])
def test_create_sound_field_get_output(dpf_sound_test_server):
    sound_field_creator = CreateSoundField(data=np.ones(100))

    with pytest.warns(
        UserWarning, match="Output has not been yet processed, use CreateSoundField.process()."
    ):
        f_out = sound_field_creator.get_output()

    sound_field_creator.process()
    f_out = sound_field_creator.get_output()

    assert len(f_out) == 100
    assert f_out.data[0] == 1.0
    assert f_out.data[50] == 1.0
    assert f_out.data[99] == 1.0


@pytest.mark.dependency(depends=["test_create_sound_field_process"])
def test_create_sound_field_get_output_as_np_array(dpf_sound_test_server):
    sound_field_creator = CreateSoundField(data=np.ones(100))
    sound_field_creator.process()
    out_arr = sound_field_creator.get_output_as_nparray()

    assert len(out_arr) == 100
    assert out_arr[0] == 1.0
    assert out_arr[50] == 1.0
    assert out_arr[99] == 1.0


@pytest.mark.dependency(depends=["test_create_sound_field_instantiation"])
def test_create_sound_field_set_get_data(dpf_sound_test_server):
    sound_field_creator = CreateSoundField()
    sound_field_creator.set_data(np.ones(100))
    data = sound_field_creator.get_data()
    assert len(data) == 100
    assert data[0] == 1.0
    assert data[50] == 1.0
    assert data[99] == 1.0


@pytest.mark.dependency(depends=["test_create_sound_field_instantiation"])
def test_create_sound_field_set_get_sampling_frequency(dpf_sound_test_server):
    sound_field_creator = CreateSoundField()

    # Error 1
    with pytest.raises(RuntimeError) as excinfo:
        sound_field_creator.set_sampling_frequency(-1234.0)
    assert str(excinfo.value) == "Sampling frequency must be greater than or equal to 0.0."

    sound_field_creator.set_sampling_frequency(1234.0)
    assert sound_field_creator.get_sampling_frequency() == 1234.0


@pytest.mark.dependency(depends=["test_create_sound_field_instantiation"])
def test_create_sound_field_set_get_unit(dpf_sound_test_server):
    sound_field_creator = CreateSoundField()

    sound_field_creator.set_unit("MyUnit")
    assert sound_field_creator.get_unit() == "MyUnit"