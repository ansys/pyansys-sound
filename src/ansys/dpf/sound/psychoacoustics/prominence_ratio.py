"""Compute ECMA 418-1 / ISO 7779 prominence ratio (PR)."""
from math import log10
import warnings

from ansys.dpf.core import Field, GenericDataContainer, Operator
import matplotlib.pyplot as plt
import numpy as np
from numpy import typing as npt

from . import PsychoacousticsParent
from ..pydpf_sound import PyDpfSoundException, PyDpfSoundWarning


class ProminenceRatio(PsychoacousticsParent):
    """ECMA 418-1 / ISO 7779 prominence ratio (PR).

    This class computes the prominence ratio (PR) on a PSD (Power Spectral Density)
    following standards ECMA 418-1 and ISO 7779.
    """

    def __init__(self, psd: Field = None, frequency_list: list = None):
        """Create a ProminenceRatio object.

        Parameters
        ----------
        psd: Field
            Power Spectral Density (PSD) of the signal on which to compute PR, as a DPF Field.
            The PSD Field has the following characteristics:
            - num_entities = 1
            - location = "TimeFreq_sets"
            - data: vector of amplitude values in unit^2/Hz;
            - time_freq_support: vector of regularly spaced frequencies in Hz associated to
            amplitude values (from 0 Hz to the maximum frequency)
            - unit = "<unit>^2/Hz" (where <unit> is Pa for example).
            You can use the function ansys.dpf.core.fields_factory.create_scalar_field()
            to create the field.

        frequency_list: (optional) list
            List of the frequencies in Hz of the tones (peaks in the spectrum) for which
            to calculate the PR.
            If this input is empty (not specified), a peak detection method is applied to
            automatically find the tones in the input spectrum. Then the PR is calculated
            for each detected tone.
        """
        super().__init__()
        self.psd = psd  # uses the setter
        self.frequency_list = frequency_list  # uses the setter
        self.__operator = Operator("compute_PR")

    @property
    def psd(self):
        """PSD property."""
        return self.__psd  # pragma: no cover

    @psd.setter
    def psd(self, psd: Field):
        """Set the PSD.

        Parameters
        -------
        psd: Field
            Power Spectral Density (PSD) of the signal on which to compute PR, as a DPF Field.
            The PSD Field has the following characteristics:
            - num_entities = 1
            - location = "TimeFreq_sets"
            - data: vector of amplitude values in unit^2/Hz;
            - time_freq_support: vector of regularly spaced frequencies in Hz associated to
            amplitude values (from 0 Hz to the maximum frequency)
            - unit = "<unit>^2/Hz" (where <unit> is Pa for example).
            You can use the function ansys.dpf.core.fields_factory.create_scalar_field()
            to create the field.
        """
        self.__psd = psd

    @psd.getter
    def psd(self) -> Field:
        """Get the PSD.

        Returns
        -------
        Field
            Power Spectral Density (PSD) of the signal on which to compute PR, as a DPF Field.
        """
        return self.__psd

    @property
    def frequency_list(self):
        """frequency_list property."""
        return self.__frequency_list  # pragma: no cover

    @frequency_list.setter
    def frequency_list(self, frequency_list: list):
        """Set the frequency_list.

        Parameters
        -------
        frequency_list: list
            List of the frequencies in Hz of the tones (peaks in the spectrum) for which
            to calculate the PR.
            If this input is empty (not specified), a peak detection method is applied to
            automatically find the tones in the input spectrum. Then the PR is calculated
            for each detected tone.
        """
        self.__frequency_list = frequency_list

    @frequency_list.getter
    def frequency_list(self) -> list:
        """Get the frequency_list.

        Returns
        -------
        list
            List of the frequencies in Hz of the tones (peaks in the spectrum) for which
            to calculate the PR.
        """
        return self.__frequency_list

    def process(self):
        """Compute PR.

        Calls the appropriate DPF Sound operator to compute the PR on the PSD.
        """
        if self.__psd == None:
            raise PyDpfSoundException("No PSD for PR computation. Use ProminenceRatio.psd.")

        self.__operator.connect(0, self.psd)

        # optional parameter: frequency list
        if self.frequency_list != None:
            # Convert to floats (if integers were provided)
            frequency_list = list(np.float64(self.frequency_list))
            self.__operator.connect(1, frequency_list)

        # Runs the operator
        self.__operator.run()

        # Stores outputs in the tuple variable
        self._output = self.__operator.get_output(0, "generic_data_container")

    def get_output(self) -> GenericDataContainer:
        """Return prominence ratio data in a tuple of GenericDataContainer.

        Returns
        -------
        GenericDataContainer
            PR curve.
            PR details.
        """
        if self._output == None:
            warnings.warn(
                PyDpfSoundWarning(
                    "Output has not been processed yet, use ProminentRatio.process()."
                )
            )

        return self._output

    def get_output_as_nparray(self) -> tuple[npt.ArrayLike] | None:
        """Return PR data as a tuple of numpy array.

        Returns
        -------
            First element is the vector of peaks' frequencies in Hz.
            Second element is the vector of peaks' PR values in dB.
            Third element is the vector of peaks' level values in dBSPL.
            Fourth element is the vector of peaks' lower frequency limits, in Hz.
            Fifth element is the vector of peaks' higher frequency limits, in Hz.
            Sixth element is the maximum PR value, in dB.

        Note: elements 1 to 5 are vectors of the same length. The 6th element is a float.
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
        """Return the number of tones.

        Returns
        -------
        int
            Number of tones.
        """
        if self.get_output() == None:
            raise PyDpfSoundException(
                "Output has not been processed yet, use ProminenceRatio.process()."
            )

        return len(self.get_output_as_nparray()[0])

    def get_peaks_frequencies(self) -> npt.ArrayLike:
        """Return the vector of peaks' frequencies.

        Returns
        -------
        numpy.ndarray
            Vector of peaks' frequencies in Hz.
        """
        if self.get_output_as_nparray() == None:
            return None

        return self.get_output_as_nparray()[0]

    def get_PR_values(self) -> npt.ArrayLike:
        """Return the vector of peaks' PR values.

        Returns
        -------
        numpy.ndarray
            Vector of peaks' PR values in dB.
        """
        if self.get_output_as_nparray() == None:
            return None

        return self.get_output_as_nparray()[1]

    def get_peaks_levels(self) -> npt.ArrayLike:
        """Return the vector of peaks' level values.

        Returns
        -------
        numpy.ndarray
            Vector of peaks' level values in dBSPL.
        """
        if self.get_output_as_nparray() == None:
            return None

        return self.get_output_as_nparray()[2]

    def get_peaks_low_frequencies(self) -> npt.ArrayLike:
        """Return the vector of peaks' lower frequency limits.

        Returns
        -------
        numpy.ndarray
            Vector of eaks' lower frequency limits in Hz.
        """
        if self.get_output_as_nparray() == None:
            return None

        return self.get_output_as_nparray()[3]

    def get_peaks_high_frequencies(self) -> npt.ArrayLike:
        """Return the vector of peaks' higher frequency limits.

        Returns
        -------
        numpy.ndarray
            Vector of peaks' higher frequency limits in Hz.
        """
        if self.get_output_as_nparray() == None:
            return None

        return self.get_output_as_nparray()[4]

    def get_max_PR_value(self) -> float:
        """Return the maximum PR value.

        Returns
        -------
        float
            Maximum PR value in dB.
        """
        if self.get_output_as_nparray() == None:
            return None

        return self.get_output_as_nparray()[5]

    def get_single_tone_info(self, tone_index: int) -> tuple[float]:
        """Return PR details for a given tone.

        Parameters
        ----------
        tone_index: int
            Index of the tone.

        Returns
        -------
        tuple[float]
            First element is the peak's frequency in Hz.
            Second element is the PR value in dB.
            Third element is the peak's level value in dBSPL.
            Fourth element is the peak's lower frequency limit in Hz.
            Fifth element is the peak's higher frequency limit in Hz.
        """
        nb_tones = self.get_nb_tones()
        if nb_tones == 0:
            raise PyDpfSoundException("No peak detected.")

        if not (0 <= tone_index < nb_tones):
            raise PyDpfSoundException(
                f"Out of bound index. tone_index must be between 0 and {nb_tones - 1}."
            )

        return (
            self.get_peaks_frequencies()[tone_index],
            self.get_PR_values()[tone_index],
            self.get_peaks_levels()[tone_index],
            self.get_peaks_low_frequencies()[tone_index],
            self.get_peaks_high_frequencies()[tone_index],
        )

    def get_reference_curve(self) -> npt.ArrayLike:
        """Return reference curve on which to compare PR.

        Returns
        -------
        numpy.ndarray
            Reference curve with which to compare PR, as defined in standards
            ECMA 418-1 and ISO 7779.
            If PR is higher, then the tone is prominent.
        """
        if self.__psd == None:
            raise PyDpfSoundException("No PSD set. Use ProminenceRatio.psd.")

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
        """Plot prominence ratio for all identified peaks, along with the reference curve."""
        if self._output == None:
            raise PyDpfSoundException(
                "Output has not been processed yet, use ProminenceRatio.process()."
            )

        tones_frequencies = self.get_peaks_frequencies()
        PR_values = self.get_PR_values()

        all_frequencies = np.copy(self.__psd.time_freq_support.time_frequencies.data)

        # Cut both curves at 11220 Hz,
        # which is the maximum frequency for which the reference curve is defined
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
            label="Reference curve",
        )

        plt.legend()
        plt.title("Prominence Ratio")
        plt.xlabel("Frequency (Hz)")
        plt.ylabel("PR (dB)")
        plt.grid(True)
        plt.show()
