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

"""Computes ISO 532-1 loudness for time-varying sounds."""

import warnings

from ansys.dpf.core import Field, Operator, types
import matplotlib.pyplot as plt
import numpy as np

from . import FIELD_DIFFUSE, FIELD_FREE, PsychoacousticsParent
from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning

# Name of the DPF Sound operator used in this module.
ID_COMPUTE_LOUDNESS_ISO_TIME_VARYING = "compute_loudness_iso532_1_vs_time"


class LoudnessISO532_1_TimeVarying(PsychoacousticsParent):
    """Computes ISO 532-1:2017 loudness for time-varying sounds.

    This class computes the loudness of a signal according to the ISO 532-1:2017 standard,
    corresponding to the "Zwicker method", for time-varying sounds.

    .. seealso::
        :class:`LoudnessISO532_1_Stationary`

    Examples
    --------
    Compute the percentile loudness of a time-varying signal in free field, and display its
    loudness over time.

    >>> from ansys.sound.core.psychoacoustics import LoudnessISO532_1_TimeVarying
    >>> loudness = LoudnessISO532_1_TimeVarying(signal=my_signal, field_type="Free")
    >>> loudness.process()
    >>> N5 = loudness.get_N5_sone()
    >>> N10 = loudness.get_N10_sone()
    >>> L5 = loudness.get_L5_phon()
    >>> L10 = loudness.get_L10_phon()
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
            Signal in Pa on which to compute time-varying ISO532-1 loudness.
        field_type : str, default: "Free"
            Sound field type. Available options are `"Free"` and `"Diffuse"`.
        """
        super().__init__()
        self.signal = signal
        self.field_type = field_type
        self.__operator = Operator(ID_COMPUTE_LOUDNESS_ISO_TIME_VARYING)

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
        """Compute the time-varying ISO532-1 loudness.

        This method calls the appropriate DPF Sound operator to compute the loudness of the signal.
        """
        if self.__signal == None:
            raise PyAnsysSoundException(
                "No signal found for loudness versus time computation. "
                "Use `LoudnessISO532_1_TimeVarying.signal`."
            )

        self.__operator.connect(0, self.signal)
        self.__operator.connect(1, self.field_type)

        # Runs the operator
        self.__operator.run()

        # Stores outputs in the tuple variable
        self._output = (
            self.__operator.get_output(0, types.field),
            self.__operator.get_output(1, types.double),
            self.__operator.get_output(2, types.double),
            self.__operator.get_output(3, types.field),
            self.__operator.get_output(4, types.double),
            self.__operator.get_output(5, types.double),
        )

    def get_output(self) -> tuple:
        """Get time-varying loudness data.

        Returns
        -------
        tuple
            -   First element (Field): instantaneous loudness in sone.

            -   Second element (float): N5 indicator in sone. N5 is the loudness that is exceeded
                during a cumulated 5 % of the signal duration.

            -   Third element (float): the N10 indicator in sone. N10 is the loudness that is
                exceeded during a cumulated 10 % of the signal duration.

            -   Fourth element (Field): instantaneous loudness level in phon.

            -   Fifth element (float): L5 indicator in phon. L5 is the loudness level that is
                exceeded during a cumulated 5 % of the signal duration.

            -   Sixth element (float): L10 indicator in phon. L10 is the loudness level that is
                exceeded during a cumulated 10 % of the signal duration.
        """
        if self._output == None:
            warnings.warn(
                PyAnsysSoundWarning(
                    "Output is not processed yet. Use the "
                    "`LoudnessISO532_1_TimeVarying.process()` method."
                )
            )

        return self._output

    def get_output_as_nparray(self) -> tuple[np.ndarray]:
        """Get time-varying loudness data in a tuple of NumPy arrays.

        Returns
        -------
        tuple[numpy.ndarray]
            -   First element: instantaneous loudness in sone.

            -   Second element: N5 percentile loudness in sone. N5 is the loudness that is exceeded
                during a cumulated 5 % of the signal duration.

            -   Third element: N10 percentile loudness in sone. N10 is the loudness that is
                exceeded during a cumulated 10 % of the signal duration.

            -   Fourth element: instantaneous loudness level in phon.

            -   Fifth element: L5 percentile loudness level in phon. L5 is the loudness level that
                is exceeded during a cumulated 5 % of the signal duration.

            -   Sixth element: L10 percentile loudness level in phon. L10 is the loudness level
                that is exceeded during a cumulated 10 % of the signal duration.

            -   Seventh element: time vector of the instantaneous loudness and loudness level, in
                seconds.
        """
        output = self.get_output()

        if output == None:
            return np.array([]), np.nan, np.nan, np.array([]), np.nan, np.nan, np.array([])

        return (
            np.array(output[0].data),
            np.array(output[1]),
            np.array(output[2]),
            np.array(output[3].data),
            np.array(output[4]),
            np.array(output[5]),
            np.array(output[0].time_freq_support.time_frequencies.data),
        )

    def get_loudness_sone_vs_time(self) -> np.ndarray:
        """Get the instantaneous loudness in sone.

        Returns
        -------
        numpy.ndarray
            Instantaneous loudness in sone.
        """
        return self.get_output_as_nparray()[0]

    def get_Nmax_sone(self) -> float:
        """Get the maximum instantaneous loudness in sone.

        Returns
        -------
        float
            Maximum loudness in sone.
        """
        return np.max(self.get_loudness_sone_vs_time())

    def get_N5_sone(self) -> float:
        """Get the N5 percentile loudness.

        N5 is the loudness that is exceeded during a cumulated 5 % of the signal duration.

        Returns
        -------
        float
            N5 percentile loudness in sone.
        """
        return self.get_output_as_nparray()[1]

    def get_N10_sone(self) -> float:
        """Get the N10 percentile loudness.

        N10 is the loudness that is exceeded during a cumulated 10 % of the signal duration.

        Returns
        -------
        float
            N10 percentile loudness in sone.
        """
        return self.get_output_as_nparray()[2]

    def get_loudness_level_phon_vs_time(self) -> np.ndarray:
        """Get the instantaneous loudness level in phon.

        Returns
        -------
        numpy.ndarray
            Instantaneous loudness level in phon.
        """
        return self.get_output_as_nparray()[3]

    def get_Lmax_phon(self) -> float:
        """Get the maximum instantaneous loudness level in phon.

        Returns
        -------
        float
            Maximum loudness level in phon.
        """
        return np.max(self.get_loudness_level_phon_vs_time())

    def get_L5_phon(self) -> float:
        """Get the L5 percentile loudness level.

        L5 is the loudness level that is exceeded during a cumulated 5 % of the signal duration.

        Returns
        -------
        float
            L5 percentile loudness level in phon.
        """
        return self.get_output_as_nparray()[4]

    def get_L10_phon(self) -> float:
        """Get the L10 percentile loudness level.

        L10 is the loudness level that is exceeded during a cumulated 10 % of the signal duration.

        Returns
        -------
        float
            L10 percentile loudness level in phon.
        """
        return self.get_output_as_nparray()[5]

    def get_time_scale(self) -> np.ndarray:
        """Get the time scale of the instantaneous loudness and loudness level.

        Returns
        -------
        numpy.ndarray
            Array of the time steps of the instantaneous loudness and loudness level, in seconds.
        """
        return self.get_output_as_nparray()[6]

    def plot(self):
        """Plot the instantaneous loudness, in sone, and loudness level, in phon.

        This method displays the instantaneous loudness (N), in sone, and instantaneous loudness
        level (L_N), in phon.
        """
        if self.get_output() == None:
            raise PyAnsysSoundException(
                "Output is not processed yet. Use the "
                "`LoudnessISO532_1_TimeVarying.process()` method."
            )

        time = self.get_time_scale()

        _, (ax1, ax2) = plt.subplots(2, 1, sharex=True)

        # Plot loudness in sone
        unit = self.get_output()[0].unit
        ax1.plot(time, self.get_loudness_sone_vs_time())
        ax1.set_title("Instantaneous loudness")
        ax1.set_ylabel(f"N ({unit})")
        ax1.grid(True)

        # Plot loudness level in phon
        unit = self.get_output()[3].unit
        ax2.plot(time, self.get_loudness_level_phon_vs_time())
        ax2.set_title("Instantaneous loudness level")
        ax2.set_xlabel("Time (s)")
        ax2.set_ylabel(r"$\mathregular{L_N}$" + f" ({unit})")
        ax2.grid(True)

        plt.show()
