"""Helpers to get examples files for PyDPF Sound."""
import os
import pathlib
import sys


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

    os.getcwd()
    print("Current Workingdir : {}".format(os.getcwd()))
    print("Sys prefix : {}".format(sys.prefix))
    print("Sys base prefix : {}".format(sys.base_prefix))
    print(p)
    print(p)
    return p
