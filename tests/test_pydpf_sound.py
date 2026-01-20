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

from unittest import mock

from ansys.dpf.core import FieldsContainer, field_from_array, fields_container_factory
from ansys.tools.common.exceptions import VersionError, VersionSyntaxError
import numpy as np
import pytest

from ansys.sound.core._pyansys_sound import (
    PyAnsysSound,
    PyAnsysSoundException,
    PyAnsysSoundWarning,
    convert_fields_container_to_np_array,
    scipy_required,
)


def test_pyansys_sound_init_subclass():
    """Test PyAnsySound subclass initialization with DPF version."""

    # Define a subclass requiring DPF Sound plugin version 1000.0.0 or higher => no error.
    class TestClass(PyAnsysSound, min_sound_version="1000.0.0"):
        """Some docstring to test version addition to documentation."""

        pass

    assert TestClass._min_sound_version == "1000.0.0"

    # Wrong version specifier type => type error (at definition).
    with pytest.raises(
        VersionSyntaxError,
        match=(
            "In class definition, `min_sound_version` argument must be a string with the form "
            'YEAR.MAJOR.MINOR, for example "2026.1.0".'
        ),
    ):

        class TestClass(PyAnsysSound, min_sound_version=1.0):
            pass

    # Define a subclass where the DPF Sound plugin version requirement is not met  => error (at
    # instantiation).
    if not pytest.SOUND_VERSION_GREATER_THAN_OR_EQUAL_TO_2027R1:
        # If plugin < 2027 R1, we must use an unmatched, but known version.
        test_version = "2027.1.0"
    else:
        # If plugin >= 2027 R1, the version can be anything, as long as it is higher than the
        # latest to date.
        test_version = "3000.0.0"

    class TestClass(PyAnsysSound, min_sound_version=test_version):
        pass

    with pytest.raises(
        VersionError,
        match=f"Class `TestClass` requires DPF Sound plugin version {test_version} or higher.",
    ):
        TestClass()


def test_pyansys_sound_instantiate():
    pyansys_sound = PyAnsysSound()
    assert pyansys_sound != None


def test_pyansys_sound_process():
    pyansys_sound = PyAnsysSound()
    with pytest.warns(
        PyAnsysSoundWarning, match="This method is not implemented for class PyAnsysSound."
    ):
        pyansys_sound.process()
    assert pyansys_sound.process() == None


def test_pyansys_sound_plot():
    pyansys_sound = PyAnsysSound()
    with pytest.warns(
        PyAnsysSoundWarning, match="This method is not implemented for class PyAnsysSound."
    ):
        pyansys_sound.plot()

    assert pyansys_sound.plot() == None


def test_pyansys_sound_get_output():
    pyansys_sound = PyAnsysSound()
    with pytest.warns(
        PyAnsysSoundWarning, match="This method is not implemented for class PyAnsysSound."
    ):
        pyansys_sound.get_output()
    out = pyansys_sound.get_output()
    assert out == None


def test_pyansys_sound_get_output_as_nparray():
    pyansys_sound = PyAnsysSound()
    with pytest.warns(
        PyAnsysSoundWarning, match="This method is not implemented for class PyAnsysSound."
    ):
        pyansys_sound.get_output_as_nparray()
    out = pyansys_sound.get_output_as_nparray()
    assert type(out) == type(np.empty(0))
    assert np.size(out) == 0
    assert np.shape(out) == (0,)


def test_convert_fields_container_to_np_array():
    """Test conversion of DPF fields container to NumPy array."""

    # Wrong input type => exception.
    with pytest.raises(PyAnsysSoundException, match="Input must be a DPF fields container."):
        convert_fields_container_to_np_array(None)

    # Empty fields container => empty NumPy array.
    fc = FieldsContainer()
    np_array = convert_fields_container_to_np_array(fc)
    assert isinstance(np_array, np.ndarray)
    assert len(np_array) == 0

    # Fields container with one field => 1D NumPy array.
    f1 = field_from_array([5.0, 48.0, 27.0])
    fc = fields_container_factory.over_time_freq_fields_container([f1])
    np_array = convert_fields_container_to_np_array(fc)
    assert isinstance(np_array, np.ndarray)
    assert len(np_array) == 3
    assert np_array.tolist() == [5.0, 48.0, 27.0]

    # Fields container with two fields => 2D NumPy array.
    f2 = field_from_array([12.0, 34.0, 49.0])
    fc = fields_container_factory.over_time_freq_fields_container([f1, f2])
    np_array = convert_fields_container_to_np_array(fc)
    assert isinstance(np_array, np.ndarray)
    assert len(np_array) == 2
    assert isinstance(np_array[0], np.ndarray)
    assert np_array[0].tolist() == [5.0, 48.0, 27.0]
    assert isinstance(np_array[1], np.ndarray)
    assert np_array[1].tolist() == [12.0, 34.0, 49.0]


def test_pyansys_sound_scipy_required():
    """Test the scipy_required decorator."""

    class TestClass(PyAnsysSound):
        @scipy_required
        def test_method(self):
            return "Package found"

    test_instance = TestClass()

    # Simulate SciPy not being installed to test exception raised.
    with mock.patch.dict("sys.modules", {"scipy": None}):
        with pytest.raises(
            PyAnsysSoundException,
            match=(
                "The function or method `test_method\(\)` requires the SciPy Python library to be "
                "installed. You can install SciPy by running `pip install scipy`, for example."
            ),
        ):
            test_instance.test_method()

    # Now test again when SciPy is installed.
    result = test_instance.test_method()
    assert result == "Package found"
