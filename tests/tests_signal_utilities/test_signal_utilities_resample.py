from unittest.mock import patch

from ansys.dpf.core import Field, FieldsContainer
import numpy as np
import pytest

from ansys.dpf.sound.signal_utilities import LoadWav, Resample


@pytest.mark.dependency()
def test_resample_instantiation(dpf_sound_test_server):
    resampler = Resample()
    assert resampler != None


@pytest.mark.dependency(depends=["test_resample_instantiation"])
def test_resample_process(dpf_sound_test_server):
    resampler = Resample()
    wav_loader = LoadWav(pytest.data_path_flute_in_container)

    # Error 1
    with pytest.raises(RuntimeError) as excinfo:
        resampler.process()
    assert str(excinfo.value) == "No signal to resample. Use Resample.set_signal()."

    wav_loader.process()
    fc = wav_loader.get_output()

    # Testing input fields container (no error expected)
    resampler.set_signal(fc)
    resampler.process()

    # Testing input field (no error expected)
    resampler.set_signal(fc[0])
    resampler.process()


@pytest.mark.dependency(depends=["test_resample_process"])
def test_resample_get_output(dpf_sound_test_server):
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc_signal = wav_loader.get_output()
    resampler = Resample(signal=fc_signal, new_sampling_frequency=88100.0)

    with pytest.warns(
        UserWarning, match="Output has not been yet processed, use Resample.process()."
    ):
        fc_out = resampler.get_output()

    resampler.process()
    fc_out = resampler.get_output()

    assert len(fc_out) == 1

    resampler.set_signal(fc_signal[0])
    resampler.process()
    f_out = resampler.get_output()

    assert len(f_out.data) == 311743
    assert f_out.data[1000] == 2.9065033686492825e-06
    assert f_out.data[3456] == -0.0007385587086901069
    assert f_out.data[30000] == 0.02302781119942665
    assert f_out.data[60000] == -0.4175410866737366


@pytest.mark.dependency(depends=["test_resample_process"])
def test_resample_get_output_as_np_array(dpf_sound_test_server):
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc_signal = wav_loader.get_output()
    resampler = Resample(signal=fc_signal[0], new_sampling_frequency=88100.0)
    resampler.process()
    out_arr = resampler.get_output_as_nparray()

    assert len(out_arr) == 311743
    assert out_arr[1000] == 2.9065033686492825e-06
    assert out_arr[3456] == -0.0007385587086901069
    assert out_arr[30000] == 0.02302781119942665
    assert out_arr[60000] == -0.4175410866737366

    resampler.set_signal(fc_signal)
    resampler.process()
    out_arr = resampler.get_output_as_nparray()

    assert len(out_arr) == 311743
    assert out_arr[1000] == 2.9065033686492825e-06
    assert out_arr[3456] == -0.0007385587086901069
    assert out_arr[30000] == 0.02302781119942665
    assert out_arr[60000] == -0.4175410866737366


@pytest.mark.dependency(depends=["test_resample_instantiation"])
def test_resample_set_get_signal(dpf_sound_test_server):
    resampler = Resample()
    fc = FieldsContainer()
    fc.labels = ["channel"]
    f = Field()
    f.data = 42 * np.ones(3)
    fc.add_field({"channel": 0}, f)
    fc.name = "testField"
    resampler.set_signal(fc)
    fc_from_get = resampler.get_signal()

    assert fc_from_get.name == "testField"
    assert len(fc_from_get) == 1
    assert fc_from_get[0].data[0, 2] == 42


@pytest.mark.dependency(depends=["test_resample_instantiation"])
def test_resample_set_get_sampling_frequency(dpf_sound_test_server):
    resampler = Resample()

    # Error
    with pytest.raises(RuntimeError) as excinfo:
        resampler.set_sampling_frequency(-12.0)
    assert str(excinfo.value) == "Sampling frequency must be strictly greater than 0.0."

    resampler.set_sampling_frequency(1234.0)
    assert resampler.get_sampling_frequency() == 1234.0


@patch("matplotlib.pyplot.show")
@pytest.mark.dependency(depends=["test_resample_process"])
def test_resample_plot(mock_show, dpf_sound_test_server):
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc_signal = wav_loader.get_output()
    resampler = Resample(signal=fc_signal, new_sampling_frequency=88100.0)
    resampler.process()
    resampler.plot()

    resampler.set_signal(fc_signal[0])
    resampler.process()
    resampler.plot()
