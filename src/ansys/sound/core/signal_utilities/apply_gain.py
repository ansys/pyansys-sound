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

"""Applies a gain to a signal."""

import warnings

from ansys.dpf.core import Field, FieldsContainer, Operator
import numpy as np

from . import SignalUtilitiesParent
from .._pyansys_sound import (
    PyAnsysSoundException,
    PyAnsysSoundWarning,
    convert_fields_container_to_np_array,
)


class ApplyGain(SignalUtilitiesParent):
    """Apply a gain to a signal.

    Examples
    --------
    Amplify a signal by applying a gain of 5 dB.

    >>> from ansys.sound.core.signal_utilities import ApplyGain
    >>> apply_gain = ApplyGain(signal=my_signal, gain=5.0, gain_in_db=True)
    >>> apply_gain.process()
    >>> amplified_signal = apply_gain.get_output()

    .. seealso::
        :ref:`load_resample_amplify_write_wav_files_example`
            Example demonstrating how to load, resample, amplify, and write WAV files.
    """

    def __init__(
        self, signal: Field | FieldsContainer = None, gain: float = 0.0, gain_in_db: bool = True
    ):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        signal : Field | FieldsContainer, default: None
            Signals to apply gain on as a DPF field or fields container.
        gain : float, default: 0.0
            Gain value in decibels (dB) or linear unit. By default, gain is specified in decibels.
            However, you can use the next parameter to change to a linear unit.
        gain_in_db : bool, default: True
            Whether gain is in dB. When ``False``, gain is in a linear unit.
        """
        super().__init__()
        self.signal = signal
        self.gain = gain
        self.gain_in_db = gain_in_db
        self.__operator = Operator("apply_gain")

    @property
    def signal(self) -> Field | FieldsContainer:
        """Input signal as a DPF field or fields container."""
        return self.__signal

    @signal.setter
    def signal(self, signal: Field | FieldsContainer):
        """Set the signal."""
        self.__signal = signal

    @property
    def gain(self) -> float:
        """Gain value in dB or in linear unit (depending on ``gain_in_db`` value)."""
        return self.__gain

    @gain.setter
    def gain(self, new_gain: float):
        """Set a new gain value."""
        self.__gain = new_gain

    @property
    def gain_in_db(self) -> bool:
        """``True`` if input gain is in dB, or ``False`` if it is in linear unit.

        Boolean that indicates whether the input gain is provided in decibels (``True``) or in
        linear unit (``False``).
        """
        return self.__gain_in_db

    @gain_in_db.setter
    def gain_in_db(self, new_gain_in_db: bool):
        """Set gain_in_db."""
        if type(new_gain_in_db) is not bool:
            raise PyAnsysSoundException(
                "'new_gain_in_db' must be a Boolean value. Specify 'True' or 'False'."
            )

        self.__gain_in_db = new_gain_in_db

    def process(self):
        """Apply a gain to the signal.

        This method calls the appropriate DPF Sound operator to apply a gain to the signal.
        """
        if self.signal == None:
            raise PyAnsysSoundException(
                "No signal to apply gain on. Use the 'ApplyGain.set_signal()' method."
            )

        self.__operator.connect(0, self.signal)
        self.__operator.connect(1, float(self.gain))
        self.__operator.connect(2, bool(self.gain_in_db))

        # Runs the operator
        self.__operator.run()

        # Stores output in the variable
        if type(self.signal) == FieldsContainer:
            self._output = self.__operator.get_output(0, "fields_container")
        elif type(self.signal) == Field:
            self._output = self.__operator.get_output(0, "field")

    def get_output(self) -> FieldsContainer | Field:
        """Get the signal with a gain as a DPF fields container.

        Returns
        -------
        FieldsContainer
            Signal with an applied gain as a DPF fields container.
        """
        if self._output == None:
            # Computing output if needed
            warnings.warn(
                PyAnsysSoundWarning(
                    "Output is not processed yet. Use the 'ApplyGain.process()' method."
                )
            )

        return self._output

    def get_output_as_nparray(self) -> np.ndarray:
        """Get the signal with a gain as a NumPy array.

        Returns
        -------
        numpy.ndarray
            Signal with an applied gain as a NumPy array.
        """
        output = self.get_output()

        if type(output) == Field:
            return output.data

        return convert_fields_container_to_np_array(output)
