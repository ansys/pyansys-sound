"""Helpers to get examples files for PyDPF Sound."""
import os
import pathlib


def get_absolute_path_for_flute_wav() -> str:
    r"""Get the absolute path for the file flute.wav.

    Returns
    -------
    :
        Absolute path to flute.wav .
    """
    # In case of CI/CD pipelines
    port_in_env = os.environ.get("ANSRV_DPF_SOUND_PORT")
    if port_in_env is not None:
        return "C:\\data\\flute.wav"

    # Obtaining flute.wav path based on the current path
    for parent in pathlib.Path(__file__).parents:
        if (parent / "tests/data/flute.wav").exists():
            p = parent / "tests/data/flute.wav"
            break

    return p.as_posix()
