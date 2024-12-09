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
from ansys.sound.core.xtract.xtract_transient_parameters import XtractTransientParameters


def test_xtract_transient_parameters_instantiation():
    xtract_transient_parameters = XtractTransientParameters()
    assert xtract_transient_parameters != None


def test_xtract_transient_parameters_getter_setter_upper_threshold():
    xtract_transient_parameters = XtractTransientParameters()

    # Invalid value
    with pytest.raises(PyAnsysSoundException) as excinfo:
        xtract_transient_parameters.upper_threshold = 150.0
    assert str(excinfo.value) == "Upper threshold must be between 0.0 and 100.0 dB."

    xtract_transient_parameters.upper_threshold = 92.0

    assert xtract_transient_parameters.upper_threshold == 92.0


def test_xtract_transient_parameters_getter_setter_lower_threshold():
    xtract_transient_parameters = XtractTransientParameters()

    # Invalid value
    with pytest.raises(PyAnsysSoundException) as excinfo:
        xtract_transient_parameters.lower_threshold = 150.0
    assert str(excinfo.value) == "Lower threshold must be between 0.0 and 100.0 dB."

    xtract_transient_parameters.lower_threshold = 92.0

    assert xtract_transient_parameters.lower_threshold == 92.0


def test_xtract_transient_parameters_getter_generic_data_container():
    xtract_transient_parameters = XtractTransientParameters()

    gdc = xtract_transient_parameters.get_parameters_as_generic_data_container()
    assert gdc is not None
