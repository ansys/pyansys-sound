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

"""Functions to download sample datasets from the PyAnsys Sound examples repository."""
from functools import wraps
import os
import shutil

from ansys.dpf.core import server as server_module
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


def _get_example_file_url(filename):  # pragma no cover
    """Get the URL of the example file in the PyAnsys Sound examples repository.

    Parameters
    ----------
    filename : str
        File in https://github.com/ansys/example-data/raw/main/pyansys-sound/

    Returns
    -------
    File url
    """
    return f"https://github.com/ansys/example-data/raw/main/pyansys-sound/{filename}"  # noqa: E231


@check_directory_exist(EXAMPLES_PATH)
def _download_file_in_local_tmp_folder(url, filename):  # pragma no cover
    """Download a file from the PyAnsys Sound examples repository to the local tmp folder.

    Parameters
    ----------
    url : str
        Url of the file to download.
        This url can be provided using _get_example_file_url() function.

    filename : str
        File name in the local tmp folder.

    Returns
    -------
    Local path of the downloaded file.
    """
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


def _download_example_file_to_server_tmp_folder(filename, server=None):  # pragma no cover
    """Download a PyAnsys Sound example file and make it available to the DPF server.

    If the server is remote, the file is uploaded to the server's temporary folder, and the remote
    path is returned. Otherwise, the local download path is returned.

    Parameters
    ----------
    filename : str
        Example file name.

    server : ansys.dpf.core.server.Server, default: None
        DPF server to which to upload the file (if remote).
        If None, attempts to use the global server.

    Returns
    -------
    str
        Path of the file on the DPF server.
    """
    # get file url in git repo
    url = _get_example_file_url(filename)
    try:
        # download file locally
        local_path = _download_file_in_local_tmp_folder(url, filename)
        if server is None:
            # If no server is provided, retrieve the global server
            server = server_module.get_or_create_server(server)
        if server.has_client():
            # If the server has a client, then it is a remote server and we need to upload the file
            # to the server's temporary folder.
            return upload_file_in_tmp_folder(file_path=local_path, server=server)
        # Otherwise, the server is a local server, and we can use the local path directly
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

    As flute_psd.txt file is opened using python 'open' function,
    we need the local path of the file.

    Examples
    --------
    >>> from ansys.sound.core.examples_helpers import download_flute_psd
    >>> filename = print(download_flute_psd()[0])

    Returns
    -------
    str
        Local path for the ``flute_psd.txt`` file.
    """
    url = _get_example_file_url("flute_psd.txt")
    try:
        # download file locally
        local_path = _download_file_in_local_tmp_folder(url, "flute_psd.txt")
    except Exception as e:  # Generate exception # pragma no cover
        raise RuntimeError(
            "For the reason that follows, retrieving the file failed.\n"
            "You can download this file from:\n"
            f"{url}\n"
            "\n"
            "The reported error message is:\n"
            f"{str(e)}"
        )

    return local_path


def download_flute_wav(server=None):
    """Download the ``flute.wav`` file.

    Returns
    -------
    str
        Path for the ``flute.wav`` file.
    """
    return _download_example_file_to_server_tmp_folder("flute.wav", server=server)


def download_accel_with_rpm_wav(server=None):
    """Download the ``accel_with_rpm.wav`` file.

    Returns
    -------
    str
        Path for the ``accel_with_rpm.wav`` file.
    """
    return _download_example_file_to_server_tmp_folder("accel_with_rpm.wav", server=server)


def download_accel_with_rpm_2_wav(server=None):
    """Download the ``accel_with_rpm_2.wav`` file.

    Returns
    -------
    str
        Path for the ``accel_with_rpm_2.wav`` file.
    """
    return _download_example_file_to_server_tmp_folder("accel_with_rpm_2.wav", server=server)


def download_accel_with_rpm_3_wav(server=None):
    """Download the ``accel_with_rpm_3.wav`` file.

    Returns
    -------
    str
        Path for the ``accel_with_rpm_3.wav`` file.
    """
    return _download_example_file_to_server_tmp_folder("accel_with_rpm_3.wav", server=server)


def download_xtract_demo_signal_1_wav(server=None):
    """Download the ``xtract_demo_signal_1.wav`` file.

    Returns
    -------
    str
        Path for the ``xtract_demo_signal_1.wav`` file.
    """
    return _download_example_file_to_server_tmp_folder("xtract_demo_signal_1.wav", server=server)


def download_xtract_demo_signal_2_wav(server=None):
    """Download the ``xtract_demo_signal_2.wav`` file.

    Returns
    -------
    str
        Path for the ``xtract_demo_signal_2.wav`` file.
    """
    return _download_example_file_to_server_tmp_folder("xtract_demo_signal_2.wav", server=server)


def download_fan_wav(server=None):
    """Download the ``Fan.wav`` file.

    Returns
    -------
    str
        Path for the ``Fan.wav`` file.
    """
    return _download_example_file_to_server_tmp_folder("Fan.wav", server=server)


def download_aircraft_wav(server=None):
    """Download the ``Aircraft.wav`` file.

    Returns
    -------
    str
        Path for the ``Aircraft.wav`` file.
    """
    return _download_example_file_to_server_tmp_folder("Aircraft.wav", server=server)


def download_aircraft10kHz_wav(server=None):
    """Download the ``Aircraft.wav`` file.

    Returns
    -------
    str
        Path for the ``Aircraft_FS10kHz.wav`` file.
    """
    return _download_example_file_to_server_tmp_folder("Aircraft_FS10kHz.wav", server=server)


def download_sound_composer_project_whatif(server=None):
    """Download the ``SoundComposer-WhatIfScenario-Motor-Gear-HVAC-Noise.scn`` file.

    This file is a Sound Composer project file.

    Returns
    -------
    str
        Path for the ``SoundComposer-WhatIfScenario-Motor-Gear-HVAC-Noise.scn`` file.
    """
    return _download_example_file_to_server_tmp_folder(
        "SoundComposer-WhatIfScenario-Motor-Gear-HVAC-Noise.scn", server=server
    )


def download_sound_composer_source_eMotor(server=None):
    """Download the ``eMotor - FEM - orders levels (harmonics source).txt`` file.

    This file is a Sound Composer source of an eMotor.

    Returns
    -------
    str
        Path for the ``eMotor - FEM - orders levels (harmonics source).txt`` file.
    """
    return _download_example_file_to_server_tmp_folder(
        "eMotor - FEM - orders levels (harmonics source).txt", server=server
    )


def download_sound_composer_source_control_eMotor(server=None):
    """Download the ``eMotor - rpm evolution.txt`` file.

    This file is an eMotor source control, from 250 to 5000 rpm, in 8 seconds.

    Returns
    -------
    str
        Path for the ``eMotor - rpm evolution.txt`` file.
    """
    return _download_example_file_to_server_tmp_folder("eMotor - rpm evolution.txt", server=server)


def download_sound_composer_FRF_eMotor(server=None):
    """Download the ``FRF - eMotor transfer.txt`` file.

    This file is a Frequency Response Function that represents the transfer of the eMotor noise
    to the receiver, to use in Sound Composer track.

    Returns
    -------
    str
        Path for the ``FRF - eMotor transfer.txt`` file.
    """
    return _download_example_file_to_server_tmp_folder("FRF - eMotor transfer.txt", server=server)


def download_sound_composer_source_WindRoadNoise(server=None):
    """Download the ``Wind and Road noise - spectrum vs vehicle speed (BBN source).txt`` file.

    This file is the definition of a source of type broadband noise, which models the wind
    and road noise of a vehicle as a function of the speed. This source is defined between 10 and
    100 km/h, in 10 km/h steps. To be used in Sound Composer track.

    Returns
    -------
    str
        Path for the ``Wind and Road noise - spectrum vs vehicle speed (BBN source).txt`` file.
    """
    return _download_example_file_to_server_tmp_folder(
        "Wind and Road noise - spectrum vs vehicle speed (BBN source).txt", server=server
    )


def download_sound_composer_source_control_WindRoadNoise(server=None):
    """Download the ``WindRoadNoise - vehicle speed.txt`` file.

    This file is a wind and noise source control, evolving from 10 to 100 kph, in 8 seconds.


    Returns
    -------
    str
        Path for the ``WindRoadNoise - vehicle speed.txt`` file.
    """
    return _download_example_file_to_server_tmp_folder(
        "WindRoadNoise - vehicle speed.txt", server=server
    )
