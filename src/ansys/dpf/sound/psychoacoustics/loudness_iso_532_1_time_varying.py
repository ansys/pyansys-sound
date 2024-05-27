"""Compute ISO 532-1 loudness for time-varying sounds."""
import warnings

from ansys.dpf.core import Field, FieldsContainer, Operator
import matplotlib.pyplot as plt
import numpy as np
from numpy import typing as npt

from . import PsychoacousticsParent
from ..pydpf_sound import PyDpfSoundException, PyDpfSoundWarning


class LoudnessISO532_1_TimeVarying(PsychoacousticsParent):
    """ISO 532-1 loudness for time-varying sounds.

    This class computes the loudness of a signal following standard ISO 532-1 for time-varying
    sounds.
    """

    def __init__(self, signal: Field | FieldsContainer = None):
        """Create a LoudnessISO532_1_TimeVarying object.

        Parameters
        ----------
        signal: Field | FieldsContainer
            Signal on which to compute time-varying ISO532-1 Loudness, as a DPF field or fields
            container.
        """
        super().__init__()
        self.signal = signal
        self.__operator = Operator("compute_loudness_iso532_1_vs_time")

    @property
    def signal(self):
        """Signal property."""
        return self.__signal  # pragma: no cover

    @signal.setter
    def signal(self, signal: Field | FieldsContainer):
        """Set the signal.

        Parameters
        -------
        signal: FieldsContainer | Field
            Signal in Pa on which to compute loudness, as a DPF field or fields container.
        """
        self.__signal = signal

    @signal.getter
    def signal(self) -> Field | FieldsContainer:
        """Get the signal.

        Returns
        -------
        FieldsContainer | Field
            The signal as a field or a fields container
        """
        return self.__signal

    def process(self):
        """Compute the time-varying ISO532-1 Loudness.

        Calls the appropriate DPF Sound operator to compute the loudness of the signal.
        """
        if self.__signal == None:
            raise PyDpfSoundException(
                "No signal for loudness vs time computation."
                + " Use LoudnessISO532_1_TimeVarying.signal"
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
        """Return time-varying loudness data in a tuple of fields or fields.

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
            warnings.warn(
                PyDpfSoundWarning(
                    "Output has not been processed yet, use LoudnessISO532_1_TimeVarying.process()."
                )
            )

        return self._output

    def get_output_as_nparray(self) -> tuple[npt.ArrayLike]:
        """Return the time-varying loudness related indicators as numpy arrays.

        Returns
        -------
        tuple[np.array]
            1st element is the loudness vs time in sone.
            2nd element is the N5 indicator, in sone.
            3rd element is the N10 indicator, in sone.
            4th element is the loudness level vs time in phon.
            5th element is the L5 indicator, in phon.
            6th element is the L10 indicator, in phon.
        """
        output = self.get_output()

        if output == None:
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

    def get_loudness_sone_vs_time(self, channel_index: int = 0) -> npt.ArrayLike:
        """Return the time-varying loudness in sone for the specified channel_index.

        Parameters
        -------
        channel_index: int
            Index of the signal channel (0 by default) for which to return time-varying loudness.

        Returns
        -------
        numpy.ndarray
            Time-varying loudness in sone.
        """
        if self.get_output() == None:
            return None

        if type(self._output[0]) == Field:
            if channel_index > 0:
                raise PyDpfSoundException(
                    f"Specified channel index ({channel_index}) does not exist."
                )

            return self.get_output_as_nparray()[0]

        else:
            loudness_vs_time = self.get_output_as_nparray()[0]

            if channel_index > loudness_vs_time.ndim - 1:
                raise PyDpfSoundException(
                    f"Specified channel index ({channel_index}) does not exist."
                )

            if loudness_vs_time.ndim == 1:
                # Only one field
                return loudness_vs_time
            else:
                return loudness_vs_time[channel_index]

    def get_N5_sone(self, channel_index: int = 0) -> float:
        """Return the N5 indicator.

        Returns N5, that is, the loudness value in sone that is exceeded 5% of the time, for the
        specified channel.

        Parameters
        -------
        channel_index: int
            Index of the signal channel (0 by default) for which to return N5.

        Returns
        -------
        numpy.float64
            N5 value in sone.
        """
        if self.get_output() == None:
            return None

        if type(self._output[0]) == Field:
            if channel_index > 0:
                raise PyDpfSoundException(
                    f"Specified channel index ({channel_index}) does not exist."
                )

            return self.get_output_as_nparray()[1]

        else:
            N5 = self.get_output_as_nparray()[1]
            if channel_index > N5.ndim - 1:
                raise PyDpfSoundException(
                    f"Specified channel index ({channel_index}) does not exist."
                )

            return N5[channel_index]

    def get_N10_sone(self, channel_index: int = 0) -> float:
        """Return the N10 indicator.

        Returns N10, that is, the loudness value in sone that is exceeded 10% of the time, for the
        specified channel.

        Parameters
        -------
        channel_index: int
            Index of the signal channel (0 by default) for which to return N10.

        Returns
        -------
        numpy.float64
            N10 value in sone.
        """
        if self.get_output() == None:
            return None

        if type(self._output[0]) == Field:
            if channel_index > 0:
                raise PyDpfSoundException(
                    f"Specified channel index ({channel_index}) does not exist."
                )

            return self.get_output_as_nparray()[2]

        else:
            N10 = self.get_output_as_nparray()[2]
            if channel_index > N10.ndim - 1:
                raise PyDpfSoundException(
                    f"Specified channel index ({channel_index}) does not exist."
                )

            return N10[channel_index]

    def get_loudness_level_phon_vs_time(self, channel_index: int = 0) -> npt.ArrayLike:
        """Return the time-varying loudness level in phon for the specified channel_index.

        Parameters
        -------
        channel_index: int
            Index of the signal channel (0 by default) for which to return time-varying loudness
            level.

        Returns
        -------
        numpy.ndarray
            Time-varying loudness level in phon.
        """
        if self.get_output() == None:
            return None

        if type(self._output[0]) == Field:
            if channel_index > 0:
                raise PyDpfSoundException(
                    f"Specified channel index ({channel_index}) does not exist."
                )

            return self.get_output_as_nparray()[3]

        else:
            loudness_level_vs_time = self.get_output_as_nparray()[3]

            if channel_index > loudness_level_vs_time.ndim - 1:
                raise PyDpfSoundException(
                    f"Specified channel index ({channel_index}) does not exist."
                )

            if loudness_level_vs_time.ndim == 1:
                # Only one field
                return loudness_level_vs_time
            else:
                return loudness_level_vs_time[channel_index]

    def get_L5_phon(self, channel_index: int = 0) -> float:
        """Return the L5 indicator.

        Returns L5, that is, the loudness level in phon that is exceeded 5% of the time, for the
        specified channel.

        Parameters
        -------
        channel_index: int
            Index of the signal channel (0 by default) for which to return L5.

        Returns
        -------
        numpy.float64
            L5 value in phon.
        """
        if self.get_output() == None:
            return None

        if type(self._output[0]) == Field:
            if channel_index > 0:
                raise PyDpfSoundException(
                    f"Specified channel index ({channel_index}) does not exist."
                )

            return self.get_output_as_nparray()[4]

        else:
            L5 = self.get_output_as_nparray()[4]
            if channel_index > L5.ndim - 1:
                raise PyDpfSoundException(
                    f"Specified channel index ({channel_index}) does not exist."
                )

            return L5[channel_index]

    def get_L10_phon(self, channel_index: int = 0) -> float:
        """Return the L10 indicator.

        Returns L10, that is, the loudness level in phon that is exceeded 10% of the time, for the
        specified channel.

        Parameters
        -------
        channel_index: int
            Index of the signal channel (0 by default) for which to return L10.

        Returns
        -------
        numpy.float64
            L10 value in phon.
        """
        if self.get_output() == None:
            return None

        if type(self._output[0]) == Field:
            if channel_index > 0:
                raise PyDpfSoundException(
                    f"Specified channel index ({channel_index}) does not exist."
                )

            return self.get_output_as_nparray()[5]

        else:
            L10 = self.get_output_as_nparray()[5]
            if channel_index > L10.ndim - 1:
                raise PyDpfSoundException(
                    f"Specified channel index ({channel_index}) does not exist."
                )

            return L10[channel_index]

    def get_time_scale(self) -> npt.ArrayLike:
        """Return time scale.

        Returns an array of the timestamps, in second, where time-varying loudness and loudness
        level are defined.

        Returns
        -------
        numpy.ndarray
            Timestamps in second.
        """
        if self.get_output() == None:
            return None

        if type(self._output[0]) == Field:
            return self._output[0].time_freq_support.time_frequencies.data
        else:
            return self._output[0][0].time_freq_support.time_frequencies.data

    def plot(self):
        """Plot the time-varying loudness in sone and loudness level in phon.

        Creates a figure window where the time-varying loudness N in sone and loudness level L_N
        in phon are displayed.
        """
        if self._output == None:
            raise PyDpfSoundException(
                "Output has not been processed yet, use LoudnessISO532_1_TimeVarying.process()."
            )

        if type(self._output[0]) == Field:
            num_channels = 1
        else:
            num_channels = len(self._output[0])

        time = self.get_time_scale()

        # Plot loudness in sone
        f, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
        for i in range(num_channels):
            ax1.plot(time, self.get_loudness_sone_vs_time(i), label="Channel {}".format(i))

        ax1.set_title("Time-varying loudness")
        if num_channels > 1:
            ax1.legend()
        ax1.set_ylabel("N (sone)")
        ax1.grid(True)

        # Plot loudness in phon

        for i in range(num_channels):
            ax2.plot(time, self.get_loudness_level_phon_vs_time(i), label="Channel {}".format(i))

        ax2.set_title("Time-varying loudness level")
        if num_channels > 1:
            ax2.legend()
        ax2.set_xlabel("Time (s)")
        ax2.set_ylabel("$L_N$ (phon)")
        ax2.grid(True)

        plt.show()
