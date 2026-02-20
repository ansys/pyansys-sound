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

"""Xtract  transient module."""

import warnings

from ansys.dpf.core import Field, Operator
import matplotlib.pyplot as plt
import numpy as np

from . import XtractParent, XtractTransientParameters
from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning


class XtractTransient(XtractParent):
    """Extracts the transient components of a signal using the Xtract algorithm.

    .. seealso::
        :class:`Xtract`, :class:`XtractTransientParameters`

    Examples
    --------
    Extract transient components from a signal, and display the transient and non-transient
    components.

    >>> from ansys.sound.core.xtract import XtractTransient
    >>> xtract_transient = XtractTransient(
    ...     input_signal=my_signal,
    ...     input_parameters=my_parameters
    ... )
    >>> xtract_transient.process()
    >>> transient_signals, non_transient_signals = xtract_transient.get_output()
    >>> xtract_transient.plot()

    .. seealso::
        :ref:`xtract_feature_example`
            Example demonstrating how to use Xtract to extract the various components of a signal.
    """

    def __init__(
        self,
        input_signal: Field = None,
        input_parameters: XtractTransientParameters = None,
    ):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        input_signal : Field, default: None
            Input signal from which to extract transient components, as a DPF field.
        input_parameters : XtractTransientParameters, default: None
            Structure that contains the parameters of the algorithm:

            - Lower threshold (float), which is between 0 and 100.
            - Upper threshold (float), which is between 0 and 100.

            This structure is of the ``XtractTransientParameters`` type. For more information,
            see this class.
        """
        super().__init__()
        self.input_signal = input_signal
        self.input_parameters = input_parameters

        # Define output fields
        self.__output_transient_signals = None
        self.__output_non_transient_signals = None

        self._output = (self.__output_transient_signals, self.__output_non_transient_signals)

        self.__operator = Operator("xtract_transient")

    @property
    def input_signal(self) -> Field:
        """Input signal from which to extract transient components, as a DPF field."""
        return self.__input_signal

    @input_signal.setter
    def input_signal(self, signal: Field):
        """Set input signal."""
        if not (signal is None or isinstance(signal, Field)):
            raise PyAnsysSoundException("Signal must be specified as a DPF field.")

        self.__input_signal = signal

    @property
    def input_parameters(self) -> XtractTransientParameters:
        """Input parameters.

        Structure that contains the parameters of the algorithm:

        - Lower threshold (float), which is between 0 and 100.
        - Upper threshold (float), which is between 0 and 100.
        """
        return self.__input_parameters

    @input_parameters.setter
    def input_parameters(self, value: XtractTransientParameters):
        """Set input parameters."""
        self.__input_parameters = value

    @property
    def output_transient_signals(self) -> Field:
        """Output transient signal as a DPF field."""
        return self.__output_transient_signals

    @property
    def output_non_transient_signals(self) -> Field:
        """Output non-transient signal as a DPF field."""
        return self.__output_non_transient_signals

    def process(self):
        """Process the transient extraction.

        This method extracts the transient components of the signals using the Xtract algorithm.
        """
        if self.input_signal is None:
            raise PyAnsysSoundException("Input signal is not set.")

        if self.input_parameters is None:
            raise PyAnsysSoundException("Input parameters are not set.")

        self.__operator.connect(0, self.input_signal)
        self.__operator.connect(1, self.input_parameters.get_parameters_as_generic_data_container())

        # Run the operator
        self.__operator.run()

        # Stores the output in the variable
        self.__output_transient_signals = self.__operator.get_output(0, "field")
        self.__output_non_transient_signals = self.__operator.get_output(1, "field")

        self._output = (self.__output_transient_signals, self.__output_non_transient_signals)

    def get_output(self) -> tuple[Field, Field]:
        """Get the output of the transient extraction.

        Returns
        -------
        Field
            Transient signal as a DPF field.
        Field
            Non-transient signal as a DPF field.
        """
        if None in self._output:
            warnings.warn(PyAnsysSoundWarning("Output is not processed yet."))

        return self._output

    def get_output_as_nparray(self) -> tuple[np.ndarray, np.ndarray]:
        """Get the output of the transient extraction as NumPy arrays.

        Returns
        -------
        numpy.ndarray
            Transient signal as a NumPy array.
        numpy.ndarray
            Non-transient signal as a NumPy array.
        """
        transient_signal, non_transient_signal = self.get_output()

        if transient_signal is None or non_transient_signal is None:
            return np.array([]), np.array([])

        return np.array(transient_signal.data), np.array(non_transient_signal.data)

    def plot(self):
        """Plot signals.

        This method plots the transient signal and non-transient signal.
        """
        transient_signal, non_transient_signal = self.get_output()
        time = transient_signal.time_freq_support.time_frequencies

        plt.figure()
        plt.plot(time.data, transient_signal.data)
        plt.xlabel(f"Time ({time.unit})")
        plt.ylabel(f"Amplitude ({transient_signal.unit})")
        plt.title(f"Transient signal")

        plt.figure()
        plt.plot(time.data, non_transient_signal.data)
        plt.xlabel(f"Time ({time.unit})")
        plt.ylabel(f"Amplitude ({non_transient_signal.unit})")
        plt.title(f"Non transient signal")

        plt.show()
