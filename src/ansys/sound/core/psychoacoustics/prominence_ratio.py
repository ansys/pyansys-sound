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

"""Computes the ECMA 418-1/ISO 7779 prominence ratio (PR)."""

from math import log10
import warnings

from ansys.dpf.core import Field, GenericDataContainer, Operator
import matplotlib.pyplot as plt
import numpy as np

from . import PsychoacousticsParent
from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning


class ProminenceRatio(PsychoacousticsParent):
    """Computes the ECMA 418-1/ISO 7779 prominence ratio (PR).

    This class computes the PR from a power spectral density (PSD), according to the ECMA 418-1 and
    ISO 7779 standards.

    .. seealso::
        :class:`ToneToNoiseRatio`, :class:`ProminenceRatioForOrdersOverTime`

    Examples
    --------
    Compute and display the prominence ratio of all identified peaks in a given power spectral
    density.

    >>> from ansys.sound.core.psychoacoustics import ProminenceRatio
    >>> prominence_ratio = ProminenceRatio(psd=my_psd)
    >>> prominence_ratio.process()
    >>> pr_values = prominence_ratio.get_PR_values()
    >>> frequencies = prominence_ratio.get_peaks_frequencies()
    >>> max_pr = prominence_ratio.get_max_PR_value()
    >>> prominence_ratio.plot()

    Compute the prominence ratio at specific frequencies.

    >>> from ansys.sound.core.psychoacoustics import ProminenceRatio
    >>> prominence_ratio = ProminenceRatio(psd=my_psd, frequency_list=[500, 1000, 2000])
    >>> prominence_ratio.process()
    >>> pr_values = prominence_ratio.get_PR_values()

    .. seealso::
        :ref:`calculate_PR_and_TNR`
            Example demonstrating how to compute tone-to-noise ratio and prominence ratio.
    """

    def __init__(self, psd: Field = None, frequency_list: list = None):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        psd : Field
            PSD of the signal on which to compute PR.
            The PSD field has the following characteristics:

            -   ``num_entities`` = 1
            -   ``location`` = "TimeFreq_sets"
            -   ``data``: Array of amplitude values in unit^2/Hz
            -   ``time_freq_support``: Array of regularly spaced frequencies in Hz associated with
                amplitude values (from 0 Hz to the maximum frequency)
            -   ``unit`` = "<unit>^2/Hz" (where <unit> is Pa for example).

            You can use the function
            :func:`create_scalar_field() <ansys.dpf.core.fields_factory.create_scalar_field>`
            to create the field.

        frequency_list : list, default: None
            List of the frequencies in Hz of the tones (peaks in the spectrum)
            on which to calculate the PR. The default is ``None``, in which case a peak
            detection method is applied to automatically find the tones in the input
            spectrum. Then, the PR is calculated for each detected tone.
        """
        super().__init__()
        self.psd = psd  # uses the setter
        self.frequency_list = frequency_list  # uses the setter
        self.__operator = Operator("compute_PR")

    @property
    def psd(self) -> Field:
        """Input power spectral density (PSD).

        The PSD field has the following characteristics:

        -   ``num_entities`` = 1
        -   ``location`` = "TimeFreq_sets"
        -   ``data``: Vector of amplitude values in unit^2/Hz
        -   ``time_freq_support``: Vector of regularly spaced frequencies in Hz associated with
            amplitude values (from 0 Hz to the maximum frequency)
        -   ``unit`` = "<unit>^2/Hz" (where <unit> is Pa for example).

        You can use the function
        :func:`create_scalar_field() <ansys.dpf.core.fields_factory.create_scalar_field>`
        to create the field.
        """
        return self.__psd

    @psd.setter
    def psd(self, psd: Field):
        """Set the PSD."""
        self.__psd = psd

    @property
    def frequency_list(self) -> list[float]:
        """Tone frequency list in Hz.

        List of the frequencies in Hz of the tones (peaks in the PSD) where the PR shall be
        calculated.

        If this parameter is unspecified (``None``), a peak detection algorithm is applied to
        locate the tones in the input PSD. Then, the PR is calculated for each detected tone.
        """
        return self.__frequency_list

    @frequency_list.setter
    def frequency_list(self, frequency_list: list[float]):
        """Set the list of tone frequencies on which to calculate the PR."""
        self.__frequency_list = frequency_list

    def process(self):
        """Compute the PR.

        This method calls the appropriate DPF Sound operator to compute the PR on the PSD.
        """
        if self.__psd == None:
            raise PyAnsysSoundException(
                "No PSD found for PR computation. Use 'ProminenceRatio.psd'."
            )

        self.__operator.connect(0, self.psd)

        # optional parameter: frequency list
        if self.frequency_list is not None:
            # Convert to floats (in case integers were provided)
            frequency_list = list(np.float64(self.frequency_list))
            self.__operator.connect(1, frequency_list)

        # Runs the operator
        self.__operator.run()

        # Stores outputs in the tuple variable
        self._output = self.__operator.get_output(0, "generic_data_container")

    def get_output(self) -> GenericDataContainer:
        """Get PR data in a tuple as a generic data container.

        Returns
        -------
        GenericDataContainer
            PR data as a generic data container.
        """
        if self._output == None:
            warnings.warn(PyAnsysSoundWarning("Output is not processed yet. \
                        Use the 'ProminentRatio.process()' method."))

        return self._output

    def get_output_as_nparray(self) -> tuple[np.ndarray] | None:
        """Get PR data in a tuple as a NumPy array.

        Returns
        -------
        tuple
            -   First element: array of the peaks' frequencies in Hz.

            -   Second element: array of the peaks' PR values in dB.

            -   Third element: array of the peaks' level values in dB SPL.

            -   Fourth element: array of the lower-frequency limits, in Hz, of the critical
                bandwidths centered on the peaks' frequencies.

            -   Fifth element: array of the upper-frequency limits, in Hz, of the critical
                bandwidths centered on the peaks' frequencies.

            -   Sixth element: maximum PR value in dB.

            .. note::
                The first five elements are arrays of the same length.
                The sixth element is a float.
        """
        pr_container = self.get_output()
        if pr_container == None:
            return None

        return (
            np.copy(pr_container.get_property("frequency_Hz").data),
            np.copy(pr_container.get_property("PR_dB").data),
            np.copy(pr_container.get_property("level_dB").data),
            np.copy(pr_container.get_property("bandwidth_lower_Hz").data),
            np.copy(pr_container.get_property("bandwidth_higher_Hz").data),
            np.copy(pr_container.get_property("PR_max")),
        )

    def get_nb_tones(self) -> int:
        """Get the number of tones.

        Returns
        -------
        int
            Number of tones.
        """
        if self.get_output() == None:
            raise PyAnsysSoundException("Output is not processed yet. \
                    Use the 'ProminenceRatio.process()' method.")

        return len(self.get_output_as_nparray()[0])

    def get_peaks_frequencies(self) -> np.ndarray:
        """Get the vector of the peaks' frequencies.

        Returns
        -------
        numpy.ndarray
            Vector of the peaks' frequencies in Hz.
        """
        if self.get_output_as_nparray() == None:
            return None

        return self.get_output_as_nparray()[0]

    def get_PR_values(self) -> np.ndarray:
        """Get the vector of the peaks' PR values.

        Returns
        -------
        numpy.ndarray
            Vector of the peaks' PR values in dB.
        """
        if self.get_output_as_nparray() == None:
            return None

        return self.get_output_as_nparray()[1]

    def get_peaks_levels(self) -> np.ndarray:
        """Get the vector of the peaks' level values.

        Returns
        -------
        numpy.ndarray
            Vector of the peaks' level values in dB SPL.
        """
        if self.get_output_as_nparray() == None:
            return None

        return self.get_output_as_nparray()[2]

    def get_peaks_low_frequencies(self) -> np.ndarray:
        """Get the vector of the peaks' lower-frequency limits.

        Returns
        -------
        numpy.ndarray
            Vector of the peaks' lower-frequency limits in Hz.
        """
        if self.get_output_as_nparray() == None:
            return None

        return self.get_output_as_nparray()[3]

    def get_peaks_high_frequencies(self) -> np.ndarray:
        """Get the vector of the peaks' higher-frequency limits.

        Returns
        -------
        numpy.ndarray
            Vector of the peaks' higher-frequency limits in Hz.
        """
        if self.get_output_as_nparray() == None:
            return None

        return self.get_output_as_nparray()[4]

    def get_max_PR_value(self) -> float:
        """Get the maximum PR value.

        Returns
        -------
        float
            Maximum PR value in dB.
        """
        if self.get_output_as_nparray() == None:
            return None

        return self.get_output_as_nparray()[5]

    def get_single_tone_info(self, tone_index: int) -> tuple[float]:
        """Get the PR information for a tone.

        Parameters
        ----------
        tone_index : int
            Index of the tone.

        Returns
        -------
        tuple[float]
            -   First element: frequency of the peak in Hz.

            -   Second element: PR value in dB.

            -   Third element: level of the peak in dB SPL.

            -   Fourth element: lower-frequency limit of the critical band centered on the peak,
                in Hz.

            -   Fifth element: higher-frequency limit of the critical band centered on the peak,
                in Hz.
        """
        nb_tones = self.get_nb_tones()
        if nb_tones == 0:
            raise PyAnsysSoundException("No peak is detected.")

        if not (0 <= tone_index < nb_tones):
            raise PyAnsysSoundException(
                f"Tone index is out of bound. It must be between 0 and {nb_tones - 1}."
            )

        return (
            self.get_peaks_frequencies()[tone_index],
            self.get_PR_values()[tone_index],
            self.get_peaks_levels()[tone_index],
            self.get_peaks_low_frequencies()[tone_index],
            self.get_peaks_high_frequencies()[tone_index],
        )

    def get_reference_curve(self) -> np.ndarray:
        """Get the reference threshold curve, above which a tone is considered as prominent.

        Returns
        -------
        numpy.ndarray
            Reference curve with which to compare the PR, as defined in the ECMA 418-1 and ISO 7779
            standards. If the PR is higher, then the tone is defined as prominent.
        """
        if self.__psd == None:
            raise PyAnsysSoundException("No PSD set. Use 'ProminenceRatio.psd'.")

        all_frequencies = self.__psd.time_freq_support.time_frequencies.data
        curve_length = len(all_frequencies)
        ref_curve = np.ndarray(curve_length)

        for index in range(curve_length):
            current_frequency = all_frequencies[index]
            if current_frequency < 89.1:
                ref_curve[index] = 0

            elif current_frequency < 1000:
                ref_curve[index] = 9 + 10 * log10(1000 / current_frequency)

            elif current_frequency < 11220:
                ref_curve[index] = 9

            else:
                ref_curve[index] = 0

        return ref_curve

    def plot(self):
        """Plot the PR for all identified peaks, along with the threshold curve."""
        if self._output == None:
            raise PyAnsysSoundException("Output is not processed yet. \
                    Use the 'ProminenceRatio.process()' method.")

        tones_frequencies = self.get_peaks_frequencies()
        PR_values = self.get_PR_values()

        all_frequencies = np.copy(self.__psd.time_freq_support.time_frequencies.data)

        # Cut both curves at 11220 Hz,
        # which is the maximum frequency for which the reference threshold curve is defined
        max_index = np.min(np.where(all_frequencies > 11220)) + 1
        all_frequencies = all_frequencies[:max_index]

        final_curve_length = len(all_frequencies)
        PR_final_curve = np.ndarray(final_curve_length)
        PR_final_curve.fill(0)

        # for each tone:
        # - find its corresponding index in all_frequencies
        # - replace this index in PR_final_curve by corresponding PR value
        for tone_index in range(self.get_nb_tones()):
            frequency = tones_frequencies[tone_index]
            PR_value = PR_values[tone_index]
            for index in range(final_curve_length):
                if abs(all_frequencies[index] - frequency) / frequency < 1.0e-3:
                    PR_final_curve[index] = PR_value
                    break

        # Plot
        plt.plot(all_frequencies, PR_final_curve, color="blue", label="PR")
        plt.plot(
            all_frequencies,
            self.get_reference_curve()[:max_index],
            color="black",
            label="Reference threshold curve",
        )

        plt.legend()
        plt.title("Prominence Ratio")
        plt.xlabel("Frequency (Hz)")
        plt.ylabel("PR (dB)")
        plt.grid(True)
        plt.show()
