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

"""Computes the tonality according to the standard ISO 1996-2:2007, annex C, over time."""

import warnings

from ansys.dpf.core import (
    Field,
    GenericDataContainer,
    GenericDataContainersCollection,
    Operator,
    types,
)
from ansys.dpf.core.collection import Collection
import matplotlib.pyplot as plt
import numpy as np

from . import PsychoacousticsParent
from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning

# Name of the DPF Sound operator used in this module.
ID_COMPUTE_TONALITY_ISO_1996_2_OVER_TIME = "compute_tonality_iso1996_2_over_time"

# List of segment details identifiers.
LIST_SEGMENT_DETAILS_KEYS = [
    "segment_start_time_s",
    "segment_end_time_s",
    "lower_critical_band_limit_Hz",
    "higher_critical_band_limit_Hz",
    "total_tonal_level_dBA",
    "total_noise_level_dBA",
]


class TonalityISO1996_2_OverTime(PsychoacousticsParent):
    """Computes the tonality according to the standard ISO 1996-2:2007, annex C, over time.

    .. note::
        The standard ISO 1996-2:2007, annex C, does not include a method for calculation over time.
        The computation of the present indicator is thus not entirely covered by the standard. The
        method used here splits the input signal into overlapping windows (segments), and then
        computes the tonality, for each window, according to the standard ISO 1996-2:2007, annex C.

    .. seealso::
        :class:`TonalityISO1996_2`, :class:`TonalityDIN45681`, :class:`TonalityISOTS20065`,
        :class:`TonalityECMA418_2`, :class:`TonalityAures`

    Examples
    --------
    Compute and display the tonality of a signal according to the 2007 version of the ISO 1996-2
    standard, annex C, over time.

    >>> from ansys.sound.core.psychoacoustics import TonalityISO1996_2_OverTime
    >>> tonality = TonalityISO1996_2_OverTime(signal=my_signal)
    >>> tonality.process()
    >>> tonal_audibility_over_time = tonality.get_tonal_audibility_over_time()
    >>> tonality.plot()

    .. seealso::
        :ref:`calculate_tonality_indicators`
            Example demonstrating how to compute various tonality indicators.
    """

    def __init__(
        self,
        signal: Field = None,
        window_length: float = 1000.0,
        overlap: float = 75.0,
        noise_pause_threshold: float = 1.0,
        effective_analysis_bandwidth: float = 5.0,
        noise_bandwidth_ratio: float = 0.75,
    ):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        signal : Field, default: None
            Input signal.
        window_length : float, default: 1000.0
            Window length in ms.
        overlap : float, default: 75.0
            Overlap between successive windows in %.
        noise_pause_threshold : float, default: 1.0
            Noise pause detection threshold ("level excess") in dB.
        effective_analysis_bandwidth : float, default: 5.0
            Effective analysis bandwidth in Hz.
        noise_critical_bandwidth_ratio : float, default: 0.75
            Noise bandwidth, in proportion to the critical bandwidth, that is taken into account
            for the calculation of the masking noise level (the default value `0.75` means that the
            masking noise level is estimated in a band delimited by 75 % of the critical bandwidth
            on each side of the tone). Value must be between `0.75` and `2`.

        For more information about the parameters, please refer to the Ansys Sound SAS user guide.
        """
        super().__init__()
        self.signal = signal
        self.window_length = window_length
        self.overlap = overlap
        self.noise_pause_threshold = noise_pause_threshold
        self.effective_analysis_bandwidth = effective_analysis_bandwidth
        self.noise_bandwidth_ratio = noise_bandwidth_ratio
        self.__operator = Operator(ID_COMPUTE_TONALITY_ISO_1996_2_OVER_TIME)

    def __str__(self) -> str:
        """Return the string representation of the object."""
        if self._output is None:
            str_tonality = (
                f"Number of segments: Not processed\n"
                f"Maximum tonal audibility: Not processed\n"
                f"Maximum tonal adjustment: Not processed"
            )
        else:
            tonal_audibility_unit = self.get_output()[0].unit
            tonal_adjustment_unit = self.get_output()[1].unit
            str_tonality = (
                f"Number of segments: {self.get_segment_count()}\n"
                f"Maximum tonal audibility: {max(self.get_tonal_audibility_over_time()):.1f} "
                f"{tonal_audibility_unit}\n"
                f"Maximum tonal adjustment: {max(self.get_tonal_adjustment_over_time()):.1f} "
                f"{tonal_adjustment_unit}"
            )

        str_name = f'"{self.signal.name}"' if self.signal is not None else "Not set"

        return (
            f"{__class__.__name__} object\n"
            "Data:\n"
            f"\tSignal name: {str_name}\n"
            f"\tIntegration window length: {self.window_length} ms\n"
            f"\tOverlap: {self.overlap} %\n"
            f"\tNoise pause detection threshold: {self.noise_pause_threshold} dB\n"
            f"\tEffective analysis bandwidth: {self.effective_analysis_bandwidth} Hz\n"
            "\tNoise bandwidth in proportion to critical bandwidth: "
            f"{self.noise_bandwidth_ratio}\n"
            f"{str_tonality}"
        )

    @property
    def signal(self) -> Field:
        """Input signal in Pa."""
        return self.__signal

    @signal.setter
    def signal(self, signal: Field):
        """Set the signal."""
        if not (isinstance(signal, Field) or signal is None):
            raise PyAnsysSoundException("Signal must be specified as a DPF field.")
        self.__signal = signal

    @property
    def window_length(self) -> int | float:
        """Length of the integration window in ms."""
        return self.__window_length

    @window_length.setter
    def window_length(self, window_length: int | float):
        """Set the window length, in ms."""
        if window_length <= 0.0:
            raise PyAnsysSoundException("Integration window length must be greater than 0 ms.")
        self.__window_length = window_length

    @property
    def overlap(self) -> int | float:
        """Overlap between successive windows in %."""
        return self.__overlap

    @overlap.setter
    def overlap(self, overlap: int | float):
        """Set the overlap, in %."""
        if overlap < 0.0 or overlap >= 100.0:
            raise PyAnsysSoundException(
                "Overlap must be greater than or equal to 0 %, and strictly smaller than 100 %."
            )
        self.__overlap = overlap

    @property
    def noise_pause_threshold(self) -> int | float:
        """Noise pause detection threshold (level excess) in dB."""
        return self.__noise_pause_threshold

    @noise_pause_threshold.setter
    def noise_pause_threshold(self, noise_pause_threshold: int | float):
        """Set the noise pause detection threshold."""
        if noise_pause_threshold <= 0.0:
            raise PyAnsysSoundException(
                "Noise pause detection threshold must be greater than 0 dB."
            )
        self.__noise_pause_threshold = noise_pause_threshold

    @property
    def effective_analysis_bandwidth(self) -> int | float:
        """Effective analysis bandwidth in Hz."""
        return self.__effective_analysis_bandwidth

    @effective_analysis_bandwidth.setter
    def effective_analysis_bandwidth(self, effective_analysis_bandwidth: int | float):
        """Set the effective analysis bandwidth, in Hz."""
        if effective_analysis_bandwidth <= 0.0:
            raise PyAnsysSoundException("Effective analysis bandwidth must be greater than 0 Hz.")
        self.__effective_analysis_bandwidth = effective_analysis_bandwidth

    @property
    def noise_bandwidth_ratio(self) -> int | float:
        """Noise bandwidth in proportion to the critical bandwidth.

        Noise bandwidth, in proportion to the critical bandwidth, that is taken into account for
        the calculation of the masking noise level (the default value `0.75` means that the masking
        noise level is estimated in a band delimited by 75 % of the critical bandwidth on each side
        of the tone). Value must be between `0.75` and `2`.
        """
        return self.__noise_bandwidth_ratio

    @noise_bandwidth_ratio.setter
    def noise_bandwidth_ratio(self, ratio: int | float):
        """Set the noise bandwidth in proportion of the critical bandwidth."""
        if ratio < 0.75 or ratio > 2.0:
            raise PyAnsysSoundException("Noise bandwidth ratio must be between 0.75 and 2.")
        self.__noise_bandwidth_ratio = ratio

    def process(self):
        """Compute the tonal audibility and tonal adjustment according to ISO1996-2 annex C."""
        if self.signal is None:
            raise PyAnsysSoundException(
                f"No input signal is set. Use ``{__class__.__name__}.signal``."
            )

        self.__operator.connect(0, self.signal)
        self.__operator.connect(1, float(self.window_length))
        self.__operator.connect(2, float(self.overlap))
        self.__operator.connect(3, float(self.noise_pause_threshold))
        self.__operator.connect(4, float(self.effective_analysis_bandwidth))
        self.__operator.connect(5, float(self.noise_bandwidth_ratio))

        # Run the operator
        self.__operator.run()

        # Stores output
        self._output = (
            self.__operator.get_output(0, types.field),
            self.__operator.get_output(1, types.field),
            self.__operator.get_output(2, GenericDataContainersCollection),
        )

    def get_output(self) -> tuple[Field, Field, Collection[GenericDataContainer]]:
        """Get the ISO 1996-2 tonality data.

        Returns
        -------
        tuple[Field, Field, Collection[GenericDataContainer]]
            -   First element (Field): tonal audibility over time, in dB.

            -   Second element (Field): tonal adjustment over time, in dB.

            -   Third element (GenericDataContainerCollection): computation details, that is, the
                segment start and end times, the main tone's critical band boundary frequencies,
                and the total tone and noise levels in dBA, for each successive window (segment) in
                the input signal.
        """
        if self._output == None:
            warnings.warn(
                PyAnsysSoundWarning(
                    f"Output is not processed yet. Use the ``{__class__.__name__}.process()`` "
                    "method."
                )
            )

        return self._output

    def get_output_as_nparray(self) -> tuple[np.ndarray]:
        """Get the ISO 1996-2 tonality data as NumPy arrays.

        Returns
        -------
        tuple[numpy.ndarray]
            -   First element: tonal audibility over time, in dB.

            -   Second element: tonal adjustment over time, in dB.

            -   Third element: time scale in s.
        """
        output = self.get_output()

        if output == None:
            return np.array([]), np.array([]), np.array([])

        return (
            np.array(output[0].data),
            np.array(output[1].data),
            np.array(output[0].time_freq_support.time_frequencies.data),
        )

    def get_tonal_audibility_over_time(self) -> np.ndarray:
        """Get the ISO 1996-2 tonal audibility over time.

        Returns
        -------
        numpy.ndarray
            ISO 1996-2 tonal audibility over time, in dB.
        """
        return self.get_output_as_nparray()[0]

    def get_tonal_adjustment_over_time(self) -> np.ndarray:
        """Get the ISO 1996-2 tonal adjustment over time.

        Returns
        -------
        numpy.ndarray
            ISO 1996-2 tonal adjustment over time, in dB.
        """
        return self.get_output_as_nparray()[1]

    def get_time_scale(self) -> np.ndarray:
        """Get the time scale.

        Returns
        -------
        numpy.ndarray
            Time scale in s.
        """
        return self.get_output_as_nparray()[2]

    def get_segment_count(self) -> int:
        """Get the number of segments.

        Returns the number of overlapping windows (segments) on which the ISO 1996-2 tonality was
        computed.

        Returns
        -------
        int
            Number of segments.
        """
        return len(self.get_output_as_nparray()[0])

    def get_segment_details(self, segment_index: int) -> dict[str, float]:
        """Get the ISO 1996-2 tonality details in the specified segment of the input signal.

        Parameters
        ----------
        segment_index : int
            Index of the segment.

        Returns
        -------
        dict[str, float]
            Dictionary containing the ISO 1996-2 tonality details for the specified segment, namely:

            -   Segment start time in s (`"segment_start_time_s"`),

            -   Segment end time in s (`"segment_end_time_s"`),

            -   Main tone's critical band lower frequency in Hz (`"lower_critical_band_limit_Hz"`),

            -   Main tone's critical band higher frequency in Hz
                (`"higher_critical_band_limit_Hz"`),

            -   Total tone level in dBA (`"total_tonal_level_dBA"`),

            -   Total noise level in dBA (`"total_noise_level_dBA"`).
        """
        segment_count = self.get_segment_count()
        if segment_count == 0:
            return {key: np.nan for key in LIST_SEGMENT_DETAILS_KEYS}

        if segment_index < 0 or segment_index >= segment_count:
            raise PyAnsysSoundException(
                f"Segment index {segment_index} is out of range. It must be between 0 and "
                f"{segment_count - 1}."
            )

        segment_details = self.get_output()[2].get_entry({"spectrum_number": segment_index})
        return {key: segment_details.get_property(key) for key in LIST_SEGMENT_DETAILS_KEYS}

    def plot(self):
        """Plot the ISO 1996-2 tonal audibility and tonal adjustment over time."""
        if self._output is None:
            raise PyAnsysSoundException(
                f"Output is not processed yet. Use the ``{__class__.__name__}.process()`` method."
            )

        tonal_audibility = self.get_tonal_audibility_over_time()
        tonal_adjustment = self.get_tonal_adjustment_over_time()
        time_scale = self.get_time_scale()
        tonal_audibility_unit = self.get_output()[0].unit
        tonal_adjustment_unit = self.get_output()[1].unit
        time_unit = self.get_output()[0].time_freq_support.time_frequencies.unit

        _, axes = plt.subplots(2, 1, sharex=True)

        axes[0].plot(time_scale, tonal_audibility)
        axes[0].set_title("ISO 1996-2 tonal audibility over time")
        axes[0].set_ylabel(r"$\mathregular{\Delta L_{ta}}$" + f" ({tonal_audibility_unit})")
        axes[0].grid()

        axes[1].plot(time_scale, tonal_adjustment)
        axes[1].set_title("ISO 1996-2 tonal adjustment over time")
        axes[1].set_ylabel(r"$\mathregular{K_t}$" + f" ({tonal_adjustment_unit})")
        axes[1].set_xlabel(f"Time ({time_unit})")
        axes[1].grid()

        plt.tight_layout()
        plt.show()
