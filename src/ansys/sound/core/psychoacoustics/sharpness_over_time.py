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

"""Computes the sharpness according to Zwicker & Fastl's model, over time."""
import warnings

from ansys.dpf.core import Field, Operator, types
import matplotlib.pyplot as plt
import numpy as np

from . import FIELD_DIFFUSE, FIELD_FREE, PsychoacousticsParent
from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning

# Name of the DPF Sound operator used in this module.
ID_COMPUTE_SHARPNESS_OVER_TIME = "compute_sharpness_over_time"


class SharpnessOverTime(PsychoacousticsParent):
    """Computes the sharpness of a signal according to Zwicker & Fastl's model, over time."""

    def __init__(self, signal: Field = None, field_type: str = FIELD_FREE):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        signal : Field, default: None
            Signal in Pa on which to compute sharpness over time as a DPF field.
        field_type : str, default: "Free"
            Sound field type. Available options are `"Free"` and `"Diffuse"`.
        """
        super().__init__()
        self.signal = signal
        self.field_type = field_type
        self.__operator = Operator(ID_COMPUTE_SHARPNESS_OVER_TIME)

    def __str__(self):
        """Return the string representation of the object."""
        if self._output is None:
            str_sharpness = "Not processed"
        else:
            str_sharpness = f"{self.get_max_sharpness():.2f} acums"

        return (
            f"{__class__.__name__} object\n"
            "Data:\n"
            f'\tSignal name: {f'"{self.signal.name}"' if self.signal is not None else "Not set"}\n'
            f"Max sharpness: {str_sharpness}"
        )

    @property
    def signal(self) -> Field:
        """Input sound signal in Pa as a DPF field."""
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
        """Compute the sharpness over time.

        This method calls the appropriate DPF Sound operator to compute the sharpness over time of
        the signal.
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

        self._output = (
            self.__operator.get_output(0, types.double),
            self.__operator.get_output(1, types.field),
        )

    def get_output(self) -> tuple:
        """Get the sharpness over time data in a tuple.

        Returns
        -------
        tuple
            -   First element is the maximum sharpness over time, in acum.

            -   Second element is the sharpness over time, in acum.
        """
        if self._output == None:
            warnings.warn(
                PyAnsysSoundWarning(
                    f"Output is not processed yet. Use the `{__class__.__name__}.process()` method."
                )
            )

        return self._output

    def get_output_as_nparray(self) -> tuple[np.ndarray]:
        """Get the sharpness over time data in a tuple of NumPy arrays.

        Returns
        -------
        tuple[numpy.ndarray]
            -   First element is the maximum sharpness over time, in acum.

            -   Second element is the sharpness over time, in acum.

            -   Third element is the time scale, in s.
        """
        output = self.get_output()

        if output == None:
            return (np.nan, np.array([]), np.array([]))

        return (
            np.array(output[0]),
            np.array(output[1].data),
            np.array(output[1].time_freq_support.time_frequencies.data),
        )

    def get_max_sharpness(self) -> float:
        """Get the maximum sharpness over time.

        Returns
        -------
        float
            Maximum sharpness over time, in acum.
        """
        return float(self.get_output_as_nparray()[0])

    def get_sharpness_over_time(self) -> np.ndarray:
        """Get the sharpness over time.

        Returns
        -------
        numpy.ndarray
            Sharpness over time, in acum.
        """
        return self.get_output_as_nparray()[1]

    def get_time_scale(self) -> np.ndarray:
        """Get the time scale.

        Returns
        -------
        numpy.ndarray
            Time scale in s.
        """
        return self.get_output_as_nparray()[2]

    def plot(self):
        """Plot the sharpness over time."""
        if self._output == None:
            raise PyAnsysSoundException(
                f"Output is not processed yet. Use the `{__class__.__name__}.process()` method."
            )

        sharpness_over_time = self.get_sharpness_over_time()
        time_scale = self.get_time_scale()

        plt.figure()
        plt.plot(time_scale, sharpness_over_time)
        plt.xlabel("Time (s)")
        plt.ylabel("S (acum)")
        plt.title("Sharpness (Zwicker & Fastl)")
        plt.grid()
        plt.show()