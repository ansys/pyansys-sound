# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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

"""Inverse short-time Fourier transform."""

import warnings

from ansys.dpf.core import Field, FieldsContainer, Operator
import matplotlib.pyplot as plt
import numpy as np

from . import SpectrogramProcessingParent
from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning


class Istft(SpectrogramProcessingParent):
    """Computes the inverse short-time Fourier transform (ISTFT) of a signal."""

    def __init__(self, stft: FieldsContainer = None):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        stft : FieldsContainer, default: None
            DPF fields container containing a short-time Fourier transform (STFT)
            computed with the ``Stft`` class.
        """
        super().__init__()
        self.stft = stft
        self.__operator = Operator("compute_istft")

    @property
    def stft(self) -> FieldsContainer:
        """Input short-time Fourier transform.

        STFT format is the same as that which is produced by the ``Stft`` class.
        """
        return self.__stft

    @stft.setter
    def stft(self, stft: FieldsContainer):
        """Set the STFT."""
        if type(stft) != FieldsContainer and stft is not None:
            raise PyAnsysSoundException("Input must be a DPF fields container.")

        if stft is not None and (
            not stft.has_label("time")
            or not stft.has_label("complex")
            or not stft.has_label("channel_number")
        ):
            raise PyAnsysSoundException(
                "STFT is in the wrong format. Make sure that it has been computed "
                "with the 'Stft' class."
            )

        self.__stft = stft

    def process(self):
        """Compute the ISTFT.

        This method calls the appropriate DPF Sound operator to compute the
        inverse STFT of the STFT.
        """
        if self.stft == None:
            raise PyAnsysSoundException(
                "No STFT input found for ISTFT computation. Use 'Istft.stft'."
            )

        self.__operator.connect(0, self.stft)

        # Runs the operator
        self.__operator.run()

        # Stores output in the variable
        self._output = self.__operator.get_output(0, "field")

    def get_output(self) -> Field:
        """Get the ISTFT resulting signal as a DPF field.

        Returns
        -------
        Field
            Signal resulting from the ISTFT as a DPF field.
        """
        if self._output == None:
            # Computing output if needed
            warnings.warn(
                PyAnsysSoundWarning(
                    "Output is not processed yet. \
                        Use the 'Istft.process()' method."
                )
            )

        return self._output

    def get_output_as_nparray(self) -> np.ndarray:
        """Get the ISTFT resulting signal as a NumPy array.

        Returns
        -------
        numpy.ndarray
            ISTFT resulting signal in a NumPy array.
        """
        output = self.get_output()
        out_as_np_array = output.data

        # return out_as_np_array
        return np.transpose(out_as_np_array)

    def plot(self):
        """Plot signals.

        Plot the signal resulting from the ISTFT.
        """
        if self._output is None:
            raise PyAnsysSoundException(
                f"Output is not processed yet. Use the `{__class__.__name__}.process()` method."
            )
        output = self.get_output()
        time = output.time_freq_support.time_frequencies

        plt.plot(time.data, output.data, label="Signal")
        plt.title(output.name)
        plt.legend()
        plt.xlabel(f"Time ({time.unit})")
        plt.ylabel(f"Amplitude ({output.unit})")
        plt.grid(True)
        plt.show()
