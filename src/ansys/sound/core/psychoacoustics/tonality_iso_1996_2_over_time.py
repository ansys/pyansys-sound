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

"""Computes the tonality of the signal accordingt to the standard ISO 1996-2:2007, annex C."""
import warnings

from ansys.dpf.core import DataTree, Field, Operator, types
from ansys.dpf.core.collection import Collection
import matplotlib.pyplot as plt
import numpy as np

from . import PsychoacousticsParent
from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning

# Name of the DPF Sound operator used in this module.
ID_COMPUTE_TONALITY_ISO_1996_2 = "compute_tonality_iso1996_2_over_time"


class TonalityISO1996_2_OverTime(PsychoacousticsParent):
    """Computes the tonality of the signal according to the standard ISO 1996-2:2007, annex C."""

    def __init__(
        self,
        signal: Field = None,
        window_length: float = 1000.0,
        overlap: float = 75.0,
        noise_pause_threshold: float = 1.0,
        effective_analysis_bandwidth: float = 5.0,
        noise_critical_bandwidth_ratio: float = 0.75,
    ):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        signal : Field, default: None
            Input signal, as a DPF field.
        window_length : float, default: 1000.0
            Length of the spectral analysis window in ms.
        overlap : float, default: 75.0
            Overlap between spectral analysis windows in %.
        noise_pause_threshold : float, default: 1.0
            Level excess for detecting noise pauses in dB.
        effective_analysis_bandwidth : float, default: 5.0
            Effective analysis bandwidth in Hz.
        noise_critical_bandwidth_ratio : float, default: 0.75
            Noise bandwidth, in proportion to the critical bandwidth, that is taken into account
            for the calculation of the masking noise level (the default value 0.75 means that the
            masking noise level is estimated in a band delimited by 75 % of the critical bandwidth
            on each side of the tone). Value must be between 0.75 and 2.
        """
        super().__init__()
        self.signal = signal
        self.window_length = window_length
        self.overlap = overlap
        self.noise_pause_threshold = noise_pause_threshold
        self.effective_analysis_bandwidth = effective_analysis_bandwidth
        self.noise_critical_bandwidth_ratio = noise_critical_bandwidth_ratio
        self.__operator = Operator(ID_COMPUTE_TONALITY_ISO_1996_2)

    def __str__(self) -> str:
        """Return the string representation of the object."""
        if self._output is None:
            str_tonality = (
                f"Number of segments: Not processed\n"
                f"Maximum tonal audibility: Not processed\n"
                f"Maximum tonal adjustment: Not processed"
            )
        else:
            str_tonality = (
                f"Number of segments: {self.get_segment_count()}\n"
                f"Maximum tonal audibility: {max(self.get_tonal_audibility_over_time()):.2f} dB\n"
                f"Maximum tonal adjustment: {max(self.get_tonal_adjustment_over_time()):.2f} dB"
            )

        return (
            f"{__class__.__name__} object\n"
            "Data:\n"
            f'\tSignal name: {f'"{self.signal.name}"' if self.signal is not None else "Not set"}\n'
            f"\tIntegration window length: {self.window_length} ms\n"
            f"\tOverlap: {self.overlap} %\n"
            f"\tNoise pause detection threshold: {self.noise_pause_threshold} dB\n"
            f"\tEffective analysis bandwidth: {self.effective_analysis_bandwidth} Hz\n"
            f"\tNoise bandwidth in proportion to CBW: {self.noise_critical_bandwidth_ratio}\n"
            f"{str_tonality}"
        )

    @property
    def signal(self) -> Field:
        """Input sound signal as a DPF field."""
        return self.__signal

    @signal.setter
    def signal(self, signal: Field):
        """Set the signal."""
        if not (isinstance(signal, Field) or signal is None):
            raise PyAnsysSoundException("Signal must be specified as a DPF field.")
        self.__signal = signal

    @property
    def window_length(self) -> float:
        """Length of the spectral analysis window in ms."""
        return self.__window_length

    @window_length.setter
    def window_length(self, window_length: float):
        """Set the window_length."""
        if window_length <= 0.0:
            raise PyAnsysSoundException("Window length must be greater than 0 ms.")
        self.__window_length = window_length

    @property
    def overlap(self) -> float:
        """Overlap between spectral analysis windows in %."""
        return self.__overlap

    @overlap.setter
    def overlap(self, overlap: float):
        """Set the overlap."""
        if overlap < 0.0 or overlap >= 100.0:
            raise PyAnsysSoundException(
                "Overlap must be greater than or equal to 0 %, and strictly smaller than 100 %."
            )
        self.__overlap = overlap

    @property
    def noise_pause_threshold(self) -> float:
        """Level excess for detecting noise pauses in dB."""
        return self.__noise_pause_threshold

    @noise_pause_threshold.setter
    def noise_pause_threshold(self, noise_pause_threshold: float):
        """Set the level excess for detecting noise pauses."""
        if noise_pause_threshold <= 0.0:
            raise PyAnsysSoundException("Noise pause threshold must be greater than 0 dB.")
        self.__noise_pause_threshold = noise_pause_threshold

    @property
    def effective_analysis_bandwidth(self) -> float:
        """Effective analysis bandwidth in Hz."""
        return self.__effective_analysis_bandwidth

    @effective_analysis_bandwidth.setter
    def effective_analysis_bandwidth(self, effective_analysis_bandwidth: float):
        """Set the effective analysis bandwidth."""
        if effective_analysis_bandwidth <= 0.0:
            raise PyAnsysSoundException("Effective analysis bandwidth must be greater than 0 Hz.")
        self.__effective_analysis_bandwidth = effective_analysis_bandwidth

    @property
    def noise_critical_bandwidth_ratio(self) -> float:
        """Noise bandwidth in proportion of the critical bandwidth.

        Noise bandwidth, in proportion to the critical bandwidth, that is taken into account for
        the calculation of the masking noise level (the default value 0.75 means that the masking
        noise level is estimated in a band delimited by 75 % of the critical bandwidth on each side
        of the tone). Value must be between 0.75 and 2.
        """
        return self.__noise_critical_bandwidth_ratio

    @noise_critical_bandwidth_ratio.setter
    def noise_critical_bandwidth_ratio(self, noise_critical_bandwidth_ratio: float):
        """Set the noise bandwidth in proportion of the critical bandwidth.

        Provided value must be between 0.75 and 2.
        """
        if noise_critical_bandwidth_ratio < 0.75 or noise_critical_bandwidth_ratio > 2.0:
            raise PyAnsysSoundException("Noise bandwidth ratio must be between 0.75 and 2.")
        self.__noise_critical_bandwidth_ratio = noise_critical_bandwidth_ratio

    def process(self):
        """Compute the tonal audibility and adjustment according to ISO1996-2 annex C."""
        if self.signal is None:
            raise PyAnsysSoundException(f"No input signal is set. Use {__class__.__name__}.signal.")

        self.__operator.connect(0, self.signal)
        self.__operator.connect(1, float(self.window_length))
        self.__operator.connect(2, float(self.overlap))
        self.__operator.connect(3, float(self.noise_pause_threshold))
        self.__operator.connect(4, float(self.effective_analysis_bandwidth))
        self.__operator.connect(5, float(self.noise_critical_bandwidth_ratio))

        # Run the operator
        self.__operator.run()

        # Stores output
        self._output = (
            self.__operator.get_output(0, types.field),
            self.__operator.get_output(1, types.field),
            self.__operator.get_output(2, types.generic_data_container).get_property("details"),
        )

    def get_output(self) -> tuple[Field, Field, Collection[DataTree]]:
        """Get the ISO 1996-2 tonality data.

        Returns
        -------
        tuple[Field, Field, Collection[DataTree]]

            -   First element is the tonal audibility over time, in dB.

            -   Second element is the tonal adjustment over time, in dB.

            -   Third element contains the computation details, that is, the main tone's critical
                band boundary frequencies, and the total tone and noise levels in dBA, for each
                successive window in the input signal.
        """
        if self._output == None:
            warnings.warn(
                PyAnsysSoundWarning(
                    "Output is not processed yet. "
                    f"Use the {__class__.__name__}.process() method."
                )
            )

        return self._output

    def get_output_as_nparray(self) -> tuple[np.ndarray]:
        """Get the ISO 1996-2 tonality data as NumPy arrays.

        Returns
        -------
        tuple[numpy.ndarray]

            -   First element is the tonal audibility over time, in dB.

            -   Second element is the tonal adjustment over time, in dB.

            -   Third element is the main tone's critical band lower boundary frequencies over time
                in Hz.

            -   Fourth element is the main tone's critical band upper boundary frequencies over
                time in Hz.

            -   Fifth element is the total tone level over time in dBA.

            -   Sixth element is the total noise level over time in dBA.

            -   Seventh element is the time sale in s.
        """
        output = self.get_output()

        if output == None:
            return (
                np.array([]),
                np.array([]),
                np.array([]),
                np.array([]),
                np.array([]),
                np.array([]),
            )

        # TODO: sort out getting the details correctly. Current code cannot work.
        return (
            np.array(output[0].data),
            np.array(output[1].data),
            np.array(output[2].get_property("Critical Band (Low)")),
            np.array(output[2].get_property("Critical Band (High)")),
            np.array(output[2].get_property("Total tonal level (dBA)")),
            np.array(output[2].get_property("Total Noise level (dBA)")),
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
        return self.get_output_as_nparray()[6]

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
        """Get the ISO 1996-2 tonality details in a segment of the input signal.

        Parameters
        ----------
        segment_index : int
            Index of the segment.

        Returns
        -------
        dict[str, float]
            Dictionary containing the ISO 1996-2 tonality details for the specified segment, namely:

            -   Tonal audibility in dB

            -   Tonal adjustment in dB

            -   Main tone's critical band lower frequency in Hz

            -   Main tone's critical band upper frequency in Hz

            -   Total tone level in dBA

            -   Total noise level in dBA
        """
        segment_count = self.get_segment_count()
        if segment_count == 0:
            return {
                "Tonal audibility (dB)": np.nan,
                "Tonal adjustment (dB)": np.nan,
                "Critical Band (Low)": np.nan,
                "Critical Band (High)": np.nan,
                "Total tonal level (dBA)": np.nan,
                "Total noise level (dBA)": np.nan,
                "Time (s)": np.nan,
            }

        if segment_index < 0 or segment_index >= segment_count - 1:
            raise PyAnsysSoundException(
                f"Segment index {segment_index} is out of range. It must be between 0 and "
                f"{segment_count - 1}."
            )

        output = self.get_output_as_nparray()
        return {
            "Tonal audibility (dB)": output[0][segment_index],
            "Tonal adjustment (dB)": output[1][segment_index],
            "Critical Band (Low)": output[2][segment_index],
            "Critical Band (High)": output[3][segment_index],
            "Total tonal level (dBA)": output[4][segment_index],
            "Total noise level (dBA)": output[5][segment_index],
            "Time (s)": output[6][segment_index],
        }

    def plot(self):
        """Plot the ISO 1996-2 tonal audibility and tonal adjustment over time."""
        if self._output is None:
            raise PyAnsysSoundException(
                f"Output is not processed yet. Use the {__class__.__name__}.process() method."
            )

        tonal_audibility = self.get_tonal_audibility_over_time()
        tonal_adjustment = self.get_tonal_adjustment_over_time()
        time_scale = self.get_time_scale()

        _, axes = plt.subplots(2, 1, sharex=True)

        axes[0].plot(time_scale, tonal_audibility)
        axes[0].set_title("ISO 1996-2 tonal audibility over time")
        axes[0].set_ylabel(r"$\mathregular{\Delta L_ta}$ (dB)")
        axes[0].grid()

        axes[1].plot(time_scale, tonal_adjustment)
        axes[1].set_title("ISO 1996-2 tonal adjustment over time")
        axes[1].set_ylabel(r"$\mathregular{K_t}$ (dB)")
        axes[1].set_xlabel("Time (s)")
        axes[1].grid()

        plt.tight_layout()
        plt.show()
