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
def _retrieve_file(url, filename, _test=False):  # pragma no cover
    # First check if file has already been downloaded
    local_path = os.path.join(EXAMPLES_PATH, os.path.basename(filename))
    local_path_no_zip = local_path.replace(".zip", "")
    if os.path.isfile(local_path_no_zip) or os.path.isdir(local_path_no_zip):
        return local_path_no_zip

    # Perform download
    try:
        file_content = requests.get(url, timeout=10).text  # 10 seconds
    except requests.exceptions.Timeout:
        print("Timed out")

    with open(local_path, "w") as f:
        f.write(file_content)
    return local_path


def _download_file(filename, directory=None, _test=False):  # pragma no cover
    url = _get_file_url(filename, directory)
    try:
        local_path = _retrieve_file(url, filename, _test)

        # In case of CI/CD pipelines
        port_in_env = os.environ.get("ANSRV_DPF_SOUND_PORT")
        if port_in_env is not None:
            return "C:\\data\\" + filename
        else:
            return local_path

    except Exception as e:  # Generate exception
        raise RuntimeError(
            "For the reason that follows, retrieving the file failed.\n"
            "You can download this file from:\n"
            f"{url}\n"
            "\n"
            "The reported error message is:\n"
            f"{str(e)}"
        )


def download_flute_psd():
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
    filename = "flute_psd.txt"
    directory = "pyansys-sound"
    url = _get_file_url(filename, directory)
    local_path = _retrieve_file(url, filename, False)
    return local_path


def download_flute_wav():
    """Download the ``flute.wav`` file.

    Returns
    -------
    str
        Path for the ``flute.wav`` file.
    """
    return _download_file("flute.wav", "pyansys-sound")


def download_flute_2_wav():
    """Download the ``flute2.wav`` file.

    Returns
    -------
    str
        Path for the ``flute2.wav`` file.
    """
    return _download_file("flute2.wav", "pyansys-sound")


def download_accel_with_rpm_wav():
    """Download the ``accel_with_rpm.wav`` file.

    Returns
    -------
    str
        Path for the ``accel_with_rpm.wav`` file.
    """
    return _download_file("accel_with_rpm.wav", "pyansys-sound")


def download_accel_with_rpm_2_wav():
    """Download the ``accel_with_rpm_2.wav`` file.

    Returns
    -------
    str
        Path for the ``accel_with_rpm_2.wav`` file.
    """
    return _download_file("accel_with_rpm_2.wav", "pyansys-sound")


def download_accel_with_rpm_3_wav():
    """Download the ``accel_with_rpm_3.wav`` file.

    Returns
    -------
    str
        Path for the ``accel_with_rpm_3.wav`` file.
    """
    return _download_file("accel_with_rpm_3.wav", "pyansys-sound")


def download_xtract_demo_signal_1_wav():
    """Download the ``xtract_demo_signal_1.wav`` file.

    Returns
    -------
    str
        Path for the ``xtract_demo_signal_1.wav`` file.
    """
    return _download_file("xtract_demo_signal_1.wav", "pyansys-sound")


def download_xtract_demo_signal_2_wav():
    """Download the ``xtract_demo_signal_2.wav`` file.

    Returns
    -------
    str
        Path for the ``xtract_demo_signal_2.wav`` file.
    """
    return _download_file("xtract_demo_signal_2.wav", "pyansys-sound")
