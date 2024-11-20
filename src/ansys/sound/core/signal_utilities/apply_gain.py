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

"""Applies a gain to a signal."""

import warnings

from ansys.dpf.core import Field, FieldsContainer, Operator
from numpy import typing as npt

from . import SignalUtilitiesParent
from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning


class ApplyGain(SignalUtilitiesParent):
    """Applies a gain to a signal."""

    def __init__(
        self, signal: Field | FieldsContainer = None, gain: float = 0.0, gain_in_db: bool = True
    ):
        """Create an ``ApplyGain`` instance.

        Parameters
        ----------
        signal: Field | FieldsContainer, default: None
            Signals to apply gain on as a DPF field or fields container.
        gain: float, default: 0.0
            Gain value in decibels (dB) or linear unit. By default, gain is specified in decibels.
            However, you can use the next parameter to change to a linear unit.
        gain_in_db: bool, default: True
            Whether gain is in dB. When ``False``, gain is in a linear unit.
        """
        super().__init__()
        self.signal = signal
        self.gain = gain
        self.gain_in_db = gain_in_db
        self.__operator = Operator("apply_gain")

    @property
    def signal(self):
        """Signal."""
        return self.__signal  # pragma: no cover

    @signal.setter
    def signal(self, signal: Field | FieldsContainer):
        """Set the signal."""
        self.__signal = signal

    @signal.getter
    def signal(self) -> Field | FieldsContainer:
        """Signal.

        Returns
        -------
        FieldsContainer | Field
            Signal as a DPF field or fields container.
        """
        return self.__signal

    @property
    def gain(self):
        """Gain value."""
        return self.__gain  # pragma: no cover

    @gain.setter
    def gain(self, new_gain: float):
        """Set a new gain value.

        Parameters
        ----------
        new_gain:
            New gain value.
        """
        self.__gain = new_gain

    @gain.getter
    def gain(self) -> float:
        """Gain value.

        Returns
        -------
        float
            Gain value.
        """
        return self.__gain

    @property
    def gain_in_db(self):
        """Gain in decibels (dB)."""
        return self.__gain_in_db  # pragma: no cover

    @gain_in_db.setter
    def gain_in_db(self, new_gain_in_db: bool):
        """Set a new value for gain in decibels (dB).

        Parameters
        ----------
        new_gain_in_db:
            Whether to set the new gain in decibels(dB). When ``False``, gain is
            set in a linear unit.
        """
        if type(new_gain_in_db) is not bool:
            raise PyAnsysSoundException(
                "'new_gain_in_db' must be a Boolean value. Specify 'True' or 'False'."
            )

        self.__gain_in_db = new_gain_in_db

    @gain_in_db.getter
    def gain_in_db(self) -> bool:
        """Flag indicating if the gain is in decibels (dB).

        Returns
        -------
        bool
            ``True`` if gain is in decibels, ``False`` if it is in a linear unit.
        """
        return self.__gain_in_db

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

    def get_output_as_nparray(self) -> npt.ArrayLike:
        """Get the signal with a gain as a NumPy array.

        Returns
        -------
        np.array
            Signal with an applied gain as a NumPy array.
        """
        output = self.get_output()

        if type(output) == Field:
            return output.data

        return self.convert_fields_container_to_np_array(output)
