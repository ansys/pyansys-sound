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

"""Computes ANSI S3.4-2007 loudness."""

import warnings

from ansys.dpf.core import Field, Operator, types
import numpy as np

from . import FIELD_DIFFUSE, FIELD_FREE, PsychoacousticsParent
from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning

# Name of the DPF Sound operator used in this module.
ID_COMPUTE_LOUDNESS_ANSI_S3_4 = "compute_loudness_ansi_s3_4"


class LoudnessANSI_S3_4(PsychoacousticsParent):
    """Computes ANSI S3.4-2007 loudness.

    This class computes the loudness of a signal according to the ANSI S3.4-2007 standard. The
    scope of this standard is now covered by the ISO 532-2:2017 standard.

    .. seealso::
        :class:`LoudnessISO532_2`

    Examples
    --------
    Compute the loudness of a signal in free field.

    >>> from ansys.sound.core.psychoacoustics import LoudnessANSI_S3_4
    >>> loudness = LoudnessANSI_S3_4(signal=my_signal, field_type="Free")
    >>> loudness.process()
    >>> loudness_value = loudness.get_loudness_sone()
    >>> loudness_level_value = loudness.get_loudness_level_phon()
    """

    def __init__(self, signal: Field = None, field_type: str = FIELD_FREE):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        signal : Field, default: None
            Input signal in Pa.
        field_type : str, default: "Free"
            Sound field type. Available options are `"Free"` and `"Diffuse"`.
        """
        super().__init__()
        self.signal = signal
        self.field_type = field_type
        self.__operator = Operator(ID_COMPUTE_LOUDNESS_ANSI_S3_4)

    def __str__(self):
        """Return the string representation of the object."""
        if self._output is None:
            str_loudness = "Not processed"
            str_loudness_level = "Not processed"
        else:
            str_loudness = f"{self.get_loudness_sone():.3} sones"
            str_loudness_level = f"{self.get_loudness_level_phon():.1f} phons"

        str_name = f'"{self.signal.name}"' if self.signal is not None else "Not set"

        return (
            f"{__class__.__name__} object\n"
            "Data:\n"
            f"\tSignal name: {str_name}\n"
            f"\tField type: {self.field_type}\n"
            f"Loudness: {str_loudness}\n"
            f"Loudness level: {str_loudness_level}"
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
        """Compute the loudness.

        This method calls the appropriate DPF Sound operator to compute the loudness of the signal.
        """
        if self.signal == None:
            raise PyAnsysSoundException(f"Signal is not set. Use `{__class__.__name__}.signal`.")

        self.__operator.connect(0, self.signal)
        self.__operator.connect(1, self.field_type)

        # Runs the operator
        self.__operator.run()

        self._output = (
            self.__operator.get_output(0, types.double),
            self.__operator.get_output(1, types.double),
        )

    def get_output(self) -> tuple[float]:
        """Get loudness data.

        Returns
        -------
        tuple[float]
            -   First element (float): loudness in sone.

            -   Second element (float): loudness level in phon.
        """
        if self._output == None:
            warnings.warn(
                PyAnsysSoundWarning(
                    "Output is not processed yet. Use the "
                    f"`{__class__.__name__}.process()` method."
                )
            )

        return self._output

    def get_output_as_nparray(self) -> tuple[np.ndarray]:
        """Get loudness data in a tuple of NumPy arrays.

        Returns
        -------
        tuple[numpy.ndarray]
            -   First element: loudness in sone.

            -   Second element: loudness level in phon.
        """
        output = self.get_output()

        if output == None:
            return np.array([]), np.array([])

        return np.array(output[0]), np.array(output[1])

    def get_loudness_sone(self) -> float:
        """Get the loudness in sone.

        Returns
        -------
        float
            Loudness value in sone.
        """
        return self.get_output()[0]

    def get_loudness_level_phon(self) -> float:
        """Get the loudness level in phon.

        Returns
        -------
        float
            Loudness level value in phon.
        """
        return self.get_output()[1]
