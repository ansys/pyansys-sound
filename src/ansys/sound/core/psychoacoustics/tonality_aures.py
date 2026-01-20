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

"""Computes the tonality of the signal according to Aures model."""

import warnings

from ansys.dpf.core import Field, Operator, types
import matplotlib.pyplot as plt
import numpy as np

from . import PsychoacousticsParent
from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning

# Name of the DPF Sound operator used in this module.
ID_COMPUTE_TONALITY_AURES = "compute_tonality_aures"


class TonalityAures(PsychoacousticsParent):
    r"""Computes the tonality of the signal according to Aures model.

    .. seealso::
        :class:`TonalityDIN45681`, :class:`TonalityISOTS20065`, :class:`TonalityECMA418_2`,
        :class:`TonalityISO1996_2`, :class:`TonalityISO1996_2_OverTime`

    References
    ----------
    -   W. Aures, "Procedure for calculating the sensory pleasantness of various sounds", Acustica
        **59**\ (2), pp. 130-141, December 1985.

    -   E. Terhardt, G. Stoll, M. Seewann, "Algorithm for extraction of pitch and pitch salience
        from complex tonal signals", J. Acoust. Soc. Am. **71**\ (3), pp. 679-688, March 1982.

    Examples
    --------
    Compute and display the tonality of a signal according to the Aures model.

    >>> from ansys.sound.core.psychoacoustics import TonalityAures
    >>> tonality = TonalityAures(signal=my_signal)
    >>> tonality.process()
    >>> tonality_value = tonality.get_tonality()
    >>> tonality.plot()

    .. seealso::
        :ref:`calculate_tonality_indicators`
            Example demonstrating how to compute various psychoacoustic indicators.
    """

    def __init__(
        self,
        signal: Field = None,
        overlap: float = 90.0,
        account_for_w1: bool = False,
        w1_threshold: float = 3.0,
    ):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        signal : Field, default: None
            Signal in Pa on which to compute Aures tonality.
        overlap : float, default: 90.0
            Overlap in % between two successive windows.
        account_for_w1 : bool, default: False
            Specifies whether bandwidth weighting w1 should be taken into account or not.
        w1_threshold : float, default: 3.0
            Threshold for bandwidth weighting. Ignored when :attr:`account_for_w1` is set to
            `False`.

        For more information about the parameters, please refer to the Ansys Sound SAS user guide.
        """
        super().__init__()
        self.signal = signal
        self.overlap = overlap
        self.account_for_w1 = account_for_w1
        self.w1_threshold = w1_threshold
        self.__operator = Operator(ID_COMPUTE_TONALITY_AURES)

    def __str__(self) -> str:
        """Return the string representation of the object."""
        if self.account_for_w1:
            str_w1 = f"Yes\n\tw1 threshold: {self.w1_threshold} dB"
        else:
            str_w1 = "No"

        if self._output is None:
            str_tonality = "Not processed"
        else:
            str_tonality = f"{self.get_tonality():.2f} tu"

        str_name = f'"{self.signal.name}"' if self.signal is not None else "Not set"

        return (
            f"{__class__.__name__} object\n"
            "Data:\n"
            f"\tSignal name: {str_name}\n"
            f"\tOverlap: {self.overlap} %\n"
            f"\tAccount for w1 weighting: {str_w1}\n"
            f"Tonality: {str_tonality}"
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
    def overlap(self) -> float:
        """Overlap in % between two successive windows."""
        return self.__overlap

    @overlap.setter
    def overlap(self, overlap: float):
        """Set the overlap between two successive windows."""
        if overlap < 0.0 or overlap >= 100.0:
            raise PyAnsysSoundException(
                "Overlap must be greater than or equal to 0 %, and strictly smaller than 100 %."
            )
        self.__overlap = overlap

    @property
    def account_for_w1(self) -> bool:
        """Specifies whether bandwidth weighting w1 should be taken into account or not.

        Given the rather high line spacing (12.5 Hz), as specified in the reference paper of
        Terhardt et al, the bandwidth weighting w1 is disabled by default. If the value is set to
        `True`, then the tone bandwidth taken into account to calculate the weighting w1 is defined
        as an X-dB bandwidth around the tone frequency, where X is the value set in the
        :attr:`w1_threshold` attribute.
        """
        return self.__account_for_w1

    @account_for_w1.setter
    def account_for_w1(self, account_for_w1: bool):
        """Set the account_for_w1."""
        self.__account_for_w1 = account_for_w1

    @property
    def w1_threshold(self) -> float:
        """Threshold in dB for the bandwidth weighting w1.

        Defines the threshold value in dB for the tone bandwidth in the calculation of the
        bandwidth weighting w1, if attribute :attr:`account_for_w1` is set to `True`. In this case,
        the bandwidth is defined as an X-dB bandwidth around the tone frequency, where X is the
        value set in this attribute.
        """
        return self.__w1_threshold

    @w1_threshold.setter
    def w1_threshold(self, w1_threshold: float):
        """Set the w1_threshold."""
        if w1_threshold < 0.0:
            raise PyAnsysSoundException(
                "Threshold for the bandwidth weighting must be greater than or equal to 0 dB."
            )
        self.__w1_threshold = w1_threshold

    def process(self):
        """Compute the Aures tonality."""
        if self.signal is None:
            raise PyAnsysSoundException(f"No input signal is set. Use {__class__.__name__}.signal.")

        self.__operator.connect(0, self.signal)
        self.__operator.connect(1, float(self.overlap))
        self.__operator.connect(2, self.account_for_w1)
        self.__operator.connect(3, float(self.w1_threshold))

        # Run the operator
        self.__operator.run()

        # Stores output
        self._output = (
            self.__operator.get_output(0, types.double),
            self.__operator.get_output(1, types.field),
            self.__operator.get_output(2, types.field),
            self.__operator.get_output(3, types.field),
        )

    def get_output(self) -> tuple[float, Field, Field, Field]:
        """Get Aures' tonality data.

        Returns
        -------
        tuple[float,Field,Field,Field]
            -   First element (float): overall tonality value, in tu (tonality unit).

            -   Second element (Field): tonality over time, in tu.

            -   Third element (Field): tonal component weighting wT over time (between 0.0 and
                1.0, no unit).

            -   Fourth element (Field): relative loudness weighting wGr over time (between 0.0
                and 1.0, no unit).
        """
        if self._output == None:
            warnings.warn(
                PyAnsysSoundWarning(
                    "Output is not processed yet. "
                    f"Use the {__class__.__name__}.process() method."
                )
            )

        return self._output

    def get_output_as_nparray(self) -> tuple[np.ndarray]:
        """Get the Aures tonality data as NumPy arrays.

        Returns
        -------
        tuple[numpy.ndarray]:
            -   First element: overall tonality value, in tu (tonality unit).

            -   Second element: tonality over time, in tu.

            -   Third element: tonal component weighting wT over time (between 0.0 and
                1.0, no unit).

            -   Fourth element: relative loudness weighting wGr over time (between 0.0
                and 1.0, no unit).

            -   Fifth element: time scale, in s.
        """
        output = self.get_output()

        if output == None:
            return (
                np.array([]),
                np.array([]),
                np.array([]),
                np.array([]),
                np.array([]),
            )

        return (
            np.array([output[0]]),
            np.array(output[1].data),
            np.array(output[2].data),
            np.array(output[3].data),
            np.array(output[1].time_freq_support.time_frequencies.data),
        )

    def get_tonality(self) -> float:
        """Get the overall Aures tonality in tu.

        Returns
        -------
        float
            Overall Aures tonality, in tu (tonality unit).
        """
        output = self.get_output_as_nparray()[0]
        if len(output) > 0:
            return self.get_output_as_nparray()[0][0]
        else:
            return np.nan

    def get_tonality_over_time(self) -> np.ndarray:
        """Get the Aures tonality over time.

        Returns
        -------
        numpy.ndarray
            Aures tonality over time, in tu (tonality unit).
        """
        return self.get_output_as_nparray()[1]

    def get_tonal_weighting_over_time(self) -> np.ndarray:
        """Get the tonal component weighting wT over time.

        Returns
        -------
        numpy.ndarray
            Tonal component weighting wT over time (between 0.0 and 1.0, no unit).
        """
        return self.get_output_as_nparray()[2]

    def get_loudness_weighting_over_time(self) -> np.ndarray:
        """Get the relative loudness weighting wGr over time.

        Returns
        -------
        numpy.ndarray
            Relative loudness weighting wGr over time (between 0.0 and 1.0, no unit).
        """
        return self.get_output_as_nparray()[3]

    def get_time_scale(self) -> np.ndarray:
        """Get the time scale.

        Returns
        -------
        numpy.ndarray
            Time scale in s.
        """
        return self.get_output_as_nparray()[4]

    def plot(self):
        """Plot the tonality over time."""
        if self._output is None:
            raise PyAnsysSoundException(
                f"Output is not processed yet. Use the {__class__.__name__}.process() method."
            )

        tonality = self.get_tonality_over_time()
        wT = self.get_tonal_weighting_over_time()
        wGr = self.get_loudness_weighting_over_time()
        time_scale = self.get_time_scale()
        tonality_unit = self.get_output()[1].unit
        time_unit = self.get_output()[1].time_freq_support.time_frequencies.unit

        _, axes = plt.subplots(3, 1, sharex=True)
        axes[0].plot(time_scale, tonality)
        axes[0].set_title("Aures tonality over time")
        axes[0].set_ylabel(f"T ({tonality_unit})")
        axes[0].grid(True)

        axes[1].plot(time_scale, wT)
        axes[1].set_title("Tonal component weighting over time")
        axes[1].set_ylabel(r"$\mathregular{w_T}$")
        axes[1].grid(True)

        axes[2].plot(time_scale, wGr)
        axes[2].set_title("Relative loudness weighting over time")
        axes[2].set_xlabel(f"Time ({time_unit})")
        axes[2].set_ylabel(r"$\mathregular{w_{Gr}}$")
        axes[2].grid(True)

        plt.tight_layout()
        plt.show()
