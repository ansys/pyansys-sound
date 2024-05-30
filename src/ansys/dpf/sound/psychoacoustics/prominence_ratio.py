"""Compute ECMA 418-1 prominence ratio (PR)."""
from math import log10
import warnings

from ansys.dpf.core import Field, GenericDataContainer, Operator
import matplotlib.pyplot as plt
import numpy as np
from numpy import typing as npt

from . import PsychoacousticsParent
from ..pydpf_sound import PyDpfSoundException, PyDpfSoundWarning


class ProminenceRatio(PsychoacousticsParent):
    """ECMA 418-1 prominence ratio (PR).

    This class computes the prominence ratio (PR) on a PSD (Power Spectral Density)
    following standard ECMA 418-1.
    """

    def __init__(self, psd: Field = None, frequency_list: list = None):
        """Instantiate a ProminenceRatio object.

        Parameters
        ----------
        psd: Field
            Power Spectral Density (PSD) of the signal on which to compute PR, as a DPF Field.

        frequency_list: (optional) tuple
            List of the frequencies of the tones (peaks in the spectrum) for which you want
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
        frequency_list: tuple
            List of the frequencies of the tones (peaks in the spectrum) for which you want
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
        tuple
            List of the frequencies of the tones (peaks in the spectrum) for which you want
            to calculate the PR.
            If this input is empty (not specified), a peak detection method is applied to
            automatically find the tones in the input spectrum. Then the PR is calculated
            for each detected tone.
        """
        return self.__frequency_list

    def process(self):
        """Compute loudness.

        Calls the appropriate DPF Sound operator to compute the loudness on the PSD.
        """
        if self.__psd == None:
            raise PyDpfSoundException("No PSD for PR computation. Use ProminenceRatio.psd.")

        self.__operator.connect(0, self.psd)

        # optional parameter: frequency list
        if self.frequency_list != None:
            self.__operator.connect(1, self.frequency_list)

        # Runs the operator
        self.__operator.run()

        # Stores outputs in the tuple variable
        self._output = self.__operator.get_output(0, "generic_data_container")

    def get_output(self) -> GenericDataContainer:
        """Return prominence ration data in a tuple of GenericDataContainer.

        Returns
        -------
        GenericDataContainer
            PR curve.
            PR details.
        """
        if self._output == None:
            warnings.warn(
                PyDpfSoundWarning(
                    "Output has not been processed yet, use Loudness_ISO532_1_Stationary.process()."
                )
            )

        return self._output

    def get_output_as_nparray(self) -> tuple[npt.ArrayLike] | None:
        """Return PR data as a tuple of numpy array.

        Returns
        -------
            First element is the vector of peaks' frequencies.
            Second element is the vector of peaks' PR values.
            Third element is the vector of peaks' level values.
            Fourth element is the vector of peaks' low frequencies.
            Fifth element is the vector of peaks' high frequencies.
            Sixth element is the maximum PR value.

        Note: elements 1 to 5 are vector which have the same length. 6th element is a float.
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
        """Return the number of tones."""
        if self.get_output_as_nparray() == None:
            return 0

        return len(self.get_output_as_nparray()[0])

    def get_peaks_frequencies(self) -> npt.ArrayLike:
        """Return the vector of peaks' frequencies."""
        if self.get_output_as_nparray() == None:
            return None

        return self.get_output_as_nparray()[0]

    def get_PR_values(self) -> npt.ArrayLike:
        """Return the vector of peaks' PR values."""
        if self.get_output_as_nparray() == None:
            return None

        return self.get_output_as_nparray()[1]

    def get_peaks_levels(self) -> npt.ArrayLike:
        """Return the vector of peaks' level values."""
        if self.get_output_as_nparray() == None:
            return None

        return self.get_output_as_nparray()[2]

    def get_peaks_low_frequencies(self) -> npt.ArrayLike:
        """Return the vector of peaks' low frequencies."""
        if self.get_output_as_nparray() == None:
            return None

        return self.get_output_as_nparray()[3]

    def get_peaks_high_frequencies(self) -> npt.ArrayLike:
        """Return the vector of peaks' high frequencies."""
        if self.get_output_as_nparray() == None:
            return None

        return self.get_output_as_nparray()[4]

    def get_max_PR_value(self) -> float:
        """Return the maximum PR value."""
        if self.get_output_as_nparray() == None:
            return None

        return self.get_output_as_nparray()[5]

    def get_all_tone_infos(self, tone_index: int) -> tuple[float]:
        """Return all values for a given tone.

        Parameters
        ----------
        tone_index: int
            index of the tone

        Return
        ------
        tuple[float]
            First element is the peak's frequency.
            Second element is the PR value.
            Third element is the peak's level value.
            Fourth element is the peak's low frequency.
            Fifth element is the peak's high frequency.
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
        """Return eference curve on which to compare PR.

        If PR is higher, then the tone is prominent.
        """
        if self.__psd == None:
            raise PyDpfSoundException("No PSD set. Use ProminenceRatio.psd.")

        all_frequencies = np.copy(self.__psd.time_freq_support.time_frequencies.data)
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
            tone = tones_frequencies[tone_index]
            PR_value = PR_values[tone_index]
            for index in range(final_curve_length):
                if abs(all_frequencies[index] - tone) / tone < 1.0e-3:
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
