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

import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundWarning
from ansys.sound.core.sound_composer import SourceParent


def test__source_parent_is_source_control_valid():
    """Test SourceParent's is_source_control_valid method."""
    source = SourceParent()

    result = source.is_source_control_valid()
    assert result is False


def test__source_parent_plot_control():
    """Test SourceParent's plot_control method."""
    source = SourceParent()
    source.plot_control()


def test__source_parent_set_from_generic_data_containers():
    """Test SourceParent's set_from_generic_data_containers method."""
    source = SourceParent()
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Cannot set from generic data containers because there is nothing to set here.",
    ):
        source.set_from_generic_data_containers(None, None)


def test__source_parent_get_as_generic_data_containers():
    """Test SourceParent's get_as_generic_data_containers method."""
    source = SourceParent()
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Cannot create generic data containers because there is no data.",
    ):
        gdc_source, gdc_source_control = source.get_as_generic_data_containers()
    assert gdc_source is None
    assert gdc_source_control is None
