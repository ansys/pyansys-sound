from ansys.dpf.core import Field, FieldsContainer
import numpy as np
import pytest

from ansys.dpf.sound.signal_utilities import LoadWav, WriteWav


@pytest.mark.dependency()
def test_write_wav_instantiation(dpf_sound_test_server):
    wav_writer = WriteWav()
    assert wav_writer != None


@pytest.mark.dependency(depends=["test_write_wav_instantiation"])
def test_write_wav_process(dpf_sound_test_server):
    wav_writer = WriteWav()
    wav_loader = LoadWav(pytest.data_path_flute_in_container)

    # Error 1
    with pytest.raises(RuntimeError) as excinfo:
        wav_writer.process()
    assert str(excinfo.value) == "Path for write wav file is not specified. Use WriteWav.set_path."

    wav_writer.set_path(r"C:\data\flute_modified.wav")

    # Error 2
    with pytest.raises(RuntimeError) as excinfo:
        wav_writer.process()
    assert str(excinfo.value) == "No signal is specified for writing, use WriteWav.set_signal."

    wav_loader.process()
    wav_writer.set_signal(wav_loader.get_output())

    # Computing, no error expected
    wav_writer.process()


@pytest.mark.dependency(depends=["test_write_wav_instantiation"])
def test_write_wav_set_get_path(dpf_sound_test_server):
    wav_writer = WriteWav()

    wav_writer.set_path(r"C:\test\path")
    p = wav_writer.get_path()

    assert p == r"C:\test\path"


@pytest.mark.dependency(depends=["test_write_wav_instantiation"])
def test_write_wav_set_get_bit_depth(dpf_sound_test_server):
    wav_writer = WriteWav()

    # Error
    with pytest.raises(RuntimeError) as excinfo:
        wav_writer.set_bit_depth("int128")
    assert (
        str(excinfo.value)
        == "Invalid bit depth, accepted values are 'float32', 'int32', 'int16', 'int8'."
    )

    wav_writer.set_bit_depth(r"int8")
    b = wav_writer.get_bit_depth()

    assert b == "int8"


@pytest.mark.dependency(depends=["test_write_wav_instantiation"])
def test_write_wav_set_get_signal(dpf_sound_test_server):
    wav_writer = WriteWav()
    fc = FieldsContainer()
    fc.labels = ["channel"]
    f = Field()
    f.data = 42 * np.ones(3)
    fc.add_field({"channel": 0}, f)
    fc.name = "testField"
    wav_writer.set_signal(fc)
    fc_from_get = wav_writer.get_signal()

    assert fc_from_get.name == "testField"
    assert len(fc_from_get) == 1
    assert fc_from_get[0].data[0, 2] == 42


@pytest.mark.dependency(depends=["test_write_wav_instantiation"])
def test_write_wav_plot(dpf_sound_test_server):
    wav_writer = WriteWav()

    with pytest.warns(UserWarning, match="Nothing to plot."):
        wav_writer.plot()