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
    return pathlib.Path(__file__).parents[5].joinpath("tests/data/flute.wav")
