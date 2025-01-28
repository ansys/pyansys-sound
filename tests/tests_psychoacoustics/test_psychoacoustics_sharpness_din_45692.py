# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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
from ansys.sound.core.psychoacoustics import SharpnessDIN45692
from ansys.sound.core.signal_utilities import LoadWav

EXP_MAX_SHARPNESS_FREE = 1.216734
EXP_MAX_SHARPNESS_DIFFUSE = 1.225831

EXP_STR_DEFAULT = (
    "SharpnessDIN45692 object\nData:\n\tSignal name: Not set\nSharpness: Not processed"
)
EXP_STR = 'SharpnessDIN45692 object\nData:\n\tSignal name: "flute"\nSharpness: 1.22 acums'


def test_sharpness_din_45692_instantiation():
    """Test the instantiation of the SharpnessDIN45692 class."""
    sharpness_obj = SharpnessDIN45692()
    assert sharpness_obj.signal is None
    assert sharpness_obj.field_type == "Free"


def test_sharpness_din_45692___str__():
    """Test the __str__ method of the SharpnessDIN45692 class."""
    sharpness_obj = SharpnessDIN45692()
    assert str(sharpness_obj) == EXP_STR_DEFAULT

    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    sharpness_obj.signal = fc[0]
    sharpness_obj.process()
    assert str(sharpness_obj) == EXP_STR


def test_sharpness_din_45692_properties():
    """Test the properties of the SharpnessDIN45692 class."""
    sharpness_obj = SharpnessDIN45692()

    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    sharpness_obj.signal = fc[0]
    assert isinstance(sharpness_obj.signal, Field)

    sharpness_obj.field_type = "Diffuse"
    assert sharpness_obj.field_type == "Diffuse"


def test_sharpness_din_45692_properties_exceptions():
    """Test the properties of the SharpnessDIN45692 class."""
    sharpness_obj = SharpnessDIN45692()

    with pytest.raises(PyAnsysSoundException, match="Signal must be specified as a DPF field."):
        sharpness_obj.signal = "WrongType"
    assert sharpness_obj.signal is None

    with pytest.raises(
        PyAnsysSoundException,
        match=(
            'Invalid field type "InvalidFieldType". Available options are "Free" and "Diffuse".'
        ),
    ):
        sharpness_obj.field_type = "InvalidFieldType"
    assert sharpness_obj.field_type == "Free"


def test_sharpness_din_45692_process():
    """Test the process method of the SharpnessDIN45692 class."""
    sharpness_obj = SharpnessDIN45692()

    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    sharpness_obj.signal = fc[0]
    sharpness_obj.process()
    assert sharpness_obj._output is not None


def test_sharpness_din_45692_process_exception():
    """Test the process method of the SharpnessDIN45692 class."""
    sharpness_obj = SharpnessDIN45692()

    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "No signal found for sharpness over time computation. Use `SharpnessDIN45692.signal`."
        ),
    ):
        sharpness_obj.process()
    assert sharpness_obj._output is None


def test_sharpness_din_45692_get_output():
    """Test the get_output method of the SharpnessDIN45692 class."""
    sharpness_obj = SharpnessDIN45692()

    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    sharpness_obj.signal = fc[0]

    sharpness_obj.field_type = "Free"
    sharpness_obj.process()

    sharpness = sharpness_obj.get_output()
    assert sharpness == pytest.approx(EXP_MAX_SHARPNESS_FREE)

    sharpness_obj.field_type = "Diffuse"
    sharpness_obj.process()

    sharpness = sharpness_obj.get_output()
    assert sharpness == pytest.approx(EXP_MAX_SHARPNESS_DIFFUSE)


def test_sharpness_din_45692_get_output_warning():
    """Test the get_output method of the SharpnessDIN45692 class."""
    sharpness_obj = SharpnessDIN45692()

    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the `SharpnessDIN45692.process\\(\\)` method.",
    ):
        output = sharpness_obj.get_output()
    assert output is None


def test_sharpness_din_45692_get_output_as_nparray():
    """Test the get_output_as_nparray method of the SharpnessDIN45692 class."""
    sharpness_obj = SharpnessDIN45692()

    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the `SharpnessDIN45692.process\\(\\)` method.",
    ):
        sharpness = sharpness_obj.get_output_as_nparray()
    assert np.isnan(sharpness)

    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    sharpness_obj.signal = fc[0]

    sharpness_obj.field_type = "Free"
    sharpness_obj.process()

    sharpness = sharpness_obj.get_output_as_nparray()
    assert sharpness[0] == pytest.approx(EXP_MAX_SHARPNESS_FREE)

    sharpness_obj.field_type = "Diffuse"
    sharpness_obj.process()

    sharpness = sharpness_obj.get_output_as_nparray()
    assert sharpness[0] == pytest.approx(EXP_MAX_SHARPNESS_DIFFUSE)


def test_sharpness_din_45692_get_sharpness():
    """Test the get_sharpness method of the SharpnessDIN45692 class."""
    sharpness_obj = SharpnessDIN45692()

    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    sharpness_obj.signal = fc[0]

    sharpness_obj.field_type = "Free"
    sharpness_obj.process()

    sharpness = sharpness_obj.get_sharpness()
    assert sharpness == pytest.approx(EXP_MAX_SHARPNESS_FREE)

    sharpness_obj.field_type = "Diffuse"
    sharpness_obj.process()

    sharpness = sharpness_obj.get_sharpness()
    assert sharpness == pytest.approx(EXP_MAX_SHARPNESS_DIFFUSE)
