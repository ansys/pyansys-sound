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

"""Xtract tonal module."""

import warnings

from ansys.dpf.core import Field, Operator, types
import matplotlib.pyplot as plt
import numpy as np

from . import XtractParent, XtractTonalParameters
from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning


class XtractTonal(XtractParent):
    """Extract tonal components using the Xtract algorithm.

    .. seealso::
        :class:`Xtract`, :class:`XtractTonalParameters`

    Examples
    --------
    Extract tonal components from a signal, and display the tonal and non-tonal components.

    >>> from ansys.sound.core.xtract import XtractTonal
    >>> xtract_tonal = XtractTonal(input_signal=my_signal, input_parameters=my_parameters)
    >>> xtract_tonal.process()
    >>> tonal_signals, non_tonal_signals = xtract_tonal.get_output()
    >>> xtract_tonal.plot()

    .. seealso::
        :ref:`xtract_feature_example`
            Example demonstrating how to use Xtract to extract the various components of a signal.
    """

    def __init__(
        self,
        input_signal: Field = None,
        input_parameters: XtractTonalParameters = None,
    ):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        input_signal : Field, default: None
            Input signal from which to extract tonal components, as a DPF field.
        input_parameters : XtractTonalParameters, default: None
            Structure that contains the parameters of the algorithm:

            - NFFT (int) is the number of points used for the FFT computation.
            - Regularity setting (float) between 0 and 1.
            - Maximum slope (float) in dB/Hz.
            - Minimum duration (float) in seconds.
            - Intertonal gap (float) in Hz.
            - Local emergence (float) in dB.

            This structure is of the ``XtractTonalParameters`` type. For more information,
            see this class.
        """
        super().__init__()
        self.input_signal = input_signal
        self.input_parameters = input_parameters

        # Define output fields
        self.__output_tonal_signals = None
        self.__output_non_tonal_signals = None

        self._output = (self.__output_tonal_signals, self.__output_non_tonal_signals)

        self.__operator = Operator("xtract_tonal")

    @property
    def input_signal(self) -> Field:
        """Input signal from which to extract tonal components, as a DPF field."""
        return self.__input_signal

    @input_signal.setter
    def input_signal(self, signal: Field):
        """Set input signal."""
        if not (signal is None or isinstance(signal, Field)):
            raise PyAnsysSoundException("Signal must be specified as a DPF field.")

        self.__input_signal = signal

    @property
    def input_parameters(self) -> XtractTonalParameters:
        """Input parameters.

        Structure that contains the parameters of the algorithm:

        - NFFT (int) is the number of points used for the FFT computation.
        - Regularity setting (float) between 0 and 1.
        - Maximum slope (float) in dB/Hz.
        - Minimum duration (float) in seconds (s).
        - Intertonal gap (float) in Hz.
        - Local emergence (float) in dB.
        """
        return self.__input_parameters

    @input_parameters.setter
    def input_parameters(self, value: XtractTonalParameters):
        """Set input parameters."""
        self.__input_parameters = value

    @property
    def output_tonal_signals(self) -> Field:
        """Output tonal signal as a DPF field."""
        return self.__output_tonal_signals

    @property
    def output_non_tonal_signals(self) -> Field:
        """Output non-tonal signal as a DPF field."""
        return self.__output_non_tonal_signals

    def process(self):
        """Process the tonal analysis."""
        if self.__input_signal is None:
            raise PyAnsysSoundException("No input signal found for tonal analysis.")

        if self.input_parameters is None:
            raise PyAnsysSoundException("Input parameters are not set.")

        self.__operator.connect(0, self.input_signal)
        self.__operator.connect(1, self.input_parameters.get_parameters_as_generic_data_container())

        # Run the operator
        self.__operator.run()

        # Stores the output in the variable
        self.__output_tonal_signals = self.__operator.get_output(0, types.field)
        self.__output_non_tonal_signals = self.__operator.get_output(1, types.field)

        self._output = (self.__output_tonal_signals, self.__output_non_tonal_signals)

    def get_output(self) -> tuple[Field, Field]:
        """Get the output of the tonal analysis.

        Returns
        -------
        Field
            Tonal signal as a DPF field.
        Field
            Non-tonal signal as a DPF field.
        """
        if None in self._output:
            warnings.warn(PyAnsysSoundWarning("Output is not processed yet."))

        return self._output

    def get_output_as_nparray(self) -> tuple[np.ndarray, np.ndarray]:
        """Get the output of the tonal analysis as NumPy arrays.

        Returns
        -------
        numpy.ndarray
            Tonal signal as a NumPy array.
        numpy.ndarray
            Non-tonal signal as a NumPy array.
        """
        tonal_signal, non_tonal_signal = self.get_output()

        if tonal_signal is None or non_tonal_signal is None:
            return np.array([]), np.array([])

        return np.array(tonal_signal.data), np.array(non_tonal_signal.data)

    def plot(self):
        """Plot the output of the tonal analysis.

        This method plots both the tonal and non-tonal signals.
        """
        tonal_signal, non_tonal_signal = self.get_output()
        time = tonal_signal.time_freq_support.time_frequencies

        plt.figure()
        plt.plot(time.data, tonal_signal.data)
        plt.xlabel(f"Time ({time.unit})")
        plt.ylabel(f"Amplitude ({tonal_signal.unit})")
        plt.title("Tonal signal")

        plt.figure()
        plt.plot(time.data, non_tonal_signal.data)
        plt.xlabel(f"Time ({time.unit})")
        plt.ylabel(f"Amplitude ({non_tonal_signal.unit})")
        plt.title("Non tonal signal")

        plt.show()
