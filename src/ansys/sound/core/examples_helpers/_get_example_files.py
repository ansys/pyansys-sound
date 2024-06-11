# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
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

"""Helpers to get examples files for PyAnsys Sound."""
import os
import pathlib


def get_absolute_path_for_flute_wav() -> str:
    """Get the absolute path for the file flute.wav.

    Returns
    -------
    str
        Absolute path to flute.wav .
    """
    return _get_absolute_path("flute.wav")


def get_absolute_path_for_xtract_demo_signal_1_wav() -> str:
    r"""Get the absolute path for the file xtract_demo_signal_1.wav.

    Returns
    -------
    str
        Absolute path to xtract_demo_signal_1.wav .
    """
    return _get_absolute_path("xtract_demo_signal_1.wav")


def get_absolute_path_for_xtract_demo_signal_2_wav() -> str:
    r"""Get the absolute path for the file xtract_demo_signal_2.wav.

    Returns
    -------
    str
        Absolute path to xtract_demo_signal_2.wav .
    """
    return _get_absolute_path("xtract_demo_signal_2.wav")


def get_absolute_path_for_flute2_wav() -> str:
    """Get the absolute path for the file flute2.wav.

    Returns
    -------
    str
        Absolute path to flute2.wav .
    """
    return _get_absolute_path("flute2.wav")


def get_absolute_path_for_accel_with_rpm_wav() -> str:
    """Get the absolute path for the file accel_with_rpm.wav.

    Returns
    -------
    str
        Absolute path to accel_with_rpm.wav .
    """
    return _get_absolute_path("accel_with_rpm.wav")


def get_absolute_path_for_sharp_noise_wav() -> str:
    """Get the absolute path for the file sharp_noise.wav.

    Returns
    -------
    str
        Absolute path to sharp_noise.wav .
    """
    return _get_absolute_path("sharp_noise.wav")


def get_absolute_path_for_sharper_noise_wav() -> str:
    """Get the absolute path for the file sharper_noise.wav.

    Returns
    -------
    str
        Absolute path to sharper_noise.wav .
    """
    return _get_absolute_path("sharper_noise.wav")


def get_absolute_path_for_rough_noise_wav() -> str:
    """Get the absolute path for the file rough_noise.wav.

    Returns
    -------
    str
        Absolute path to rough_noise.wav .
    """
    return _get_absolute_path("rough_noise.wav")


def get_absolute_path_for_rough_tone_wav() -> str:
    """Get the absolute path for the file rough_tone.wav.

    Returns
    -------
    str
        Absolute path to rough_tone.wav .
    """
    return _get_absolute_path("rough_tone.wav")


def get_absolute_path_for_fluctuating_noise_wav() -> str:
    """Get the absolute path for the file fluctuating_noise.wav.

    Returns
    -------
    str
        Absolute path to fluctuating_noise.wav .
    """
    return _get_absolute_path("fluctuating_noise.wav")


def get_absolute_path_for_fluctuating_tone_wav() -> str:
    """Get the absolute path for the file fluctuating_tone.wav.

    Returns
    -------
    str
        Absolute path to fluctuating_tone.wav .
    """
    return _get_absolute_path("fluctuating_tone.wav")


def get_absolute_path_for_flute_psd_txt() -> str:
    """Get the absolute path for the file flute_psd.txt.

    Returns
    -------
    str
        Absolute path to flute_psd.txt .
    """
    for parent in pathlib.Path(__file__).parents:  # pragma: no cover
        if (parent / "tests/data/" / "flute_psd.txt").exists():
            p = parent / "tests/data/" / "flute_psd.txt"
            return p.as_posix()


def _get_absolute_path(filename: str) -> str:
    """Get the absolute path for the file specified in filename.

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
        if (parent / "tests/data/" / filename).exists():
            p = parent / "tests/data/" / filename
            return p.as_posix()
