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

"""Helpers to check DPF server version."""

from functools import wraps
from typing import Any, Callable

from ansys.dpf.core import _global_server


def requires_dpf_version(min_dpf_version: str) -> Callable:
    """Check that the current DPF server matches or is higher than a certain version.

    This decorator ensures that the decorated function or method can only be used if the current
    DPF server version allows it.

    Parameters
    ----------
    min_dpf_version : str, default: None
        Minimum DPF server version required for the decorated function or method.
        The version must be specified as a string with the form MAJOR.MINOR, for example "11.0".

    Returns
    -------
    callable
        The decorator.

    .. note::
       This function must be used as a function or method decorator.
    """

    def decorator(func) -> Callable:
        """Wrap the original function or method to include DPF version check.

        Parameters
        ----------
        func : callable
            The function or method to which the decorator applies.

        Returns
        -------
        callable
            The wrapped function or method.
        """
        if not isinstance(min_dpf_version, str):
            raise TypeError(
                "requires_dpf_version decorator argument must be a string with the form "
                "MAJOR.MINOR, for example '11.0'."
            )

        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            """Check DPF server version before calling the original function or method.

            Returns
            -------
            Any
                The original function's or method's output.
            """
            _check_dpf_version(
                min_dpf_version,
                (
                    f"Function or method `{func.__name__}()` requires DPF server version "
                    f"{min_dpf_version} or higher."
                ),
            )
            return func(*args, **kwargs)

        return wrapper

    return decorator


def _check_dpf_version(min_dpf_version: str, error_msg: str):
    """Check the current DPF server and raise an exception if the specified version is higher.

    Parameters
    ----------
    min_dpf_version : str
        Minimum DPF version required.
    error_msg : str
        Error message to display if the version check fails.
    """
    if min_dpf_version is not None:
        # Retrieve the current server.
        server = _global_server()

        # This raises an exception if the current DPF server version is lower than
        # min_dpf_version.
        server.check_version(min_dpf_version, error_msg)
