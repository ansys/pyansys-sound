"""Compute ISO 532-1 loudness for stationary sounds."""
import warnings

from ansys.dpf.core import Field, FieldsContainer, Operator
import matplotlib.pyplot as plt
import numpy as np
from numpy import typing as npt

from . import PsychoacousticsParent
from ..pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning

LOUDNESS_SONE_ID = "sone"
LOUDNESS_LEVEL_PHON_ID = "phon"
SPECIFIC_LOUDNESS_ID = "specific"


class LoudnessISO532_1_Stationary(PsychoacousticsParent):
    """ISO 532-1 loudness for stationary sounds.

    This class computes the loudness of a signal following standard ISO 532-1 for stationary
    sounds.
    """

    def __init__(self, signal: Field | FieldsContainer = None):
        """Create a LoudnessISO532_1_Stationary object.

        Parameters
        ----------
        signal: Field | FieldsContainer
            Signal in Pa on which to compute loudness, as a DPF Field or Fields Container.
        """
        super().__init__()
        self.signal = signal
        self.__operator = Operator("compute_loudness_iso532_1")

    @property
    def signal(self):
        """Signal property."""
        return self.__signal  # pragma: no cover

    @signal.setter
    def signal(self, signal: Field | FieldsContainer):
        """Set the signal.

        Parameters
        ----------
        signal: FieldsContainer | Field
            Signal in Pa on which to compute loudness, as a DPF Field or Fields Container.

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
        """Compute loudness.

        Calls the appropriate DPF Sound operator to compute the loudness of the signal.
        """
        if self.__signal == None:
            raise PyAnsysSoundException(
                "No signal for loudness computation. Use LoudnessISO532_1_Stationary.signal."
            )

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
                PyAnsysSoundWarning(
                    "Output has not been processed yet, use LoudnessISO532_1_Stationary.process()."
                )
            )

        return self._output

    def get_output_as_nparray(self) -> tuple[npt.ArrayLike]:
        """Return loudness data as a tuple of numpy array.

        Returns
        -------
        tuple[numpy.ndarray]
            First element is the loudness in sone.
            Second element is the loudness level in phon.
            Third element is the specific loudness in sone/Bark.
        """
        output = self.get_output()

        if output == None:
            return None

        if type(output[0]) == Field:
            return (np.array(output[0].data), np.array(output[1].data), np.array(output[2].data))

        return (
            self.convert_fields_container_to_np_array(output[0]),
            self.convert_fields_container_to_np_array(output[1]),
            self.convert_fields_container_to_np_array(output[2]),
        )

    def get_loudness_sone(self, channel_index: int = 0) -> np.float64:
        """Return loudness in sone.

           Returns the loudness in sone as a float, for the specified channel index.

        Parameters
        ----------
        channel_index: int
            Index of the signal channel (0 by default) for which to return the specified output.

        Returns
        -------
        numpy.float64
            Loudness value in sone.
        """
        return self._get_output_parameter(channel_index, LOUDNESS_SONE_ID)

    def get_loudness_level_phon(self, channel_index: int = 0) -> np.float64:
        """Return loudness level in phon.

        Returns the loudness level in phon as a float, for the specified channel index.

        Parameters
        ----------
        channel_index: int
            Index of the signal channel (0 by default) for which to return the specified output.

        Returns
        -------
        numpy.float64
            Loudness level value in phon.
        """
        return self._get_output_parameter(channel_index, LOUDNESS_LEVEL_PHON_ID)

    def get_specific_loudness(self, channel_index: int = 0) -> npt.ArrayLike:
        """Return specific loudness.

        Returns the specific loudness in sone/Bark, for the specified channel index.

        Parameters
        ----------
        channel_index: int
            Index of the signal channel (0 by default) for which to return the specified output.

        Returns
        -------
        numpy.ndarray
            Specific loudness array in sone/Bark.
        """
        return self._get_output_parameter(channel_index, SPECIFIC_LOUDNESS_ID)

    def get_bark_band_indexes(self) -> npt.ArrayLike:
        """Return Bark band indexes.

        Returns the Bark band indexes used for loudness calculation as a numpy array.

        Returns
        -------
        numpy.ndarray
            Array of Bark band idexes.
        """
        output = self.get_output()

        if output == None:
            return None

        specific_loudness = output[2]

        if type(specific_loudness) == Field:
            return np.copy(specific_loudness.time_freq_support.time_frequencies.data)
        else:
            return np.copy(specific_loudness[0].time_freq_support.time_frequencies.data)

    def get_bark_band_frequencies(self) -> npt.ArrayLike:
        """Return Bark band frequencies.

        Return the frequencies corresponding to Bark band indexes as a numpy array.

        Reference:
        Traunmüller, Hartmut. "Analytical Expressions for the Tonotopic Sensory Scale." Journal of
        the Acoustical Society of America. Vol. 88, Issue 1, 1990, pp. 97–100.

        Returns
        -------
        numpy.ndarray
            Array of Bark band frequencies.
        """
        return self._convert_bark_to_hertz(self.get_bark_band_indexes())

    def plot(self):
        """Plot specific loudness.

        Creates a figure window where the specific loudness in sone/Bark as a function of Bark band
        index is displayed.
        """
        if self._output == None:
            raise PyAnsysSoundException(
                "Output has not been processed yet, use LoudnessISO532_1_Stationary.process()."
            )

        bark_band_indexes = self.get_bark_band_indexes()
        specific_loudness_as_nparray = self.get_output_as_nparray()[2]

        if type(self._output[2]) == Field:
            num_channels = 1
            plt.plot(bark_band_indexes, specific_loudness_as_nparray)
        else:
            num_channels = len(self._output[2])
            if num_channels == 1:
                plt.plot(bark_band_indexes, specific_loudness_as_nparray)
            else:
                for ichannel in range(num_channels):
                    plt.plot(
                        bark_band_indexes,
                        specific_loudness_as_nparray[ichannel],
                        label="Channel {}".format(ichannel),
                    )

        plt.title("Specific loudness")
        plt.xlabel("Bark band index")
        plt.ylabel("N' (sone/Bark)")
        plt.grid(True)
        if num_channels > 1:
            plt.legend()
        plt.show()

    def _get_output_parameter(
        self, channel_index: int, output_id: str
    ) -> np.float64 | npt.ArrayLike:
        """Return individual loudness result.

        Returns the loudness or loudness level in phon as a float, or the specific loudness as a
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
        numpy.float64 | numpy.ndarray
            Loudness or loudness level value (float, in sone or phon, respectively), or specific
            loudness (numpy array, in sone/Bark).
        """
        loudness_data = self.get_output_as_nparray()
        if loudness_data == None:
            return None

        # Get last channel index.
        channel_max = len(loudness_data[0]) - 1

        # Check that specified channel index exists.
        if channel_index > channel_max:
            raise PyAnsysSoundException(
                f"Specified channel index ({channel_index}) does not exist."
            )

        # Return output parameter (loudness, loudness level, or specific loudness) for the specified
        # channel.
        if output_id == SPECIFIC_LOUDNESS_ID:
            if channel_max > 0:
                return loudness_data[2][channel_index]
            else:
                return loudness_data[2]
        else:
            if output_id == LOUDNESS_SONE_ID:
                unit_index = 0
            elif output_id == LOUDNESS_LEVEL_PHON_ID:
                unit_index = 1
            else:
                raise PyAnsysSoundException("Invalid identifier of output parameter.")

            if channel_max > 0:
                return loudness_data[unit_index][channel_index][0]
            else:
                return loudness_data[unit_index][0]
