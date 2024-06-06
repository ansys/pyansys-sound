"""Functions to download sample datasets from the pyansys data repository."""
from functools import wraps
import os
import shutil
import urllib.request

from ansys.sound.core.examples_helpers import EXAMPLES_PATH


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
    saved_file, resp = urllib.request.urlretrieve(url)
    shutil.move(saved_file, local_path)
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

    except Exception as e:  # Genering exception
        raise RuntimeError(
            "For the reason mentioned below, retrieving the file from internet failed.\n"
            "You can download this file from:\n"
            f"{url}\n"
            "\n"
            "The reported error message is:\n"
            f"{str(e)}"
        )


def download_flute_psd():
    """Download PSD of flute.wav.

    Examples
    --------
    >>> from ansys.sound.core.examples_helpers import download_flute_psd
    >>> filename = print(download_flute_psd()[0])

    Returns
    -------
    str
        Local path of flute_psd.txt
    str
        Path on the docker container of flute_psd.txt

    """
    return _download_file("flute_psd.txt", "pyansys-sound")


def download_flute_wav():
    """Download flute.wav.

    Returns
    -------
    str
        Local path of flute.wav
    str
        Path on the docker container of flute.wav
    """
    return _download_file("flute.wav", "pyansys-sound")


def download_flute_2_wav():
    """Download flute2.wav.

    Returns
    -------
    str
        Local path of flute2.wav
    str
        Path on the docker container of flute2.wav
    """
    return _download_file("flute2.wav", "pyansys-sound")


def download_accel_with_rpm_wav():
    """Download accel_with_rpm.wav.

    Returns
    -------
    str
        Local path of accel_with_rpm.wav
    str
        Path on the docker container of accel_with_rpm.wav
    """
    return _download_file("accel_with_rpm.wav", "pyansys-sound")


def download_accel_with_rpm_2_wav():
    """Download accel_with_rpm_2.wav.

    Returns
    -------
    str
        Local path of accel_with_rpm_2.wav
    str
        Path on the docker container of accel_with_rpm_2.wav
    """
    return _download_file("accel_with_rpm_2.wav", "pyansys-sound")


def download_accel_with_rpm_3_wav():
    """Download accel_with_rpm_3.wav.

    Returns
    -------
    str
        Local path of accel_with_rpm_3.wav
    str
        Path on the docker container of accel_with_rpm_3.wav
    """
    return _download_file("accel_with_rpm_3.wav", "pyansys-sound")


def download_xtract_demo_signal_1_wav():
    """Download accel_with_rpm_3.wav.

    Returns
    -------
    str
        Local path of xtract_demo_signal_1.wav
    str
        Path on the docker container of xtract_demo_signal_1.wav
    """
    return _download_file("xtract_demo_signal_1.wav", "pyansys-sound")


def download_xtract_demo_signal_2_wav():
    """Download xtract_demo_signal_2.wav.

    Returns
    -------
    str
        Local path of xtract_demo_signal_2.wav
    str
        Path on the docker container of xtract_demo_signal_2.wav
    """
    return _download_file("xtract_demo_signal_2.wav", "pyansys-sound")
