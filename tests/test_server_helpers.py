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

from ansys.dpf.gate.errors import DpfVersionNotSupported
import pytest

from ansys.sound.core.server_helpers import (
    connect_to_or_start_server,
    validate_dpf_sound_connection,
    version_requires,
)


def test_validate_dpf_sound_connection():
    validate_dpf_sound_connection()


def test_connect_to_or_start_server():
    s = connect_to_or_start_server(port="6780", ip="127.0.0.1", use_license_context=True)
    print(s)


def test_version_requires():
    """Test the version_requires decorator."""

    class DummyClass:
        """A dummy class to test the version_requires decorator."""

        def __init__(self):
            self.__dummy = None

        @version_requires("1.0")
        def dummy_method_pass(self):
            return "This function requires DPF version 1.0 or higher."

        @version_requires("666.0")
        def dummy_method_fail(self):
            return "This function requires DPF version 666.0 or higher."

    # This should NOT raise an exception if the server version is 1.0 or higher
    DC = DummyClass()
    result = DC.dummy_method_pass()
    assert result == "This function requires DPF version 1.0 or higher."

    # This should raise an exception if the server version is lower than 666.0
    with pytest.raises(
        DpfVersionNotSupported,
        match=(
            "Function `dummy_method_fail` of class `DummyClass` requires DPF server"
            " version 666.0 or higher."
        ),
    ):
        DC.dummy_method_fail()
