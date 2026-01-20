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

"""Crops a signal."""

import warnings

from ansys.dpf.core import Field, FieldsContainer, Operator
import numpy as np

from . import SignalUtilitiesParent
from .._pyansys_sound import (
    PyAnsysSoundException,
    PyAnsysSoundWarning,
    convert_fields_container_to_np_array,
)


class CropSignal(SignalUtilitiesParent):
    """Crop a signal.

    This class allows cropping a signal, that is, extracting a segment of it.

    Examples
    --------
    Crop a signal between 1.0 s and 3.0 s.

    >>> from ansys.sound.core.signal_utilities import CropSignal
    >>> crop_signal = CropSignal(signal=my_signal, start_time=1.0, end_time=3.0)
    >>> crop_signal.process()
    >>> signal_segment = crop_signal.get_output()
    """

    def __init__(
        self, signal: Field | FieldsContainer = None, start_time: float = 0.0, end_time: float = 0.0
    ):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        signal : FieldsContainer | Field, default: None
            Signal to resample as a DPF field or fields container.
        start_time : float, default: 0.0
            Start time of the part to crop in seconds.
        end_time : float, default: 0.0
            End time of the part to crop in seconds.
        """
        super().__init__()
        self.signal = signal
        self.start_time = start_time
        self.end_time = end_time
        self.__operator = Operator("get_cropped_signal")

    @property
    def start_time(self) -> float:
        """Start time of the part to crop in s."""
        return self.__start_time

    @start_time.setter
    def start_time(self, new_start: float):
        """Set a new start time."""
        if new_start < 0.0:
            raise PyAnsysSoundException("Start time must be greater than or equal to 0.0.")
        self.__start_time = new_start

    @property
    def end_time(self) -> float:
        """End time of the part to crop in s."""
        return self.__end_time

    @end_time.setter
    def end_time(self, new_end: float):
        """Set a new end time."""
        if new_end < 0.0:
            raise PyAnsysSoundException("End time must be greater than or equal to 0.0.")

        if new_end < self.start_time:
            raise PyAnsysSoundException("End time must be greater than or equal to the start time.")

        self.__end_time = new_end

    @property
    def signal(self) -> Field | FieldsContainer:
        """Input signal as a DPF field or fields container."""
        return self.__signal

    @signal.setter
    def signal(self, signal: Field | FieldsContainer):
        """Set the signal."""
        self.__signal = signal

    def process(self):
        """Crop the signal.

        This method calls the appropriate DPF Sound operator to crop the signal.
        """
        if self.signal == None:
            raise PyAnsysSoundException("No signal found to crop. \
                Use the 'CropSignal.set_signal()' method.")

        self.__operator.connect(0, self.signal)
        self.__operator.connect(1, float(self.start_time))
        self.__operator.connect(2, float(self.end_time))

        # Runs the operator
        self.__operator.run()

        # Stores output in the variable
        if type(self.signal) == FieldsContainer:
            self._output = self.__operator.get_output(0, "fields_container")
        elif type(self.signal) == Field:
            self._output = self.__operator.get_output(0, "field")

    def get_output(self) -> FieldsContainer | Field:
        """Get the cropped signal as a DPF fields container.

        Returns
        -------
        FieldsContainer | Field
            Cropped signal in a DPF fields container.
        """
        if self._output == None:
            # Computing output if needed
            warnings.warn(PyAnsysSoundWarning("Output is not processed yet. \
                        Use the 'CropSignal.process()' method."))

        return self._output

    def get_output_as_nparray(self) -> np.ndarray:
        """Get the cropped signal as a NumPy array.

        Returns
        -------
        numpy.ndarray
            Cropped signal in a NumPy array.
        """
        output = self.get_output()

        if type(output) == Field:
            return output.data

        return convert_fields_container_to_np_array(output)
