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
    Abstract mother class for PyAnsys Sound.

    This is the mother of all PyAnsysSound classes, should not be used as is.
    """

    def __init__(self):
        """Init class PyAnsysSound.

        This function inits the class by filling its attributes.
        """
        self._output = None

    def plot(self):
        """Plot the output.

        Nothing to plot for this class.
        """
        warnings.warn(PyAnsysSoundWarning("Nothing to plot."))
        return None

    def process(self):
        """Process inputs.

        Nothing to process for this class.

        Returns
        -------
        None
                None.
        """
        warnings.warn(PyAnsysSoundWarning("Nothing to process."))
        return None

    def get_output(self) -> None | FieldsContainer:
        """Get output.

        Nothing to output for this class.

        Returns
        -------
        FieldsContainer
                Empty fields container.
        """
        warnings.warn(PyAnsysSoundWarning("Nothing to output."))
        return self._output

    def get_output_as_nparray(self) -> ArrayLike:
        """Get output as nparray.

        Nothing to output for this class.

        Returns
        -------
        np.array
                Empty numpy array.
        """
        warnings.warn(PyAnsysSoundWarning("Nothing to output."))
        return np.empty(0)

    def convert_fields_container_to_np_array(self, fc):
        """Convert fields container to numpy array.

        Converts a multichannel signal contained in a DPF Fields Container into a numpy array.

        Returns
        -------
        np.array
                The fields container as a numpy array.
        """
        num_channels = len(fc)
        np_array = np.array(fc[0].data)

        if num_channels > 1:
            for i in range(1, num_channels):
                np_array = np.vstack((np_array, fc[i].data))

        return np_array


class PyAnsysSoundException(Exception):
    """PyAnsys Sound Exception."""

    def __init__(self, *args: object) -> None:
        """Init method."""
        super().__init__(*args)


class PyAnsysSoundWarning(Warning):
    """PyAnsys Sound Warning."""

    def __init__(self, *args: object) -> None:
        """Init method."""
        super().__init__(*args)
