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

from ansys.dpf.core import Field, FieldsContainer
import numpy as np
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ansys.sound.core.signal_utilities import CreateSoundFieldsContainer

EXP_STR_PROCESSED = (
    "CreateSoundFieldsContainer object with 2 field(s).\n"
    "Output:\n"
    "DPF  Fields Container\n"
    "  with 2 field(s)\n"
    "  defined on labels: channel \n"
    "\n"
    "  with:\n"
    "  - field 0 {channel:  1} with Nodal location, 3 components and 0 entities.\n"
    "  - field 1 {channel:  2} with Nodal location, 3 components and 0 entities.\n"
)
EXP_STR_NOT_PROCESSED = "CreateSoundFieldsContainer object with 0 field(s).\nOutput: None"


def test_create_sound_fields_container_instantiation():
    """Test CreateSoundFieldsContainer instantiation."""
    sound_fields_container_creator = CreateSoundFieldsContainer()
    assert isinstance(sound_fields_container_creator, CreateSoundFieldsContainer)


def test_create_sound_fields_container_properties():
    """Test CreateSoundFieldsContainer properties."""
    sound_fields_container_creator = CreateSoundFieldsContainer()

    field_list = [Field(), Field()]
    sound_fields_container_creator.fields = field_list
    assert sound_fields_container_creator.fields is field_list

    field_tuple = (Field(), Field())
    sound_fields_container_creator.fields = field_tuple
    assert sound_fields_container_creator.fields is field_tuple

    field_np_array = np.array([Field(), Field()])
    sound_fields_container_creator.fields = field_np_array
    assert sound_fields_container_creator.fields is field_np_array


def test_create_sound_fields_container_properties_exceptions():
    """Test CreateSoundFieldsContainer properties exceptions."""
    sound_fields_container_creator = CreateSoundFieldsContainer()

    # Not a list, tuple, or numpy array
    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "Attribute `fields` must be provided as a list, tuple, or numpy array of DPF fields."
        ),
    ):
        sound_fields_container_creator.fields = "WrongType"

    # Does not only contain DPF fields
    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "Attribute `fields` must be provided as a list, tuple, or numpy array of DPF fields."
        ),
    ):
        sound_fields_container_creator.fields = [Field(), "NotAField"]


def test_create_sound_fields_container___str__():
    """Test CreateSoundFieldsContainer __str__ method."""
    sound_fields_container_creator = CreateSoundFieldsContainer()
    assert str(sound_fields_container_creator) == EXP_STR_NOT_PROCESSED

    sound_fields_container_creator.fields = [Field(), Field()]
    sound_fields_container_creator.process()
    assert str(sound_fields_container_creator) == EXP_STR_PROCESSED


def test_create_sound_fields_container_process():
    """Test CreateSoundFieldsContainer process method."""
    sound_fields_container_creator = CreateSoundFieldsContainer()

    sound_fields_container_creator.process()
    assert isinstance(sound_fields_container_creator._output, FieldsContainer)
    assert len(sound_fields_container_creator._output) == 0

    sound_fields_container_creator.fields = [Field(), Field()]
    sound_fields_container_creator.process()
    assert isinstance(sound_fields_container_creator._output, FieldsContainer)
    assert len(sound_fields_container_creator._output) == 2


def test_create_sound_fields_container_get_output():
    sound_fields_container_creator = CreateSoundFieldsContainer([Field(), Field()])

    with pytest.warns(
        PyAnsysSoundWarning,
        match=(
            "Output is not processed yet. Use the `CreateSoundFieldsContainer.process\(\)` "
            "method."
        ),
    ):
        output = sound_fields_container_creator.get_output()
    assert output is None

    sound_fields_container_creator.process()
    output = sound_fields_container_creator.get_output()

    assert isinstance(output, FieldsContainer)
    assert len(output) == 2
    assert isinstance(output[0], Field)
    assert isinstance(output[1], Field)
