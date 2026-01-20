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

"""Computes roughness for stationary sounds."""

import warnings

from ansys.dpf.core import Field, Operator, types
import matplotlib.pyplot as plt
import numpy as np

from . import PsychoacousticsParent
from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning

# Name of the DPF Sound operator used in this module.
ID_COMPUTE_ROUGHNESS = "compute_roughness"


class Roughness(PsychoacousticsParent):
    """Computes the roughness and the roughness over time of a sound.

    Reference: Daniel and Weber, "Psychoacoustical roughness: implementation of an
    optimized model." Acta Acustica united with Acustica, 83, pp. 113-123 (1997).

    .. seealso::
        :class:`FluctuationStrength`

    Examples
    --------
    Compute the roughness of a signal, and display the specific roughness and roughness over time.

    >>> from ansys.sound.core.psychoacoustics import Roughness
    >>> roughness = Roughness(signal=my_signal)
    >>> roughness.process()
    >>> roughness_value = roughness.get_roughness()
    >>> roughness.plot()

    .. seealso::
        :ref:`calculate_psychoacoustic_indicators`
            Example demonstrating how to compute various psychoacoustic indicators.
    """

    def __init__(self, signal: Field = None):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        signal : Field, default: None
            Signal in Pa on which to compute roughness.
        """
        super().__init__()
        self.signal = signal
        self.__operator = Operator(ID_COMPUTE_ROUGHNESS)

    def __str__(self):
        """Return the string representation of the object."""
        if self._output is None:
            str_roughness = "Not processed"
        else:
            str_roughness = f"{self.get_roughness():.2f} aspers"

        str_name = f'"{self.signal.name}"' if self.signal is not None else "Not set"

        return (
            f"{__class__.__name__} object\n"
            "Data:\n"
            f"\tSignal name: {str_name}\n"
            f"Overall roughness: {str_roughness}"
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

    def process(self):
        """Compute the roughness.

        This method calls the appropriate DPF Sound operator to compute the roughness of the signal.
        """
        if self.signal == None:
            raise PyAnsysSoundException(
                "No signal found for roughness computation. Use `Roughness.signal`."
            )

        self.__operator.connect(0, self.signal)

        # Runs the operator
        self.__operator.run()

        # Stores outputs in the tuple variable
        self._output = (
            self.__operator.get_output(0, types.double),
            self.__operator.get_output(1, types.field),
            self.__operator.get_output(2, types.field),
        )

    def get_output(self) -> tuple:
        """Get roughness data.

        Returns
        -------
        tuple
            -   First element (float): overall roughness in asper.

            -   Second element (Field): specific roughness, that is, the roughness in each
                Bark band, in asper/Bark.

            -   Third element (Field): roughness over time, in asper.
        """
        if self._output == None:
            warnings.warn(
                PyAnsysSoundWarning(
                    "Output is not processed yet. Use the `Roughness.process()` method."
                )
            )

        return self._output

    def get_output_as_nparray(self) -> tuple[np.ndarray]:
        """Get roughness data in a tuple of NumPy arrays.

        Returns
        -------
        tuple[numpy.ndarray]
            -   First element: overall roughness in asper.

            -   Second element: specific roughness, that is, the roughness in each Bark band,
                in asper/Bark.

            -   Third element: Bark band indexes at which the specific roughness is defined,
                in Bark.

            -   Fourth element: roughness over time, in asper.

            -   Fifth element: time scale of the roughness over time, in s.
        """
        output = self.get_output()

        if output == None:
            return np.nan, np.array([]), np.array([]), np.array([]), np.array([])

        return (
            np.array(output[0]),
            np.array(output[1].data),
            np.array(output[1].time_freq_support.time_frequencies.data),
            np.array(output[2].data),
            np.array(output[2].time_freq_support.time_frequencies.data),
        )

    def get_roughness(self) -> float:
        """Get the overall roughness in asper.

        Returns
        -------
        float
            Roughness value in asper.
        """
        return float(self.get_output_as_nparray()[0])

    def get_specific_roughness(self) -> np.ndarray:
        """Get the specific roughness in asper/Bark.

        Returns
        -------
        numpy.ndarray
            Specific roughness, that is, the roughness in each Bark band, in asper/Bark.
        """
        return self.get_output_as_nparray()[1]

    def get_bark_band_indexes(self) -> np.ndarray:
        """Get Bark band indexes.

        This method gets the Bark band indexes used for the roughness calculation as a NumPy array.

        Returns
        -------
        numpy.ndarray
            Array of Bark band indexes.
        """
        return self.get_output_as_nparray()[2]

    def get_bark_band_frequencies(self) -> np.ndarray:
        """Get Bark band frequencies.

        This method gets the frequencies corresponding to Bark band indexes as a NumPy array.

        Reference:
        Traunmüller, Hartmut. "Analytical Expressions for the Tonotopic Sensory Scale." Journal of
        the Acoustical Society of America. Vol. 88, Issue 1, 1990, pp. 97–100.

        Returns
        -------
        numpy.ndarray
            Array of Bark band frequencies.
        """
        return self._convert_bark_to_hertz(self.get_bark_band_indexes())

    def get_roughness_over_time(self) -> np.ndarray:
        """Get the roughness over time in asper.

        Returns
        -------
        numpy.ndarray
            Roughness over time in asper.
        """
        return self.get_output_as_nparray()[3]

    def get_time_scale(self) -> np.ndarray:
        """Get the time scale of the roughness over time, in s.

        Returns
        -------
        numpy.ndarray
            Time scale of the roughness over time, in s.
        """
        return self.get_output_as_nparray()[4]

    def plot(self):
        """Plot the specific roughness and the roughness over time.

        This method displays the specific roughness and the roughness over time.
        """
        if self._output == None:
            raise PyAnsysSoundException(
                "Output is not processed yet. Use the `Roughness.process()` method."
            )

        bark_band_indexes = self.get_bark_band_indexes()
        specific_roughness = self.get_specific_roughness()
        roughness_over_time = self.get_roughness_over_time()
        time_scale = self.get_time_scale()
        bark_unit = self.get_output()[1].time_freq_support.time_frequencies.unit
        time_unit = self.get_output()[2].time_freq_support.time_frequencies.unit
        specific_roughness_unit = self.get_output()[1].unit
        roughness_over_time_unit = self.get_output()[2].unit

        _, axes = plt.subplots(2, 1, sharex=False)

        axes[0].plot(bark_band_indexes, specific_roughness)
        axes[0].set_title("Specific roughness")
        axes[0].set_xlabel(f"z ({bark_unit})")
        axes[0].set_ylabel(f"R' ({specific_roughness_unit})")
        axes[0].grid(True)

        axes[1].plot(time_scale, roughness_over_time)
        axes[1].set_title("Roughness over time")
        axes[1].set_xlabel(f"Time ({time_unit})")
        axes[1].set_ylabel(f"R ({roughness_over_time_unit})")
        axes[1].grid(True)

        plt.tight_layout()
        plt.show()
