"""Compute fluctuation strength."""
import warnings

from ansys.dpf.core import Field, FieldsContainer, Operator
import matplotlib.pyplot as plt
import numpy as np
from numpy import typing as npt

from . import PsychoacousticsParent
from ..pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning

TOTAL_FS_ID = "total"
SPECIFIC_FS_ID = "specific"


class FluctuationStrength(PsychoacousticsParent):
    """Fluctuation strength for stationary sounds.

    This class computes the fluctuation strength of a signal, according to Sontacchi's master
    thesis work: "Entwicklung eines Modulkonzeptes fur die psychoakustische Gerauschanalyse under
    MATLAB". Master thesis, Technischen Universitat Graz, pp. 1-112 (1998).
    """

    def __init__(self, signal: Field | FieldsContainer = None):
        """Create a FluctuationStrength object.

        Parameters
        ----------
        signal: Field | FieldsContainer
            Signal in Pa on which to compute fluctuation strength, as a DPF Field or Fields
            Container.
        """
        super().__init__()
        self.signal = signal
        self.__operator = Operator("compute_fluctuation_strength")

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
            Signal in Pa on which to compute fluctuation strength, as a DPF Field or
            FieldsContainer.

        """
        self.__signal = signal

    @signal.getter
    def signal(self) -> Field | FieldsContainer:
        """Get the input signal.

        Returns
        -------
        FieldsContainer | Field
            The signal in Pa as a Field or a FieldsContainer.
        """
        return self.__signal

    def process(self):
        """Compute fluctuation strength.

        Calls the corresponding DPF Sound operator to compute the fluctuation strength
        of the signal.
        """
        if self.__signal == None:
            raise PyAnsysSoundException(
                "No signal for fluctuation strength computation. Use FluctuationStrength.signal."
            )

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
        """Return fluctuation strength data in a tuple of field or fields container.

        Returns
        -------
        tuple(FieldsContainer) | tuple(Field)
            First element is the fluctuation strength in vacil.
            Second element is the specific fluctuation strength in vacil/Bark.
        """
        if self._output == None:
            warnings.warn(
                PyAnsysSoundWarning(
                    "Output has not been processed yet, use FluctuationStrength.process()."
                )
            )

        return self._output

    def get_output_as_nparray(self) -> tuple[npt.ArrayLike]:
        """Return fluctuation strength data as a tuple of numpy array.

        Returns
        -------
        tuple[numpy.ndarray]
            First element is the fluctuation strength in vacil.
            Second element is the specific fluctuation strength in vacil/Bark.
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

    def get_fluctuation_strength(self, channel_index: int = 0) -> np.float64:
        """Return fluctuation strength in vacil.

           Returns the fluctuation strength in vacil as a float, for the specified channel index.

        Parameters
        ----------
        channel_index: int
            Index of the signal channel (0 by default) for which to return the specified output.

        Returns
        -------
        numpy.float64
            Fluctuation strength value in vacil.
        """
        return self._get_output_parameter(channel_index, TOTAL_FS_ID)

    def get_specific_fluctuation_strength(self, channel_index: int = 0) -> npt.ArrayLike:
        """Return specific fluctuation strength.

        Return the specific fluctuation strength in vacil/Bark, for the specified channel index.

        Parameters
        ----------
        channel_index: int
            Index of the signal channel (0 by default) for which to return the specified output.

        Returns
        -------
        numpy.ndarray
            Specific fluctuation strength array in vacil/Bark.
        """
        return self._get_output_parameter(channel_index, SPECIFIC_FS_ID)

    def get_bark_band_indexes(self) -> npt.ArrayLike:
        """Return Bark band indexes.

        Return the Bark band indexes used for fluctuation strength calculation as a numpy array.

        Returns
        -------
        numpy.ndarray
            Array of Bark band idexes.
        """
        output = self.get_output()

        if output == None:
            return None

        specific_fluctuation_strength = output[1]

        if type(specific_fluctuation_strength) == Field:
            return np.copy(specific_fluctuation_strength.time_freq_support.time_frequencies.data)
        else:
            return np.copy(specific_fluctuation_strength[0].time_freq_support.time_frequencies.data)

    def get_bark_band_frequencies(self) -> npt.ArrayLike:
        """Return Bark band frequencies.

        Return the frequencies corresponding to Bark band indexes as a numpy array.

        Reference:
        Traunmüller, Hartmut. "Analytical Expressions for the Tonotopic Sensory Scale." Journal of
        the Acoustical Society of America. Vol. 88, Issue 1, 1990, pp. 97-100.

        Returns
        -------
        numpy.ndarray
            Array of Bark band frequencies.
        """
        return self._convert_bark_to_hertz(self.get_bark_band_indexes())

    def plot(self):
        """Plot specific fluctuation strength.

        Creates a figure window where the specific fluctuation strength in vacil/Bark as a function
        of Bark band index is displayed.
        """
        if self._output == None:
            raise PyAnsysSoundException(
                "Output has not been processed yet, use FluctuationStrength.process()."
            )

        bark_band_indexes = self.get_bark_band_indexes()
        specific_fluctuation_strength_as_nparray = self.get_output_as_nparray()[1]

        if type(self._output[1]) == Field:
            num_channels = 1
            plt.plot(bark_band_indexes, specific_fluctuation_strength_as_nparray)
        else:
            num_channels = len(self._output[1])
            if num_channels == 1:
                plt.plot(bark_band_indexes, specific_fluctuation_strength_as_nparray)
            else:
                for ichannel in range(num_channels):
                    plt.plot(
                        bark_band_indexes,
                        specific_fluctuation_strength_as_nparray[ichannel],
                        label="Channel {}".format(ichannel),
                    )

        plt.title("Specific fluctuation strength")
        plt.xlabel("Bark band index")
        plt.ylabel("Fluctuation strength (vacil/Bark)")
        plt.grid(True)
        if num_channels > 1:
            plt.legend()
        plt.show()

    def _get_output_parameter(
        self, channel_index: int, output_id: str
    ) -> np.float64 | npt.ArrayLike:
        """Return individual fluctuation strength result.

        Returns the fluctuation strength as a float, or the specific fluctuation strength as a
        numpy array, according to specified output_id, and for the specified channel.

        Parameters
        ----------
        channel_index: int
            Index of the signal channel for which to return the specified output.
        output_id: str
            Identifier of the specific output parameter that should be returned:
                - "total" for overall fluctuation strength value in vacil.
                - "specific" for specific fluctuation strength array in vacil/Bark.

        Returns
        -------
        numpy.float64 | numpy.ndarray
            Fluctuation strength (float) in vacil or specific fluctuation strength (numpy array)
            in vacil/Bark.
        """
        fluctuation_strength_data = self.get_output_as_nparray()
        if fluctuation_strength_data == None:
            return None

        # Get last channel index.
        channel_max = len(fluctuation_strength_data[0]) - 1

        # Check that specified channel index exists.
        if channel_index > channel_max:
            raise PyAnsysSoundException(
                f"Specified channel index ({channel_index}) does not exist."
            )

        # Return output parameter (fluctuation strength or specific fluctuation strength) for the
        # specified channel.
        if output_id == SPECIFIC_FS_ID:
            if channel_max > 0:
                return fluctuation_strength_data[1][channel_index]
            else:
                return fluctuation_strength_data[1]
        elif output_id == TOTAL_FS_ID:
            if channel_max > 0:
                return fluctuation_strength_data[0][channel_index][0]
            else:
                return fluctuation_strength_data[0][0]
        else:
            raise PyAnsysSoundException("Invalid identifier of output parameter.")
