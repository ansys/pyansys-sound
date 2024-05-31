"""Compute roughness."""
import warnings

from ansys.dpf.core import Field, FieldsContainer, Operator
import matplotlib.pyplot as plt
import numpy as np
from numpy import typing as npt

from . import PsychoacousticsParent
from ..pydpf_sound import PyDpfSoundException, PyDpfSoundWarning

TOTAL_ROUGHNESS_ID = "total"
SPECIFIC_ROUGHNESS_ID = "specific"


class Roughness(PsychoacousticsParent):
    """Roughness for stationary sounds.

    This class computes the roughness of a signal, according to Daniel and Weber, "Psychoacoustical
    roughness: implementation of an optimized model." Acta Acustica united with Acustica, 83, pp.
    113-123 (1997).
    """

    def __init__(self, signal: Field | FieldsContainer = None):
        """Create a Roughness object.

        Parameters
        ----------
        signal: Field | FieldsContainer
            Signal in Pa on which to compute roughness, as a DPF Field or Fields Container.
        """
        super().__init__()
        self.signal = signal
        self.__operator = Operator("compute_roughness")

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
            Signal in Pa on which to compute roughness, as a DPF Field or Fields Container.

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
        """Compute roughness.

        Calls the appropriate DPF Sound operator to compute the roughness of the signal.
        """
        if self.__signal == None:
            raise PyDpfSoundException("No signal for roughness computation. Use Roughness.signal.")

        self.__operator.connect(0, self.signal)

        # Runs the operator
        self.__operator.run()

        # Stores outputs in the tuple variable
        if type(self.signal) == FieldsContainer:
            self._output = (
                self.__operator.get_output(0, "fields_container"),
                self.__operator.get_output(1, "fields_container"),
            )
        elif type(self.signal) == Field:
            self._output = (
                self.__operator.get_output(0, "field"),
                self.__operator.get_output(1, "field"),
            )

    def get_output(self) -> tuple[FieldsContainer] | tuple[Field]:
        """Return roughness data in a tuple of field or fields container.

        Returns
        -------
        tuple(FieldsContainer) | tuple(Field)
            First element is the roughness in asper.
            Second element is the specific roughness in asper/Bark.
        """
        if self._output == None:
            warnings.warn(
                PyDpfSoundWarning("Output has not been processed yet, use Roughness.process().")
            )

        return self._output

    def get_output_as_nparray(self) -> tuple[npt.ArrayLike]:
        """Return roughness data as a tuple of numpy array.

        Returns
        -------
        tuple[numpy.ndarray]
            First element is the roughness in asper.
            Second element is the specific roughness in asper/Bark.
        """
        output = self.get_output()

        if output == None:
            return None

        if type(output[0]) == Field:
            return (np.array(output[0].data), np.array(output[1].data))

        return (
            self.convert_fields_container_to_np_array(output[0]),
            self.convert_fields_container_to_np_array(output[1]),
        )

    def get_roughness(self, channel_index: int = 0) -> np.float64:
        """Return roughness in asper.

           Returns the roughness in asper as a float, for the specified channel index.

        Parameters
        ----------
        channel_index: int
            Index of the signal channel (0 by default) for which to return the specified output.

        Returns
        -------
        numpy.float64
            Roughness value in asper.
        """
        return self._get_output_parameter(channel_index, TOTAL_ROUGHNESS_ID)

    def get_specific_roughness(self, channel_index: int = 0) -> npt.ArrayLike:
        """Return specific roughness.

        Returns the specific roughness in asper/Bark, for the specified channel index.

        Parameters
        ----------
        channel_index: int
            Index of the signal channel (0 by default) for which to return the specified output.

        Returns
        -------
        numpy.ndarray
            Specific roughness array in asper/Bark.
        """
        return self._get_output_parameter(channel_index, SPECIFIC_ROUGHNESS_ID)

    def get_bark_band_indexes(self) -> npt.ArrayLike:
        """Return Bark band indexes.

        Returns the Bark band indexes used for roughness calculation as a numpy array.

        Returns
        -------
        numpy.ndarray
            Array of Bark band idexes.
        """
        output = self.get_output()

        if output == None:
            return None

        specific_roughness = output[1]

        if type(specific_roughness) == Field:
            return np.copy(specific_roughness.time_freq_support.time_frequencies.data)
        else:
            return np.copy(specific_roughness[0].time_freq_support.time_frequencies.data)

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
        """Plot specific roughness.

        Creates a figure window where the specific roughness in asper/Bark as a function of Bark
        band index is displayed.
        """
        if self._output == None:
            raise PyDpfSoundException("Output has not been processed yet, use Roughness.process().")

        bark_band_indexes = self.get_bark_band_indexes()
        specific_roughness_as_nparray = self.get_output_as_nparray()[1]

        if type(self._output[1]) == Field:
            num_channels = 1
            plt.plot(bark_band_indexes, specific_roughness_as_nparray)
        else:
            num_channels = len(self._output[1])
            if num_channels == 1:
                plt.plot(bark_band_indexes, specific_roughness_as_nparray)
            else:
                for ichannel in range(num_channels):
                    plt.plot(
                        bark_band_indexes,
                        specific_roughness_as_nparray[ichannel],
                        label="Channel {}".format(ichannel),
                    )

        plt.title("Specific roughness")
        plt.xlabel("Bark band index")
        plt.ylabel("Roughness (asper/Bark)")
        plt.grid(True)
        if num_channels > 1:
            plt.legend()
        plt.show()

    def _get_output_parameter(
        self, channel_index: int, output_id: str
    ) -> np.float64 | npt.ArrayLike:
        """Return individual roughness result.

        Returns the roughness as a float, or the specific roughness as a numpy array, according to
        specified output_id, and for the specified channel.

        Parameters
        ----------
        channel_index: int
            Index of the signal channel for which to return the specified output.
        output_id: str
            Identifier of the specific output parameter that should be returned:
                - "total" for overall roughness value in asper.
                - "specific" for specific roughness array in asper/Bark.

        Returns
        -------
        numpy.float64 | numpy.ndarray
            Roughness (float) in asper or specific roughness (numpy array) in asper/Bark.
        """
        if self.get_output() == None or not (self._check_channel_index(channel_index)):
            return None

        roughness_data = self.get_output_as_nparray()

        # Get last channel index.
        channel_max = len(roughness_data[0]) - 1

        # Return output parameter (roughness or specific roughness) for the specified channel.
        if output_id == SPECIFIC_ROUGHNESS_ID:
            if channel_max > 0:
                return roughness_data[1][channel_index]
            else:
                return roughness_data[1]
        elif output_id == TOTAL_ROUGHNESS_ID:
            if channel_max > 0:
                return roughness_data[0][channel_index][0]
            else:
                return roughness_data[0][0]
        else:
            raise PyDpfSoundException("Invalid identifier of output parameter.")
