# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ansys.sound.core.standard_levels import OverallLevelParent


def test__overall_level_parent_instantiation():
    """Test OverallLevelParent instantiation."""
    level_obj = OverallLevelParent()
    assert level_obj.scale == "dB"
    assert level_obj.reference_value == 1.0
    assert level_obj.frequency_weighting == ""


def test__overall_level_parent_properties():
    """Test OverallLevelParent properties."""
    level_obj = OverallLevelParent()

    level_obj.scale = "RMS"
    assert level_obj.scale == "RMS"

    level_obj.scale = "dB"
    assert level_obj.scale == "dB"

    level_obj.reference_value = 2e-5
    assert level_obj.reference_value == 2e-5

    level_obj.frequency_weighting = "A"
    assert level_obj.frequency_weighting == "A"

    level_obj.frequency_weighting = "B"
    assert level_obj.frequency_weighting == "B"

    level_obj.frequency_weighting = "C"
    assert level_obj.frequency_weighting == "C"

    level_obj.frequency_weighting = ""
    assert level_obj.frequency_weighting == ""


def test__overall_level_parent_properties_exceptions():
    """Test OverallLevelParent properties exceptions."""
    level_obj = OverallLevelParent()

    with pytest.raises(PyAnsysSoundException, match="The scale type must be either 'dB' or 'RMS'."):
        level_obj.scale = "Invalid"

    with pytest.raises(
        PyAnsysSoundException, match="The reference value must be strictly positive."
    ):
        level_obj.reference_value = -1

    with pytest.raises(
        PyAnsysSoundException, match="The reference value must be strictly positive."
    ):
        level_obj.reference_value = 0

    with pytest.raises(
        PyAnsysSoundException,
        match="The frequency weighting must be one of \\['', 'A', 'B', 'C'\\].",
    ):
        level_obj.frequency_weighting = "Invalid"


def test__overall_level_parent_get_output_warnings():
    """Test OverallLevelParent get_output method warnings."""
    level_obj = OverallLevelParent()
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the OverallLevelParent.process\\(\\) method.",
    ):
        output = level_obj.get_output()
    assert output is None


def test__overall_level_parent_get_output_as_nparray():
    """Test OverallLevelParent get_output_as_nparray method."""
    level_obj = OverallLevelParent()
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the OverallLevelParent.process\\(\\) method.",
    ):
        output = level_obj.get_output_as_nparray()
    assert output is None


def test__overall_level_parent_get_level():
    """Test OverallLevelParent get_level method."""
    level_obj = OverallLevelParent()
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the OverallLevelParent.process\\(\\) method.",
    ):
        output = level_obj.get_level()
    assert output is None
