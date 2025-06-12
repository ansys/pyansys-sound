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

"""Computes the sharpness according to the DIN 45692 standard."""
import warnings

from ansys.dpf.core import Field, Operator, types
import numpy as np

from . import FIELD_DIFFUSE, FIELD_FREE, PsychoacousticsParent
from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning

# Name of the DPF Sound operator used in this module.
ID_COMPUTE_SHARPNESS_DIN = "compute_sharpness_din45692"


class SharpnessDIN45692(PsychoacousticsParent):
    """Computes the sharpness of a signal according to the DIN 45692 standard.

    .. note::
        The calculation of this indicator is based on the specific loudness result from
        the loudness model for stationary sounds defined in the ISO 532-1 standard.
        This is the same loudness model used in the
        :class:`LoudnessISO532_1_Stationary` class.
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
        self.__operator = Operator(ID_COMPUTE_SHARPNESS_DIN)

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
        """Compute the DIN 45692 sharpness.

        This method calls the appropriate DPF Sound operator.
        """
        if self.signal == None:
            raise PyAnsysSoundException(
                "No signal found for sharpness over time computation. Use "
                f"`{__class__.__name__}.signal`."
            )

        self.__operator.connect(0, self.signal)
        self.__operator.connect(1, self.field_type)

        # Runs the operator
        self.__operator.run()

        # We skip pins 1 & 2, as they relate to sharpness over time. See class
        # `SharpnessDIN45692OverTime`.
        self._output = self.__operator.get_output(0, types.double)

    def get_output(self) -> float:
        """Get the DIN 45692 sharpness.

        Returns
        -------
        float
            Sharpness value in acum.
        """
        if self._output == None:
            warnings.warn(
                PyAnsysSoundWarning(
                    f"Output is not processed yet. Use the `{__class__.__name__}.process()` method."
                )
            )

        return self._output

    def get_output_as_nparray(self) -> np.ndarray:
        """Get the DIN 45692 sharpness as a NumPy array.

        Returns
        -------
        numpy.ndarray
            Singleton array containing the sharpness value in acum.
        """
        output = self.get_output()

        if output == None:
            return np.nan

        return np.array([output])

    def get_sharpness(self) -> float:
        """Get the DIN 45692 sharpness.

        Returns
        -------
        float
            Sharpness value in acum.
        """
        return self.get_output()
