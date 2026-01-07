# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from ansys.dpf.core import Field, FieldsContainer
import numpy as np
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ansys.sound.core.signal_utilities import LoadWav, WriteWav


def test_write_wav_instantiation():
    wav_writer = WriteWav()
    assert wav_writer != None


def test_write_wav_process():
    wav_writer = WriteWav()

    # Error 1
    with pytest.raises(
        PyAnsysSoundException,
        match="Path for writing WAV file is not specified. Use `WriteWav.path_to_write`.",
    ):
        wav_writer.process()

    wav_writer.path_to_write = pytest.temporary_folder + r"\flute_modified.wav"

    # Error 2
    with pytest.raises(PyAnsysSoundException) as excinfo:
        wav_writer.process()
    assert (
        str(excinfo.value)
        == "No signal is specified for writing to a WAV file. \
                    Use `WriteWav.signal`."
    )

    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()

    # Test process with FieldsContainer
    wav_writer.signal = wav_loader.get_output()
    wav_writer.process()

    # Test process with Field
    wav_writer.signal = wav_loader.get_output()[0]
    wav_writer.process()


def test_write_wav_set_get_path():
    wav_writer = WriteWav()

    wav_writer.path_to_write = r"C:\test\path"
    p = wav_writer.path_to_write

    assert p == r"C:\test\path"


def test_write_wav_set_get_bit_depth():
    wav_writer = WriteWav()

    # Error
    with pytest.raises(PyAnsysSoundException) as excinfo:
        wav_writer.bit_depth = "int128"
    assert (
        str(excinfo.value)
        == "Bit depth is invalid. Accepted values are 'float32', 'int32', 'int16', and 'int8'."
    )

    wav_writer.bit_depth = r"int8"
    b = wav_writer.bit_depth

    assert b == "int8"


def test_write_wav_set_get_signal():
    wav_writer = WriteWav()
    f = Field()
    f.data = 42 * np.ones(3)
    wav_writer.signal = f
    f_from_get = wav_writer.signal
    assert f_from_get.data[0, 2] == 42

    fc = FieldsContainer()
    fc.labels = ["channel"]
    fc.add_field({"channel": 0}, f)
    fc.name = "testField"
    wav_writer.signal = fc
    fc_from_get = wav_writer.signal

    assert fc_from_get.name == "testField"
    assert len(fc_from_get) == 1
    assert fc_from_get[0].data[0, 2] == 42

    with pytest.raises(
        PyAnsysSoundException, match="Signal must be specified as a `Field` or `FieldsContainer`."
    ):
        wav_writer.signal = "WrongType"


def test_write_wav_plot():
    wav_writer = WriteWav()

    with pytest.warns(PyAnsysSoundWarning, match="Nothing to plot."):
        wav_writer.plot()
