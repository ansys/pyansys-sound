"""Functions to download sample datasets from the pyansys data repository."""
from functools import wraps
import os
import shutil
import urllib.request
import zipfile

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


@check_directory_exist(EXAMPLES_PATH)
def _decompress(filename):  # pragma no cover
    zip_ref = zipfile.ZipFile(filename, "r")
    zip_ref.extractall(EXAMPLES_PATH)
    return zip_ref.close()


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
        return local_path_no_zip, None

    # Perform download
    saved_file, resp = urllib.request.urlretrieve(url)
    shutil.move(saved_file, local_path)
    if get_ext(local_path) in [".zip"]:
        _decompress(local_path)
        local_path = local_path[:-4]
    return local_path, resp


def _download_file(filename, directory=None, _test=False):  # pragma no cover
    url = _get_file_url(filename, directory)
    try:
        return _retrieve_file(url, filename, _test)
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
    >>> filename = print(download_flute_psd())

    """
    return _download_file("flute_psd.txt", "pyansys-sound")[0]
