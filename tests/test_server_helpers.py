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

import os
from turtle import rt

from ansys.dpf.core import download_file, upload_file_in_tmp_folder
from ansys.dpf.core.server import get_or_create_server
from ansys.tools.common.exceptions import VersionError, VersionSyntaxError
import pytest

from ansys.sound.core.server_helpers import (
    _check_sound_version,
    _check_sound_version_and_raise,
    connect_to_or_start_server,
    requires_sound_version,
    server_download,
    server_upload,
    validate_dpf_sound_connection,
)
from ansys.sound.core.server_helpers._check_version import get_sound_version


def test_validate_dpf_sound_connection():
    """Test the validate_dpf_sound_connection function."""
    validate_dpf_sound_connection()


def test_connect_to_or_start_server():
    """Test the connect_to_or_start_server function."""
    server, license_context = connect_to_or_start_server(use_license_context=False)
    assert server is not None
    assert license_context is None

    server, license_context = connect_to_or_start_server(use_license_context=True)
    assert server is not None
    assert license_context is not None


def test_requires_sound_version():
    """Test the requires_sound_version decorator."""

    # Wrong version specifier type => error (at definition).
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
        # If plugin >= 2027 R1, the version can be anything, as long as it is higher than the
        # latest to date).
        assert not _check_sound_version("3000.0.0")


def test_get_sound_version():
    """Test the get_sound_version function."""
    if not pytest.SOUND_VERSION_GREATER_THAN_OR_EQUAL_TO_2027R1:
        with pytest.raises(
            VersionError,
            match=(
                "Function get_sound_version\(\) requires DPF Sound plugin version 2027.1.0 or "
                "higher."
            ),
        ):
            get_sound_version()
    else:
        version = get_sound_version()
        assert isinstance(version, str)
        assert len(version.split(".")) == 3


@pytest.mark.skipif(pytest.is_server_local, reason="Test only runs with a remote server.")
def test_server_upload_remote_case():
    """Test the server_upload function in the remote server case."""
    local_path1 = pytest.data_path_flute

    # Define a second local path, different from the first to avoid confusion with the original.
    local_path2 = pytest.data_path_flute[:-4] + "_upload_check.wav"
    # Delete the file if it exists.
    if os.path.exists(local_path2):
        os.remove(local_path2)
    assert not os.path.exists(local_path2)

    with server_upload(local_path1) as server_path:
        assert server_path != local_path1 and server_path != local_path2

        # Re-download the uploaded file to check it exists server-side.
        download_file(server_path, local_path2)

    # Verify the downloaded file.
    assert os.path.exists(local_path2)
    assert os.path.getsize(local_path2) == os.path.getsize(local_path1)

    # Clean up.
    os.remove(local_path2)


def test_server_upload_local_case():
    """Test the server_upload function in the local server case."""
    local_path = pytest.data_path_flute

    # Mock a local server.
    server = get_or_create_server(None)
    is_local = server.local_server

    try:
        server.local_server = True

        with server_upload(local_path) as server_path:
            assert server_path == local_path

    finally:
        # Restore the original local_server property.
        server.local_server = is_local


@pytest.mark.skipif(pytest.is_server_local, reason="Test only runs with a remote server.")
def test_server_download_remote_case():
    """Test the server_download function in the remote server case."""
    # Create a dummy file for testing.
    local_path = os.path.join(os.path.dirname(pytest.data_path_flute), "download_check.txt")
    with open(local_path, "w") as f:
        f.write("dummy content")

    with server_download(local_path) as server_path:
        assert server_path != local_path

        # To mock an operator saving a file at the returned server path, upload the dummy file.
        uploaded_path = upload_file_in_tmp_folder(file_path=local_path)
        assert uploaded_path == server_path

        # Delete the local file to later check the download.
        os.remove(local_path)
        assert not os.path.exists(local_path)

    # After exiting the context manager, the file should have been downloaded from the server.
    assert os.path.exists(local_path)

    # Clean up.
    os.remove(local_path)


def test_server_download_local_case():
    """Test the server_download function in the local server case."""
    # Create a dummy file for testing.
    local_path = os.path.join(os.path.dirname(pytest.data_path_flute), "download_check.txt")
    with open(local_path, "w") as f:
        f.write("dummy content")

    # Mock a local server.
    server = get_or_create_server(None)
    is_local = server.local_server

    try:
        server.local_server = True

        with server_download(local_path) as server_path:
            assert server_path == local_path

            # Delete the file.
            os.remove(local_path)
            assert not os.path.exists(local_path)

        # Check that the file is still absent (nothing happened on context manager exit).
        assert not os.path.exists(local_path)

    finally:
        # Restore the original local_server property.
        server.local_server = is_local

        # Clean up if necessary.
        if os.path.exists(local_path):
            os.remove(local_path)
