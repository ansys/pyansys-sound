"""Compute Loudness."""
import warnings

from ansys.dpf.core import Field, FieldsContainer, Operator
import matplotlib.pyplot as plt
import numpy as np
from numpy import typing as npt

from . import PsychoacousticsParent
from ..pydpf_sound import PyDpfSoundException, PyDpfSoundWarning


class LoudnessVsTime(PsychoacousticsParent):
    """Loudness vs Time.

    This class computes the loudness vs time of a signal.
    """

    def __init__(self, signal: Field | FieldsContainer = None):
        """Create a LoudnessVsTime class.

        Parameters
        ----------
        signal:
            Mono signal on which to compute Loudness vs Time, as a DPF Field or Fields Container.
        """
        super().__init__()
        self.signal = signal
        self.__operator = Operator("compute_loudness_iso532_1_vs_time")

    @property
    def signal(self):
        """Signal property."""
        return self.__signal  # pragma: no cover*

    @signal.setter
    def signal(self, signal: Field | FieldsContainer):
        """Set the signal."""
        self.__signal = signal

    @signal.getter
    def signal(self) -> Field | FieldsContainer:
        """Get the signal.

        Returns
        -------
        FieldsContainer | Field
                The signal as a Field or a FieldsContainer
        """
        return self.__signal

    def process(self):
        """Compute the Loudness vs Time.

        Calls the appropriate DPF Sound operator to compute the loudness of the signal.
        """
        if self.__signal == None:
            raise PyDpfSoundException(
                "No signal for loudness vs time computation. Use LoudnessVsTime.signal"
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
                self.__operator.get_output(3, "fields_container"),
                self.__operator.get_output(4, "fields_container"),
                self.__operator.get_output(5, "fields_container"),
            )
        elif type(self.signal) == Field:
            self._output = (
                self.__operator.get_output(0, "field"),
                self.__operator.get_output(1, "field"),
                self.__operator.get_output(2, "field"),
                self.__operator.get_output(3, "field"),
                self.__operator.get_output(4, "field"),
                self.__operator.get_output(5, "field"),
            )

    def get_output(self) -> tuple[FieldsContainer] | tuple[Field]:
        """Return the loudness in a tuple of fields container.

        Returns
        -------
            tuple(FieldsContainer) | tuple(Field)
                1st element is the loudness vs time in sone.
                2nd element is the N5 indicator, in sone.
                3rd element is the N10 indicator, in sone.
                4th element is the loudness vs time in phon.
                5th element is the L5 indicator, in phon.
                6th element is the L10 indicator, in phon.
        """
        if self._output == None:
            # Computing output if needed
            warnings.warn(
                PyDpfSoundWarning(
                    "Output has not been yet processed, use LoudnessVsTime.process()."
                )
            )

        return self._output

    def get_output_as_nparray(self) -> tuple[npt.ArrayLike]:
        """Return the loudness vs time as numpy arrays.

        Returns
        -------
            tuple[np.array]
                1st element is the loudness vs time in sone.
                2nd element is the N5 indicator, in sone.
                3rd element is the N10 indicator, in sone.
                4th element is the loudness vs time in phon.
                5th element is the L5 indicator, in phon.
                6th element is the L10 indicator, in phon.
        """
        output = self.get_output()

        if output == None:
            warnings.warn(
                PyDpfSoundWarning(
                    "Output has not been yet processed, use LoudnessVsTime.process()."
                )
            )
            return None

        if type(output[0]) == Field:
            return (
                np.array(output[0].data),
                np.array(output[1].data),
                np.array(output[2].data),
                np.array(output[3].data),
                np.array(output[4].data),
                np.array(output[5].data),
            )

        return (
            self.convert_fields_container_to_np_array(output[0]),
            self.convert_fields_container_to_np_array(output[1]),
            self.convert_fields_container_to_np_array(output[2]),
            self.convert_fields_container_to_np_array(output[3]),
            self.convert_fields_container_to_np_array(output[4]),
            self.convert_fields_container_to_np_array(output[5]),
        )

    def get_loudness_vs_time_sone(self, channel_number: int = 0) -> npt.ArrayLike:
        """Return the loudness vs time in sone for channel i.

        Returns
        -------
        npt.ArrayLike
            Loudness vs time in sone.
        """
        if self._output == None:
            # Computing output if needed
            warnings.warn(
                PyDpfSoundWarning(
                    "Output has not been yet processed, use LoudnessVsTime.process()."
                )
            )
            return None

        if type(self._output[0]) == Field:
            return self.get_output_as_nparray()[0]
        else:
            return self.get_output_as_nparray()[0][channel_number]

    def get_N5_sone(self, channel_number: int = 0) -> float:
        """Return the N5 indicator in sone for channel i.

        Returns
        -------
        float
            N5 value in sone.
        """
        if self._output == None:
            # Computing output if needed
            warnings.warn(
                PyDpfSoundWarning(
                    "Output has not been yet processed, use LoudnessVsTime.process()."
                )
            )
            return None

        if type(self._output[0]) == Field:
            return self.get_output_as_nparray()[1]
        else:
            return self.get_output_as_nparray()[1][channel_number]

    def get_N10_sone(self, channel_number: int = 0) -> float:
        """Return the N10 indicator in sone for channel i.

        Returns
        -------
        float
            N10 value in sone.
        """
        if self._output == None:
            # Computing output if needed
            warnings.warn(
                PyDpfSoundWarning(
                    "Output has not been yet processed, use LoudnessVsTime.process()."
                )
            )
            return None

        if type(self._output[0]) == Field:
            return self.get_output_as_nparray()[2]
        else:
            return self.get_output_as_nparray()[2][channel_number]

    def get_loudness_vs_time_phon(self, channel_number: int = 0) -> npt.ArrayLike:
        """Return the loudness vs time in phon for channel i.

        Returns
        -------
        npt.ArrayLike
            Loudness vs time in phon.
        """
        if self._output == None:
            # Computing output if needed
            warnings.warn(
                PyDpfSoundWarning(
                    "Output has not been yet processed, use LoudnessVsTime.process()."
                )
            )
            return None

        if type(self._output[0]) == Field:
            return self.get_output_as_nparray()[3]
        else:
            return self.get_output_as_nparray()[3][channel_number]

    def get_L5_sone(self, channel_number: int = 0) -> float:
        """Return the L5 indicator in phon for channel i.

        Returns
        -------
        float
            L5 value in phon.
        """
        if self._output == None:
            # Computing output if needed
            warnings.warn(
                PyDpfSoundWarning(
                    "Output has not been yet processed, use LoudnessVsTime.process()."
                )
            )
            return None

        if type(self._output[0]) == Field:
            return self.get_output_as_nparray()[4]
        else:
            return self.get_output_as_nparray()[4][channel_number]

    def get_L10_sone(self, channel_number: int = 0) -> float:
        """Return the L10 indicator in phon for channel i.

        Returns
        -------
        float
            L10 value in phon.
        """
        if self._output == None:
            # Computing output if needed
            warnings.warn(
                PyDpfSoundWarning(
                    "Output has not been yet processed, use LoudnessVsTime.process()."
                )
            )
            return None

        if type(self._output[0]) == Field:
            return self.get_output_as_nparray()[5]
        else:
            return self.get_output_as_nparray()[5][channel_number]

    def plot(self):
        """Plot the Loudness vs time in sone and in phon."""
        # Plot loudness in sone
        if type(self._output[0]) == Field:
            num_channels = 1
            field = self._output[0]
        else:
            num_channels = len(self._output[0])
            field = self._output[0][0]

        time = field.time_freq_support.time_frequencies.data

        f, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
        for i in range(num_channels):
            ax1.plot(time, self.get_loudness_vs_time_sone(i), label="Channel {}".format(i))

        ax1.set_title("Loudness vs time (Sone)")
        ax1.legend()
        ax1.set_ylabel("Sone")
        ax1.grid(True)

        # Plot loudness in phon

        for i in range(num_channels):
            ax2.plot(time, self.get_loudness_vs_time_phon(i), label="Channel {}".format(i))

        ax2.set_title("Loudness vs time (Phon)")
        ax2.legend()
        ax2.set_xlabel("Time")
        ax2.set_ylabel("Phon")
        ax2.grid(True)

        plt.show()
