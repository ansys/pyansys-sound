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

"""PyAnsys Sound interface."""

from functools import wraps
from typing import Any, Callable
import warnings

from ansys.dpf.core import FieldsContainer
import numpy as np

from ansys.sound.core.server_helpers._check_server_version import _check_dpf_version

REFERENCE_ACOUSTIC_PRESSURE_IN_AIR = 2e-5


class PyAnsysSound:
    """
    Provides the abstract base class for PyAnsys Sound.

    This is the base class of all PyAnsys Sound classes and should not be used as is.
    """

    # Declare minimum DPF version class attribute.
    _min_dpf_version = None

    def __init_subclass__(cls, *, min_dpf_version: str = None, **kwargs):
        """Store minimum DPF version requirement for subclasses.

        This is executed at subclass creation time. It stores the specified minimum DPF version
        requirement for the created subclass as a class attribute. It also adds the version
        requirement in the class docstring.

        .. note::
            The specified version is not tested against the current DPF server version just yet,
            because the server might not yet exist, and because doing this check at class creation
            time might affect other class creations with different version requirements. The actual
            check is done at class instantiation time.

        Parameters
        ----------
        min_dpf_version : str, optional
            Minimum DPF version required for the subclass.
            The version must be a string with the form MAJOR.MINOR, for example "11.0".
        """
        if min_dpf_version is not None:
            # Check version specifier validity.
            if not isinstance(min_dpf_version, str):
                raise TypeError(
                    "In class definition, `min_dpf_version` argument must be a string with the "
                    'form MAJOR.MINOR, for example "11.0".'
                )

            # Append version requirement to subclass docstring.
            if isinstance(cls.__doc__, str):
                cls.__doc__ += f"\n\t*Added in DPF server version {min_dpf_version}.*"

        # Update the subclass's class attribute (to later check compliance, at class instantiation).
        cls._min_dpf_version = min_dpf_version

        # Proceed with the subclass creation.
        super().__init_subclass__(**kwargs)

    def __init__(self):
        """Initialize the class.

        Checks DPF version compliance (if specified in class definition), and initialize necessary
        attributes.
        """
        # Check current DPF server version against class minimum requirement (if specified).
        _check_dpf_version(
            self._min_dpf_version,
            (
                f"Class `{self.__class__.__name__}` requires DPF server version "
                f"{self._min_dpf_version} or higher."
            ),
        )

        # Initialize output attribute.
        self._output = None

    def plot(self):
        """Plot the output.

        There is nothing to plot.
        """
        warnings.warn(
            PyAnsysSoundWarning(
                f"This method is not implemented for class {self.__class__.__name__}."
            )
        )
        return None

    def process(self):
        """Process inputs.

        There is nothing to process.
        """
        warnings.warn(
            PyAnsysSoundWarning(
                f"This method is not implemented for class {self.__class__.__name__}."
            )
        )
        return None

    def get_output(self) -> None:
        """Get output.

        There is nothing to output.

        Returns
        -------
        None
            None
        """
        warnings.warn(
            PyAnsysSoundWarning(
                f"This method is not implemented for class {self.__class__.__name__}."
            )
        )
        return self._output

    def get_output_as_nparray(self) -> np.ndarray:
        """Get output as a NumPy array.

        There is nothing to output.

        Returns
        -------
        numpy.ndarray
            Empty NumPy array.
        """
        warnings.warn(
            PyAnsysSoundWarning(
                f"This method is not implemented for class {self.__class__.__name__}."
            )
        )
        return np.empty(0)


class PyAnsysSoundException(Exception):
    """Provides the PyAnsys Sound exception."""

    def __init__(self, *args: object) -> None:
        """Init method."""
        super().__init__(*args)


class PyAnsysSoundWarning(Warning):
    """Provides the PyAnsys Sound warning."""

    def __init__(self, *args: object) -> None:
        """Init method."""
        super().__init__(*args)


def convert_fields_container_to_np_array(fields_container: FieldsContainer) -> np.ndarray:
    """Convert a DPF fields container to a NumPy array.

    This function converts a DPF fields container into a NumPy array.

    Parameters
    ----------
    fc : FieldsContainer
        DPF fields container to convert into a NumPy array.

    Returns
    -------
    numpy.ndarray
        DPF fields container in a NumPy array.
        Data in each field of the fields container is converted to a NumPy array and vertically
        stacked into another NumPy array.
    """
    if not isinstance(fields_container, FieldsContainer):
        raise PyAnsysSoundException("Input must be a DPF fields container.")

    match len(fields_container):
        case 0:
            # Empty fields container => empty NumPy array
            return np.empty(0)
        case 1:
            # Single field => 1D NumPy array
            return np.array(fields_container[0].data)
        case _:
            # Multiple fields => 2D NumPy array
            return np.vstack([np.array(field.data) for field in fields_container])


def scipy_required(func: Callable) -> Callable:
    """Decorate a function or method to ensure that SciPy is installed.

    If it is not installed, an exception is raised suggesting to install it.

    Parameters
    ----------
    func : Callable
        The function or method to which the decorator applies.

    Returns
    -------
    Callable
        The decorated function or method.
    """
    return _package_required(func, "SciPy")


def _package_required(func: Callable, package: str) -> Callable:
    """Decorate a function or method to ensure that the specified package is installed.

    If it is not installed, an exception is raised suggesting to install it.

    Parameters
    ----------
    func : Callable
        The function or method to which the decorator applies.
    package : str
        Name of the package required by the decorated function or method.

    Returns
    -------
    Callable
        The decorated function or method.
    """

    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        """Check package availability before calling the original function or method.

        Returns
        -------
        Any
            The original function's or method's output.
        """
        package_lowercase = package.lower()
        try:
            __import__(package_lowercase)
        except (ModuleNotFoundError, ImportError):
            raise PyAnsysSoundException(
                f"The function or method `{func.__name__}()` requires the {package} Python library "
                f"to be installed. You can install {package} by running `pip install "
                f"{package_lowercase}`, for example."
            )
        return func(*args, **kwargs)

    return wrapper
