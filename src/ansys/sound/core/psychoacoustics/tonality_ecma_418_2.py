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

"""Computes ECMA 418-2 tonality."""
import warnings

from ansys.dpf.core import Field, Operator, types
import matplotlib.pyplot as plt
import numpy as np

from . import PsychoacousticsParent
from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning

# Name of the DPF Sound operator used in this module.
ID_COMPUTE_TONALITY_ECMA_418_2 = "compute_tonality_ecma418_2"


class TonalityECMA418_2(PsychoacousticsParent):
    """Computes ECMA 418-2 tonality.

    This class is used to compute the tonality according to the ECMA 418-2 standard (Hearing Model
    of Sottek), formerly known as ECMA 74, annex G.
    """

    def __init__(self, signal: Field = None):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        signal: Field, default: None
            Signal in Pa on which to calculate the tonality.
        """
        super().__init__()
        self.signal = signal
        self.__operator = Operator(ID_COMPUTE_TONALITY_ECMA_418_2)

    def __str__(self):
        """Return the string representation of the object."""
        if self._output is None:
            str_tonality = "Not processed\n"
        else:
            str_tonality = f"{self.get_tonality():.2f} tuHMS\n"

        return (
            f"{__class__.__name__} object.\n"
            "Data\n"
            f'Signal name: "{self.signal.name}"\n'
            f"Tonality: {str_tonality}"
        )

    @property
    def signal(self) -> Field:
        """Input signal in Pa."""
        return self.__signal

    @signal.setter
    def signal(self, signal: Field):
        """Set signal."""
        if not (isinstance(signal, Field) or signal is None):
            raise PyAnsysSoundException("Signal must be specified as a DPF field.")
        self.__signal = signal

    def process(self):
        """Compute the ECMA 418-2 tonality.

        This method calls the appropriate DPF Sound operator.
        """
        if self.signal == None:
            raise PyAnsysSoundException(
                f"No input signal defined. Use ``{__class__.__name__}.signal``."
            )

        # Connect the operator input(s).
        self.__operator.connect(0, self.signal)

        # Run the operator.
        self.__operator.run()

        # Store the operator outputs in a tuple.
        self._output = (
            self.__operator.get_output(0, types.double),
            self.__operator.get_output(1, types.field),
            self.__operator.get_output(2, types.field),
        )

    def get_output(self) -> tuple[float, Field, Field]:
        """Get the ECMA 418-2 tonality data, in a tuple containing data of various types.

        Returns
        -------
        tuple
            -   First element (float): ECMA 418-2 tonality, in tuHMS.

            -   Second element (Field): ECMA 418-2 tonality over time, in tuHMS.

            -   Third element (Field): ECMA 418-2 tone frequency over time, in Hz.
        """
        if self._output == None:
            warnings.warn(
                PyAnsysSoundWarning(
                    f"Output is not processed yet. "
                    f"Use the ``{__class__.__name__}.process()`` method."
                )
            )

        return self._output

    def get_output_as_nparray(self) -> tuple[float, np.ndarray, np.ndarray]:
        """Get the ECMA 418-2 tonality data, in a tuple of NumPy arrays.

        Returns
        -------
        tuple[numpy.ndarray]
            -   First element: ECMA 418-2 tonality, in tuHMS.

            -   Second element: ECMA 418-2 tonality over time, in tuHMS.

            -   Third element: ECMA 418-2 tone frequency over time, in Hz.

            -   Fourth element: associated time scale for tonality, in s.

            -   Fifth element: associated time scale for tone frequency, in s.
        """
        output = self.get_output()

        if output == None:
            return (
                np.nan,
                np.array([]),
                np.array([]),
                np.array([]),
                np.array([]),
            )

        return (
            np.array(output[0]),
            np.array(output[1].data),
            np.array(output[2].data),
            np.array(output[1].time_freq_support.time_frequencies.data),
            np.array(output[2].time_freq_support.time_frequencies.data),
        )

    def get_tonality(self) -> float:
        """Get the ECMA 418-2 tonality, in tuHMS.

        Returns
        -------
        float
            ECMA 418-2 tonality, in tuHMS.
        """
        return self.get_output_as_nparray()[0]

    def get_tonality_over_time(self) -> np.ndarray:
        """Get the ECMA 418-2 tonality over time, in tuHMS.

        Returns
        -------
        numpy.ndarray
            ECMA 418-2 tonality over time, in tuHMS.
        """
        return self.get_output_as_nparray()[1]

    def get_tone_frequency_over_time(self) -> np.ndarray:
        """Get the ECMA 418-2 tone frequency over time, in Hz.

        Returns
        -------
        numpy.ndarray
            ECMA 418-2 tone frequency over time, in Hz.
        """
        return self.get_output_as_nparray()[2]

    def get_tonality_time_scale(self) -> np.ndarray:
        """Get the ECMA 418-2 tonality time scale, in s.

        Returns
        -------
        numpy.ndarray
            Time array, in seconds, of the ECMA 418-2 tonality over time.
        """
        return self.get_output_as_nparray()[3]

    def get_tone_frequency_time_scale(self) -> np.ndarray:
        """Get the ECMA 418-2 tone frequency time scale, in s.

        Returns
        -------
        numpy.ndarray
            Time array, in seconds, of the ECMA 418-2 tone frequency over time.
        """
        return self.get_output_as_nparray()[4]

    def plot(self):
        """Plot the ECMA 418-2's tonality and tone frequency over time.

        This method displays the tonality in dB and the tone frequency in Hz, over time.
        """
        if self._output == None:
            raise PyAnsysSoundException(
                f"Output is not processed yet. Use the ``{__class__.__name__}.process()`` method."
            )

        # Get data to plot
        tonality_over_time = self.get_tonality_over_time()
        ft_over_time = self.get_tone_frequency_over_time()
        time_scale_tonality = self.get_tonality_time_scale()
        time_scale_ft = self.get_tone_frequency_time_scale()
        tonality_unit = self.get_output()[1].unit
        time_unit = self.get_output()[1].time_freq_support.time_frequencies.unit
        frequency_unit = self.get_output()[2].unit

        # Plot ECMA 418-2 parameters over time.
        _, axes = plt.subplots(2, 1, sharex=True)
        axes[0].plot(time_scale_tonality, tonality_over_time)
        axes[0].set_title("ECMA418-2 psychoacoustic tonality")
        axes[0].set_ylabel(f"T ({tonality_unit})")
        axes[0].grid(True)

        axes[1].plot(time_scale_ft, ft_over_time)
        axes[1].set_title("ECMA418-2 tone frequency")
        axes[1].set_ylabel(r"$\mathregular{f_{ton}}$" + f" ({frequency_unit})")
        axes[1].grid(True)
        axes[1].set_xlabel(f"Time ({time_unit})")

        plt.tight_layout()
        plt.show()
