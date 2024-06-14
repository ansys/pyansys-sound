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

"""Sum signals."""
import warnings

from ansys.dpf.core import Field, FieldsContainer, Operator
from numpy import typing as npt

from . import SignalUtilitiesParent
from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning


class SumSignals(SignalUtilitiesParent):
    """Sum signals.

    This class sum signals.
    """

    def __init__(self, signals: FieldsContainer = None):
        """Create a sum signal class.

        Parameters
        ----------
        signals:
            Input signals to sum, each field of the signal will be summed.
        """
        super().__init__()
        self.signals = signals
        self.__operator = Operator("sum_signals")

    @property
    def signals(self):
        """Signals property."""
        return self.__signals  # pragma: no cover

    @signals.setter
    def signals(self, signals: FieldsContainer):
        """Set the signals to sum."""
        self.__signals = signals

    @signals.getter
    def signals(self) -> FieldsContainer:
        """Get the signal.

        Returns
        -------
        FieldsContainer
                The signal as a FieldsContainer
        """
        return self.__signals

    def process(self):
        """Sum signals.

        Calls the appropriate DPF Sound operator to sum signals.
        """
        if self.signals == None:
            raise PyAnsysSoundException(
                "No signal on which to apply gain. Use SumSignals.set_signal()."
            )

        self.__operator.connect(0, self.signals)

        # Runs the operator
        self.__operator.run()

        # Stores output in the variable
        self._output = self.__operator.get_output(0, "field")

    def get_output(self) -> Field:
        """Return the summed signals as a field.

        Returns
        -------
        Field
                The summed signal in a Field.
        """
        if self._output == None:
            # Computing output if needed
            warnings.warn(
                PyAnsysSoundWarning("Output has not been yet processed, use SumSignals.process().")
            )

        return self._output

    def get_output_as_nparray(self) -> npt.ArrayLike:
        """Return the signal with a gain as a numpy array.

        Returns
        -------
        np.array
                The summed signal in a numpy array.
        """
        output = self.get_output()
        return output.data
