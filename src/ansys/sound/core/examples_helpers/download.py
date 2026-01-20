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

"""Functions to download example data from the PyAnsys Sound examples repository.

This module provides functions to download example data files used in PyAnsys Sound.

When implementing a new PyAnsys Sound example that requires new example data file(s), a new
download function must be added to this module. Importantly, there are two different cases to
consider:

-   If the example data file requires a DPF Sound operator to open and use (typically WAV files,
    but also Sound Composer project files, and other Ansys file formats), then the file must be
    made available on the DPF server side. In this case, define the download function with a call
    to function :func:`._download_file_and_upload_to_server_tmp_folder`. For example,
    ``path_on_server = _download_file_and_upload_to_server_tmp_folder("my_file.wav", my_server)``.

-   Conversely, if the example data file is opened using Python's standard or third-party libraries
    (for example, CSV files, or non-Ansys text files), then the file must remain local, that is, on
    the client side, where the Python process is running. In this case, define the download
    function with a call to function :func:`._download_file_in_local_examples_folder`. For example,
    ``path_on_client = _download_file_in_local_examples_folder("my_file.csv")``.

Note: in any case, the example data files must be submitted to the PyAnsys Sound examples
repository, through a pull request, for the implemented download function to work. You can create
the pull request by following this link:
https://github.com/ansys/example-data/upload/main/pyansys-sound.
"""

from functools import wraps
import os

from ansys.dpf.core import server as server_module
from ansys.dpf.core import upload_file_in_tmp_folder
import platformdirs
import requests

# Setup data directory
USER_DATA_PATH = platformdirs.user_data_dir(appname="ansys_sound_core", appauthor="Ansys")
if not os.path.exists(USER_DATA_PATH):
    os.makedirs(USER_DATA_PATH)  # pragma: no cover

EXAMPLES_PATH = os.path.join(USER_DATA_PATH, "examples")


def check_directory_exist(directory):
    """Check the existence of a directory."""

    def wrap_function(func):
        @wraps(func)
        def inner_wrapper(*args, **kwargs):
            # Check if folder exists
            if not os.path.exists(directory):
                os.makedirs(directory)  # pragma: no cover

            return func(*args, **kwargs)

        return inner_wrapper

    return wrap_function


def provide_error_context():
    """Capture exceptions and provide additional context in the error message."""

    def wrap_function(func):
        @wraps(func)
        def inner_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:  # pragma: no cover
                raise RuntimeError(
                    "For the reason that follows, retrieving the file failed.\n"
                    "You can download this file from:\n"
                    f"{_get_example_file_url(args[0])}\n"
                    "\n"
                    "The reported error message is:\n"
                    f"{str(e)}"
                )

        return inner_wrapper

    return wrap_function


def _get_example_file_url(filename):
    """Get the URL of the example file in the PyAnsys Sound examples repository.

    Parameters
    ----------
    filename : str
        File in https://github.com/ansys/example-data/raw/main/pyansys-sound/

    Returns
    -------
    File url
    """
    return f"https://github.com/ansys/example-data/raw/main/pyansys-sound/{filename}"


@provide_error_context()
@check_directory_exist(EXAMPLES_PATH)
def _download_file_in_local_examples_folder(filename):
    """Download a file from the PyAnsys Sound examples repository to the local example files folder.

    The specified file is retrieved from the PyAnsys Sound examples repository at the URL
    https://github.com/ansys/example-data/raw/main/pyansys-sound/

    Parameters
    ----------
    filename : str
        File name in the local examples folder.

    Returns
    -------
    Local path of the downloaded example file.
    """
    # Download content.
    remote_file = requests.get(
        _get_example_file_url(filename),
        timeout=10,
    )  # timeout in seconds.

    # Copy content into local file.
    local_path = os.path.join(EXAMPLES_PATH, os.path.basename(filename))
    with open(local_path, "wb") as f:
        f.write(remote_file.content)
    return local_path


@provide_error_context()
def _download_file_and_upload_to_server_tmp_folder(filename, server=None):
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
    # Download file locally.
    local_path = _download_file_in_local_examples_folder(filename)

    if server is None:
        # If no server is provided, retrieve the global server.
        server = server_module.get_or_create_server(server)

    if server.has_client():
        # If the server has a client, then it is a remote server and we need to upload the file
        # to the server's temporary folder.
        return upload_file_in_tmp_folder(file_path=local_path, server=server)  # pragma: no cover
    # Otherwise, the server is a local server, and we can use the local path directly.
    return local_path  # pragma: no cover


def download_flute_psd():
    """Download the `flute_psd.txt` file with the PSD corresponding to `flute.wav`.

    As `flute_psd.txt` is opened using Python's ``open()`` function, and not a DPF Sound operator,
    we do not need to upload the file onto the server side. The local path of the file suffices.

    Returns
    -------
    str
        Local path for the `flute_psd.txt` file.
    """
    return _download_file_in_local_examples_folder("flute_psd.txt")


def download_flute_wav(server=None):
    """Download the ``flute.wav`` file.

    Returns
    -------
    str
        Path for the ``flute.wav`` file.
    """
    return _download_file_and_upload_to_server_tmp_folder("flute.wav", server=server)


