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

"""Sums signals."""
import warnings

from ansys.dpf.core import Field, FieldsContainer, Operator
from numpy import typing as npt

from . import SignalUtilitiesParent
from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning


class SumSignals(SignalUtilitiesParent):
    """Sums signals."""

    def __init__(self, signals: FieldsContainer = None):
        """Create a ``SumSignals`` instance.

        Parameters
        ----------
        signals: FieldsContainer, default: None
            Input signals to sum. Each field of the signal is summed.
        """
        super().__init__()
        self.signals = signals
        self.__operator = Operator("sum_signals")

    @property
    def signals(self):
        """Signals."""
        return self.__signals  # pragma: no cover

    @signals.setter
    def signals(self, signals: FieldsContainer):
        """Set the signals to sum."""
        self.__signals = signals

    @signals.getter
    def signals(self) -> FieldsContainer:
        """Signals.

        Returns
        -------
        FieldsContainer
            Signals as a DPF fields container.
        """
        return self.__signals

    def process(self):
        """Sum signals.

        This method calls the appropriate DPF Sound operator to sum signals.
        """
        if self.signals == None:
            raise PyAnsysSoundException(
                "No signal to apply gain on. Use the 'SumSignals.set_signal()' method."
            )

        self.__operator.connect(0, self.signals)

        # Run the operator
        self.__operator.run()

        # Store output in the variable
        self._output = self.__operator.get_output(0, "field")

    def get_output(self) -> Field:
        """Get the summed signals as a DPF field.

        Returns
        -------
        Field
            Summed signal in a DPF field.
        """
        if self._output == None:
            # Computing output if needed
            warnings.warn(
                PyAnsysSoundWarning(
                    "Output is not processed yet. \
                        Use the 'SumSignals.process()' method."
                )
            )

        return self._output

    def get_output_as_nparray(self) -> npt.ArrayLike:
        """Get the signal with a gain as a NumPy array.

        Returns
        -------
        np.array
            Summed signal in a NumPy array.
        """
        output = self.get_output()
        return output.data
