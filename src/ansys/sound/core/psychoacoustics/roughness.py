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

"""Computes roughness for stationary sounds."""
import warnings

from ansys.dpf.core import Field, FieldsContainer, Operator
import matplotlib.pyplot as plt
import numpy as np
from numpy import typing as npt

from . import PsychoacousticsParent
from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning

TOTAL_ROUGHNESS_ID = "total"
SPECIFIC_ROUGHNESS_ID = "specific"


class Roughness(PsychoacousticsParent):
    """Computes the roughness for stationary sounds.

    Reference: Daniel and Weber, "Psychoacoustical roughness: implementation of an
    optimized model." Acta Acustica united with Acustica, 83, pp. 113-123 (1997).
    """

    def __init__(self, signal: Field | FieldsContainer = None):
        """Create a ``Roughness`` object.

        Parameters
        ----------
        signal: Field | FieldsContainer
            Signal in Pa to compute roughness on as a DPF field or fields container.
        """
        super().__init__()
        self.signal = signal
        self.__operator = Operator("compute_roughness")

    @property
    def signal(self):
        """Signal."""
        return self.__signal  # pragma: no cover

    @signal.setter
    def signal(self, signal: Field | FieldsContainer):
        """Set the signal.

        Parameters
        ----------
        signal: Field | FieldsContainer
            Signal in Pa to compute roughness on as a DPF field or fields container.

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
        """Compute the roughness.

        This method calls the appropriate DPF Sound operator to compute the roughness of the signal.
        """
        if self.__signal == None:
            raise PyAnsysSoundException(
                "No signal found for roughness computation. Use 'Roughness.signal'."
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
        """Get roughness data in a tuple as a PDF fields container or field.

        Returns
        -------
        tuple(FieldsContainer) | tuple(Field)

            - First element is the roughness in asper.
            - Second element is the specific roughness in asper/Bark.
        """
        if self._output == None:
            warnings.warn(
                PyAnsysSoundWarning(
                    "Output is not processed yet. \
                        Use the 'Roughness.process()' method."
                )
            )

        return self._output

    def get_output_as_nparray(self) -> tuple[npt.ArrayLike]:
        """Get roughness data in a tuple as a NumPy array.

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
        """Get the roughness in asper for a signal.

           This method gets the roughness in asper as a float for the specified channel index.

        Parameters
        ----------
        channel_index: int, default: 0
            Index of the signal channel to get the specified output for.

        Returns
        -------
        numpy.float64
            Roughness value in asper.
        """
        return self._get_output_parameter(channel_index, TOTAL_ROUGHNESS_ID)

    def get_specific_roughness(self, channel_index: int = 0) -> npt.ArrayLike:
        """Get the specific roughness for a signal.

        This method gets the specific roughness in asper/Bark for the specified channel index.

        Parameters
        ----------
        channel_index: int, default: 0
            Index of the signal channel to get the specified output for.

        Returns
        -------
        numpy.ndarray
            Specific roughness array in asper/Bark.
        """
        return self._get_output_parameter(channel_index, SPECIFIC_ROUGHNESS_ID)

    def get_bark_band_indexes(self) -> npt.ArrayLike:
        """Get Bark band indexes.

        This method gets the Bark band indexes used for the roughness calculation as a NumPy array.

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
        """Plot the specific roughness.

        This method creates a figure window that displays the specific roughness in asper/Bark as a
        function of the Bark band index.
        """
        if self._output == None:
            raise PyAnsysSoundException(
                "Output is not processed yet. \
                    Use the 'Roughness.process()' method."
            )

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
        """Get the individual roughness result for the signal channel.

        This method returns the roughness as a float or the specific roughness as a
        NumPy array, according to specified output ID.

        Parameters
        ----------
        channel_index: int
            Index of the signal channel to get the specified output for.
        output_id: str
            ID of the specific output parameter to return. Options are:

            - ``"total"``: For overall roughness value in asper
            - ``"specific"``: for specific roughness array in asper/Bark

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
            raise PyAnsysSoundException("Identifier of output parameter is invalid.")
