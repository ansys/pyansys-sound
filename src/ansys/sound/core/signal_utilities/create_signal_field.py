# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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

"""PyAnsys Sound signal field creation."""

import warnings

from ansys.dpf.core import Field, Operator
import numpy as np

from . import SignalUtilitiesParent
from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning


class CreateSignalField(SignalUtilitiesParent):
    """Create a PyAnsys Sound field containing a time-domain signal.

    This class creates a DPF field from a series of time-domain - typically acoustic - signal
    samples.

    .. seealso::
        :class:`CreateSignalFieldsContainer`

    Examples
    --------
    Create a PyAnsys Sound field containing a time-domain signal from signal data.

    >>> from ansys.sound.core.signal_utilities import CreateSignalField
    >>> create_signal_field = CreateSignalField(
    ...     data=my_signal_data,
    ...     sampling_frequency=44100.0,
    ...     unit="Pa",
    ... )
    >>> create_signal_field.process()
    >>> signal_as_a_field = create_signal_field.get_output()
    """

    def __init__(
        self,
        data: np.ndarray = np.empty(0),
        sampling_frequency: float = 44100.0,
        unit: str = "Pa",
    ):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        data : numpy.ndarray, default: np.empty(0)
            Time-domain signal data in the form of a 1D NumPy array.
        sampling_frequency : float, default: 44100.0
            Sampling frequency of the data, in Hz.
        unit : str, default: "Pa"
            Unit of the data.
        """
        super().__init__()
        self.data = data
        self.sampling_frequency = sampling_frequency
        self.unit = unit
        self.__operator = Operator("create_field_from_vector")

    @property
    def data(self) -> np.ndarray:
        """Time-domain signal data in the form of a 1D NumPy array."""
        return self.__data

    @data.setter
    def data(self, data: np.ndarray):
        """Set the data."""
        self.__data = data

    @property
    def unit(self) -> str:
        """Unit of the data to store."""
        return self.__unit

    @unit.setter
    def unit(self, new_unit: str):
        """Set a new unit."""
        self.__unit = new_unit

    @property
    def sampling_frequency(self) -> float:
        """Sampling frequency in Hz of the data."""
        return self.__sampling_frequency

    @sampling_frequency.setter
    def sampling_frequency(self, new_sampling_frequency: float):
        """Set a new sampling frequency."""
        if new_sampling_frequency < 0.0:
            raise PyAnsysSoundException("Sampling frequency must be greater than or equal to 0.0.")
        self.__sampling_frequency = new_sampling_frequency

    def process(self):
        """Create the PyAnsys Sound signal field.

        This method calls the appropriate DPF Sound operator to create the signal field.
        """
        if np.size(self.data) == 0:
            raise PyAnsysSoundException(
                "No data to use. Use the 'CreateSignalField.set_data()' method."
            )

        self.__operator.connect(0, self.data.tolist())
        self.__operator.connect(1, float(self.sampling_frequency))
        self.__operator.connect(2, str(self.unit))

        # Runs the operator
        self.__operator.run()

        # Stores output in the variable
        self._output = self.__operator.get_output(0, "field")

    def get_output(self) -> Field:
        """Get the created time-domain signal DPF field.

        Returns
        -------
        Field
            Time-domain signal DPF field.
        """
        if self._output == None:
            # Computing output if needed
            warnings.warn(
                PyAnsysSoundWarning(
                    "Output is not processed yet. Use the 'CreateSignalField.process()' method."
                )
            )

        return self._output

    def get_output_as_nparray(self) -> np.ndarray:
        """Get the time-domain signal data as a NumPy array.

        Returns
        -------
        numpy.ndarray
            Time-domain signal data in a NumPy array.
        """
        output = self.get_output()
        return output.data
