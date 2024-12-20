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

"""Functions to download sample datasets from the PyAnsys Sound examples repository."""
from functools import wraps
import os
import shutil

from ansys.dpf.core import upload_file_in_tmp_folder
import platformdirs
import requests

# Setup data directory
USER_DATA_PATH = platformdirs.user_data_dir(appname="ansys_sound_core", appauthor="Ansys")
if not os.path.exists(USER_DATA_PATH):  # pragma: no cover
    os.makedirs(USER_DATA_PATH)

EXAMPLES_PATH = os.path.join(USER_DATA_PATH, "examples")


def check_directory_exist(directory):  # pragma no cover
    """Check the existence of a directory."""

    def wrap_function(func):
        @wraps(func)
        def inner_wrapper(*args, **kwargs):
            # Check if folder exists
            if not os.path.exists(directory):
                os.makedirs(directory)

            return func(*args, **kwargs)

        return inner_wrapper

    return wrap_function


def get_ext(filename):  # pragma no cover
    """Extract the extension of the filename."""
    ext = os.path.splitext(filename)[1].lower()
    return ext


def delete_downloads():  # pragma no cover
    """Delete all downloaded examples to free space or update the files."""
    if os.path.exists(EXAMPLES_PATH):
        shutil.rmtree(EXAMPLES_PATH)
    return True


def _get_file_url(filename, directory=None):  # pragma no cover
    if directory:
        return (
            f"https://github.com/ansys/example-data/raw/master/{directory}/{filename}"  # noqa: E231
        )
    return f"https://github.com/ansys/example-data/raw/master/{filename}"  # noqa: E231


@check_directory_exist(EXAMPLES_PATH)
def _retrieve_file(url, filename):  # pragma no cover
    # First check if file has already been downloaded
    local_path = os.path.join(EXAMPLES_PATH, os.path.basename(filename))
    local_path_no_zip = local_path.replace(".zip", "")
    if os.path.isfile(local_path_no_zip) or os.path.isdir(local_path_no_zip):
        return local_path_no_zip

    # Perform download
    try:
        file_content = requests.get(url, timeout=10).content  # 10 seconds
    except requests.exceptions.Timeout:
        print("Timed out")

    with open(local_path, "wb") as f:
        f.write(file_content)
    return local_path


def _download_file_and_retrieve_path_in_dpf_server(
    filename, directory=None, server=None
):  # pragma no cover
    """Download a file from the PyAnsys Sound examples repository and upload it to the DPF server.

    This function downloads a file from the PyAnsys Sound examples repository and uploads it to
    the DPF server. This allows to be independent on the server configuration.

    Parameters
    ----------
    filename : str
        File name.

    directory : str, optional
        Directory where the file is located.
        For PyAnsys Sound repository, should be set to 'pyansys-sound'

    server : ansys.dpf.core.server.Server, optional
        DPF server on which to upload the file, to make it available easily.

    Returns
    -------
    str
        Path on the DPF server on which to find the file.
    """
    # get file url in git repo
    url = _get_file_url(filename, directory)
    try:
        # download file locally
        local_path = _retrieve_file(url, filename)
        # upload file to DPF server,
        # so that we are independent on the server configuration
        server_path = upload_file_in_tmp_folder(file_path=local_path, server=server)
        return server_path

    except Exception as e:  # Generate exception
        raise RuntimeError(
            "For the reason that follows, retrieving the file failed.\n"
            "You can download this file from:\n"
            f"{url}\n"
            "\n"
            "The reported error message is:\n"
            f"{str(e)}"
        )


def download_flute_psd(server=None):
    """Download the PSD of the ``flute.wav`` file.

    Examples
    --------
    >>> from ansys.sound.core.examples_helpers import download_flute_psd
    >>> filename = print(download_flute_psd()[0])

    Returns
    -------
    str
        Local path for the ``flute_psd.txt`` file.
    str
        Path on the Docker container for the ``flute_psd.txt`` file.

    """
    return _download_file_and_retrieve_path_in_dpf_server(
        "flute_psd.txt", "pyansys-sound", server=server
    )


def download_flute_wav(server=None):
    """Download the ``flute.wav`` file.

    Returns
    -------
    str
        Path for the ``flute.wav`` file.
    """
    return _download_file_and_retrieve_path_in_dpf_server(
        "flute.wav", "pyansys-sound", server=server
    )


def download_flute_2_wav(server=None):
    """Download the ``flute2.wav`` file.

    Returns
    -------
    str
        Path for the ``flute2.wav`` file.
    """
    return _download_file_and_retrieve_path_in_dpf_server(
        "flute2.wav", "pyansys-sound", server=server
    )


def download_accel_with_rpm_wav(server=None):
    """Download the ``accel_with_rpm.wav`` file.

    Returns
    -------
    str
        Path for the ``accel_with_rpm.wav`` file.
    """
    return _download_file_and_retrieve_path_in_dpf_server(
        "accel_with_rpm.wav", "pyansys-sound", server=server
    )


def download_accel_with_rpm_2_wav(server=None):
    """Download the ``accel_with_rpm_2.wav`` file.

    Returns
    -------
    str
        Path for the ``accel_with_rpm_2.wav`` file.
    """
    return _download_file_and_retrieve_path_in_dpf_server(
        "accel_with_rpm_2.wav", "pyansys-sound", server=server
    )


def download_accel_with_rpm_3_wav(server=None):
    """Download the ``accel_with_rpm_3.wav`` file.

    Returns
    -------
    str
        Path for the ``accel_with_rpm_3.wav`` file.
    """
    return _download_file_and_retrieve_path_in_dpf_server(
        "accel_with_rpm_3.wav", "pyansys-sound", server=server
    )


def download_xtract_demo_signal_1_wav(server=None):
    """Download the ``xtract_demo_signal_1.wav`` file.

    Returns
    -------
    str
        Path for the ``xtract_demo_signal_1.wav`` file.
    """
    return _download_file_and_retrieve_path_in_dpf_server(
        "xtract_demo_signal_1.wav", "pyansys-sound", server=server
    )


def download_xtract_demo_signal_2_wav(server=None):
    """Download the ``xtract_demo_signal_2.wav`` file.

    Returns
    -------
    str
        Path for the ``xtract_demo_signal_2.wav`` file.
    """
    return _download_file_and_retrieve_path_in_dpf_server(
        "xtract_demo_signal_2.wav", "pyansys-sound", server=server
    )
