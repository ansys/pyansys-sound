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

"""Computes ISO/TS 20065:2022 tonality."""
import warnings

from ansys.dpf.core import Field, GenericDataContainersCollection, Operator, types
import matplotlib.pyplot as plt
import numpy as np

from . import PsychoacousticsParent
from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning

# Name of the DPF Sound operator used in this module.
ID_COMPUTE_TONALITY_ISOTS_20065 = "compute_tonality_isots_20065"

TONE_TYPES = ("", "FG")


class TonalityISOTS20065(PsychoacousticsParent):
    """Computes ISO/TS 20065:2022 tonality.

    This class is used to compute the tonality (mean audibility) of a signal according to the
    ISO/TS 20065:2022 standard.
    """

    def __init__(self, signal: Field = None, window_length: float = 3.0, overlap: float = 0.0):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        signal: Field, default: None
            Signal in Pa on which to calculate the tonality.
        window_length: float, default: 3.0
            Length, in s, of each slice of the signal used to calculate an average spectrum.
        overlap: float, default: 0.0
            Overlap, in %, between two successive slices of the signal.

        For more information about the parameters, please refer to the Ansys Sound SAS user guide.
        """
        super().__init__()
        self.signal = signal
        self.window_length = window_length
        self.overlap = overlap
        self.__operator = Operator(ID_COMPUTE_TONALITY_ISOTS_20065)

    def __str__(self):
        """Overloads the __str__ method."""
        return (
            f"{__class__.__name__} object.\n"
            "Data\n"
            f'\tSignal name: "{self.signal.name}"\n'
            f"\tWindow length: {self.window_length} s\n"
            f"\tOverlap: {self.overlap} %\n"
            f"Mean tonality (audibility DL): "
            f"{self.get_mean_audibility():.1f} (+/-{self.get_uncertainty():.1f}) dB"
        )

    @property
    def signal(self) -> Field:
        """Input signal in Pa."""
        return self.__signal

    @signal.setter
    def signal(self, signal: Field):
        """Set signal."""
        if not (isinstance(signal, Field) or signal is None):
            raise PyAnsysSoundException("Signal must be specified as a DPF field.")
        self.__signal = signal

    @property
    def window_length(self) -> float:
        """Length, in s, of a slice of the signal used to compute each spectrum."""
        return self.__window_length

    @window_length.setter
    def window_length(self, window_length: float):
        """Set window length."""
        if window_length <= 0.0:
            raise PyAnsysSoundException("Window length must be strictly positive.")
        self.__window_length = window_length

    @property
    def overlap(self) -> float:
        """Overlap, in %, between two consecutive slices of the signal."""
        return self.__overlap

    @overlap.setter
    def overlap(self, overlap: float):
        """Set overlap property."""
        if not (0.0 <= overlap < 100.0):
            raise PyAnsysSoundException(
                "Overlap must be positive and strictly smaller than 100.0 %."
            )
        self.__overlap = overlap

    def process(self):
        """Compute the ISO/TS 20065 tonality.

        This method calls the appropriate DPF Sound operator.
        """
        if self.signal == None:
            raise PyAnsysSoundException(
                f"No input signal defined. Use `{__class__.__name__}.signal`."
            )

        # Connect the operator input(s).
        self.__operator.connect(0, self.signal)
        self.__operator.connect(1, self.window_length)
        self.__operator.connect(2, self.overlap)

        # Run the operator.
        self.__operator.run()

        # Store the operator outputs in a tuple.
        self._output = (
            self.__operator.get_output(0, types.double),
            self.__operator.get_output(1, types.double),
            self.__operator.get_output(2, types.field),
            self.__operator.get_output(3, types.field),
            self.__operator.get_output(4, types.field),
            self.__operator.get_output(5, GenericDataContainersCollection),
        )

    def get_output(self) -> tuple:
        """Get the ISO/TS 20065 tonality data, in a tuple containing data of various types.

        Returns
        -------
        tuple
            -   First element (float): ISO/TS 20065 tonality (mean audibility DL), in dB.

            -   Second element (float): ISO/TS 20065 tonality uncertainty, in dB.

            -   Third element (Field): ISO/TS 20065 tonality over time (decisive audibility DLj),
                in dB.

            -   Fourth element (Field): ISO/TS 20065 tonality uncertainty over time, in dB.

            -   Fifth element (Field): ISO/TS 20065 decisive frequency over time, in Hz.

            -   Sixth element (GenericDataContainerCollection): ISO/TS 20065 tonality details
                (individual tone data for each spectrum).
        """
        if self._output == None:
            warnings.warn(
                PyAnsysSoundWarning(
                    f"Output is not processed yet. "
                    f"Use the `{__class__.__name__}.process()` method."
                )
            )

        return self._output

    def get_output_as_nparray(self) -> tuple[np.ndarray]:
        """Get the ISO/TS 20065 tonality data, in a tuple of NumPy arrays.

        Returns
        -------
        tuple[numpy.ndarray]
            -   First element: ISO/TS 20065 tonality (mean audibility DL), in dB.

            -   Second element: ISO/TS 20065 tonality uncertainty, in dB.

            -   Third element: ISO/TS 20065 tonality over time (decisive audibility DLj), in dB.

            -   Fourth element: ISO/TS 20065 tonality uncertainty over time, in dB.

            -   Fifth element: ISO/TS 20065 decisive frequency over time, in Hz.

            -   Sixth element: time scale, in s.
        """
        output = self.get_output()

        if output == None:
            return (
                np.nan,
                np.nan,
                np.array([]),
                np.array([]),
                np.array([]),
                np.array([]),
            )

        return (
            np.array(output[0]),
            np.array(output[1]),
            np.array(output[2].data),
            np.array(output[3].data),
            np.array(output[4].data),
            np.array(output[2].time_freq_support.time_frequencies.data),
        )

    def get_mean_audibility(self) -> float:
        """Get the ISO/TS 20065 tonality (mean audibility DL), in dB.

        Returns
        -------
        float
            Mean audibility DL in dB.
        """
        return self.get_output()[0]

    def get_uncertainty(self) -> float:
        """Get the ISO/TS 20065 uncertainty, in dB.

        Returns
        -------
        float
            Uncertainty in dB.
        """
        return self.get_output()[1]

    def get_decisive_audibility_over_time(self) -> np.ndarray:
        """Get the ISO/TS 20065 decisive audibility DLj, in dB over time.

        Returns
        -------
        numpy.ndarray
            Decisive audibility DLj, in dB over time.
        """
        return self.get_output_as_nparray()[2]

    def get_uncertainty_over_time(self) -> np.ndarray:
        """Get the ISO/TS 20065 decisive audibility uncertainty, in dB over time.

        Returns
        -------
        numpy.ndarray
            Decisive audibility uncertainty, in dB over time.
        """
        return self.get_output_as_nparray()[3]

    def get_decisive_frequency_over_time(self) -> np.ndarray:
        """Get the ISO/TS 20065 decisive frequency, in Hz over time.

        Returns
        -------
        numpy.ndarray
            Decisive frequency, in Hz over time.
        """
        return self.get_output_as_nparray()[4]

    def get_time_scale(self) -> np.ndarray:
        """Get the ISO/TS 20065 time scale, in s.

        Returns
        -------
        numpy.ndarray
            Time array, in seconds, of the ISO/TS 20065 parameters over time
            (decisive audibility and uncertainty).
        """
        return self.get_output_as_nparray()[5]

    def get_spectrum_number(self) -> int:
        """Get the number of spectra.

        Returns the number of analyzed spectra, that is, the number of computation time steps.

        Returns
        -------
        int
            Number of spectra.
        """
        return len(self.get_output()[3])

    def get_spectrum_details(self, spectrum_index: int) -> tuple[float]:
        """Get the spectrum data for a specific spectrum.

        Returns the data (decisive audibility, uncertainty, and decisive frequency) corresponding
        to a specific spectrum (time step).

        Parameters
        ----------
        spectrum_index: int
            Index of the spectrum. The index is 0-based.

        Returns
        -------
        tuple[float]
            -   First element: decisive audibility DLj in dB.

            -   Second element: uncertainty in dB.

            -   Third element: decisive frequency in Hz.
        """
        # Check validity of the input spectrum index.
        self.__check_spectrum_index(spectrum_index)

        return (
            self.get_output_as_nparray()[2][spectrum_index],
            self.get_output_as_nparray()[3][spectrum_index],
            self.get_output_as_nparray()[4][spectrum_index],
        )

    def get_tone_number(self, spectrum_index: int) -> int:
        """Get the number of tones for a specific spectrum.

        Returns the number of tones detected in a specific spectrum (that is, at a specific time
        step).

        Parameters
        ----------
        spectrum_index: int
            Index of the spectrum where the tone was detected. The index is 0-based.

        Returns
        -------
        int
            Number of tones detected in this spectrum.
        """
        # Check validity of the input spectrum index.
        self.__check_spectrum_index(spectrum_index)

        # Extract collection.
        collection = self.get_output()[5]
        # Extract spectrum tones' data from collection, as a GenericDataContainer.
        spectrum = collection.get_entry(spectrum_index)

        return len(spectrum.get_property("audibilities"))

    def get_tone_details(self, spectrum_index: int, tone_index: int) -> tuple:
        """Get the tone data, for a specific spectrum.

        Returns all the data associated with a specific detected tone, in a specific spectrum (that
        is, at a specific time step).

        Parameters
        ----------
        spectrum_index: int
            Index of the spectrum where the tone was detected. The index is 0-based.
        tone_index: int
            Index of the tone whose details are requested. The index is 0-based.

        Returns
        -------
        tuple
            -   First element (float): decisive difference DLj in dB.

            -   Second element (float): uncertainty, in dB.

            -   Third element (float): decisive frequency, in Hz.

            -   Fourth element (str): tone type ('' for individual tones, or 'FG' for groups
                of tones).

            -   Fifth element (float): critical band lower limit, in Hz.

            -   Sixth element (float): critical band upper limit, in Hz.

            -   Seventh element (float): mean narrow-band masking noise level Ls, in dBA.

            -   Eighth element (float): tone level Lt, in dBA.

            -   Ninth element (float): masking noise level Lg, in dBA.

            -   Tenth element (float): masking index av, in dB.
        """
        # Check validities of input indexes.
        self.__check_spectrum_index(spectrum_index)

        if tone_index >= self.get_tone_number(spectrum_index):
            raise PyAnsysSoundException(
                f"Tone index {tone_index} is out of bounds "
                f"(total tone count in specified spectrum is {self.get_spectrum_number()})."
            )

        # Extract collection.
        collection = self.get_output()[5]
        # Extract spectrum tones' data from collection, as a GenericDataContainer.
        spectrum = collection.get_entry(spectrum_index)

        return (
            spectrum.get_property("audibilities").data[tone_index],
            spectrum.get_property("uncertainties").data[tone_index],
            spectrum.get_property("frequencies").data[tone_index],
            TONE_TYPES[int(spectrum.get_property("types").data[tone_index])],
            spectrum.get_property("critical_band_lower_limits").data[tone_index],
            spectrum.get_property("critical_band_upper_limits").data[tone_index],
            spectrum.get_property("mean_narrowband_masking_noise_levels").data[tone_index],
            spectrum.get_property("tone_levels").data[tone_index],
            spectrum.get_property("masking_noise_levels").data[tone_index],
            spectrum.get_property("masking_indices").data[tone_index],
        )

    def plot(self):
        """Plot the ISO/TS 20065's decisive audibility and frequency over time.

        This method displays the decisive audibility DLj in dB, and the decisive frequency in Hz,
        over time.
        """
        if self._output == None:
            raise PyAnsysSoundException(
                f"Output is not processed yet. Use the `{__class__.__name__}.process()` method."
            )

        # Get data to plot
        decisive_audibility_over_time = self.get_decisive_audibility_over_time()
        decisive_frequency_over_time = self.get_decisive_frequency_over_time()
        time_scale = self.get_time_scale()
        difference_unit = self.get_output()[2].unit
        frequency_unit = self.get_output()[4].unit
        time_unit = self.get_output()[2].time_freq_support.time_frequencies.unit

        # Plot ISO/TS 20065 parameters over time.
        _, axes = plt.subplots(2, 1, sharex=True)
        axes[0].plot(time_scale, decisive_audibility_over_time)
        axes[0].set_title("ISO/TS 20065 decisive audibility")
        axes[0].set_ylabel(r"$\mathregular{\Delta L_j}$" + f" ({difference_unit})")
        axes[0].grid(True)

        axes[1].plot(time_scale, decisive_frequency_over_time)
        axes[1].set_title("ISO/TS 20065 decisive frequency")
        axes[1].set_ylabel(r"$\mathregular{f_T}$" + f" ({frequency_unit})")
        axes[1].grid(True)
        axes[1].set_xlabel(f"Time ({time_unit})")

        plt.tight_layout()
        plt.show()

    def __check_spectrum_index(self, spectrum_index: int):
        """Check whether a specific spectrum index is valid.

        Raises an error if the spectrum index is out of bounds.

        Parameters
        ----------
        spectrum_index: int
            Index of the spectrum to check.
        """
        if spectrum_index >= self.get_spectrum_number():
            raise PyAnsysSoundException(
                f"Spectrum index {spectrum_index} is out of bounds "
                f"(total spectrum count is {self.get_spectrum_number()})."
            )
