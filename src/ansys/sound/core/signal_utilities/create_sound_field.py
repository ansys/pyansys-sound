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

"""Creates a PyAnsys Sound field."""
import warnings

from ansys.dpf.core import Field, Operator
import numpy as np
from numpy import typing as npt

from . import SignalUtilitiesParent
from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning


class CreateSoundField(SignalUtilitiesParent):
    """Creates a PyAnsys Sound field.

    This class creates a DPF field with correct PyAnsys Sound metadata from a vector.
    """

    def __init__(
        self,
        data: npt.ArrayLike = np.empty(0),
        sampling_frequency: float = 44100.0,
        unit: str = "Pa",
    ):
        """Create a ``CreateSoundField`` instance.

        Parameters
        ----------
        data:
            Data to use to create the PyAnsys Sound field as a 1D NumPy array.
        sampling_frequency: float, default: 44100.0
            Sampling frequency of the data.
        unit: str, default: "Pa"
            Unit of the data.
        """
        super().__init__()
        self.data = data
        self.sampling_frequency = sampling_frequency
        self.unit = unit
        self.__operator = Operator("create_field_from_vector")

    @property
    def data(self):
        """Data."""
        return self.__data  # pragma: no cover

    @data.setter
    def data(self, data: npt.ArrayLike):
        """Set the data."""
        self.__data = data

    @data.getter
    def data(self) -> npt.ArrayLike:
        """Get data.

        Returns
        -------
        np.array
            Data as a NumPy array.
        """
        return self.__data

    @property
    def unit(self):
        """Unit."""
        return self.__unit  # pragma: no cover

    @unit.setter
    def unit(self, new_unit: str):
        """Set a new unit.

        Parameters
        ----------
        new_unit: str
            New unit as a string.
        """
        self.__unit = new_unit

    @unit.getter
    def unit(self) -> str:
        """Get the unit.

        Returns
        -------
        str
            Unit.
        """
        return self.__unit

    @property
    def sampling_frequency(self):
        """Sampling frequency."""
        return self.__sampling_frequency  # pragma: no cover

    @sampling_frequency.setter
    def sampling_frequency(self, new_sampling_frequency: float):
        """Set a new sampling frequency.

        Parameters
        ----------
        new_sampling_frequency: float
            New sampling frequency in Hz.
        """
        if new_sampling_frequency < 0.0:
            raise PyAnsysSoundException("Sampling frequency must be greater than or equal to 0.0.")
        self.__sampling_frequency = new_sampling_frequency

    @sampling_frequency.getter
    def sampling_frequency(self) -> float:
        """Get the sampling frequency.

        Returns
        -------
        float
            Sampling frequency.
        """
        return self.__sampling_frequency

    def process(self):
        """Create the PyAnsys Sound field.

        This method calls the appropriate DPF Sound operator to create the PyAnsys Sound field.
        """
        if np.size(self.data) == 0:
            raise PyAnsysSoundException(
                "No data to use. Use the 'CreateSoundField.set_data()' method."
            )

        self.__operator.connect(0, self.data.tolist())
        self.__operator.connect(1, float(self.sampling_frequency))
        self.__operator.connect(2, str(self.unit))

        # Runs the operator
        self.__operator.run()

        # Stores output in the variable
        self._output = self.__operator.get_output(0, "field")

    def get_output(self) -> Field:
        """Get the data as a DPF field.

        Returns
        -------
        Field
            Data in a DPF field.
        """
        if self._output == None:
            # Computing output if needed
            warnings.warn(
                PyAnsysSoundWarning(
                    "Output is not processed yet. Use the 'CreateSoundField.process()' method."
                )
            )

        return self._output

    def get_output_as_nparray(self) -> npt.ArrayLike:
        """Get the data as a NumPy array.

        Returns
        -------
        np.array
            Data in a NumPy array.
        """
        output = self.get_output()
        return output.data
