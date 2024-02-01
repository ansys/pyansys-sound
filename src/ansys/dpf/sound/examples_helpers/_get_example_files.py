"""Helpers to get examples files for PyDPF Sound."""

import os
from os import path


def get_absolute_path_for_flute_wav() -> str:
    r"""Get the absolute path for the file flute.wav.

    Returns
    -------
    :
        Absolute path to flute.wav .
    """
    # Directory of the current file
    dir_path = os.path.dirname(os.path.realpath(__file__))

    # Obtaining flute.wav path based on the current path
    full_path_flute_wav = path.realpath(dir_path + "../../../../../../tests/data/flute.wav")
    return full_path_flute_wav
