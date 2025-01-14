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

ID_COMPUTE_TONALITY_ECMA_418_2 = "compute_tonality_ecma418_2"


class TonalityECMA418_2(PsychoacousticsParent):
    """Computes ECMA 418-2 tonality.

    This class is used to compute the tonality according to the ECMA 418-2 standard (Hearing Model
      of Sottek). The standard is also know as ECMA74_G.
    """

    def __init__(self, signal: Field = None):
        """Create a ``TonalityECMA418_2`` object.

        Parameters
        ----------
        signal: Field, default: None
            Signal in Pa on which to calculate the tonality, as a DPF field.

        For more information about the parameters, please refer to Ansys Sound SAS' user guide.
        """
        super().__init__()
        self.signal = signal
        self.__operator = Operator(ID_COMPUTE_TONALITY_ECMA_418_2)

    def __str__(self):
        """Return the string representation of the object."""
        return (
            f"{__class__.__name__} object.\n"
            "Data\n"
            f'Signal name: "{self.signal.name}"\n'
            f"Tonality: {self.get_tonality()} tuHMS\n"
        )

    @property
    def signal(self) -> Field:
        """Signal in Pa, as a DPF field. Default is None."""
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

    def get_output(self) -> tuple[float, Field, Field, Field]:
        """Get the ECMA 418-2 tonality data, in a tuple containing data of various types.

        Returns
        -------
        tuple
            First element (float) is the ECMA 418-2 tonality, in tuHMS.

            Second element (Field) is the ECMA 418-2 tonality over time, in tuHMS.

            Third element (Field) is the ECMA 418-2 tone frequency over time, in Hz.
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
            First element is the ECMA 418-2 tonality, in tuHMS.

            Second element is the ECMA 418-2 tonality over time, in tuHMS.

            Third element is the ECMA 418-2 tone frequency over time, in Hz.

            Fourth element is the associated time scale, in s.
        """
        output = self.get_output()

        if output == None:
            return (
                np.nan,
                np.array([]),
                np.array([]),
                np.array([]),
            )

        return (
            np.array(output[0]),
            np.array(output[1].data),
            np.array(output[2].data),
            np.array(output[1].time_freq_support.time_frequencies.data),
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

    def get_time_scale(self) -> np.ndarray:
        """Get the ECMA 418-2 time scale, in s.

        Returns
        -------
        numpy.ndarray
            Array of the computation times, in seconds, of the ECMA 418-2 parameters over time
            (tonality and tonal frequencies).
        """
        return self.get_output_as_nparray()[3]

    def plot(self):
        """Plot the ECMA 418-2's toanlity and tone frequency over time.

        This method creates a figure window that displays the tonality in dB
        and the tone frequencies in Hz over time.
        """
        if self._output == None:
            raise PyAnsysSoundException(
                f"Output is not processed yet. Use the ``{__class__.__name__}.process()`` method."
            )

        # Get data to plot
        tonality_over_time = self.get_tonality_over_time()
        ft_over_time = self.get_tone_frequency_over_time()
        time_scale = self.get_time_scale()

        # Plot DIN 45681 parameters over time.
        _, axes = plt.subplots(2, 1, sharex=True)
        axes[0].plot(time_scale, tonality_over_time)
        axes[0].set_title("ECMA418-2 psychoacoustic tonality")
        axes[0].set_ylabel(r"T $\mathregular{tu_HMS}$")
        axes[0].grid(True)

        axes[1].plot(time_scale, ft_over_time)
        axes[1].set_title("DIN45681 decisive frequency")
        axes[1].set_ylabel(r"$\mathregular{f_ton}$ (Hz)")
        axes[1].grid(True)

        plt.tight_layout()
        plt.show()
