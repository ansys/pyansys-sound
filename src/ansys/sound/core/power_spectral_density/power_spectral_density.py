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

"""Power Spectral Density (PSD) module."""

import warnings

from ansys.dpf.core import Field, Operator
import matplotlib.pyplot as plt
import numpy as np
from numpy import typing as npt

from . import PowerSpectralDensityParent
from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning

ID_POWER_SPECTRAL_DENSITY = "compute_power_spectral_density"


class PowerSpectralDensity(PowerSpectralDensityParent):
    """Power Spectral Density (PSD) class.

    This class provides the Power Spectral Density (PSD) calculation for a given signal.
    """

    def __init__(
        self,
        input_signal: Field,
        window_type: str = "HANN",
        window_length: int = 2048,
        fft_size: int = 2048,
        overlap: int = 1536,
    ):
        """Init.

        Init the class.
        """
        super().__init__()

        # Input parameters
        self.input_signal = input_signal
        self.window_type = window_type
        self.window_length = window_length
        self.fft_size = fft_size
        self.overlap = overlap

        # Define output fields
        self._output = None

        self.__operator = Operator(ID_POWER_SPECTRAL_DENSITY)

    @property
    def input_signal(self) -> Field:
        """Input signal."""
        return self.__input_signal  # pragma: no cover

    @input_signal.setter
    def input_signal(self, value: Field):
        """Set input signal."""
        self.__input_signal = value

    @property
    def window_type(self) -> str:
        """Window type."""
        return self.__window_type  # pragma: no cover

    @window_type.setter
    def window_type(self, value: str):
        """Set window type."""
        self.__window_type = value

    @property
    def window_length(self) -> int:
        """Window length."""
        return self.__window_length  # pragma: no cover

    @window_length.setter
    def window_length(self, value: int):
        """Set window length."""
        self.__window_length = value

    @property
    def fft_size(self) -> int:
        """FFT size."""
        return self.__fft_size  # pragma: no cover

    @fft_size.setter
    def fft_size(self, value: int):
        """Set FFT size."""
        self.__fft_size = value

    @property
    def overlap(self) -> int:
        """Overlap."""
        return self.__overlap  # pragma: no cover

    @overlap.setter
    def overlap(self, value: int):
        """Set overlap."""
        self.__overlap = value

    def process(self):
        """Process the Power Spectral Density (PSD) calculation.

        This method processes the Power Spectral Density (PSD) calculation.
        """
        # Check input signal
        if self.input_signal is None:
            raise PyAnsysSoundException("Input signal is not set")

        # Set operator inputs
        self.__operator.connect(0, self.input_signal)
        self.__operator.connect(1, self.window_type)
        self.__operator.connect(2, self.window_length)
        self.__operator.connect(3, self.fft_size)
        self.__operator.connect(4, self.overlap)

        # Run the operator
        self.__operator.run()

        # Get the output
        self._output = self.__operator.get_output(0, "field")

    def get_output(self) -> Field:
        """Get the output."""
        if self._output is None:
            warnings.warn(PyAnsysSoundWarning("No output is available."))

        return self._output

    def get_output_as_nparray(self) -> npt.ArrayLike:
        """Get the output as a numpy array.

        Returns
        -------
        numpy.ndarray
            The output as a numpy array.
        """
        l_output = self.get_output()

        if l_output is None:
            return (np.array([]), np.array([]))

        l_psd = l_output.data
        l_frequencies = l_output.time_freq_support.time_frequencies.data

        return (np.array(l_psd), np.array(l_frequencies))

    def plot(self):
        """Plot the Power Spectral Density (PSD) calculation.

        This method plots the Power Spectral Density (PSD) calculation.
        """
        # Get the output
        psd_values, l_frequencies = self.get_output_as_nparray()

        # Plot the PSD
        plt.plot(l_frequencies, psd_values)
        plt.title("Power Spectral Density (PSD)")
        plt.xlabel("Frequency")
        plt.ylabel("PSD")
        plt.show()