def download_accel_with_rpm_wav(server=None):
    """Download the ``accel_with_rpm.wav`` file.

    Returns
    -------
    str
        Path for the ``accel_with_rpm.wav`` file.
    """
    return _download_file_and_upload_to_server_tmp_folder("accel_with_rpm.wav", server=server)


def download_accel_with_rpm_2_wav(server=None):
    """Download the ``accel_with_rpm_2.wav`` file.

    Returns
    -------
    str
        Path for the ``accel_with_rpm_2.wav`` file.
    """
    return _download_file_and_upload_to_server_tmp_folder("accel_with_rpm_2.wav", server=server)


def download_accel_with_rpm_3_wav(server=None):
    """Download the ``accel_with_rpm_3.wav`` file.

    Returns
    -------
    str
        Path for the ``accel_with_rpm_3.wav`` file.
    """
    return _download_file_and_upload_to_server_tmp_folder("accel_with_rpm_3.wav", server=server)


def download_xtract_demo_signal_1_wav(server=None):
    """Download the ``xtract_demo_signal_1.wav`` file.

    Returns
    -------
    str
        Path for the ``xtract_demo_signal_1.wav`` file.
    """
    return _download_file_and_upload_to_server_tmp_folder("xtract_demo_signal_1.wav", server=server)


def download_xtract_demo_signal_2_wav(server=None):
    """Download the ``xtract_demo_signal_2.wav`` file.

    Returns
    -------
    str
        Path for the ``xtract_demo_signal_2.wav`` file.
    """
    return _download_file_and_upload_to_server_tmp_folder("xtract_demo_signal_2.wav", server=server)


def download_fan_wav(server=None):
    """Download the ``Fan.wav`` file.

    Returns
    -------
    str
        Path for the ``Fan.wav`` file.
    """
    return _download_file_and_upload_to_server_tmp_folder("Fan.wav", server=server)


def download_aircraft_wav(server=None):
    """Download the ``Aircraft.wav`` file.

    Returns
    -------
    str
        Path for the ``Aircraft.wav`` file.
    """
    return _download_file_and_upload_to_server_tmp_folder("Aircraft.wav", server=server)


def download_aircraft10kHz_wav(server=None):
    """Download the ``Aircraft.wav`` file.

    Returns
    -------
    str
        Path for the ``Aircraft_FS10kHz.wav`` file.
    """
    return _download_file_and_upload_to_server_tmp_folder("Aircraft_FS10kHz.wav", server=server)


def download_turbo_whistling_wav(server=None):
    """Download the ``Turbo_Whistling.wav`` file.

    Returns
    -------
    str
        Path for the ``Turbo_Whistling.wav`` file.
    """
    return _download_file_and_upload_to_server_tmp_folder("Turbo_Whistling.wav", server=server)


def download_sound_composer_project_whatif(server=None):
    """Download the ``SoundComposer-WhatIfScenario-Motor-Gear-HVAC-Noise.scn`` file.

    This file is a Sound Composer project file.

    Returns
    -------
    str
        Path for the ``SoundComposer-WhatIfScenario-Motor-Gear-HVAC-Noise.scn`` file.
    """
    return _download_file_and_upload_to_server_tmp_folder(
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
    return _download_file_and_upload_to_server_tmp_folder(
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
    return _download_file_and_upload_to_server_tmp_folder(
        "eMotor - rpm evolution.txt",
        server=server,
    )


def download_sound_composer_FRF_eMotor(server=None):
    """Download the ``FRF - eMotor transfer.txt`` file.

    This file is a Frequency Response Function that represents the transfer of the eMotor noise
    to the receiver, to use in Sound Composer track.

    Returns
    -------
    str
        Path for the ``FRF - eMotor transfer.txt`` file.
    """
    return _download_file_and_upload_to_server_tmp_folder(
        "FRF - eMotor transfer.txt",
        server=server,
    )


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
    return _download_file_and_upload_to_server_tmp_folder(
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
    return _download_file_and_upload_to_server_tmp_folder(
        "WindRoadNoise - vehicle speed.txt", server=server
    )


def download_HVAC_test_wav(server=None):
    """Download the ``HVAC_test.wav`` file.

    This file is a stationary automotive HVAC noise.

    Returns
    -------
    str
        Path for the ``HVAC_test.wav`` file.
    """
    return _download_file_and_upload_to_server_tmp_folder("HVAC_test.wav", server=server)


def download_all_carHVAC_wav(server=None) -> str:
    """Download all the ``carHVAC<i>.wav`` files.

    This function downloads 20 WAV files named ``carHVAC1.wav`` to ``carHVAC20.wav``.

    Returns
    -------
    str
        Path where the ``carHVAC<i>.wav`` files are located.
    """
    for i in range(20):
        filepath = _download_file_and_upload_to_server_tmp_folder(
            f"carHVAC{i+1}.wav",
            server=server,
        )
    return os.path.dirname(filepath)


def download_JLT_CE_data_csv():
    """Download the ``JLT_CE_data.csv`` file.

    As JLT_CE_data.csv file is opened using Python's ``csv`` package, we need the local path of the
    file.

    Returns
    -------
    str
        Local path for the ``JLT_CE_data.csv`` file.
    """
    return _download_file_in_local_examples_folder("JLT_CE_data.csv")
