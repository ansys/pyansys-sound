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

"""PyAnsys Sound interface."""
import warnings

import numpy as np

from ansys.sound.core.server_helpers._check_server_version import _check_dpf_version

REFERENCE_ACOUSTIC_PRESSURE = 2e-5


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
        warnings.warn(PyAnsysSoundWarning("There is nothing to plot."))
        return None

    def process(self):
        """Process inputs.

        There is nothing to process.
        """
        warnings.warn(PyAnsysSoundWarning("There is nothing to process."))
        return None

    def get_output(self) -> None:
        """Get output.

        There is nothing to output.

        Returns
        -------
        None
            None
        """
        warnings.warn(PyAnsysSoundWarning("There is nothing to output."))
        return self._output

    def get_output_as_nparray(self) -> np.ndarray:
        """Get output as a NumPy array.

        There is nothing to output.

        Returns
        -------
        numpy.ndarray
            Empty NumPy array.
        """
        warnings.warn(PyAnsysSoundWarning("There is nothing to output."))
        return np.empty(0)

    def convert_fields_container_to_np_array(self, fc) -> np.ndarray:
        """Convert a DPF fields container to a NumPy array.

        This method converts a DPF fields container that contains several signals into a
        NumPy array.

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
        num_channels = len(fc)
        np_array = np.array(fc[0].data)

        if num_channels > 1:
            for i in range(1, num_channels):
                np_array = np.vstack((np_array, fc[i].data))

        return np_array


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
