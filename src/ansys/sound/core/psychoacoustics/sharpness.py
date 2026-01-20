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

"""Computes the sharpness of the signal according to Zwicker & Fastl's model."""

import warnings

from ansys.dpf.core import Field, Operator, types
import numpy as np

from . import FIELD_DIFFUSE, FIELD_FREE, PsychoacousticsParent
from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning

# Name of the DPF Sound operator used in this module.
ID_COMPUTE_SHARPNESS = "compute_sharpness"


class Sharpness(PsychoacousticsParent):
    """Computes the sharpness of a signal according to Zwicker & Fastl's model.

    .. note::
        The calculation of this indicator is based on the loudness model for stationary sounds
        defined in the standard ISO 532-1. It is the loudness model of the class
        :class:`LoudnessISO532_1_Stationary`.

    .. seealso::
        :class:`SharpnessDIN45692`, :class:`SharpnessOverTime`,
        :class:`LoudnessISO532_1_Stationary`

    Examples
    --------
    Compute the sharpness of a signal according to Zwicker & Fastl's model.

    >>> from ansys.sound.core.psychoacoustics import Sharpness
    >>> sharpness = Sharpness(signal=my_signal)
    >>> sharpness.process()
    >>> sharpness_value = sharpness.get_sharpness()

    .. seealso::
        :ref:`calculate_psychoacoustic_indicators`
            Example demonstrating how to compute various psychoacoustic indicators.
    """

    def __init__(self, signal: Field = None, field_type: str = FIELD_FREE):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        signal : Field, default: None
            Signal in Pa on which to compute sharpness.
        field_type : str, default: "Free"
            Sound field type. Available options are `"Free"` and `"Diffuse"`.
        """
        super().__init__()
        self.signal = signal
        self.field_type = field_type
        self.__operator = Operator(ID_COMPUTE_SHARPNESS)

    def __str__(self):
        """Return the string representation of the object."""
        if self._output is None:
            str_sharpness = "Not processed"
        else:
            str_sharpness = f"{self.get_sharpness():.2f} acums"

        str_name = f'"{self.signal.name}"' if self.signal is not None else "Not set"

        return (
            f"{__class__.__name__} object\n"
            "Data:\n"
            f"\tSignal name: {str_name}\n"
            f"Sharpness: {str_sharpness}"
        )

    @property
    def signal(self) -> Field:
        """Input signal in Pa."""
        return self.__signal

    @signal.setter
    def signal(self, signal: Field):
        """Set the signal."""
        if not (isinstance(signal, Field) or signal is None):
            raise PyAnsysSoundException("Signal must be specified as a DPF field.")
        self.__signal = signal

    @property
    def field_type(self) -> str:
        """Sound field type.

        Available options are `"Free"` and `"Diffuse"`.
        """
        return self.__field_type

    @field_type.setter
    def field_type(self, field_type: str):
        """Set the sound field type."""
        if field_type.lower() not in [FIELD_FREE.lower(), FIELD_DIFFUSE.lower()]:
            raise PyAnsysSoundException(
                f'Invalid field type "{field_type}". Available options are "{FIELD_FREE}" and '
                f'"{FIELD_DIFFUSE}".'
            )
        self.__field_type = field_type

    def process(self):
        """Compute the sharpness.

        This method calls the appropriate DPF Sound operator to compute the sharpness
        of the signal.
        """
        if self.signal == None:
            raise PyAnsysSoundException(
                "No signal found for sharpness computation. Use `Sharpness.signal`."
            )

        self.__operator.connect(0, self.signal)
        self.__operator.connect(1, self.field_type)

        # Runs the operator
        self.__operator.run()

        self._output = float(self.__operator.get_output(0, types.double))

    def get_output(self) -> float:
        """Get the sharpness value.

        Returns
        -------
        float
            Sharpness value in acum.
        """
        if self._output == None:
            warnings.warn(
                PyAnsysSoundWarning(
                    "Output is not processed yet. Use the `Sharpness.process()` method."
                )
            )

        return self._output

    def get_output_as_nparray(self) -> np.ndarray:
        """Get the sharpness as a NumPy array.

        Returns
        -------
        numpy.ndarray:
            Singleton array containing the sharpness value in acum.
        """
        output = self.get_output()

        if output == None:
            return np.nan

        return np.array([output])

    def get_sharpness(self) -> float:
        """Get the sharpness value.

        Returns
        -------
        float
            Sharpness value in acum.
        """
        return self.get_output()
