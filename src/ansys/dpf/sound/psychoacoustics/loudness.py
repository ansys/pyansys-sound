"""Compute ISO 532-1 loudness for stationary sounds."""
import warnings

from ansys.dpf.core import Field, FieldsContainer, Operator
import matplotlib.pyplot as plt
from numpy import typing as npt

from . import PsychoacousticsParent
from ..pydpf_sound import PyDpfSoundException, PyDpfSoundWarning


class Loudness_ISO532_1_stationary(PsychoacousticsParent):
    """ISO 532-1 loudness for stationary sounds.

    This class computes the loudness of a signal following standard ISO 532-1 for stationary
    sounds.
    """

    def __init__(self, signal: Field | FieldsContainer = None):
        """Instantiate a Loudness_ISO532_1_stationary object.

        Parameters
        ----------
        signal: Field | FieldsContainer
            Signal in Pa on which to compute the Loudness, as a DPF Field or Fields Container.
        """
        super().__init__()
        self.signal = signal
        self.__operator = Operator("compute_loudness_iso532_1")

    @property
    def signal(self):
        """Signal property."""
        return self.__signal  # pragma: no cover*

    @signal.setter
    def signal(self, signal: Field | FieldsContainer):
        """Set the signal.

        Parameters
        -------
        signal: FieldsContainer | Field
            Signal in Pa on which to compute the Loudness, as a DPF Field or Fields Container.

        """
        self.__signal = signal

    @signal.getter
    def signal(self) -> Field | FieldsContainer:
        """Get the signal.

        Returns
        -------
        FieldsContainer | Field
            The signal in Pa as a Field or a FieldsContainer.
        """
        return self.__signal

    def process(self):
        """Compute the loudness.

        Calls the appropriate DPF Sound operator to compute the loudness of the signal.
        """
        if self.__signal == None:
            raise PyDpfSoundException("No signal for loudness computation. Use Loudness.signal.")

        self.__operator.connect(0, self.signal)

        # Runs the operator
        self.__operator.run()

        # Stores outputs in the tuple variable
        if type(self.signal) == FieldsContainer:
            self._output = (
                self.__operator.get_output(0, "fields_container"),
                self.__operator.get_output(1, "fields_container"),
                self.__operator.get_output(2, "fields_container"),
            )
        elif type(self.signal) == Field:
            self._output = (
                self.__operator.get_output(0, "field"),
                self.__operator.get_output(1, "field"),
                self.__operator.get_output(2, "field"),
            )

    def get_output(self) -> tuple[FieldsContainer] | tuple[Field]:
        """Return loudness data in a tuple of field or fields container.

        Returns
        -------
        tuple(FieldsContainer) | tuple(Field)
            First element is the loudness in sone.
            Second element is the loudness level in phon.
            Third element is the specific loudness in sone/Bark.
        """
        if self._output == None:
            warnings.warn(
                PyDpfSoundWarning("Output has not been processed yet, use Loudness.process().")
            )

        return self._output

    def get_output_as_nparray(self) -> tuple[npt.ArrayLike]:
        """Return loudness data as a tuple of numpy array.

        Returns
        -------
        tuple[npt.ArrayLike]
            First element is the loudness in sone.
            Second element is the loudness level in phon.
            Third element is the specific loudness in sone/Bark.
        """
        output = self.get_output()

        if output == None:
            warnings.warn(
                PyDpfSoundWarning("Output has not been processed yet, use Loudness.process().")
            )
            return None

        if type(output[0]) == Field:
            return (output[0].data, output[1].data, output[2].data)

        return (
            self.convert_fields_container_to_np_array(output[0]),
            self.convert_fields_container_to_np_array(output[1]),
            self.convert_fields_container_to_np_array(output[2]),
        )

    def get_loudness_sone(self, channel_index: int = 0) -> float:
        """Return loudness in sone.

           Returns the loudness in sone as a float, for the specified channel index.

        Parameters
        ----------
        channel_index: int
            Index of the signal channel (0 by default) for which to return the specified output.

        Returns
        -------
        float
            Loudness value in sone.
        """
        return self._get_output_parameter(channel_index, "sone")

    def get_loudness_level_phon(self, channel_index: int = 0) -> float:
        """Return loudness level in phon.

        Returns the loudness level in phon as a float, for the specified channel index.

        Parameters
        ----------
        channel_index: int
            Index of the signal channel (0 by default) for which to return the specified output.

        Returns
        -------
        float
            Loudness level value in phon.
        """
        return self._get_output_parameter(channel_index, "phon")

    def get_specific_loudness(self, channel_index: int = 0) -> npt.ArrayLike:
        """Return specific loudness.

        Returns the specific loudness in sone/Bark, for the specified channel index.

        Parameters
        ----------
        channel_index: int
            Index of the signal channel (0 by default) for which to return the specified output.

        Returns
        -------
        npt.ArrayLike
            Specific loudness array in sone/Bark.
        """
        return self._get_output_parameter(channel_index, "specific")

    def get_Bark_band_indexes(self) -> npt.ArrayLike:
        """Return Bark band indexes.

        Returns the Bark band indexes used for loudness calculation as a numpy array.

        Returns
        -------
        npt.ArrayLike
            Array of Bark band idexes.
        """
        output = self.get_output()

        if output == None:
            warnings.warn(
                PyDpfSoundWarning("Output has not been processed yet, use Loudness.process().")
            )
            return None

        specific_loudness = output[2]

        if type(specific_loudness) == Field:
            return specific_loudness.time_freq_support.time_frequencies.data
        else:
            return specific_loudness[0].time_freq_support.time_frequencies.data

    def get_Bark_band_frequencies(self) -> npt.ArrayLike:
        """Return Bark band frequencies.

        Return the frequencies corresponding to Bark band indexes as a numpy array.

        Reference:
        Traunmüller, Hartmut. "Analytical Expressions for the Tonotopic Sensory Scale." Journal of
        the Acoustical Society of America. Vol. 88, Issue 1, 1990, pp. 97–100.

        Returns
        -------
        npt.ArrayLike
            Array of Bark band frequencies.
        """
        Bark_band_indexes = self.get_Bark_band_indexes()

        for iBark in range(len(Bark_band_indexes)):
            if Bark_band_indexes[iBark] < 2:
                Bark_band_indexes[iBark] = (Bark_band_indexes[iBark] - 0.3) / 0.85
            elif Bark_band_indexes[iBark] > 20.1:
                Bark_band_indexes[iBark] = (Bark_band_indexes[iBark] + 4.422) / 1.22
        return 1920 * (Bark_band_indexes + 0.53) / (26.28 - Bark_band_indexes)

    def plot(self):
        """Plot specific loudness.

        Creates a figure window where the specific loudness in sone/Bark as a function of Bark band
        index is displayed.
        """
        if self._output == None:
            raise PyDpfSoundException("Output has not been processed yet, use Loudness.process().")

        specific_loudness = self.get_output()[2]

        if type(specific_loudness) == Field:
            num_channels = 1
            bark_band_indexes = specific_loudness.time_freq_support.time_frequencies.data
            specific_loudness_as_nparray = self.get_output_as_nparray()[2]
            plt.plot(bark_band_indexes, specific_loudness_as_nparray)
        else:
            num_channels = len(specific_loudness)
            bark_band_indexes = specific_loudness[0].time_freq_support.time_frequencies.data
            specific_loudness_as_nparray = self.get_output_as_nparray()[2]

            if num_channels == 1:
                plt.plot(bark_band_indexes, specific_loudness_as_nparray)
            else:
                for ichannel in range(num_channels):
                    plt.plot(
                        bark_band_indexes,
                        specific_loudness_as_nparray[:, ichannel],
                        label="Channel {}".format(ichannel),
                    )

        plt.title("Specific loudness")
        plt.xlabel("Bark band index")
        plt.ylabel("N' (sones/Bark)")
        plt.grid(True)
        if num_channels > 1:
            plt.legend()
        plt.show()

    def _get_output_parameter(self, channel_index: int, output_id: str) -> float | npt.ArrayLike:
        """Return individual loudness result.

        Returns the loudness or loudness level in phon as a float, or the specific loudness as an
        numpy array, according to specified output_id, and for the specified channel.

        Parameters
        ----------
        channel_index: int
            Index of the signal channel for which to return the specified output.
        output_id: str
            Identifier of the specific output parameter that should be returned:
                - "sone" for overall loudness value in sone.
                - "phon" for overall loudness level value in phon.
                - "specific" for specific loudness array in sone/Bark.

        Returns
        -------
        float | numpy array
            Loudness or loudness level value (float, in sone or phon, respectively), or specific
            loudness (numpy array, in sone/Bark).
        """
        if self._output == None:
            warnings.warn(
                PyDpfSoundWarning("Output has not been processed yet, use Loudness.process().")
            )
            return None

        # Extract specified result from output field or fields container
        if output_id == "sone":
            fc_loudness_result = self._output[0]
        elif output_id == "phon":
            fc_loudness_result = self._output[1]
        elif output_id == "specific":
            fc_loudness_result = self._output[2]

        # Get the result corresponding to specified channel
        if type(fc_loudness_result) == FieldsContainer:
            if channel_index > len(fc_loudness_result) - 1:
                raise PyDpfSoundException(
                    f"Specified channel index ({channel_index}) does not exist."
                )
            f_loudness_result = fc_loudness_result[channel_index]
        elif type(fc_loudness_result) == Field:
            # fc_loudness_scalar can only be a field if signal is monophonic
            if channel_index > 0:
                raise PyDpfSoundException(
                    f"Signal is monophonic. Specified channel index ({channel_index})"
                    " does not exist."
                )
            f_loudness_result = fc_loudness_result

        if output_id == "specific":
            return f_loudness_result.data
        else:
            return f_loudness_result.data[0]
