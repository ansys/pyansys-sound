# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Computes ISO 532-1 loudness for time-varying sounds."""
import warnings

from ansys.dpf.core import Field, FieldsContainer, Operator
import matplotlib.pyplot as plt
import numpy as np
from numpy import typing as npt

from . import PsychoacousticsParent
from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning


class LoudnessISO532_1_TimeVarying(PsychoacousticsParent):
    """Computes ISO 532-1 loudness for time-varying sounds.

    This class computes the loudness of a signal following the ISO 532-1 standard for time-varying
    sounds.
    """

    def __init__(self, signal: Field | FieldsContainer = None):
        """Create a ``LoudnessISO532_1_TimeVarying`` object.

        Parameters
        ----------
        signal: Field | FieldsContainer
            Signal to compute time-varying ISO532-1 loudness on as a DPF field or fields
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
        ----------
        signal: FieldsContainer | Field
            Signal in Pa to compute loudness on as a DPF field or fields container.
        """
        self.__signal = signal

    @signal.getter
    def signal(self) -> Field | FieldsContainer:
        """Signal.

        Returns
        -------
        Field | FieldsContainer
            Signal as a DPF field or a fields container.
        """
        return self.__signal

    def process(self):
        """Compute the time-varying ISO532-1 loudness.

        This method calls the appropriate DPF Sound operator to compute the loudness of the signal.
        """
        if self.__signal == None:
            raise PyAnsysSoundException(
                "No signal found for loudness versus time computation."
                + " Use 'LoudnessISO532_1_TimeVarying.signal'."
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
        """Get time-varying loudness data in a tuple as a DPF fields container or field.

        Returns
        -------
        tuple(FieldsContainer) | tuple(Field)
            First element is the loudness versus the time in sone.

            Second element is the N5 indicator in sone.

            Third element is the N10 indicator in sone.

            Fourth element is the loudness versus the time in phon.

            Fifth element is the L5 indicator in phon.

            Sixth element is the L10 indicator in phon.
        """
        if self._output == None:
            warnings.warn(
                PyAnsysSoundWarning(
                    "Output is not processed yet. Use the "
                    "'LoudnessISO532_1_TimeVarying.process()' method."
                )
            )

        return self._output

    def get_output_as_nparray(self) -> tuple[npt.ArrayLike]:
        """Get indicators for time-varying loudness in a tuple as a NumPy array.

        Returns
        -------
        tuple[numpy.ndarray]
            First element is the loudness versus the time in sone.

            Second element is the N5 indicator in sone.

            Third element is the N10 indicator in sone.

            Fourth element is the loudness versus the time in phon.

            Fifth element is the L5 indicator in phon.

            Sixth element is the L10 indicator in phon.
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
        """Get the time-varying loudness in sone for a signal channel.

        Parameters
        ----------
        channel_index: int, default: 0
            Index of the signal channel to get time-varying loudness for.

        Returns
        -------
        numpy.ndarray
            Time-varying loudness in sone.
        """
        if self.get_output() == None or not (self._check_channel_index(channel_index)):
            return None

        if type(self._output[0]) == Field:
            return self.get_output_as_nparray()[0]

        else:
            loudness_vs_time = self.get_output_as_nparray()[0]
            if loudness_vs_time.ndim == 1:
                # Only one field
                return loudness_vs_time
            else:
                return loudness_vs_time[channel_index]

    def get_N5_sone(self, channel_index: int = 0) -> float:
        """Get the N5 indicator for a signal channel.

        This method gets the N5 indicator, which is the loudness value in sone that is
        exceeded 5% of the time.

        Parameters
        ----------
        channel_index: int, default: 0
            Index of the signal channel to get the N5 indicator for.

        Returns
        -------
        numpy.float64
            N5 indicator value in sone.
        """
        if self.get_output() == None or not (self._check_channel_index(channel_index)):
            return None

        if type(self._output[0]) == Field:
            return self.get_output_as_nparray()[1][0]

        else:
            N5 = self.get_output_as_nparray()[1]
            return N5[channel_index]

    def get_N10_sone(self, channel_index: int = 0) -> float:
        """Get the N10 indicator for a signal channel.

        This method gets the N10 channel, which is the loudness value in sone that is
        exceeded 10% of the time.

        Parameters
        ----------
        channel_index: int, default: 0
            Index of the signal channel to get the N10 indicator for.

        Returns
        -------
        numpy.float64
            N10 indicator value in sone.
        """
        if self.get_output() == None or not (self._check_channel_index(channel_index)):
            return None

        if type(self._output[0]) == Field:
            return self.get_output_as_nparray()[2][0]

        else:
            N10 = self.get_output_as_nparray()[2]
            return N10[channel_index]

    def get_loudness_level_phon_vs_time(self, channel_index: int = 0) -> npt.ArrayLike:
        """Get the time-varying loudness level in phon for a signal channel.

        Parameters
        ----------
        channel_index: int, default: 0
            Index of the signal channel to get the time-varying loudness level for.

        Returns
        -------
        numpy.ndarray
            Time-varying loudness level in phon.
        """
        if self.get_output() == None or not (self._check_channel_index(channel_index)):
            return None

        if type(self._output[0]) == Field:
            return self.get_output_as_nparray()[3]

        else:
            loudness_level_vs_time = self.get_output_as_nparray()[3]
            if loudness_level_vs_time.ndim == 1:
                # Only one field
                return loudness_level_vs_time
            else:
                return loudness_level_vs_time[channel_index]

    def get_L5_phon(self, channel_index: int = 0) -> float:
        """Get the L5 indicator for a signal channel.

        This method gets the L5 indicator, which is the loudness level in phon that is
        exceeded 5% of the time.

        Parameters
        ----------
        channel_index: int, default: 0
            Index of the signal channel to get the L5 indicator for.

        Returns
        -------
        numpy.float64
            L5 value in phon.
        """
        if self.get_output() == None or not (self._check_channel_index(channel_index)):
            return None

        if type(self._output[0]) == Field:
            return self.get_output_as_nparray()[4][0]

        else:
            L5 = self.get_output_as_nparray()[4]
            return L5[channel_index]

    def get_L10_phon(self, channel_index: int = 0) -> float:
        """Get the L10 indicator for a signal channel.

        This method gets the L10 indicator, which is the loudness level in phon that is
        exceeded 10% of the time.

        Parameters
        ----------
        channel_index: int, default: 0
            Index of the signal channel to get the L10 indicator for.

        Returns
        -------
        numpy.float64
            L10 value in phon.
        """
        if self.get_output() == None or not (self._check_channel_index(channel_index)):
            return None

        if type(self._output[0]) == Field:
            return self.get_output_as_nparray()[5][0]

        else:
            L10 = self.get_output_as_nparray()[5]
            return L10[channel_index]

    def get_time_scale(self) -> npt.ArrayLike:
        """Get the time scale.

        This method gets an array of the timestamps in seconds where time-varying
        loudness and loudness level are defined.

        Returns
        -------
        numpy.ndarray
            Timestamps in seconds.
        """
        if self.get_output() == None:
            return None

        if type(self._output[0]) == Field:
            return np.copy(self._output[0].time_freq_support.time_frequencies.data)
        else:
            return np.copy(self._output[0][0].time_freq_support.time_frequencies.data)

    def plot(self):
        """Plot the time-varying loudness in sone and loudness level in phon.

        This method creates a figure window that displays the time-varying loudness (N)
        in sone and loudness level (L_N) in phon.
        """
        if self.get_output() == None:
            raise PyAnsysSoundException(
                "Output is not processed yet. Use the "
                "'LoudnessISO532_1_TimeVarying.process()' method."
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
        ax2.set_ylabel(r"$\mathregular{L_N}$ (phon)")
        ax2.grid(True)

        plt.show()
