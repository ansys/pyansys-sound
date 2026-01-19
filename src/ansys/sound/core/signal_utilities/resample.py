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

"""Resample a signal."""

import warnings

from ansys.dpf.core import Field, FieldsContainer, Operator
import numpy as np

from . import SignalUtilitiesParent
from .._pyansys_sound import (
    PyAnsysSoundException,
    PyAnsysSoundWarning,
    convert_fields_container_to_np_array,
)


class Resample(SignalUtilitiesParent):
    """Resample a signal.

    Examples
    --------
    Resample a signal to a new sampling frequency.

    >>> from ansys.sound.core.signal_utilities import Resample
    >>> resample = Resample(signal=my_signal, new_sampling_frequency=48000.0)
    >>> resample.process()
    >>> resampled_signal = resample.get_output()

    .. seealso::
        :ref:`load_resample_amplify_write_wav_files_example`
            Example demonstrating how to load, resample, amplify, and write WAV files.
    """

    def __init__(
        self, signal: Field | FieldsContainer = None, new_sampling_frequency: float = 44100.0
    ):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        signal : Field | FieldsContainer, default: None
            Signal to resample as a DPF field or fields container.
        new_sampling_frequency : float, default: 44100.0
            New sampling frequency to use.
        """
        super().__init__()
        self.signal = signal
        self.new_sampling_frequency = new_sampling_frequency
        self.__operator = Operator("resample")

    @property
    def new_sampling_frequency(self) -> float:
        """New sampling frequency in Hz."""
        return self.__new_sampling_frequency

    @new_sampling_frequency.setter
    def new_sampling_frequency(self, new_sampling_frequency: float):
        """Set a new sampling frequency."""
        if new_sampling_frequency < 0.0:
            raise PyAnsysSoundException("Sampling frequency must be greater than 0.0.")

        self.__new_sampling_frequency = new_sampling_frequency

    @property
    def signal(self) -> Field | FieldsContainer:
        """Input signal as a DPF field or fields container."""
        return self.__signal

    @signal.setter
    def signal(self, signal: Field | FieldsContainer):
        """Set the signal."""
        self.__signal = signal

    def process(self):
        """Resample the signal.

        This method calls the appropriate DPF Sound operator to resample the signal.
        """
        if self.signal == None:
            raise PyAnsysSoundException(
                "No signal to resample. Use the 'Resample.set_signal()' method."
            )

        self.__operator.connect(0, self.signal)
        self.__operator.connect(1, float(self.new_sampling_frequency))

        # Runs the operator
        self.__operator.run()

        # Stores output in the variable
        if type(self.signal) == FieldsContainer:
            self._output = self.__operator.get_output(0, "fields_container")
        elif type(self.signal) == Field:
            self._output = self.__operator.get_output(0, "field")

    def get_output(self) -> FieldsContainer | Field:
        """Get the resampled signal as a DPF fields container.

        Returns
        -------
        FieldsContainer
            Resampled signal in a DPF fields container.
        """
        if self._output == None:
            # Computing output if needed
            warnings.warn(PyAnsysSoundWarning("Output is not processed yet. \
                        Use the 'Resample.process()' method."))

        return self._output

    def get_output_as_nparray(self) -> np.ndarray:
        """Get the resampled signal as a NumPy array.

        Returns
        -------
        numpy.ndarray
            Resampled signal in a NumPy array.
        """
        output = self.get_output()

        if type(output) == Field:
            return output.data

        return convert_fields_container_to_np_array(output)
