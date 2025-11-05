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
from ansys.dpf.gate.errors import DpfVersionNotSupported

from ansys.sound.core.server_helpers import (_check_dpf_version,
                                             connect_to_or_start_server,
                                             requires_dpf_version,
                                             validate_dpf_sound_connection)


def test_validate_dpf_sound_connection():
    validate_dpf_sound_connection()


def test_connect_to_or_start_server():
    s = connect_to_or_start_server(port="6780", ip="127.0.0.1", use_license_context=True)
    print(s)


def test_requires_dpf_version():
    """Test the requires_dpf_version decorator."""

    # Wrong version specifier type => type error (at definition).
    with pytest.raises(
        TypeError,
        match=(
            "requires_dpf_version decorator argument must be a string with the form MAJOR.MINOR, "
            "for example '11.0'."
        ),
    ):

        class DummyClass:
            """A dummy class to test type error in the requires_dpf_version decorator."""

            @requires_dpf_version(5.0)
            def dummy_method_type_error(self):
                pass

    class DummyClass:
        """A dummy class to test the requires_dpf_version decorator."""

        @requires_dpf_version("1.0")
        def dummy_method_pass(self):
            return "This method requires DPF version 1.0 or higher."

        @requires_dpf_version("666.0")
        def dummy_method_fail(self):
            return "This method requires DPF version 666.0 or higher."

    # This should NOT raise an exception if the server version is 1.0 or higher
    DC = DummyClass()
    result = DC.dummy_method_pass()
    assert result == "This method requires DPF version 1.0 or higher."

    # This should raise an exception if the server version is lower than 666.0
    with pytest.raises(
        DpfVersionNotSupported,
        match=(
            "Method `dummy_method_fail` of class `DummyClass` requires DPF server version 666.0 or "
            "higher."
        ),
    ):
        DC.dummy_method_fail()


def test__check_dpf_version():
    """Test the _check_dpf_version function."""

    # This should NOT raise an exception if the server version is 1.0 or higher
    _check_dpf_version("1.0", "Test error message.")

    # This should raise an exception if the server version is lower than 666.0
    with pytest.raises(
        DpfVersionNotSupported,
        match=("Test error message."),
    ):
        _check_dpf_version("666.0", "Test error message.")
