"""Helpers to get examples files for PyDPF Sound."""
import os
import pathlib


def get_absolute_path_for_flute_wav() -> str:
    r"""Get the absolute path for the file flute.wav.

    Returns
    -------
    str
        Absolute path to flute.wav .
    """
    return _get_absolute_path("flute.wav")


def get_absolute_path_for_flute_modified_wav() -> str:
    r"""Get the absolute path for the file flute.wav.

    Returns
    -------
    str
        Absolute path to flute.wav .
    """
    return _get_absolute_path("flute_modified.wav")


def _get_absolute_path(filename: str) -> str:
    r"""Get the absolute path for the file specified in filename.

    Parameters
    ----------
    filename: str
        Wav file name for which to get the path.

    Returns
    -------
    str
        Absolute path to specified wav file name.
    """
    # In case of CI/CD pipelines
    port_in_env = os.environ.get("ANSRV_DPF_SOUND_PORT")
    if port_in_env is not None:
        return "C:\\data\\" + filename

    # Obtaining flute.wav path based on the current path
    for parent in pathlib.Path(__file__).parents:  # pragma: no cover
        if (parent / "tests/data/" + filename).exists():
            p = parent / "tests/data/" + filename
            return p.as_posix()
