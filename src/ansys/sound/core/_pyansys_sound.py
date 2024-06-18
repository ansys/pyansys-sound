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

"""PyAnsys Sound interface."""
import warnings

from ansys.dpf.core import FieldsContainer
import numpy as np
from numpy.typing import ArrayLike


class PyAnsysSound:
    """
    Provides the abstract base class for PyAnsys Sound.

    This is the base class of all PyAnsys Sound classes and should not be used as is.
    """

    def __init__(self):
        """Init class PyAnsysSound.

        This function inits the class by filling its attributes.
        """
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

        Returns
        -------
        None
                None.
        """
        warnings.warn(PyAnsysSoundWarning("There is nothing to process."))
        return None

    def get_output(self) -> None | FieldsContainer:
        """Get output.

        There is nothing to output.

        Returns
        -------
        FieldsContainer
            Empty DPF fields container.
        """
        warnings.warn(PyAnsysSoundWarning("There is nothing to output."))
        return self._output

    def get_output_as_nparray(self) -> ArrayLike:
        """Get output as a NumPy array.

        There is nothing to output.

        Returns
        -------
        np.array
            Empty NumPy array.
        """
        warnings.warn(PyAnsysSoundWarning("There is nothing to output."))
        return np.empty(0)

    def convert_fields_container_to_np_array(self, fc):
        """Convert a DPF fields container to a NumPy array.

        This method converts a multichannel signal contained in a DPF fields container to a
        NumPy array.

        Returns
        -------
        np.array
            DPF fields container in a NumPy array.
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
