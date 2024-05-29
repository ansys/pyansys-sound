from ansys.dpf.core import Field, FieldsContainer
import numpy as np
import pytest

from ansys.dpf.sound.pydpf_sound import PyDpfSoundException, PyDpfSoundWarning
from ansys.dpf.sound.signal_utilities import LoadWav, WriteWav


def test_write_wav_instantiation(dpf_sound_test_server):
    wav_writer = WriteWav()
    assert wav_writer != None


def test_write_wav_process(dpf_sound_test_server):
    wav_writer = WriteWav()
    wav_loader = LoadWav(pytest.data_path_flute_in_container)

    # Error 1
    with pytest.raises(PyDpfSoundException) as excinfo:
        wav_writer.process()
    assert str(excinfo.value) == "Path for write wav file is not specified. Use WriteWav.set_path."

    wav_writer.path_to_write = r"C:\data\flute_modified.wav"

    # Error 2
    with pytest.raises(PyDpfSoundException) as excinfo:
        wav_writer.process()
    assert str(excinfo.value) == "No signal is specified for writing, use WriteWav.set_signal."

    wav_loader.process()
    wav_writer.signal = wav_loader.get_output()

    # Computing, no error expected
    wav_writer.process()


def test_write_wav_set_get_path(dpf_sound_test_server):
    wav_writer = WriteWav()

    wav_writer.path_to_write = r"C:\test\path"
    p = wav_writer.path_to_write

    assert p == r"C:\test\path"


def test_write_wav_set_get_bit_depth(dpf_sound_test_server):
    wav_writer = WriteWav()

    # Error
    with pytest.raises(PyDpfSoundException) as excinfo:
        wav_writer.bit_depth = "int128"
    assert (
        str(excinfo.value)
        == "Invalid bit depth, accepted values are 'float32', 'int32', 'int16', 'int8'."
    )

    wav_writer.bit_depth = r"int8"
    b = wav_writer.bit_depth

    assert b == "int8"


def test_write_wav_set_get_signal(dpf_sound_test_server):
    wav_writer = WriteWav()
    fc = FieldsContainer()
    fc.labels = ["channel"]
    f = Field()
    f.data = 42 * np.ones(3)
    fc.add_field({"channel": 0}, f)
    fc.name = "testField"
    wav_writer.signal = fc
    fc_from_get = wav_writer.signal

    assert fc_from_get.name == "testField"
    assert len(fc_from_get) == 1
    assert fc_from_get[0].data[0, 2] == 42


def test_write_wav_plot(dpf_sound_test_server):
    wav_writer = WriteWav()

    with pytest.warns(PyDpfSoundWarning, match="Nothing to plot."):
        wav_writer.plot()
