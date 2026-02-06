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

"""Xtract class."""

import warnings

from ansys.dpf.core import Field, Operator, types
import matplotlib.pyplot as plt
import numpy as np

from . import (
    XtractDenoiserParameters,
    XtractParent,
    XtractTonalParameters,
    XtractTransientParameters,
)
from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning


class Xtract(XtractParent):
    """Extract signal components using the Xtract algorithm.

    This algorithm chains a denoising step, a tonal extraction step, and a transient extraction
    step. It allows separating the noise, tonal, transient, and remainder components of a signal.
    The Xtract algorithm is the same as that which is implemented in Ansys Sound Analysis and
    Specification (SAS).

    .. seealso::
        :class:`XtractDenoiser`, :class:`XtractDenoiserParameters`, :class:`XtractTonal`,
        :class:`XtractTonalParameters`, :class:`XtractTransient`, :class:`XtractTransientParameters`

    Examples
    --------
    Extract and display the different signal components using the Xtract algorithm.

    >>> from ansys.sound.core import Xtract
    >>> xtract = Xtract(
    ...     input_signal=my_signal,
    ...     parameters_denoiser=my_denoiser_params,
    ...     parameters_tonal=my_tonal_params,
    ...     parameters_transient=my_transient_params,
    ... )
    >>> xtract.process()
    >>> noise_signal, tonal_signal, transient_signal, remainder_signal = xtract.get_output()
    >>> xtract.plot()

    .. seealso::
        :ref:`xtract_feature_example`
            Example demonstrating how to use Xtract to extract the various components of a signal.
    """

    def __init__(
        self,
        input_signal: Field = None,
        parameters_denoiser: XtractDenoiserParameters = None,
        parameters_tonal: XtractTonalParameters = None,
        parameters_transient: XtractTransientParameters = None,
    ):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        input_signal : Field, default: None
            Input signal on which to apply the Xtract processing as a DPF field.
        parameters_denoiser : XtractDenoiserParameters, default: None
            Structure that contains the parameters of the denoising step:

            - Noise PSD (Field) is the power spectral density (PSD) of the noise.

            This structure is of the ``XtractDenoiserParameters`` type. For more information,
            see this class.
        parameters_tonal : XtractTonalParameters, default: None
            Structure that contains the parameters of the tonal extraction step:

            - NFFT (int) is the number of points used for the FFT computation.
            - Regularity setting (float) in percent.
            - Maximum slope (float) in dB/Hz.
            - Minimum duration (float) in seconds.
            - Intertonal gap (float) in Hz.
            - Local emergence (float) in dB.

            This structure is of the ``XtractTonalParameters`` type. For more information,
            see this class.
        parameters_transient : XtractTransientParameters, default: None
            Structure that contains the parameters of the transient extraction step:

            - Lower threshold (float), which is between 0 and 100 percent.
            - Upper threshold (float), which is between 0 and 100 percent.

            This structure is of the ``XtractTransientParameters`` type. For more information,
            see this class.
        """
        super().__init__()
        self.input_signal = input_signal
        self.parameters_denoiser = parameters_denoiser
        self.parameters_tonal = parameters_tonal
        self.parameters_transient = parameters_transient

        # Define output fields
        self.__output_noise_signal = None
        self.__output_tonal_signal = None
        self.__output_transient_signal = None
        self.__output_remainder_signal = None

        self._output = (
            self.__output_noise_signal,
            self.__output_tonal_signal,
            self.__output_transient_signal,
            self.__output_remainder_signal,
        )

        self.__operator = Operator("xtract")

    @property
    def input_signal(self) -> Field:
        """Input signal on which to apply the Xtract processing as a DPF field."""
        return self.__input_signal

    @input_signal.setter
    def input_signal(self, value: Field):
        """Input signal."""
        self.__input_signal = value

    @property
    def parameters_denoiser(self) -> XtractDenoiserParameters:
        """Parameters of the denoiser step.

        Structure that contains the parameters of the denoising step:

        - Power spectral density of the noise as a DPF field.
        """
        return self.__parameters_denoiser

    @parameters_denoiser.setter
    def parameters_denoiser(self, value: XtractDenoiserParameters):
        """Set parameters of the denoiser step."""
        self.__parameters_denoiser = value

    @property
    def parameters_tonal(self) -> XtractTonalParameters:
        """Parameters of the tonal extraction step.

        Structure that contains the parameters of the tonal extraction step:

        - NFFT (int) is the number of points used for the FFT computation.
        - Regularity setting (float) between 0 and 1.
        - Maximum slope (float) in dB/Hz.
        - Minimum duration (float) in seconds (s).
        - Intertonal gap (float) in Hz.
        - Local emergence (float) in dB.
        """
        return self.__parameters_tonal

    @parameters_tonal.setter
    def parameters_tonal(self, value: XtractTonalParameters):
        """Set parameters of the tonal extraction step."""
        self.__parameters_tonal = value

    @property
    def parameters_transient(self) -> XtractTransientParameters:
        """Parameters of the transient extraction step.

        Structure that contains the parameters of the transient extraction step:

        - Lower threshold (float), which is between 0 and 100.
        - Upper threshold (float), which is between 0 and 100.
        """
        return self.__parameters_transient

    @parameters_transient.setter
    def parameters_transient(self, value: XtractTransientParameters):
        """Set parameters of the transient extraction step."""
        self.__parameters_transient = value

    @property
    def output_noise_signal(self) -> Field:
        """Noise signal as a DPF field."""
        return self.__output_noise_signal

    @property
    def output_tonal_signal(self) -> Field:
        """Tonal signal as a DPF field."""
        return self.__output_tonal_signal

    @property
    def output_transient_signal(self) -> Field:
        """Transient signal as a DPF field."""
        return self.__output_transient_signal

    @property
    def output_remainder_signal(self) -> Field:
        """Remainder signal as a DPF field."""
        return self.__output_remainder_signal

    def process(self):
        """Process the Xtract algorithm."""
        if self.input_signal is None:
            raise PyAnsysSoundException("Input signal is not set.")

        if self.parameters_denoiser is None:
            raise PyAnsysSoundException("Input parameters for the denoiser extraction are not set.")

        if self.parameters_tonal is None:
            raise PyAnsysSoundException("Input parameters for the tonal extraction are not set.")

        if self.parameters_transient is None:
            raise PyAnsysSoundException(
                "Input parameters for the transient extraction are not set."
            )

        self.__operator.connect(0, self.input_signal)
        self.__operator.connect(
            1, self.parameters_denoiser.get_parameters_as_generic_data_container()
        )
        self.__operator.connect(2, self.parameters_tonal.get_parameters_as_generic_data_container())
        self.__operator.connect(
            3, self.parameters_transient.get_parameters_as_generic_data_container()
        )

        # Runs the operator
        self.__operator.run()

        # Stores the outputs
        self.__output_noise_signal = self.__operator.get_output(0, types.fields_container)[0]
        self.__output_tonal_signal = self.__operator.get_output(1, types.fields_container)[0]
        self.__output_transient_signal = self.__operator.get_output(2, types.fields_container)[0]
        self.__output_remainder_signal = self.__operator.get_output(3, types.fields_container)[0]

        self._output = (
            self.__output_noise_signal,
            self.__output_tonal_signal,
            self.__output_transient_signal,
            self.__output_remainder_signal,
        )

    def get_output(self) -> tuple[Field, Field, Field, Field]:
        """Get the output of the Xtract algorithm in a tuple of DPF fields.

        Returns
        -------
        Field
            Noise signal as a DPF field.
        Field
            Tonal signal as a DPF field.
        Field
            Transient signal as a DPF field.
        Field
            Remainder signal as a DPF field.
        """
        if None in self._output:
            warnings.warn(PyAnsysSoundWarning("Output is not processed yet."))

        return self._output

    def get_output_as_nparray(
        self,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Get the output of the Xtract algorithm in a tuple as NumPy arrays.

        Returns
        -------
        numpy.ndarray
            Noise signal as a NumPy array.
        numpy.ndarray
            Tonal signal as a NumPy array.
        numpy.ndarray
            Transient signal as a NumPy array.
        numpy.ndarray
            Remainder signal as a NumPy array.
        """
        output = self.get_output()

        if None in output:
            return np.array([]), np.array([]), np.array([]), np.array([])

        return tuple(np.array(signal.data) for signal in output)

    def plot(self):
        """Plot the Xtract algorithm results."""
        (
            noise_signal,
            tonal_signal,
            transient_signal,
            remainder_signal,
        ) = self.get_output()
        time = noise_signal.time_freq_support.time_frequencies

        _, axs = plt.subplots(4, figsize=(10, 20))

        axs[0].plot(time.data, noise_signal.data)
        axs[0].set_ylabel(f"Amplitude ({noise_signal.unit})")
        axs[0].set_title("Noise signal")

        axs[1].plot(time.data, tonal_signal.data)
        axs[1].set_ylabel(f"Amplitude ({tonal_signal.unit})")
        axs[1].set_title("Tonal signal")

        axs[2].plot(time.data, transient_signal.data)
        axs[2].set_ylabel(f"Amplitude ({transient_signal.unit})")
        axs[2].set_title("Transient signal")

        axs[3].plot(time.data, remainder_signal.data)
        axs[3].set_xlabel(f"Time ({time.unit})")
        axs[3].set_ylabel(f"Amplitude ({remainder_signal.unit})")
        axs[3].set_title("Remainder signal")

        plt.show()
