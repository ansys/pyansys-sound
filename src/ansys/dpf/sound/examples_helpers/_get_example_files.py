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
    print(os.getcwd())
    full_path_flute_wav = path.abspath("tests/data/flute.wav")
    return full_path_flute_wav
