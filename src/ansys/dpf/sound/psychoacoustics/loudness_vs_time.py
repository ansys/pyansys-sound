"""Compute Loudness."""
import warnings

from ansys.dpf.core import Field, FieldsContainer, Operator
import matplotlib.pyplot as plt
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
                1st element is the loudness vs time in Sone.
                2nd element is the N5 indicator, in Sone.
                3rd element is the N10 indicator, in Sone.
                4th element is the loudness vs time in Phon.
                5th element is the L5 indicator, in Phon.
                6th element is the L10 indicator, in Phon.
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
                1st element is the loudness vs time in Sone.
                2nd element is the N5 indicator, in Sone.
                3rd element is the N10 indicator, in Sone.
                4th element is the loudness vs time in Phon.
                5th element is the L5 indicator, in Phon.
                6th element is the L10 indicator, in Phon.
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
                output[0].data,
                output[1].data,
                output[2].data,
                output[3].data,
                output[4].data,
                output[5].data,
            )

        return (
            self.convert_fields_container_to_np_array(output[0]),
            self.convert_fields_container_to_np_array(output[1]),
            self.convert_fields_container_to_np_array(output[2]),
            self.convert_fields_container_to_np_array(output[3]),
            self.convert_fields_container_to_np_array(output[4]),
            self.convert_fields_container_to_np_array(output[5]),
        )

    def get_loudness_vs_time_sone(self) -> Field | FieldsContainer:
        """Return the loudness vs time in Sone.

        Returns
        -------
            tuple(FieldsContainer) | tuple(Field)
        """
        if self._output == None:
            # Computing output if needed
            warnings.warn(
                PyDpfSoundWarning(
                    "Output has not been yet processed, use LoudnessVsTime.process()."
                )
            )
            return None

        return self._output[0]

    def get_N5_sone(self) -> Field | FieldsContainer:
        """Return the N5 indicator in Sone.

        Returns
        -------
            tuple(FieldsContainer) | tuple(Field)
        """
        if self._output == None:
            # Computing output if needed
            warnings.warn(
                PyDpfSoundWarning(
                    "Output has not been yet processed, use LoudnessVsTime.process()."
                )
            )
            return None

        return self._output[1]

    def get_N10_sone(self) -> Field | FieldsContainer:
        """Return the N10 indicator in Sone.

        Returns
        -------
            tuple(FieldsContainer) | tuple(Field)
        """
        if self._output == None:
            # Computing output if needed
            warnings.warn(
                PyDpfSoundWarning(
                    "Output has not been yet processed, use LoudnessVsTime.process()."
                )
            )
            return None

        return self._output[2]

    def get_loudness_vs_time_phon(self) -> Field | FieldsContainer:
        """Return the loudness vs time in Phon.

        Returns
        -------
            tuple(FieldsContainer) | tuple(Field)
        """
        if self._output == None:
            # Computing output if needed
            warnings.warn(
                PyDpfSoundWarning(
                    "Output has not been yet processed, use LoudnessVsTime.process()."
                )
            )
            return None

        return self._output[3]

    def get_L5_sone(self) -> Field | FieldsContainer:
        """Return the L5 indicator in Phon.

        Returns
        -------
            tuple(FieldsContainer) | tuple(Field)
        """
        if self._output == None:
            # Computing output if needed
            warnings.warn(
                PyDpfSoundWarning(
                    "Output has not been yet processed, use LoudnessVsTime.process()."
                )
            )
            return None

        return self._output[4]

    def get_L10_sone(self) -> Field | FieldsContainer:
        """Return the L10 indicator in Phon.

        Returns
        -------
            tuple(FieldsContainer) | tuple(Field)
        """
        if self._output == None:
            # Computing output if needed
            warnings.warn(
                PyDpfSoundWarning(
                    "Output has not been yet processed, use LoudnessVsTime.process()."
                )
            )
            return None

        return self._output[5]

    def plot(self):
        """Plot the Loudness vs time in Sone and in Phon.

        Plots the Loudness vs time in Sone and in Phon.
        """
        # Plot loudness in Sone
        loudness_time_sone = self.get_loudness_vs_time_sone()

        if type(loudness_time_sone) == Field:
            num_channels = 0
            field = loudness_time_sone
        else:
            num_channels = len(loudness_time_sone)
            field = loudness_time_sone[0]

        time = field.time_freq_support.time_frequencies.data

        plt.figure(0)
        for i in range(num_channels):
            plt.plot(time, loudness_time_sone[i].data, label="Channel {}".format(i))

        plt.title("Loudness vs time (Sone)")
        plt.legend()
        plt.xlabel("Time")
        plt.ylabel("Sone")
        plt.grid(True)

        # Plot loudness in phon
        loudness_time_phon = self.get_loudness_vs_time_phon()

        if type(loudness_time_phon) == Field:
            num_channels = 0
            field = loudness_time_phon
        else:
            num_channels = len(loudness_time_phon)
            field = loudness_time_phon[0]

        time = field.time_freq_support.time_frequencies.data

        plt.figure(1)

        for i in range(num_channels):
            plt.plot(time, loudness_time_phon[i].data, label="Channel {}".format(i))

        plt.title("Loudness vs time (Phon)")
        plt.legend()
        plt.xlabel("Time")
        plt.ylabel("Phon")
        plt.grid(True)
        plt.show()
