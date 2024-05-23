from ansys.dpf.core import Field, FieldsContainer
import numpy as np
import pytest

from ansys.dpf.sound.psychoacoustics import Sharpness
from ansys.dpf.sound.pydpf_sound import PyDpfSoundException, PyDpfSoundWarning
from ansys.dpf.sound.signal_utilities import LoadWav

EXP_SHARPNESS_1 = 1.6609569787979126
EXP_SHARPNESS_2 = 2.4972000122070312


@pytest.mark.dependency()
def test_sharpness_instantiation(dpf_sound_test_server):
    sharpness_computer = Sharpness()
    assert sharpness_computer != None


@pytest.mark.dependency(depends=["test_sharpness_instantiation"])
def test_sharpness_process(dpf_sound_test_server):
    sharpness_computer = Sharpness()

    # No signal -> error
    with pytest.raises(
        PyDpfSoundException,
        match="No signal for sharpness computation. Use Sharpness.signal.",
    ):
        sharpness_computer.process()

    # Get a signal
    wav_loader = LoadWav(pytest.data_path_sharp_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal as field container
    sharpness_computer.signal = fc

    # Compute: no error
    sharpness_computer.process()

    # Set signal as field
    sharpness_computer.signal = fc[0]

    # Compute: no error
    sharpness_computer.process()


@pytest.mark.dependency(depends=["test_sharpness_process"])
def test_sharpness_get_output(dpf_sound_test_server):
    sharpness_computer = Sharpness()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_sharp_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    sharpness_computer.signal = fc

    # Compute
    sharpness_computer.process()

    sharpness = sharpness_computer.get_output()
    assert sharpness != None


@pytest.mark.dependency(depends=["test_sharpness_process"])
def test_sharpness_get_sharpness(dpf_sound_test_server):
    sharpness_computer = Sharpness()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_sharp_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal as a field
    sharpness_computer.signal = fc[0]

    # Sharpness not calculated yet -> warning
    with pytest.warns(
        PyDpfSoundWarning,
        match="Output has not been processed yet, use Sharpness.process().",
    ):
        sharpness = sharpness_computer.get_sharpness()
    assert sharpness == None

    # Compute
    sharpness_computer.process()

    # Request second channel's sharpness while signal is a field (mono) -> error
    with pytest.raises(
        PyDpfSoundException, match="Specified channel index \\(1\\) does not exist."
    ):
        sharpness = sharpness_computer.get_sharpness(1)

    sharpness = sharpness_computer.get_sharpness(0)
    assert sharpness == pytest.approx(EXP_SHARPNESS_1)

    # Set signal as a fields container
    sharpness_computer.signal = fc

    # Compute
    sharpness_computer.process()

    sharpness = sharpness_computer.get_sharpness(0)
    assert sharpness == pytest.approx(EXP_SHARPNESS_1)

    # Add a second signal in the fields container
    # Note: No need to re-assign the signal property, as fc is simply an alias for it
    wav_loader = LoadWav(pytest.data_path_sharper_noise_in_container)
    wav_loader.process()
    fc.add_field({"channel_number": 1}, wav_loader.get_output()[0])

    # Compute again
    sharpness_computer.process()
    sharpness = sharpness_computer.get_sharpness(1)
    assert sharpness == pytest.approx(EXP_SHARPNESS_2)


@pytest.mark.dependency(depends=["test_sharpness_process"])
def test_sharpness_get_output_as_nparray_from_fields_container(
    dpf_sound_test_server,
):
    sharpness_computer = Sharpness()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_sharp_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    sharpness_computer.signal = fc

    # Sharpness not calculated yet -> warning
    with pytest.warns(
        PyDpfSoundWarning,
        match="Output has not been processed yet, use Sharpness.process().",
    ):
        sharpness = sharpness_computer.get_output_as_nparray()
    assert sharpness == None

    # Compute
    sharpness_computer.process()

    sharpness = sharpness_computer.get_output_as_nparray()
    assert len(sharpness) == 1
    assert sharpness[0] == pytest.approx(EXP_SHARPNESS_1)


@pytest.mark.dependency(depends=["test_sharpness_process"])
def test_sharpness_get_output_as_nparray_from_field(dpf_sound_test_server):
    sharpness_computer = Sharpness()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_sharp_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    sharpness_computer.signal = fc[0]

    # Compute
    sharpness_computer.process()

    sharpness = sharpness_computer.get_output_as_nparray()
    assert len(sharpness) == 1
    assert sharpness[0] == pytest.approx(EXP_SHARPNESS_1)


@pytest.mark.dependency(depends=["test_sharpness_instantiation"])
def test_sharpness_set_get_signal(dpf_sound_test_server):
    sharpness_computer = Sharpness()
    fc = FieldsContainer()
    fc.labels = ["channel"]
    f = Field()
    f.data = 42 * np.ones(3)
    fc.add_field({"channel": 0}, f)
    fc.name = "testField"
    sharpness_computer.signal = fc
    fc_from_get = sharpness_computer.signal

    assert fc_from_get.name == "testField"
    assert len(fc_from_get) == 1
    assert fc_from_get[0].data[0, 2] == 42
