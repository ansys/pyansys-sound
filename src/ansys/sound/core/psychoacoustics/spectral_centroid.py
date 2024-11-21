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

"""Computes the spectral centroid of the signal."""
import warnings

from ansys.dpf.core import Field, Operator
import numpy as np
from numpy import typing as npt

from . import PsychoacousticsParent
from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning


class SpectralCentroid(PsychoacousticsParent):
    """Computes the spectral centroid of a signal."""

    def __init__(self, signal: Field = None):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        signal : Field
            Signal to compute spectral centroid on as a DPF field.
        """
        super().__init__()
        self.signal = signal
        self.__operator = Operator("compute_spectral_centroid")

    @property
    def signal(self):
        """Signal."""
        return self.__signal  # pragma: no cover

    @signal.setter
    def signal(self, signal: Field):
        """Set the signal.

        Parameters
        -------
        signal : Field
            Signal to compute spectral centroid on as a DPF field.
        """
        self.__signal = signal

    @signal.getter
    def signal(self) -> Field:
        """Signal.

        Returns
        -------
        Field
            Signal as a DPF field.
        """
        return self.__signal

    def process(self):
        """Compute the spectral centroid."""
        if self.signal is None:
            raise PyAnsysSoundException(
                "No signal found for spectral centroid computation. Use 'SpectralCentroid.signal'."
            )

        self.__operator.connect(0, self.signal)

        # Run the operator
        self.__operator.run()

        # Stores output
        self._output = self.__operator.get_output(0, "double")

    def get_output(self) -> float:
        """Get the spectral centroid.

        Returns
        -------
        float
            Spectral centroid in Hz.
        """
        if self._output == None:
            warnings.warn(
                PyAnsysSoundWarning(
                    "Output is not processed yet. \
                        Use the 'SpectralCentroid.process()' method."
                )
            )

        return self._output

    def get_output_as_nparray(self) -> npt.ArrayLike:
        """Get the spectral centroid as a NumPy array.

        Returns
        -------
        numpy.ndarray:
            Array of spectral centroid values in Hz.
        """
        output = self.get_output()

        if output == None:
            return np.array([])

        return np.array([output])

    def get_spectral_centroid(self) -> float:
        """Get the spectral centroid.

        Returns
        -------
        float
            Spectral centroid in Hz.
        """
        return self.get_output()

    def __str__(self):
        """Create the string for print() call.

        Returns
        -------
        str
            Formatted info about self.
        """
        str = __class__.__name__ + " object\n"
        str += "Data\n"
        str += "\t Signal name: " + self.signal.name + "\n"
        str += f"\t Spectral centroid: {self.get_spectral_centroid():.1f} Hz\n"

        return str
