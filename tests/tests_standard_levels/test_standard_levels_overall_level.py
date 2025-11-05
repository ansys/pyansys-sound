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

import numpy as np
import pytest
from ansys.dpf.core import Field

from ansys.sound.core._pyansys_sound import (PyAnsysSoundException,
                                             PyAnsysSoundWarning)
from ansys.sound.core.signal_utilities import LoadWav
from ansys.sound.core.standard_levels import OverallLevel

EXP_STR_NOT_SET = (
    "OverallLevel object.\nData\n\tSignal: Not set\n\tScale type: dB\n\tReference value: 1.0\n"
    "\tFrequency weighting: None\nOutput level value: Not processed"
)
EXP_STR_ALL_SET = (
    'OverallLevel object.\nData\n\tSignal: "flute"\n\tScale type: RMS\n\tReference value: 1.0\n'
    "\tFrequency weighting: None\nOutput level value: Not processed"
)
EXP_STR_ALL_PROCESSED = (
    'OverallLevel object.\nData\n\tSignal: "flute"\n\tScale type: dB\n\tReference value: 2e-05\n'
    "\tFrequency weighting: A\nOutput level value: 86.7 dBA (re 2e-05)"
)
EXP_LEVEL_DEFAULT = -5.76525
EXP_LEVEL_RMS = 0.514917
EXP_LEVEL_DBSPL = 88.2142
EXP_LEVEL_DBA = 86.7392
EXP_LEVEL_DBB = 88.004
EXP_LEVEL_DBC = 88.2132


def test_overall_level_instantiation():
    """Test OverallLevel instantiation."""
    level_obj = OverallLevel()
    assert level_obj.signal == None
    assert level_obj.scale == "dB"
    assert level_obj.reference_value == 1.0
    assert level_obj.frequency_weighting == ""


def test_overall_level_properties():
    """Test OverallLevel properties."""
    level_obj = OverallLevel()
    level_obj.signal = Field()
    assert type(level_obj.signal) == Field

    level_obj.scale = "RMS"
    assert level_obj.scale == "RMS"

    level_obj.reference_value = 2e-5
    assert level_obj.reference_value == 2e-5

    level_obj.frequency_weighting = "A"
    assert level_obj.frequency_weighting == "A"


def test_overall_level_properties_exceptions():
    """Test OverallLevel properties exceptions."""
    level_obj = OverallLevel()
    with pytest.raises(PyAnsysSoundException, match="The signal must be provided as a DPF field."):
        level_obj.signal = "InvalidType"

    with pytest.raises(PyAnsysSoundException, match="The scale type must be either 'dB' or 'RMS'."):
        level_obj.scale = "Invalid"

    with pytest.raises(
        PyAnsysSoundException, match="The reference value must be strictly positive."
    ):
        level_obj.reference_value = -1

    with pytest.raises(
        PyAnsysSoundException,
        match="The frequency weighting must be one of \\['', 'A', 'B', 'C'\\].",
    ):
        level_obj.frequency_weighting = "Invalid"


def test_overall_level___str__():
    """Test OverallLevel __str__ method."""
    level_obj = OverallLevel()
    assert str(level_obj) == EXP_STR_NOT_SET

    loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    loader.process()
    f_signal = loader.get_output()[0]

    level_obj.signal = f_signal
    level_obj.scale = "RMS"
    assert str(level_obj) == EXP_STR_ALL_SET

    level_obj.scale = "dB"
    level_obj.reference_value = 2e-5
    level_obj.frequency_weighting = "A"
    level_obj.process()
    assert str(level_obj) == EXP_STR_ALL_PROCESSED


def test_overall_level_process():
    """Test OverallLevel process method."""
    loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    loader.process()
    f_signal = loader.get_output()[0]

    level_obj = OverallLevel(signal=f_signal)
    level_obj.process()
    assert level_obj.get_output() is not None


def test_overall_level_process_exceptions():
    """Test OverallLevel process method exceptions."""
    level_obj = OverallLevel()
    with pytest.raises(
        PyAnsysSoundException,
        match="No input signal is set. Use OverallLevel.signal.",
    ):
        level_obj.process()


def test_overall_level_get_output():
    """Test OverallLevel get_output method."""
    loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    loader.process()
    f_signal = loader.get_output()[0]

    level_obj = OverallLevel(signal=f_signal)
    level_obj.process()
    output = level_obj.get_output()
    assert type(output) == float
    assert output == pytest.approx(EXP_LEVEL_DEFAULT)

    level_obj.scale = "RMS"
    level_obj.process()
    assert level_obj.get_output() == pytest.approx(EXP_LEVEL_RMS)

    level_obj.scale = "dB"
    level_obj.reference_value = 2e-5
    level_obj.process()
    assert level_obj.get_output() == pytest.approx(EXP_LEVEL_DBSPL)

    level_obj.frequency_weighting = "A"
    level_obj.process()
    assert level_obj.get_output() == pytest.approx(EXP_LEVEL_DBA)

    level_obj.frequency_weighting = "B"
    level_obj.process()
    assert level_obj.get_output() == pytest.approx(EXP_LEVEL_DBB)

    level_obj.frequency_weighting = "C"
    level_obj.process()
    assert level_obj.get_output() == pytest.approx(EXP_LEVEL_DBC)


def test_overall_level_get_output_warnings():
    """Test OverallLevel get_output method warnings."""
    level_obj = OverallLevel()
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the OverallLevel.process\\(\\) method.",
    ):
        output = level_obj.get_output()
    assert output is None


def test_overall_level_get_output_as_nparray():
    """Test OverallLevel get_output_as_nparray method."""
    loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    loader.process()
    f_signal = loader.get_output()[0]

    level_obj = OverallLevel(signal=f_signal)
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the OverallLevel.process\\(\\) method.",
    ):
        assert level_obj.get_output_as_nparray() is None

    level_obj.process()
    output = level_obj.get_output_as_nparray()
    assert type(output) == np.ndarray
    assert len(output) == 1
    assert output[0] == pytest.approx(EXP_LEVEL_DEFAULT)


def test_overall_level_get_level():
    """Test OverallLevel get_level method."""
    loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    loader.process()
    f_signal = loader.get_output()[0]

    level_obj = OverallLevel(signal=f_signal)
    level_obj.process()
    output = level_obj.get_level()
    assert type(output) == float
    assert output == pytest.approx(EXP_LEVEL_DEFAULT)
