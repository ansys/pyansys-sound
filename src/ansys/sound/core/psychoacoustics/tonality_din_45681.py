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

"""Computes DIN 45681 tonality."""
import warnings

from ansys.dpf.core import Field, GenericDataContainersCollection, Operator
import matplotlib.pyplot as plt
import numpy as np
from numpy import typing as npt

from . import PsychoacousticsParent
from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning

TONE_TYPES = ("", "FG")


class TonalityDIN45681(PsychoacousticsParent):
    """Computes DIN 45681 tonality.

    This class computes the tonality (mean difference) and tonal adjustment of a signal following
    the DIN 45681 standard.
    """

    def __init__(self, signal: Field = None, window_length: float = 3.0, overlap: float = 0.0):
        """Create a ``TonalityDIN45681`` object.

        Parameters
        ----------
        signal: Field, default: None
            Signal in Pa as a DPF field.
        window_length: float, default: 3.0
            Window length in s.
        overlap: float, default: 0.0
            Overlap in %.
        """
        super().__init__()
        self.signal = signal
        self.window_length = window_length
        self.overlap = overlap
        self.__operator = Operator("compute_tonality_din45681")

    def __str__(self):
        """Overloads the __str__ method."""
        string = (
            f"{__class__.__name__} object.\n"
            "Data\n"
            f'Signal name: "{self.signal.name}"\n'
            f"Window length: {self.window_length:.1f} s\n"
            f"Overlap: {self.overlap:.1f} %\n"
            f"Mean difference DL: {self.get_mean_difference():.1f} (+/-{self.get_uncertainty():.1f}) dB\n"
            f"Tonal adjustment Kt: {self.get_tonal_adjustment():d} dB\n"
        )

        return string

    @property
    def signal(self):
        """Signal property."""
        return self.__signal

    @signal.setter
    def signal(self, signal: Field):
        """Set signal property."""
        if not isinstance(signal, Field):
            raise PyAnsysSoundException("Signal must be specified as a DPF field.")
        self.__signal = signal

    @property
    def window_length(self):
        """Signal property."""
        return self.__window_length

    @window_length.setter
    def window_length(self, window_length: float):
        """Set window length property."""
        if window_length <= 0.0:
            raise PyAnsysSoundException("Window length must be strictly positive.")
        self.__window_length = window_length

    @property
    def overlap(self):
        """Overlap property."""
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
        """Compute the DIN 45681 tonality.

        This method calls the appropriate DPF Sound operator.
        """
        if self.signal == None:
            raise PyAnsysSoundException(
                f"No input signal defined. Use ``{__class__.__name__}.signal``."
            )

        # Connect the operator input(s).
        self.__operator.connect(0, self.signal)
        self.__operator.connect(1, self.window_length)
        self.__operator.connect(2, self.overlap)

        # Run the operator.
        self.__operator.run()

        # Store the operator outputs in a tuple.
        self._output = (
            self.__operator.get_output(0, "double"),
            self.__operator.get_output(1, "double"),
            self.__operator.get_output(2, "double"),
            self.__operator.get_output(3, "field"),
            self.__operator.get_output(4, "field"),
            self.__operator.get_output(5, "field"),
            self.__operator.get_output(6, "field"),
            self.__operator.get_output(7, GenericDataContainersCollection),
        )

    def get_output(self) -> tuple:
        """Get DIN 45681 tonality data in a tuple of various types.

        Returns
        -------
        tuple
            First element (float) is the DIN 45681 tonality (mean difference DL) in dB.

            Second element (float) is the DIN 45681 tonality uncertainty in dB.

            Third element (float) is the DIN 45681 tonal adjustment Kt in dB.

            Fourth element (Field) is the DIN 45681 tonality over time (decisive difference DLj) in
            dB.

            Fifth element (Field) is the DIN 45681 tonality uncertainty over time in dB.

            Sixth element (Field) is the DIN 45681 decisive frequency over time in Hz.

            Seventh element (Field) is the DIN 45681 tonal adjustment Kt over time in dB.

            Eighth element (GenericDataContainer) is the DIN 45681 tonality details (spectrum
            data, tone data).
        """
        if self._output == None:
            warnings.warn(
                PyAnsysSoundWarning(
                    f"Output is not processed yet. Use the ``{__class__.__name__}.process()`` method."
                )
            )

        return self._output

    def get_output_as_nparray(self) -> tuple[npt.ArrayLike]:
        """Get DIN 45681 tonality data in a tuple of NumPy arrays.

        Returns
        -------
        tuple[numpy.ndarray]
            First element is the DIN 45681 tonality (mean difference DL) in dB.

            Second element is the DIN 45681 tonality uncertainty in dB.

            Third element is the DIN 45681 tonal adjustment Kt in dB.

            Fourth element is the DIN 45681 tonality over time (decisive difference DLj) in dB.

            Fifth element is the DIN 45681 tonality uncertainty over time in dB.

            Sixth element is the DIN 45681 decisive frequency over time in Hz.

            Seventh element is the DIN 45681 tonal adjustment Kt over time in dB.

            Eighth element is the time scale in s.

            Ninth element is the DIN 45681 tonality details (spectrum data, tone data).
        """
        output = self.get_output()

        if output == None:
            return (
                np.nan,
                np.nan,
                np.nan,
                np.array([]),
                np.array([]),
                np.array([]),
                np.array([]),
                np.array([]),
                np.array([]),
            )

        return (
            np.array(output[0]),
            np.array(output[1]),
            np.array(output[2]),
            np.array(output[3].data),
            np.array(output[4].data),
            np.array(output[5].data),
            np.array(output[6].data),
            np.array(output[3].time_freq_support.time_frequencies.data),
            np.array(output[7]),
        )

    def get_mean_difference(self) -> float:
        """Get the DIN 45681 tonality (mean difference DL) in dB.

        Returns
        -------
        float
            Mean difference DL in dB.
        """
        return self.get_output()[0]

    def get_uncertainty(self) -> float:
        """Get the DIN 45681 uncertainty in dB.

        Returns
        -------
        float
            Uncertainty in dB.
        """
        return self.get_output()[1]

    def get_tonal_adjustment(self) -> float:
        """Get the DIN 45681 tonal adjustment in dB.

        Returns
        -------
        float
            Tonal adjustment Kt in dB.
        """
        return self.get_output()[2]

    def get_decisive_difference_over_time(self) -> npt.ArrayLike:
        """Get the DIN 45681 decisive difference DLj in dB over time.

        Returns
        -------
        numpy.ndarray
            Decisive difference DLj in dB over time.
        """
        return self.get_output_as_nparray()[3]

    def get_uncertainty_over_time(self) -> npt.ArrayLike:
        """Get the DIN 45681 decisive difference uncertainty in dB over time.

        Returns
        -------
        numpy.ndarray
            Decisive difference uncertainty in dB over time.
        """
        return self.get_output_as_nparray()[4]

    def get_decisive_frequency_over_time(self) -> npt.ArrayLike:
        """Get the DIN 45681 decisive frequency in Hz over time.

        Returns
        -------
        numpy.ndarray
            Decisive frequency in Hz over time.
        """
        return self.get_output_as_nparray()[5]

    def get_tonal_adjustment_over_time(self) -> npt.ArrayLike:
        """Get the DIN 45681 tonal adjustment Kt in dB over time.

        Returns
        -------
        numpy.ndarray
            Tonal adjustment Kt in dB over time.
        """
        return self.get_output_as_nparray()[6]

    def get_time_scale(self) -> npt.ArrayLike:
        """Get the DIN 45681 time scale in s.

        Returns
        -------
        numpy.ndarray
            Computation timestamps in s.
        """
        return self.get_output_as_nparray()[7]

    def get_spectrum_number(self) -> int:
        """Get the number of spectra.

        Returns
        -------
        int
            Number of spectra.
        """
        return len(self.get_output()[3])

    def get_spectrum_details(self, spectrum_index: int = 0) -> tuple[float, float, float]:
        """Get the spectrum data.

        Parameters
        ----------
        spectrum_index: int, default: 0
            Index of the spectrum to get.

        Returns
        -------
        tuple[float,float,float]
            Decisive difference DLj in dB.
            Uncertainty in dB.
            Decisive frequency in Hz.
        """
        self.__check_spectrum_index(spectrum_index)

        return (
            self.get_output_as_nparray()[3][spectrum_index],
            self.get_output_as_nparray()[4][spectrum_index],
            self.get_output_as_nparray()[5][spectrum_index],
        )

    def get_tone_number(self, spectrum_index: int = 0) -> int:
        """Get the number of tones.

        Returns
        -------
        int
            Number of tones.
        """
        self.__check_spectrum_index(spectrum_index)

        collection = self.get_output()[7]
        spectrum = collection.get_entry(spectrum_index)

        return len(spectrum.get_property("differences"))

    def get_tone_details(
        self, spectrum_index: int = 0, tone_index: int = 0
    ) -> tuple[float, float, float, str, float, float, float, float, float, float]:
        """Get the tone data.

        Parameters
        ----------
        spectrum_index: int, default: 0
            Index of the spectrum where the tone was detected.
        tone_index: int, default: 0
            Index of the tone whose details are requested.

        Returns
        -------
        tuple[float,float,float,str,float,float,float,float,float,float]
            Decisive difference DLj in dB.
            Uncertainty in dB.
            Decisive frequency in Hz.
            Tone type ('' or 'FG').
            Critical band lower limit in Hz.
            Critical band upper limit in Hz.
            Mean narrow-band masking noise level Ls in dBA.
            Tone level Lt in dBA.
            Masking noise level Lg in dBA.
            Masking index av in dB.
        """
        self.__check_spectrum_index(spectrum_index)

        if tone_index >= self.get_tone_number(spectrum_index):
            raise PyAnsysSoundException(
                f"Tone index {tone_index} out of bounds (total tone count in specified spectrum is {self.get_spectrum_number()})."
            )

        collection = self.get_output()[7]
        spectrum = collection.get_entry(spectrum_index)

        return (
            spectrum.get_property("differences").data[tone_index],
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
        """Plot the DIN 45681 decisive difference, decisive frequency, and tonal adjustment over time.

        This method creates a figure window that displays decisive difference DLj in dB, decisive
        frequency in Hz, and tonal adjustment Kt in dB, over time.
        """
        if self._output == None:
            raise PyAnsysSoundException(
                f"Output is not processed yet. Use the ``{__class__.__name__}.process()`` method."
            )

        decisive_difference_over_time = self.get_decisive_difference_over_time()
        decisive_frequency_over_time = self.get_decisive_frequency_over_time()
        tonal_adjustment_over_time = self.get_tonal_adjustment_over_time()

        time_scale = self.get_time_scale()

        # Plot DIN 45681 parameters over time.
        _, axes = plt.subplots(3, 1, sharex=True)
        axes[0].plot(time_scale, decisive_difference_over_time)
        axes[0].set_title("DIN45681 decisive difference")
        axes[0].set_ylabel(r"$\mathregular{\Delta L_j}$ (dB)")
        axes[0].grid(True)

        axes[1].plot(time_scale, decisive_frequency_over_time)
        axes[1].set_title("DIN45681 decisive frequency")
        axes[1].set_ylabel(r"$\mathregular{f_T}$ (Hz)")
        axes[1].grid(True)

        axes[2].plot(time_scale, tonal_adjustment_over_time)
        axes[2].set_title("DIN45681 tonal adjustment")
        axes[2].set_xlabel("Time (s)")
        axes[2].set_ylabel(r"$\mathregular{K_T}$ (dB)")
        axes[2].grid(True)

        plt.tight_layout()
        plt.show()

    def __check_spectrum_index(self, spectrum_index: int):
        """Check whether a specified spectrum index is available.

        Raises an error if the spectrum index is out of bounds.

        Parameters
        ----------
        spectrum_index: int
            Index of the spectrum to check.
        """
        if spectrum_index >= self.get_spectrum_number():
            raise PyAnsysSoundException(
                f"Spectrum index {spectrum_index} is out of bounds (total spectrum count is {self.get_spectrum_number()})."
            )
