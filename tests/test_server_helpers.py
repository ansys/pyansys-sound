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

from ansys.tools.common.exceptions import VersionError, VersionSyntaxError
import pytest

from ansys.sound.core.server_helpers import (
    _check_sound_version,
    _check_sound_version_and_raise,
    connect_to_or_start_server,
    requires_sound_version,
    validate_dpf_sound_connection,
)


def test_validate_dpf_sound_connection():
    validate_dpf_sound_connection()


def test_connect_to_or_start_server():
    s = connect_to_or_start_server(port="6780", ip="127.0.0.1", use_license_context=True)
    print(s)


def test_requires_sound_version():
    """Test the requires_sound_version decorator."""

    # Wrong version specifier type => version syntax error (at instantiation).
    class DummyClass:
        """A dummy class to test version type error in the requires_sound_version decorator."""

        @requires_sound_version(1000)
        def dummy_method_type_error(self):
            pass

    with pytest.raises(
        VersionSyntaxError,
        match=(
            "Version argument must be a string with the form YEAR.MAJOR.MINOR, for example "
            "'2026.1.0'."
        ),
    ):
        DummyClass().dummy_method_type_error()

    class DummyClass:
        """A dummy class to test the requires_sound_version decorator."""

        @requires_sound_version("2024.2.0")
        def dummy_method_pass(self):
            return "This method requires DPF Sound plugin version 2024.2.0 or higher."

        @requires_sound_version("3000.0.0")
        def dummy_method_fail(self):
            return "This method requires DPF Sound plugin version 3000.0.0 or higher."

    # This should NOT raise an exception (plugin version always > 2024.2.0)
    dummy = DummyClass()
    result = dummy.dummy_method_pass()
    assert result == "This method requires DPF Sound plugin version 2024.2.0 or higher."

    # This should raise an exception (plugin version always < 3000.0.0)
    # If plugin >= 2027 R1, the raised error is that of a version mismatch.
    # If plugin < 2027 R1, the raised error is that of an unknown version, because 3000.0.0 is not
    # in the matching versions dictionary.
    if not pytest.SOUND_VERSION_GREATER_THAN_OR_EQUAL_TO_2027R1:
        error_message = "Unknown DPF Sound plugin version 3000.0.0."
    else:
        error_message = (
            "DPF Sound plugin version error: Function or method `dummy_method_fail\(\)` requires "
            "DPF Sound plugin version 3000.0.0 or higher."
        )
    with pytest.raises(VersionError, match=error_message):
        dummy.dummy_method_fail()


def test__check_sound_version():
    """Test the _check_sound_version function."""
    # Version met.
    assert _check_sound_version("2024.2.0")

    # Version NOT met.
    if not pytest.SOUND_VERSION_GREATER_THAN_OR_EQUAL_TO_2027R1:
        # If plugin < 2027 R1, there are two cases to test:
        # The version exists in the dictionary but is not met.
        assert not _check_sound_version("2027.1.0")
        # The version does not exist in the dictionary.
        with pytest.raises(VersionError, match=("Unknown DPF Sound plugin version 3000.0.0.")):
            _check_sound_version("3000.0.0")
    else:
        # If plugin >= 2027 R1, the version can be anything (as long as it is higher).
        assert not _check_sound_version("3000.0.0")

    # Wrong version specifier type => version syntax error.
    with pytest.raises(
        VersionSyntaxError,
        match=(
            "Version argument must be a string with the form YEAR.MAJOR.MINOR, for example "
            "'2026.1.0'."
        ),
    ):
        _check_sound_version(None)


def test__check_sound_version_and_raise():
    """Test the _check_sound_version_and_raise function."""
    # Version met.
    _check_sound_version_and_raise("2024.2.0", "Test error message.")

    # Version NOT met.
    if not pytest.SOUND_VERSION_GREATER_THAN_OR_EQUAL_TO_2027R1:
        # Check error with an unmatched, but known version => 2027R1.
        test_version = "2027.1.0"
    else:
        # Check error with any unmatchable version.
        test_version = "3000.0.0"
    with pytest.raises(
        VersionError,
        match="DPF Sound plugin version error: Test error message.",
    ):
        _check_sound_version_and_raise(test_version, "Test error message.")
