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

"""Compute the fluctuation strength."""

import warnings

from ansys.dpf.core import Field, Operator, types
import matplotlib.pyplot as plt
import numpy as np

from . import PsychoacousticsParent
from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning

# Name of the DPF Sound operator used in this module.
ID_COMPUTE_FLUCTUATION_STRENGTH = "compute_fluctuation_strength"


class FluctuationStrength(PsychoacousticsParent):
    """Computes the fluctuation strength for a stationary sound.

    This class computes the fluctuation strength of a signal according to Sontacchi's master
    thesis work.

    Reference: "Entwicklung eines Modulkonzeptes fur die psychoakustische Gerauschanalyse under
    MATLAB". Master thesis, Technischen Universitat Graz, pp. 1-112 (1998).

    .. seealso::
        :class:`Roughness`

    Examples
    --------
    Compute the fluctuation strength of a signal, and display the specific fluctuation strength.

    >>> from ansys.sound.core.psychoacoustics import FluctuationStrength
    >>> fluctuation_strength = FluctuationStrength(signal=my_signal)
    >>> fluctuation_strength.process()
    >>> fluctuation_strength_value = fluctuation_strength.get_fluctuation_strength()
    >>> fluctuation_strength.plot()

    .. seealso::
        :ref:`calculate_psychoacoustic_indicators`
            Example demonstrating how to compute various psychoacoustic indicators.
    """

    def __init__(
        self,
        signal: Field = None,
    ):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        signal : Field, default: None
            Signal in Pa on which to compute fluctuation strength.
        """
        super().__init__()
        self.signal = signal
        self.__operator = Operator(ID_COMPUTE_FLUCTUATION_STRENGTH)

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
        """Compute the fluctuation strength.

        This method calls the corresponding DPF Sound operator to compute the fluctuation strength
        of the signal.
        """
        if self.signal == None:
            raise PyAnsysSoundException(
                "No signal found for fluctuation strength computation."
                " Use `FluctuationStrength.signal`."
            )

        self.__operator.connect(0, self.signal)

        # Runs the operator
        self.__operator.run()

        self._output = (
            self.__operator.get_output(0, types.double),
            self.__operator.get_output(1, types.field),
        )

    def get_output(self) -> tuple:
        """Get fluctuation strength and specific fluctuation strength.

        Returns
        -------
        tuple
            -   First element (float): fluctuation strength in vacil.

            -   Second element (Field): specific fluctuation strength, that is, the fluctuation
                strength in each Bark band, in vacil.
        """
        if self._output == None:
            warnings.warn(
                PyAnsysSoundWarning(
                    "Output is not processed yet. Use the `FluctuationStrength.process()` method."
                )
            )

        return self._output

    def get_output_as_nparray(self) -> tuple[np.ndarray]:
        """Get fluctuation strength data in a tuple of NumPy arrays.

        Returns
        -------
        tuple[numpy.ndarray]
            -   First element: fluctuation strength in vacil.

            -   Second element: specific fluctuation strength, that is, the fluctuation strength in
                each Bark band, in vacil.

            -   Third element: Bark band indexes at which the specific fluctuation strength is
                defined, in Bark.
        """
        output = self.get_output()

        if output is None:
            return (np.nan, np.array([]), np.array([]))

        return (
            np.array(output[0]),
            np.array(output[1].data),
            np.array(output[1].time_freq_support.time_frequencies.data),
        )

    def get_fluctuation_strength(self) -> float:
        """Get fluctuation strength in vacil.

        Returns
        -------
        float
            Fluctuation strength in vacil.
        """
        return self.get_output_as_nparray()[0]

    def get_specific_fluctuation_strength(self) -> np.ndarray:
        """Get the specific fluctuation strength.

        Returns
        -------
        numpy.ndarray
            Specific fluctuation strength, that is, the fluctuation strength in each Bark band, in
            vacil.
        """
        return self.get_output_as_nparray()[1]

    def get_bark_band_indexes(self) -> np.ndarray:
        """Get the Bark band indexes.

        This method returns the Bark band indexes used for the fluctuation strength calculation as
        a NumPy array.

        Returns
        -------
        numpy.ndarray
            Array of Bark band indexes, in Bark.
        """
        return self.get_output_as_nparray()[2]

    def get_bark_band_frequencies(self) -> np.ndarray:
        """Get Bark band frequencies.

        This method returns the frequencies corresponding to the Bark band indexes, as a NumPy
        array.

        Reference: Traunmüller, Hartmut. "Analytical Expressions for the Tonotopic Sensory Scale."
        Journal of the Acoustical Society of America. Vol. 88, Issue 1, 1990, pp. 97-100.

        Returns
        -------
        numpy.ndarray
            Array of Bark band frequencies, in Hz.
        """
        return self._convert_bark_to_hertz(self.get_bark_band_indexes())

    def plot(self):
        """Plot the specific fluctuation strength.

        This method displays the specific fluctuation strength, in vacil, as a function of the Bark
        band index.
        """
        if self._output == None:
            raise PyAnsysSoundException(
                "Output is not processed yet. Use the `FluctuationStrength.process()` method."
            )

        bark_band_indexes = self.get_bark_band_indexes()
        specific_fluctuation_strength = self.get_output_as_nparray()[1]
        unit = self.get_output()[1].unit

        plt.plot(bark_band_indexes, specific_fluctuation_strength)
        plt.title("Specific fluctuation strength")
        plt.xlabel(f"Bark band index")
        plt.ylabel(f"Fluctuation strength ({unit})")
        plt.grid(True)
        plt.show()
