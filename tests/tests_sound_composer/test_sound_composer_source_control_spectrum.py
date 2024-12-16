# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
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

from ansys.sound.core._pyansys_sound import PyAnsysSoundException
from ansys.sound.core.sound_composer import SourceControlSpectrum

EXP_STR = "Duration: 0.0 s\nMethod: IFFT"


def test_source_control_spectrum_instantiation():
    """Test SourceControlSpectrum instantiation."""
    # Test instantiation.
    control = SourceControlSpectrum()
    assert isinstance(control, SourceControlSpectrum)


def test_source_control_spectrum_properties():
    """Test SourceControlSpectrum properties."""
    control = SourceControlSpectrum()

    # Test duration setter.
    control.duration = 1.0
    assert control.duration == 1.0

    # Test method setter.
    control.method = 1
    assert control.method == 1


def test_source_control_spectrum_propertiess_exceptions():
    """Test SourceControlSpectrum properties' exceptions."""
    control = SourceControlSpectrum()

    # Test duration setter exception.
    with pytest.raises(PyAnsysSoundException, match="Duration must be positive."):
        control.duration = -1.0

    # Test method setter exception.
    with pytest.raises(
        PyAnsysSoundException,
        match="Method must be an integer. Available options are:\n1: IFFT\n2: Hybrid",
    ):
        control.method = 3


def test_source_control_spectrum___str__():
    """Test SourceControlSpectrum __str__ method."""
    control = SourceControlSpectrum()
    assert str(control) == EXP_STR
