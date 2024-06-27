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

"""Adds zeros to the end of a signal."""
import warnings

from ansys.dpf.core import Field, FieldsContainer, Operator
from numpy import typing as npt

from . import SignalUtilitiesParent
from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning


class ZeroPad(SignalUtilitiesParent):
    """Adds zeros to the end of a signal."""

    def __init__(self, signal: Field | FieldsContainer = None, duration_zeros: float = 0.0):
        """Create a ``ZeroPad`` instance.

        Parameters
        ----------
        signal: Field | FieldsContainer, default: None
            Signal to add zeros to the end of as a DPF field or fields container.
        duration_zeros: float: default: 0.0
            Duration in seconds of the zeros to append to the input signal.
        """
        super().__init__()
        self.signal = signal
        self.duration_zeros = duration_zeros
        self.__operator = Operator("append_zeros_to_signal")

    @property
    def signal(self):
        """Signal."""
        return self.__signal  # pragma: no cover

    @signal.setter
    def signal(self, signal: Field | FieldsContainer):
        """Set the signal."""
        self.__signal = signal

    @signal.getter
    def signal(self) -> Field | FieldsContainer:
        """Signal.

        Returns
        -------
        Field | FieldsContainer
            Signal as a DPF field or fields container.
        """
        return self.__signal

    @property
    def duration_zeros(self):
        """Duration zeros property."""
        return self.__duration_zeros  # pragma: no cover

    @duration_zeros.setter
    def duration_zeros(self, new_duration_zeros: float):
        """Set the new duration of zeros.

        Parameters
        ----------
        new_duration_zeros: float
            New duration for the zero padding in seconds.
        """
        if new_duration_zeros < 0.0:
            raise PyAnsysSoundException("Zero duration must be greater than 0.0.")

        self.__duration_zeros = new_duration_zeros

    @duration_zeros.getter
    def duration_zeros(self) -> float:
        """Get the sampling frequency.

        Returns
        -------
        float
            Sampling frequency.
        """
        return self.__duration_zeros

    def process(self):
        """Pad the end of the signal with zeros.

        This method calls the appropriate DPF Sound operator to append zeros to the
        end of the signal.
        """
        if self.signal == None:
            raise PyAnsysSoundException(
                "No signal found to zero pad. \
                    Use the 'ZeroPad.set_signal()' method."
            )

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
            warnings.warn(
                PyAnsysSoundWarning(
                    "Output is not processed yet. \
                        Use the 'ZeroPad.process()' method."
                )
            )

        return self._output

    def get_output_as_nparray(self) -> npt.ArrayLike:
        """Get the zero-padded signal as a NumPy array.

        Returns
        -------
        np.array
            Zero-padded signal in a NumPy array.
        """
        output = self.get_output()

        if type(output) == Field:
            return output.data

        return self.convert_fields_container_to_np_array(output)
