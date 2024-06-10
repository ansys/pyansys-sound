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

"""Resample."""

import warnings

from ansys.dpf.core import Field, FieldsContainer, Operator
from numpy import typing as npt

from . import SignalUtilitiesParent
from ..pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning


class Resample(SignalUtilitiesParent):
    """Resample.

    This class resamples signals.
    """

    def __init__(
        self, signal: Field | FieldsContainer = None, new_sampling_frequency: float = 44100.0
    ):
        """Create a resample class.

        Parameters
        ----------
        signal:
            Signal to resample as a DPF Field or FieldsContainer.
        new_sampling_frequency:
            New sampling frequency to use
        """
        super().__init__()
        self.signal = signal
        self.new_sampling_frequency = new_sampling_frequency
        self.__operator = Operator("resample")

    @property
    def new_sampling_frequency(self):
        """Property new sampling frequency."""
        return self.__new_sampling_frequency  # pragma: no cover

    @new_sampling_frequency.setter
    def new_sampling_frequency(self, new_sampling_frequency: float):
        """Set the new sampling frequency.

        Parameters
        ----------
        new_sampling_frequency:
            New sampling frequency.
        """
        if new_sampling_frequency < 0.0:
            raise PyAnsysSoundException("Sampling frequency must be strictly greater than 0.0.")

        self.__new_sampling_frequency = new_sampling_frequency

    @new_sampling_frequency.getter
    def new_sampling_frequency(self) -> float:
        """Get the sampling frequency.

        Returns
        -------
        float
                The sampling frequency.
        """
        return self.__new_sampling_frequency

    @property
    def signal(self):
        """Property signal."""
        return self.__signal  # pragma: no cover

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
        """Resample the signal.

        Calls the appropriate DPF Sound operator to resample the signal.
        """
        if self.signal == None:
            raise PyAnsysSoundException("No signal to resample. Use Resample.set_signal().")

        self.__operator.connect(0, self.signal)
        self.__operator.connect(1, float(self.new_sampling_frequency))

        # Runs the operator
        self.__operator.run()

        # Stores output in the variable
        if type(self.signal) == FieldsContainer:
            self._output = self.__operator.get_output(0, "fields_container")
        elif type(self.signal) == Field:
            self._output = self.__operator.get_output(0, "field")

    def get_output(self) -> FieldsContainer | Field:
        """Return the resampled signal as a fields container.

        Returns
        -------
        FieldsContainer
                The resampled signal in a dpf.FieldsContainer.
        """
        if self._output == None:
            # Computing output if needed
            warnings.warn(
                PyAnsysSoundWarning("Output has not been yet processed, use Resample.process().")
            )

        return self._output

    def get_output_as_nparray(self) -> npt.ArrayLike:
        """Return the resampled signal as a numpy array.

        Returns
        -------
        np.array
                The resampled signal in a numpy array.
        """
        output = self.get_output()

        if type(output) == Field:
            return output.data

        return self.convert_fields_container_to_np_array(output)
