from ansys.dpf.core import Field, FieldsContainer
import numpy as np
import pytest

from ansys.sound.core.pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ansys.sound.core.signal_utilities import LoadWav, SumSignals


@pytest.mark.dependency()
def test_sum_signals_instantiation(dpf_sound_test_server):
    sum_gain = SumSignals()
    assert sum_gain != None


@pytest.mark.dependency(depends=["test_sum_signals_instantiation"])
def test_sum_signals_process(dpf_sound_test_server):
    sum_gain = SumSignals()
    wav_loader = LoadWav(pytest.data_path_white_noise_in_container)

    # Error 1
    with pytest.raises(PyAnsysSoundException) as excinfo:
        sum_gain.process()
    assert str(excinfo.value) == "No signal on which to apply gain. Use SumSignals.set_signal()."

    wav_loader.process()
    fc = wav_loader.get_output()

    # Testing input fields container (no error expected)
    sum_gain.signals = fc
    sum_gain.process()


@pytest.mark.dependency(depends=["test_sum_signals_process"])
def test_sum_signals_get_output(dpf_sound_test_server):
    wav_loader = LoadWav(pytest.data_path_white_noise_in_container)
    wav_loader.process()
    fc_signal = wav_loader.get_output()
    sum_gain = SumSignals(signals=fc_signal)

    with pytest.warns(
        PyAnsysSoundWarning, match="Output has not been yet processed, use SumSignals.process()."
    ):
        fc_out = sum_gain.get_output()

    sum_gain.process()
    f_out = sum_gain.get_output()

    assert len(f_out) == 480000
    assert f_out.data[1000] == 0.033935546875
    assert f_out.data[3456] == 0.22674560546875
    assert f_out.data[30000] == -0.72344970703125
    assert f_out.data[60000] == -0.13690185546875


@pytest.mark.dependency(depends=["test_sum_signals_process"])
def test_sum_signals_get_output_as_np_array(dpf_sound_test_server):
    wav_loader = LoadWav(pytest.data_path_white_noise_in_container)
    wav_loader.process()
    fc_signal = wav_loader.get_output()
    sum_gain = SumSignals(signals=fc_signal)

    with pytest.warns(
        PyAnsysSoundWarning, match="Output has not been yet processed, use SumSignals.process()."
    ):
        fc_out = sum_gain.get_output()

    sum_gain.process()
    out = sum_gain.get_output_as_nparray()

    assert len(out) == 480000
    assert out[1000] == 0.033935546875
    assert out[3456] == 0.22674560546875
    assert out[30000] == -0.72344970703125
    assert out[60000] == -0.13690185546875


@pytest.mark.dependency(depends=["test_sum_signals_instantiation"])
def test_sum_signals_set_get_signals(dpf_sound_test_server):
    sum_gain = SumSignals()

    fc = FieldsContainer()
    fc.labels = ["channel"]
    f = Field()
    f.data = 42 * np.ones(3)
    fc.add_field({"channel": 0}, f)
    fc.name = "testField"
    sum_gain.signals = fc
    fc_from_get = sum_gain.signals

    assert fc_from_get.name == "testField"
    assert len(fc_from_get) == 1
    assert fc_from_get[0].data[0, 2] == 42
