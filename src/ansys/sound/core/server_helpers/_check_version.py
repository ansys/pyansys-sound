# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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

"""Helpers to check DPF Sound plugin version."""

from functools import wraps
from typing import Any, Callable

from ansys.dpf.core import Operator, _global_server, available_operator_names, types
from ansys.tools.common.exceptions import VersionError, VersionSyntaxError
from packaging.version import parse

# Dictionary mapping DPF Sound plugin versions to corresponding DPF Server versions.
MATCHING_VERSIONS = {
    "2024.2.0": "8.0",
    "2025.1.0": "9.0",
    "2025.2.0": "10.0",
    "2026.1.0": "11.0",
    "2027.1.0": "12.0",
}


def requires_sound_version(min_sound_version: str) -> Callable:
    """Check that the current DPF Sound plugin matches or is higher than a certain version.

    This decorator ensures that the decorated function or method can only be used if the current
    DPF Sound plugin version allows it.

    Parameters
    ----------
    min_sound_version : str
        Minimum DPF Sound plugin version required for the decorated function or method.
        The version must be specified as a string with the form YEAR.MAJOR.MINOR, for example
        "2026.1.0".

    Returns
    -------
    callable
        The decorator.

    .. note::
       This function must be used as a function or method decorator.
    """

    def decorator(func) -> Callable:
        """Wrap the original function or method to include DPF Sound plugin version check.

        Parameters
        ----------
        func : callable
            The function or method to which the decorator applies.

        Returns
        -------
        callable
            The wrapped function or method.
        """
        if not isinstance(min_sound_version, str):
            raise VersionSyntaxError(
                "requires_sound_version decorator argument must be a string with the form "
                "YEAR.MAJOR.MINOR, for example '2026.1.0'."
            )

        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            """Check DPF Sound plugin version before calling the original function or method.

            Returns
            -------
            Any
                The original function's or method's output.
            """
            _check_sound_version_and_raise(
                min_sound_version,
                (
                    f"Function or method `{func.__name__}()` requires DPF Sound plugin version "
                    f"{min_sound_version} or higher."
                ),
            )
            return func(*args, **kwargs)

        return wrapper

    return decorator


def _check_sound_version_and_raise(min_sound_version: str, error_msg: str):
    """Check the DPF Sound plugin version and raise an exception if the specified version is higher.

    Parameters
    ----------
    min_sound_version : str
        Minimum DPF Sound plugin version required.
    error_msg : str
        Error message to display if the version check fails.
    """
    if not _check_sound_version(min_sound_version):
        raise VersionError(f"DPF Sound plugin version error: {error_msg}")


def _check_sound_version(min_sound_version: str) -> bool:
    """Check the DPF Sound plugin version.

    Before Ansys 2027 R1, the DPF Sound plugin version is verified according to the DPF Server/DPF
    Sound version matching dictionary. From Ansys 2027 R1 onwards, the DPF Sound plugin version is
    retrieved directly from the server.

    Parameters
    ----------
    min_sound_version : str
        Minimum DPF Sound plugin version required.

    Returns
    -------
    bool
        True if the current DPF Sound plugin version is greater than or equal to the specified
        version, False otherwise.
    """
    if "get_version_info" not in available_operator_names():
        # Operator get_version_info is only introduced in Ansys 2027 R1, so if it does not exist,
        # we use the matching DPF server version to perform the check.
        if min_sound_version not in MATCHING_VERSIONS:
            raise VersionError(f"Unknown DPF Sound plugin version {min_sound_version}.")

        return _global_server().meet_version(MATCHING_VERSIONS[min_sound_version])

    version_retriever = Operator("get_version_info")
    version_retriever.run()
    year = version_retriever.get_output(0, types.int)
    major = version_retriever.get_output(1, types.int)
    minor = version_retriever.get_output(2, types.int)

    return parse(f"{year}.{major}.{minor}") >= parse(min_sound_version)
