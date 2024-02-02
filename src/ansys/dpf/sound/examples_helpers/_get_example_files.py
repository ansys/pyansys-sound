"""Helpers to get examples files for PyDPF Sound."""
import pathlib


def get_absolute_path_for_flute_wav() -> str:
    r"""Get the absolute path for the file flute.wav.

    Returns
    -------
    :
        Absolute path to flute.wav .
    """
    # Obtaining flute.wav path based on the current path

    for parent in pathlib.Path(__file__).parents:
        if (parent / "tests/data/flute.wav").exists():
            p = parent / "tests/data/flute.wav"
            break

    return p
