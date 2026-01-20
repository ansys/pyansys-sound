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

"""Adds zeros to the end of a signal."""

import warnings

from ansys.dpf.core import Field, FieldsContainer, Operator
import numpy as np

from . import SignalUtilitiesParent
from .._pyansys_sound import (
    PyAnsysSoundException,
    PyAnsysSoundWarning,
    convert_fields_container_to_np_array,
)


class ZeroPad(SignalUtilitiesParent):
    """Add zeros to the end of a signal.

    Examples
    --------
    Add 1 second worth of zeros to the end of a signal.

    >>> from ansys.sound.core.signal_utilities import ZeroPad
    >>> zero_pad = ZeroPad(signal=my_signal, duration_zeros=1.0)
    >>> zero_pad.process()
    >>> zero_padded_signal = zero_pad.get_output()
    """

    def __init__(self, signal: Field | FieldsContainer = None, duration_zeros: float = 0.0):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        signal : Field | FieldsContainer, default: None
            Signal to add zeros to the end of as a DPF field or fields container.
        duration_zeros : float: default: 0.0
            Duration in seconds of the zeros to append to the input signal.
        """
        super().__init__()
        self.signal = signal
        self.duration_zeros = duration_zeros
        self.__operator = Operator("append_zeros_to_signal")

    @property
    def signal(self) -> Field | FieldsContainer:
        """Input signal as a DPF field or fields container."""
        return self.__signal

    @signal.setter
    def signal(self, signal: Field | FieldsContainer):
        """Set the signal."""
        self.__signal = signal

    @property
    def duration_zeros(self) -> float:
        """Duration in s of the zero-padding at the end of the signal."""
        return self.__duration_zeros

    @duration_zeros.setter
    def duration_zeros(self, new_duration_zeros: float):
        """Set the zero-padding duration."""
        if new_duration_zeros < 0.0:
            raise PyAnsysSoundException("Zero duration must be greater than 0.0.")

        self.__duration_zeros = new_duration_zeros

    def process(self):
        """Pad the end of the signal with zeros.

        This method calls the appropriate DPF Sound operator to append zeros to the
        end of the signal.
        """
        if self.signal == None:
            raise PyAnsysSoundException("No signal found to zero pad. \
                    Use the 'ZeroPad.set_signal()' method.")

        self.__operator.connect(0, self.signal)
        self.__operator.connect(1, float(self.duration_zeros))

        # Run the operator
        self.__operator.run()

        # Store output in the variable
        if type(self.signal) == FieldsContainer:
            self._output = self.__operator.get_output(0, "fields_container")
        elif type(self.signal) == Field:
            self._output = self.__operator.get_output(0, "field")

    def get_output(self) -> FieldsContainer | Field:
        """Get the zero-padded signal as a DPF fields container or field.

        Returns
        -------
        FieldsContainer | Field
             Zero-padded signal in a DPF fields container or field.
        """
        if self._output == None:
            # Computing output if needed
            warnings.warn(PyAnsysSoundWarning("Output is not processed yet. \
                        Use the 'ZeroPad.process()' method."))

        return self._output

    def get_output_as_nparray(self) -> np.ndarray:
        """Get the zero-padded signal as a NumPy array.

        Returns
        -------
        numpy.ndarray
            Zero-padded signal in a NumPy array.
        """
        output = self.get_output()

        if type(output) == Field:
            return output.data

        return convert_fields_container_to_np_array(output)
