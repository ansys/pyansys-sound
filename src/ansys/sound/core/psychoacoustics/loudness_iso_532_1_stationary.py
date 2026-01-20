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

"""Computes ISO 532-1 loudness for stationary sounds."""

import warnings

from ansys.dpf.core import Field, Operator, types
import matplotlib.pyplot as plt
import numpy as np

from . import FIELD_DIFFUSE, FIELD_FREE, PsychoacousticsParent
from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning

# Name of the DPF Sound operator used in this module.
ID_COMPUTE_LOUDNESS_ISO_STATIONARY = "compute_loudness_iso532_1"


class LoudnessISO532_1_Stationary(PsychoacousticsParent):
    """Computes ISO 532-1:2017 loudness for stationary sounds.

    This class computes the loudness of a signal according to the ISO 532-1:2017 standard,
    corresponding to the "Zwicker method", for stationary sounds.

    .. seealso::
        :class:`LoudnessISO532_1_TimeVarying`, :class:`LoudnessISO532_2`

    Examples
    --------
    Compute the loudness of a signal in free field, and display its specific loudness.

    >>> from ansys.sound.core.psychoacoustics import LoudnessISO532_1_Stationary
    >>> loudness = LoudnessISO532_1_Stationary(signal=my_signal, field_type="Free")
    >>> loudness.process()
    >>> loudness_value = loudness.get_loudness_sone()
    >>> loudness_level_value = loudness.get_loudness_level_phon()
    >>> loudness.plot()

    .. seealso::
        :ref:`calculate_psychoacoustic_indicators`
            Example demonstrating how to compute various psychoacoustic indicators.
    """

    def __init__(
        self,
        signal: Field = None,
        field_type: str = FIELD_FREE,
    ):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        signal : Field, default: None
            Signal in Pa on which to compute loudness.
        field_type : str, default: "Free"
            Sound field type. Available options are `"Free"` and `"Diffuse"`.
        """
        super().__init__()
        self.signal = signal
        self.field_type = field_type
        self.__operator = Operator(ID_COMPUTE_LOUDNESS_ISO_STATIONARY)

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
            raise PyAnsysSoundException(
                "No signal found for loudness computation. "
                "Use `LoudnessISO532_1_Stationary.signal`."
            )

        self.__operator.connect(0, self.signal)
        self.__operator.connect(1, self.field_type)

        # Runs the operator
        self.__operator.run()

        self._output = (
            self.__operator.get_output(0, types.double),
            self.__operator.get_output(1, types.double),
            self.__operator.get_output(2, types.field),
        )

    def get_output(self) -> tuple:
        """Get loudness, loudness level, specific loudness.

        Returns
        -------
        tuple
            -   First element (float): loudness in sone.

            -   Second element (float): loudness level in phon.

            -   Third element (Field): specific loudness in sone/Bark, as a function of the Bark
                band index.
        """
        if self._output == None:
            warnings.warn(
                PyAnsysSoundWarning(
                    "Output is not processed yet. Use the "
                    "`LoudnessISO532_1_Stationary.process()` method."
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

            -   Third element: specific loudness in sone/Bark, as a function of the Bark band index.

            -   Fourth element: Bark band indexes, in Bark.
        """
        output = self.get_output()

        if output == None:
            return np.nan, np.nan, np.array([]), np.array([])

        return (
            np.array(output[0]),
            np.array(output[1]),
            np.array(output[2].data),
            np.array(output[2].time_freq_support.time_frequencies.data),
        )

    def get_loudness_sone(self) -> float:
        """Get the loudness in sone.

        Returns
        -------
        float
            Loudness in sone.
        """
        return self.get_output_as_nparray()[0]

    def get_loudness_level_phon(self) -> float:
        """Get the loudness level in phon.

        Returns
        -------
        float
            Loudness level in phon.
        """
        return self.get_output_as_nparray()[1]

    def get_specific_loudness(self) -> np.ndarray:
        """Get the specific loudness.

        Returns
        -------
        numpy.ndarray
            Specific loudness array in sone/Bark, as a function of the Bark band index.
        """
        return self.get_output_as_nparray()[2]

    def get_bark_band_indexes(self) -> np.ndarray:
        """Get Bark band indexes.

        This method returns the Bark band indexes used for the loudness calculation as a NumPy
        array.

        Returns
        -------
        numpy.ndarray
            Array of Bark band indexes, in Bark.
        """
        return self.get_output_as_nparray()[3]

    def get_bark_band_frequencies(self) -> np.ndarray:
        """Get Bark band frequencies.

        This method returns the frequencies corresponding to the Bark band indexes as a NumPy array.

        Reference:
        Traunmüller, Hartmut. "Analytical Expressions for the Tonotopic Sensory Scale." Journal of
        the Acoustical Society of America. Vol. 88, Issue 1, 1990, pp. 97–100.

        Returns
        -------
        numpy.ndarray
            Array of Bark band frequencies in Hz.
        """
        return self._convert_bark_to_hertz(self.get_bark_band_indexes())

    def plot(self):
        """Plot the specific loudness.

        This method displays the specific loudness in sone/Bark as a function of the Bark band
        index.
        """
        if self._output == None:
            raise PyAnsysSoundException(
                "Output is not processed yet. Use the "
                "`LoudnessISO532_1_Stationary.process()` method."
            )

        bark_band_indexes = self.get_bark_band_indexes()
        specific_loudness = self.get_specific_loudness()
        unit = self.get_output()[2].unit

        plt.plot(bark_band_indexes, specific_loudness)
        plt.title("Specific loudness")
        plt.xlabel("Bark band index")
        plt.ylabel(f"N' ({unit})")
        plt.grid(True)
        plt.show()
