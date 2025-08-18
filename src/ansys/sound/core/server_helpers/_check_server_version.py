# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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

"""Helpers to check DPF version."""

from functools import wraps

from ansys.dpf.core import _global_server


def method_available_from_version(min_version):
    """Check that the method being called matches or is higher than a certain DPF server version.

    Parameters
    ----------
    min_version : str, default: None
        Minimum DPF server version required for the method to be called.
        The version must be a string. Ex: "11.0"

    .. note::
       This function must be used as a decorator.
    """

    def decorator(func):
        # first arg *must* be a tuple containing the version
        if not isinstance(min_version, str):
            raise TypeError(
                "method_available_from_version decorator argument must be a string with a dot "
                "separator."
            )

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            """Call the original method."""
            server = _global_server()

            server.check_version(
                min_version,
                (
                    f"Method `{func.__name__}` of class `{self.__class__.__name__}` "
                    f"requires DPF server version {min_version} or higher."
                ),
            )

            return func(self, *args, **kwargs)

        return wrapper

    return decorator


def class_available_from_version(min_version):
    """Check that the instantiated class matches or is higher than a certain DPF server version.

    Parameters
    ----------
    min_version : str, default: None
        Minimum DPF server version required for the class to be instantiated.
        The version must be a string. Ex: "11.0"

    .. note::
       This function must be used as a decorator.
    """

    def decorator(cls):
        if not isinstance(min_version, str):
            raise TypeError(
                "class_available_from_version decorator argument must be a string with a dot "
                "separator."
            )

        class WrappedClass(cls):
            def __init__(self, *args, **kwargs):
                server = _global_server()
                server.check_version(
                    min_version,
                    (
                        f"Class `{self.__class__.__name__}` requires DPF server version "
                        f"{min_version} or higher.",
                    ),
                )
                super().__init__(*args, **kwargs)

        # Preserve class metadata.
        WrappedClass.__name__ = cls.__name__
        WrappedClass.__doc__ = cls.__doc__
        WrappedClass.__module__ = cls.__module__
        return WrappedClass

    return decorator
