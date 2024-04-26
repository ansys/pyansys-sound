"""Compute Loudness."""
import warnings

from ansys.dpf.core import Field, FieldsContainer, Operator
import matplotlib.pyplot as plt
from numpy import typing as npt

from . import PsychoacousticsParent
from ..pydpf_sound import PyDpfSoundException, PyDpfSoundWarning


class Loudness(PsychoacousticsParent):
    """Loudness.

    This class computes the loudness of a signal.
    """

    def __init__(self, signal: Field | FieldsContainer = None):
        """Create a Loudness class.

        Parameters
        ----------
        signal:
            Mono signal on which to compute the Loudness, as a DPF Field or Fields Container.
        """
        super().__init__()
        self.signal = signal
        self.__operator = Operator("compute_loudness_iso532_1")

    @property
    def signal(self):
        """Signal property."""
        return self.__signal

    @signal.setter
    def signal(self, signal: Field | FieldsContainer):
        """Set the signal."""
        self.__signal = signal

    def process(self):
        """Compute the loudness.

        Calls the appropriate DPF Sound operaot to compute the loudness of the signal.
        """
        if self.__signal == None:
            raise PyDpfSoundException("No signal for loudness computation. Use Loudness.signal")

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
        """Return the loudness in a tuple of fields container.

        First element is the loudness in Sone.
        Second element is the loudness in Phon.
        Third element is the Specific loudness, in Sone vs Bark bands

        Returns
        -------
        tuple(FieldsContainer) | tuple(Field)
        """
        if self._output == None:
            # Computing output if needed
            warnings.warn(
                PyDpfSoundWarning("Output has not been yet processed, use Loudness.process().")
            )

        return self._output

    def get_output_as_nparray(self) -> tuple[npt.ArrayLike]:
        """Return the loudness as numpy arrays.

        Returns
        -------
            tuple[np.array]
                First element is the loudness in Sone.
                Second element is the loudness in Phon.
                Third element is the Specific loudness, in Sone vs Bark bands
        """
        output = self.get_output()

        if output == None:
            warnings.warn(
                PyDpfSoundWarning("Output has not been yet processed, use Loudness.process().")
            )
            return None

        if type(output[0]) == Field:
            return (output[0].data, output[1].data, output[2].data)

        return (
            self.convert_fields_container_to_np_array(output[0]),
            self.convert_fields_container_to_np_array(output[1]),
            self.convert_fields_container_to_np_array(output[2]),
        )

    def get_loudness_sone(self) -> Field | FieldsContainer:
        """Return the loudness in Sone.

        Returns
        -------
            tuple(FieldsContainer) | tuple(Field)
        """
        if self._output == None:
            # Computing output if needed
            warnings.warn(
                PyDpfSoundWarning("Output has not been yet processed, use Loudness.process().")
            )
            return None

        return self._output[0]

    def get_loudness_phon(self) -> Field | FieldsContainer:
        """Return the loudness in Phon.

        Returns
        -------
            tuple(FieldsContainer) | tuple(Field)
        """
        if self._output == None:
            # Computing output if needed
            warnings.warn(
                PyDpfSoundWarning("Output has not been yet processed, use Loudness.process().")
            )
            return None

        return self._output[1]

    def get_specific_loudness(self) -> Field | FieldsContainer:
        """Return the Specific loudness.

        Returns
        -------
            tuple(FieldsContainer) | tuple(Field)
        """
        if self._output == None:
            # Computing output if needed
            warnings.warn(
                PyDpfSoundWarning("Output has not been yet processed, use Loudness.process().")
            )
            return None

        return self._output[2]

    def plot(self):
        """Plot the specific loudness.

        Plots the specific loudness.
        """
        specific_loudness = self.get_specific_loudness()

        if type(specific_loudness) == Field:
            num_channels = 0
            field = specific_loudness
        else:
            num_channels = len(specific_loudness)
            field = specific_loudness[0]

        bark_bands = field.time_freq_support.time_frequencies.data

        for i in range(num_channels):
            plt.plot(bark_bands, specific_loudness[i].data, label="Channel {}".format(i))

        plt.title("Specific loudness")
        plt.legend()
        plt.xlabel("Bark band index")
        plt.ylabel("sones/Bark")
        plt.grid(True)
        plt.show()
