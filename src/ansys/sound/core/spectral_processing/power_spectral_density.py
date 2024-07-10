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

from ansys.dpf.core import Field, Operator, TimeFreqSupport, fields_factory, locations
import matplotlib.pyplot as plt
import numpy as np
from numpy import typing as npt

from . import SpectralProcessingParent
from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning

ID_POWER_SPECTRAL_DENSITY = "compute_power_spectral_density"


class PowerSpectralDensity(SpectralProcessingParent):
    """Power Spectral Density (PSD) class.

    This class provides the Power Spectral Density (PSD) calculation for a given signal.
    """

    def __init__(
        self,
        input_signal: Field,
        fft_size: int = 2048,
        window_type: str = "HANN",
        window_length: int = 2048,
        overlap: float = 0.25,
    ):
        """Init.

        Init the class.

        Parameters
        ----------
        signal: Field
            Mono signal to compute a DPF field.
        window_type: str, default: 'HANN'
            Window type used for the FFT computation. Options are ``'BARTLETT'``, ``'BLACKMAN'``,
            ``'BLACKMANHARRIS'``,``'HAMMING'``, ``'HANN'``, ``'KAISER'``, and
            ``'RECTANGULAR'``.
        window_length : int, optional
            Window length, by default 2048.
        fft_size: int, default: 2048
            Size (as an integer) of the FFT to compute the STFT.
            Use a power of 2 for better performance.
        overlap: float, default: 0.25
            Overlap value between two successive FFT computations. Values can range from 0 to 1.
            For example, ``0`` means no overlap, and ``0.5`` means 50% overlap.
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

    # check supporté variables
    @window_type.setter
    def window_type(self, value: str):
        """Set window type."""
        if (
            value != "BLACKMANHARRIS"
            and value != "HANN"
            and value != "HAMMING"
            and value != "KAISER"
            and value != "BARTLETT"
            and value != "RECTANGULAR"
        ):
            raise PyAnsysSoundException(
                "Window type is invalid. Options are 'BARTLETT', 'BLACKMAN', 'BLACKMANHARRIS', "
                "'HAMMING', 'HANN', 'KAISER', and 'RECTANGULAR'."
            )
        self.__window_type = value

    @property
    def window_length(self) -> int:
        """Window length."""
        return self.__window_length  # pragma: no cover

    @window_length.setter
    def window_length(self, value: int):
        """Set window length."""
        if value < 0:
            raise PyAnsysSoundException("Window length must be positive")
        self.__window_length = value

    @property
    def fft_size(self) -> int:
        """FFT size."""
        return self.__fft_size  # pragma: no cover

    @fft_size.setter
    def fft_size(self, value: int):
        """Set FFT size."""
        if value < 0:
            raise PyAnsysSoundException("FFT size must be positive")
        self.__fft_size = value

    @property
    def overlap(self) -> int:
        """Overlap."""
        return self.__overlap  # pragma: no cover

    @overlap.setter
    def overlap(self, value: int):
        """Set overlap."""
        if value < 0.0 or value > 1.0:
            raise PyAnsysSoundException("Window overlap must be between 0.0 and 1.0.")
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

    def get_PSD_squared_linear(self) -> Field:
        """Get the Power Spectral Density (PSD), as squared linear values, in a Field.

        Returns
        -------
        Field
            The Power Spectral Density (PSD) as a squared linear field.
        """
        return self.get_output()

    def get_PSD_squared_linear_as_nparray(self) -> npt.ArrayLike:
        """Get the Power Spectral Density (PSD), as squared linear values, in a numpy array.

        Returns
        -------
        numpy.ndarray
            The Power Spectral Density (PSD), as squared linear values, in a numpy array.
        """
        return self.get_output_as_nparray()

    def get_PSD_dB(self, ref_value: float = 1.0) -> Field:
        """Get the Power Spectral Density (PSD) in dB/Hz, as a Field.

        Parameters
        ----------
        ref_value : float, optional
            Reference value for dB calculation, by default 1.0. Example: ref_value = 2e-5 for Pa.

        Returns
        -------
        Field
            The Power Spectral Density (PSD) as dB.
        """
        # Get the output
        psd_values, frequencies = self.get_output_as_nparray()

        # Apply the formula to each element
        psd_dB_values = 10 * np.log10(psd_values / ref_value**2)

        psd_dB_field = fields_factory.create_scalar_field(
            num_entities=1, location=locations.time_freq
        )
        psd_dB_field.append(psd_dB_values, 1)
        support = TimeFreqSupport()
        frequencies_field = fields_factory.create_scalar_field(
            num_entities=1, location=locations.time_freq
        )
        frequencies_field.append(frequencies, 1)
        support.time_frequencies = frequencies_field

        psd_dB_field.time_freq_support = support

        return psd_dB_field

    def get_PSD_dB_as_nparray(self, ref_value: float = 1.0) -> npt.ArrayLike:
        """Get the Power Spectral Density (PSD) as dB/Hz as a numpy array.

        Parameters
        ----------
        ref_value : float, optional
            Reference value for dB calculation, by default 1.0.

        Returns
        -------
        numpy.ndarray
            The Power Spectral Density (PSD) as dB as a numpy array.
        """
        return np.array(self.get_PSD_dB(ref_value).data)

    def get_frequencies(self) -> npt.ArrayLike:
        """Get the frequencies.

        Returns
        -------
        numpy.ndarray
            The frequencies.
        """
        # Get the output
        _, l_frequencies = self.get_output_as_nparray()

        return l_frequencies

    def plot(self, display_in_dB: bool = False):
        """Plot the Power Spectral Density (PSD).

        Parameters
        ----------
        display_in_dB : bool, optional
            Display the PSD in dB otherwise in Unit^2/Hz, by default False.
        """
        unit = self.input_signal.unit
        if display_in_dB == False:
            # Get the output in linear scale
            psd_values, l_frequencies = self.get_output_as_nparray()

            # Plot the PSD
            plt.plot(l_frequencies, psd_values)
            plt.title("Power Spectral Density (PSD)")
            plt.xlabel("Frequency (Hz)")
            plt.ylabel(f"Level {unit}^2/Hz")
            plt.show()
        else:
            # Get the output in dB
            psd_dB_values = self.get_PSD_dB_as_nparray()
            l_frequencies = self.get_frequencies()

            # Plot the PSD in dB
            plt.plot(l_frequencies, psd_dB_values)
            plt.title("Power Spectral Density (PSD) in dB/Hz")
            plt.xlabel("Frequency (Hz)")
            plt.ylabel("Level (dB/Hz)")
            plt.show()
