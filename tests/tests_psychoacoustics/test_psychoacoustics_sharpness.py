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

from ansys.dpf.core import Field
import numpy as np
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ansys.sound.core.psychoacoustics import Sharpness
from ansys.sound.core.signal_utilities import LoadWav

if pytest.SERVERS_VERSION_GREATER_THAN_OR_EQUAL_TO_11_0:
    # Bug fix (ID#1325159) & third-party update (IPP) in DPF Sound 2026 R1
    EXP_SHARPNESS_1_FREE = 1.661001
    EXP_SHARPNESS_1_DIFFUSE = 1.747807
    EXP_SHARPNESS_2_FREE = 2.497226
    EXP_SHARPNESS_2_DIFFUSE = 2.629008
else:
    EXP_SHARPNESS_1_FREE = 1.660957
    EXP_SHARPNESS_1_DIFFUSE = 1.747762
    EXP_SHARPNESS_2_FREE = 2.497200
    EXP_SHARPNESS_2_DIFFUSE = 2.628972

EXP_STR_DEFAULT = "Sharpness object\nData:\n\tSignal name: Not set\nSharpness: Not processed"
EXP_STR = 'Sharpness object\nData:\n\tSignal name: ""\nSharpness: 1.66 acums'


def test_sharpness_instantiation():
    """Test the instantiation of the Sharpness class."""
    sharpness_computer = Sharpness()
    assert sharpness_computer != None


def test_sharpness___str__():
    """Test the __str__ method of the Sharpness class."""
    sharpness_computer = Sharpness()
    assert str(sharpness_computer) == EXP_STR_DEFAULT

    # Get a signal
    wav_loader = LoadWav(pytest.data_path_sharp_noise)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    sharpness_computer.signal = fc[0]

    # Compute
    sharpness_computer.process()

    assert str(sharpness_computer) == EXP_STR


def test_sharpness_process():
    """Test the process method of the Sharpness class."""
    sharpness_computer = Sharpness()

    # No signal -> error
    with pytest.raises(
        PyAnsysSoundException,
        match="No signal found for sharpness computation. Use `Sharpness.signal`.",
    ):
        sharpness_computer.process()

    # Get a signal
    wav_loader = LoadWav(pytest.data_path_sharp_noise)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    sharpness_computer.signal = fc[0]

    # Compute: no error
    sharpness_computer.process()
    assert sharpness_computer._output is not None


def test_sharpness_get_output():
    """Test the get_output method of the Sharpness class."""
    sharpness_computer = Sharpness()

    # Get a signal
    wav_loader = LoadWav(pytest.data_path_sharp_noise)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    sharpness_computer.signal = fc[0]

    # Sharpness not calculated yet -> warning
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the `Sharpness.process\\(\\)` method.",
    ):
        sharpness = sharpness_computer.get_output()
    assert sharpness == None

    # Compute with free field
    sharpness_computer.field_type = "Free"
    sharpness_computer.process()

    sharpness = sharpness_computer.get_output()
    assert sharpness == pytest.approx(EXP_SHARPNESS_1_FREE)

    # Compute with diffuse field
    sharpness_computer.field_type = "Diffuse"
    sharpness_computer.process()

    sharpness = sharpness_computer.get_output()
    assert sharpness == pytest.approx(EXP_SHARPNESS_1_DIFFUSE)

    # Test another signal
    wav_loader.path_to_wav = pytest.data_path_sharper_noise
    wav_loader.process()
    fc = wav_loader.get_output()
    sharpness_computer.signal = fc[0]

    # Compute with free field
    sharpness_computer.field_type = "Free"
    sharpness_computer.process()

    sharpness = sharpness_computer.get_output()
    assert sharpness == pytest.approx(EXP_SHARPNESS_2_FREE)

    # Compute with diffuse field
    sharpness_computer.field_type = "Diffuse"
    sharpness_computer.process()

    sharpness = sharpness_computer.get_output()
    assert sharpness == pytest.approx(EXP_SHARPNESS_2_DIFFUSE)


def test_sharpness_get_sharpness():
    """Test the get_sharpness method of the Sharpness class."""
    sharpness_computer = Sharpness()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_sharp_noise)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    sharpness_computer.signal = fc[0]

    # Compute with free field
    sharpness_computer.field_type = "Free"
    sharpness_computer.process()

    sharpness = sharpness_computer.get_sharpness()
    assert sharpness == pytest.approx(EXP_SHARPNESS_1_FREE)

    # Compute with diffuse field
    sharpness_computer.field_type = "Diffuse"
    sharpness_computer.process()

    sharpness = sharpness_computer.get_sharpness()
    assert sharpness == pytest.approx(EXP_SHARPNESS_1_DIFFUSE)


def test_sharpness_get_output_as_nparray():
    """Test the get_output_as_nparray method of the Sharpness class."""
    sharpness_computer = Sharpness()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_sharp_noise)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    sharpness_computer.signal = fc[0]

    # Sharpness not calculated yet -> warning and NaN value
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the `Sharpness.process\\(\\)` method.",
    ):
        sharpness = sharpness_computer.get_output_as_nparray()
    assert np.isnan(sharpness)

    # Compute
    sharpness_computer.process()

    sharpness = sharpness_computer.get_output_as_nparray()
    assert type(sharpness) == np.ndarray
    assert len(sharpness) == 1
    assert sharpness[0] == pytest.approx(EXP_SHARPNESS_1_FREE)


def test_sharpness_set_get_signal():
    """Test the signal property of the Sharpness class."""
    sharpness_computer = Sharpness()
    f_signal = Field()
    f_signal.data = 42 * np.ones(3)
    sharpness_computer.signal = f_signal

    assert isinstance(sharpness_computer.signal, Field)
    assert len(sharpness_computer.signal.data[0]) == 3
    assert sharpness_computer.signal.data[0][0] == 42

    # Set invalid value
    with pytest.raises(PyAnsysSoundException, match="Signal must be specified as a DPF field."):
        sharpness_computer.signal = "WrongType"


def test_sharpness_set_get_field_type():
    """Test the field_type property of the Sharpness class."""
    sharpness_computer = Sharpness()

    # Set value
    sharpness_computer.field_type = "Diffuse"
    assert sharpness_computer.field_type == "Diffuse"

    # Check case insensitivity
    sharpness_computer.field_type = "diffuse"
    assert sharpness_computer.field_type == "diffuse"

    sharpness_computer.field_type = "DIFFUSE"
    assert sharpness_computer.field_type == "DIFFUSE"

    # Set invalid value
    with pytest.raises(
        PyAnsysSoundException,
        match='Invalid field type "Invalid". Available options are "Free" and "Diffuse".',
    ):
        sharpness_computer.field_type = "Invalid"
