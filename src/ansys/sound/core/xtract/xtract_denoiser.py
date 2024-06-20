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

"""Xtract denoiser class."""

from typing import Tuple
import warnings

from ansys.dpf.core import Field, FieldsContainer, Operator
import matplotlib.pyplot as plt
import numpy as np
from numpy import typing as npt

from . import XtractDenoiserParameters, XtractParent
from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning


class XtractDenoiser(XtractParent):
    """Provides signal denoising using the Xtract algorithm."""

    def __init__(
        self,
        input_signal: FieldsContainer | Field = None,
        input_parameters: XtractDenoiserParameters = None,
    ):
        """Create an ``XtractDenoiser`` instance.

        Parameters
        ----------
        input_signal: FieldsContainer | Field, default: None
            One or more signals to denoise as a DPF fields container or field. When inputting a
            fields container, each signal (each field of the fields container) is processed
            individually.
        input_parameters: XtractDenoiserParametersm default: None
            Structure that contains the parameters of the algorithm:

            - Noise PSD (Field): Power spectral density of the noise

            This structure is of the ``XtractDenoiserParameters`` type. For more information,
            see this class.
        """
        super().__init__()
        self.input_signal = input_signal
        self.input_parameters = input_parameters

        # Define output fields
        self.__output_denoised_signals = None
        self.__output_noise_signals = None

        self._output = (self.__output_denoised_signals, self.__output_noise_signals)

        self.__operator = Operator("xtract_denoiser")

    @property
    def input_signal(self) -> FieldsContainer | Field:
        """Input signal.

        Returns
        -------
        FieldsContainer | Field
            One or more signals to denoise as a DPF fields container or field. When inputting a
            fields container, each signal (each field of the fields container) is processed
            individually.
        """
        return self.__input_signal  # pragma: no cover

    @input_signal.setter
    def input_signal(self, value: FieldsContainer | Field):
        """Set input signal."""
        self.__input_signal = value

    @property
    def input_parameters(self) -> XtractDenoiserParameters:
        """Input parameters.

        Returns
        -------
        XtractDenoiserParameters
            Structure that contains the parameters of the algorithm.
        """
        return self.__input_parameters  # pragma: no cover

    @input_parameters.setter
    def input_parameters(self, value: XtractDenoiserParameters):
        """Input parameters."""
        self.__input_parameters = value

    @property
    def output_denoised_signals(self) -> FieldsContainer | Field:
        """Output denoised signals.

        Returns
        -------
        FieldsContainer | Field
            One or more denoised signals as a DPF fields container or field (depending on
            the input).
        """
        return self.__output_denoised_signals  # pragma: no cover

    @property
    def output_noise_signals(self) -> FieldsContainer | Field:
        """Output noise signals.

        Returns
        -------
        FieldsContainer | Field
            One or more noise signals as a DPF fields container or field (depending on the input).
            The noise signal is the original signal minus the denoised signal.
        """
        return self.__output_noise_signals  # pragma: no cover

    def process(self):
        """Apply denoising."""
        if self.input_signal is None:
            raise PyAnsysSoundException("Input signal is not set.")

        if self.input_parameters is None:
            raise PyAnsysSoundException("Input parameters are not set.")

        self.__operator.connect(0, self.input_signal)
        self.__operator.connect(1, self.input_parameters.get_parameters_as_generic_data_container())

        # Runs the operator
        self.__operator.run()

        # Stores the output in the variable
        if type(self.input_signal) == Field:
            self.__output_denoised_signals = self.__operator.get_output(0, "field")
            self.__output_noise_signals = self.__operator.get_output(1, "field")
        else:
            self.__output_denoised_signals = self.__operator.get_output(0, "fields_container")
            self.__output_noise_signals = self.__operator.get_output(1, "fields_container")

        self._output = (self.__output_denoised_signals, self.__output_noise_signals)

    def get_output(self) -> Tuple[FieldsContainer, FieldsContainer] | Tuple[Field, Field]:
        """Get the output of the denoising.

        Returns
        -------
        Tuple[FieldsContainer, FieldsContainer] | Tuple[Field, Field]
            Denoised signal and noise signal in a tuple as
            DPF fields containers or fields (depending on the input).
        """
        if self.__output_denoised_signals == None or self.__output_noise_signals == None:
            warnings.warn(PyAnsysSoundWarning("Output is not processed yet."))

        return self._output  # i.e. self.__output_denoised_signals, self.__output_noise_signals

    def get_output_as_nparray(self) -> Tuple[npt.ArrayLike, npt.ArrayLike]:
        """Get the output of the denoising as NumPy arrays.

        Returns
        -------
        Tuple[npt.ArrayLike, npt.ArrayLike]
            Denoised signal and noise signal in a tuple as NumPy arrays.
        """
        l_output_denoised_signals, l_output_noise_signals = self.get_output()

        if type(l_output_denoised_signals) == Field:
            return np.array(l_output_denoised_signals.data), np.array(l_output_noise_signals.data)
        else:
            if self.output_denoised_signals is None or self.output_noise_signals is None:
                return np.array([]), np.array([])
            else:
                return self.convert_fields_container_to_np_array(
                    l_output_denoised_signals
                ), self.convert_fields_container_to_np_array(l_output_noise_signals)

    def plot(self):
        """Plot signals.

        This method plots both the denoised signal and the noise signal.
        """
        ################
        #
        # Plot denoised signal
        #
        l_output_denoised_signals = self.get_output()[0]
        l_output_denoised_signals_as_field = (
            l_output_denoised_signals
            if type(l_output_denoised_signals) == Field
            else l_output_denoised_signals[0]
        )

        l_np_output_denoised, l_np_output_noise = self.get_output_as_nparray()

        l_time_data = l_output_denoised_signals_as_field.time_freq_support.time_frequencies.data
        l_time_unit = l_output_denoised_signals_as_field.time_freq_support.time_frequencies.unit
        l_unit = l_output_denoised_signals_as_field.unit

        ################
        # Note: by design, we have l_np_output_denoised.ndim == l_np_output_noise.ndim
        if l_np_output_denoised.ndim == 1:
            ###########
            # Field type
            plt.figure()
            plt.plot(l_time_data, l_np_output_denoised)
            plt.xlabel("Time (" + l_time_unit + ")")
            plt.ylabel("Amplitude (" + l_unit + ")")
            plt.title(f"Denoised signal")

            plt.figure()
            plt.plot(l_time_data, l_np_output_noise)
            plt.xlabel("Time (" + l_time_unit + ")")
            plt.ylabel("Amplitude (" + l_unit + ")")
            plt.title(f"Noise signal")
        else:
            ###########
            # FieldsContainer type
            for l_i in range(len(l_np_output_denoised)):
                plt.figure()
                plt.plot(l_time_data, l_np_output_denoised[l_i], label=f"Channel {l_i}")
                plt.xlabel("Time (" + l_time_unit + ")")
                plt.ylabel("Amplitude (" + l_unit + ")")
                plt.title(f"Denoised signal  - channel {l_i}")

            for l_i in range(len(l_np_output_noise)):
                plt.figure()
                plt.plot(l_time_data, l_np_output_noise[l_i], label=f"Channel {l_i}")
                plt.xlabel("Time (" + l_time_unit + ")")
                plt.ylabel("Amplitude (" + l_unit + ")")
                plt.title(f"Noise signal - channel {l_i}")

        # Show all figures created
        plt.show()
