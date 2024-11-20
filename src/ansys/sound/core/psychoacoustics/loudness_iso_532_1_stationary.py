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

"""Computes ISO 532-1 loudness for stationary sounds."""
import warnings

from ansys.dpf.core import Field, FieldsContainer, Operator
import matplotlib.pyplot as plt
import numpy as np
from numpy import typing as npt

from . import PsychoacousticsParent
from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning

LOUDNESS_SONE_ID = "sone"
LOUDNESS_LEVEL_PHON_ID = "phon"
SPECIFIC_LOUDNESS_ID = "specific"


class LoudnessISO532_1_Stationary(PsychoacousticsParent):
    """Computes ISO 532-1 loudness for stationary sounds.

    This class computes the loudness of a signal following the ISO 532-1 standard for stationary
    sounds.
    """

    def __init__(self, signal: Field | FieldsContainer = None):
        """Create a ``LoudnessISO532_1_Stationary`` object.

        Parameters
        ----------
        signal: Field | FieldsContainer
            Signal in Pa to compute loudness on as a DPF field or fields container.
        """
        super().__init__()
        self.signal = signal
        self.__operator = Operator("compute_loudness_iso532_1")

    @property
    def signal(self):
        """Signal."""
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
            Signal in Pa as a DPF field or fields container.
        """
        return self.__signal

    def process(self):
        """Compute the loudness.

        This method calls the appropriate DPF Sound operator to compute the loudness of the signal.
        """
        if self.__signal == None:
            raise PyAnsysSoundException(
                "No signal found for loudness computation. "
                "Use 'LoudnessISO532_1_Stationary.signal'."
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
        """Get loudness data in a tuple of a DPF field container or field.

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
                    "Output is not processed yet. Use the "
                    "'LoudnessISO532_1_Stationary.process()' method."
                )
            )

        return self._output

    def get_output_as_nparray(self) -> tuple[npt.ArrayLike]:
        """Get loudness data in a tuple as a NumPy array.

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
        """Get the loudness in sone for a signal channel.

           This method gets the loudness in sone as a float for a specified channel index.

        Parameters
        ----------
        channel_index: int, default 0
            Index of the signal channel to get the specified output for.

        Returns
        -------
        numpy.float64
            Loudness value in sone.
        """
        return self._get_output_parameter(channel_index, LOUDNESS_SONE_ID)

    def get_loudness_level_phon(self, channel_index: int = 0) -> np.float64:
        """Get the loudness level in phon for a signal channel.

        This method gets the loudness level in phon as a float for a specified channel index.

        Parameters
        ----------
        channel_index: int, default: 0
            Index of the signal channel to get the specified output for.

        Returns
        -------
        numpy.float64
            Loudness level value in phon.
        """
        return self._get_output_parameter(channel_index, LOUDNESS_LEVEL_PHON_ID)

    def get_specific_loudness(self, channel_index: int = 0) -> npt.ArrayLike:
        """Get the specific loudness for a signal channel.

        This method gets the specific loudness in sone/Bark for a specified channel index.

        Parameters
        ----------
        channel_index: int, default: 0
            Index of the signal channel to get the specified output for.

        Returns
        -------
        numpy.ndarray
            Specific loudness array in sone/Bark.
        """
        return self._get_output_parameter(channel_index, SPECIFIC_LOUDNESS_ID)

    def get_bark_band_indexes(self) -> npt.ArrayLike:
        """Get Bark band indexes.

        This method gets the Bark band indexes used for the loudness calculation as a NumPy array.

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
        """Get Bark band frequencies.

        This method gets the frequencies corresponding to Bark band indexes as a NumPy array.

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
        """Plot the specific loudness.

        This method creates a figure window that displays the specific loudness in sone/Bark as a
        function of the Bark band index.
        """
        if self._output == None:
            raise PyAnsysSoundException(
                "Output is not processed yet. Use the "
                "'LoudnessISO532_1_Stationary.process()' method."
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
        """Get the individual loudness result for a signal channel.

        This method gets the loudness or loudness level for the specified channel in phon
        as a float or the specific loudness as a NumPy array according to the output ID.

        Parameters
        ----------
        channel_index: int
            Index of the signal channel to get the specified output for.
        output_id: str
            ID of the specific output parameter to return. Options are:

            - ``"sone"``: For overall loudness value in sone
            - ``"phon"``: For overall loudness level value in phon.
            - ``"specific"``: For specific loudness array in sone/Bark

        Returns
        -------
        numpy.float64 | numpy.ndarray
            Loudness or loudness level value (float, in sone or phon, respectively), or specific
            loudness (numpy array, in sone/Bark).
        """
        if self.get_output() == None or not (self._check_channel_index(channel_index)):
            return None

        loudness_data = self.get_output_as_nparray()

        # Get last channel index.
        channel_max = len(loudness_data[0]) - 1

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
                raise PyAnsysSoundException("ID of output parameter is invalid.")

            if channel_max > 0:
                return loudness_data[unit_index][channel_index][0]
            else:
                return loudness_data[unit_index][0]
