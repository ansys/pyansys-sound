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


@pytest.mark.skipif(
    not pytest.SOUND_VERSION_GREATER_THAN_OR_EQUAL_TO_2027R1,
    reason="Operator get_version_info unavailable before 2027 R1.",
)
def test_requires_sound_version():
    """Test the requires_sound_version decorator."""

    # Wrong version specifier type => version syntax error (at definition).
    with pytest.raises(
        VersionSyntaxError,
        match=(
            "requires_sound_version decorator argument must be a string with the form "
            "YEAR.MAJOR.MINOR, for example '2026.1.0'."
        ),
    ):

        class DummyClass:
            """A dummy class to test version type error in the requires_sound_version decorator."""

            @requires_sound_version(1000)
            def dummy_method_type_error(self):
                pass

    class DummyClass:
        """A dummy class to test the requires_sound_version decorator."""

        @requires_sound_version("1000.12.0")
        def dummy_method_pass(self):
            return "This method requires DPF Sound plugin version 1000.12.0 or higher."

        @requires_sound_version("3000.0.0")
        def dummy_method_fail(self):
            return "This method requires DPF Sound plugin version 3000.0.0 or higher."

    # This should NOT raise an exception (plugin version always > 1000.12.0)
    DC = DummyClass()
    result = DC.dummy_method_pass()
    assert result == "This method requires DPF Sound plugin version 1000.12.0 or higher."

    # This should raise an exception (plugin version always < 3000.0.0)
    with pytest.raises(
        VersionError,
        match=(
            "Function or method `dummy_method_fail\(\)` requires DPF Sound plugin version 3000.0.0 "
            "or higher."
        ),
    ):
        DC.dummy_method_fail()


@pytest.mark.skipif(
    not pytest.SOUND_VERSION_GREATER_THAN_OR_EQUAL_TO_2027R1,
    reason="Testing the case where get_version_info is available (ie for 2027 R1 and higher).",
)
def test__check_sound_version_2027R1_or_higher():
    """Test the _check_sound_version function for plugin version >= 2027R1."""
    # Verify that operator get_version_info returns a version >= 2024.2.0
    assert _check_sound_version("2024.2.0")

    # Verify that operator get_version_info returns a version < 3000.1.0
    assert not _check_sound_version("3000.1.0")

    # Wrong version specifier type => version syntax error.
    with pytest.raises(
        VersionSyntaxError,
        match=(
            "Version argument must be a string with the form YEAR.MAJOR.MINOR, for example "
            "'2026.1.0'."
        ),
    ):
        _check_sound_version(None)


@pytest.mark.skipif(
    pytest.SOUND_VERSION_GREATER_THAN_OR_EQUAL_TO_2027R1,
    reason="Testing the case where get_version_info is not available (ie before 2027 R1).",
)
def test__check_sound_version_2026R1_or_lower():
    """Test the _check_sound_version function for plugin version < 2027R1."""
    # Verify that 2024.2.0 is in matching version dictionary and is met with the current version.
    assert _check_sound_version("2024.2.0")

    # Verify that 2027.1.0 is in matching version dictionary and is NOT met with the current
    # version (as this test is skipped when the version is >= 2027 R1).
    assert not _check_sound_version("2027.1.0")

    # Verify that 3000.0.0 is NOT in matching version dictionary.
    with pytest.raises(VersionError, match=("Unknown DPF Sound plugin version 3000.0.0.")):
        _check_sound_version("3000.0.0")


@pytest.mark.skipif(
    not pytest.SOUND_VERSION_GREATER_THAN_OR_EQUAL_TO_2027R1,
    reason="DPF Sound version check require DPF server version 12.0 or higher.",
)
def test__check_sound_version_and_raise():
    """Test the _check_sound_version_and_raise function."""

    # This should NOT raise an exception (plugin version always > 1000.12.0)
    _check_sound_version_and_raise("1000.12.0", "Test error message.")

    # This should raise an exception (plugin version always < 3000.0.0)
    with pytest.raises(VersionError, match=("DPF Sound plugin version error: Test error message.")):
        _check_sound_version_and_raise("3000.0.0", "Test error message.")
