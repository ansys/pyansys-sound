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

"""Sums signals."""

import warnings

from ansys.dpf.core import Field, FieldsContainer, Operator
import numpy as np

from . import SignalUtilitiesParent
from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning


class SumSignals(SignalUtilitiesParent):
    """Sum signals.

    Sum several signals together.

    Examples
    --------
    >>> from ansys.sound.core.signal_utilities import SumSignals
    >>> sum_signals = SumSignals(signals=my_signals)
    >>> sum_signals.process()
    >>> summed_signal = sum_signals.get_output()
    """

    def __init__(self, signals: FieldsContainer = None):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        signals : FieldsContainer, default: None
            Input signals, in a ``FieldsContainer`` where each ``Field`` contains a signal to sum
            with the others. If necessary, the classes :class:`CreateSignalField` (for
            single-channel signals) and :class:`CreateSignalFieldsContainer` (for single- or
            multi-channel signals) can help create such input from signal data.
        """
        super().__init__()
        self.signals = signals
        self.__operator = Operator("sum_signals")

    @property
    def signals(self) -> FieldsContainer:
        """Input signals as a DPF fields container."""
        return self.__signals

    @signals.setter
    def signals(self, signals: FieldsContainer):
        """Set the signals to sum."""
        self.__signals = signals

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
            warnings.warn(PyAnsysSoundWarning("Output is not processed yet. \
                        Use the 'SumSignals.process()' method."))

        return self._output

    def get_output_as_nparray(self) -> np.ndarray:
        """Get the signal with a gain as a NumPy array.

        Returns
        -------
        numpy.ndarray
            Summed signal in a NumPy array.
        """
        output = self.get_output()
        return output.data
