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

"""Compute the level over time."""

import warnings

from ansys.dpf.core import Field, Operator, types
import matplotlib.pyplot as plt
import numpy as np

from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ._standard_levels_parent import DICT_FREQUENCY_WEIGHTING, DICT_SCALE, StandardLevelsParent

DICT_TIME_WEIGHTING = {"Fast": 1, "Slow": 0, "Impulse": 2, "Custom": 3}
DICT_ANALYSIS_WINDOW = {
    "RECTANGULAR": 0,
    "HANN": 1,
    "HAMMING": 2,
    "BLACKMAN": 3,
    "BLACKMAN-HARRIS": 4,
    "BARTLETT": 5,
}

ID_COMPUTE_LEVEL_OVER_TIME = "compute_level_over_time"


class LevelOverTime(StandardLevelsParent):
    """Compute the level over time.

    This class computes the level over time of a signal.

    .. seealso::
        :class:`OverallLevel`

    Examples
    --------
    Compute and display the SPL over time of an acoustic signal.

    >>> from ansys.sound.core.standard_levels import LevelOverTime
    >>> level_over_time = LevelOverTime(signal=signal, reference_value=2e-5, scale="dB")
    >>> level_over_time.process()
    >>> level_max = level_over_time.get_level_max()
    >>> instantaneous_level = level_over_time.get_level_over_time()
    >>> level_over_time.plot()

    .. seealso::
        :ref:`calculate_levels`
            Example demonstrating how to calculate standard levels.
    """

    def __init__(
        self,
        signal: Field = None,
        scale: str = "dB",
        reference_value: float = 1.0,
        frequency_weighting: str = "",
        time_weighting: str = "Fast",
    ):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        signal : Field, default: None
            The signal to process.
        scale : str, default: "dB"
            The scale type of the output level. Available options are `"dB"` and `"RMS"`.
        reference_value : float, default: 1.0
            The reference value for the level computation. If the overall level is computed with a
            signal in Pa, the reference value should be 2e-5 (Pa).
        frequency_weighting : str, default: ""
            The frequency weighting to apply to the signal before computing the level. Available
            options are `""`, `"A"`, `"B"`,  and `"C"`, to get level in dB (or dBSPL), dBA, dBB,
            and dBC, respectively. Note that the frequency weighting is only applied if the
            attribute :attr:`scale` is set to `"dB"`.
        time_weighting : str, default: "Fast"
            The time weighting to use when computing the level over time. Available options are
            `"Fast"`, `"Slow"`, `"Impulse"`, and `"Custom"`. When `"Custom"` is selected, the user
            can provide custom parameters using the method :meth:`set_custom_parameters()`.
        """
        super().__init__()
        self.signal = signal
        self.scale = scale
        self.reference_value = reference_value
        self.frequency_weighting = frequency_weighting
        self.time_weighting = time_weighting
        self.__time_step = 25.0
        self.__window_size = 1000.0
        self.__analysis_window = "RECTANGULAR"
        self.__operator = Operator(ID_COMPUTE_LEVEL_OVER_TIME)

    def __str__(self) -> str:
        """Return the string representation of the object."""
        str_custom_param = ""
        if self.time_weighting == "Custom":
            str_custom_param = (
                f"\tTime step: {self.__time_step} ms\n"
                f"\tWindow size: {self.__window_size} ms\n"
                f"\tAnalysis window: {self.__analysis_window}\n"
            )

        str_name = f'"{self.signal.name}"' if self.signal is not None else "Not set"
        str_frequency_weighting = (
            self.frequency_weighting if len(self.frequency_weighting) > 0 else "None"
        )
        if self._output is not None:
            max_level = self.get_level_max()
            unit = self.get_output()[1].unit
            str_level = f"{max_level:.1f} {unit}"
        else:
            str_level = "Not processed"

        return (
            f"{__class__.__name__} object.\n"
            "Data\n"
            f"\tSignal: {str_name}\n"
            f"\tScale type: {self.scale}\n"
            f"\tReference value: {self.reference_value}\n"
            f"\tFrequency weighting: {str_frequency_weighting}\n"
            f"\tTime weighting: {self.time_weighting}\n{str_custom_param}"
            f"Maximum level: {str_level}"
        )

    @property
    def signal(self) -> Field:
        """Input signal."""
        return self.__signal

    @signal.setter
    def signal(self, signal: Field):
        """Set the signal."""
        if signal is not None:
            if not isinstance(signal, Field):
                raise PyAnsysSoundException("The signal must be provided as a DPF field.")
        self.__signal = signal

    @property
    def scale(self) -> str:
        """Scale type of the output level.

        Specifies whether the output level shall be provided on a decibel (`"dB"`) or linear
        (`"RMS"`) scale.
        """
        return self.__scale

    @scale.setter
    def scale(self, scale: str):
        """Set the scale type."""
        if scale not in DICT_SCALE.keys():
            raise PyAnsysSoundException("The scale type must be either 'dB' or 'RMS'.")
        self.__scale = scale

    @property
    def reference_value(self) -> float:
        """Reference value for the level computation.

        If the overall level is computed with a sound pressure signal in Pa, the reference value
        should be 2e-5 (Pa).
        """
        return self.__reference_value

    @reference_value.setter
    def reference_value(self, value: float):
        """Set the reference value."""
        if value <= 0:
            raise PyAnsysSoundException("The reference value must be strictly positive.")
        self.__reference_value = value

    @property
    def frequency_weighting(self) -> str:
        """Frequency weighting of the computed level.

        Available options are `""`, `"A"`, `"B"`, and `"C"`. If attribute :attr:`reference_value`
        is 2e-5 Pa, these options allow level calculation in dBSPL, dBA, dBB, and dBC, respectively.
        Note that the frequency weighting is only applied if the attribute :attr:`scale` is set to
        `"dB"`.
        """
        return self.__frequency_weighting

    @frequency_weighting.setter
    def frequency_weighting(self, weighting: str):
        """Set the frequency weighting."""
        if weighting not in DICT_FREQUENCY_WEIGHTING.keys():
            raise PyAnsysSoundException(
                f"The frequency weighting must be one of {list(DICT_FREQUENCY_WEIGHTING.keys())}."
            )
        self.__frequency_weighting = weighting

    @property
    def time_weighting(self) -> str:
        """Time weighting of the computed level.

        Available options are `"Fast"`, `"Slow"`, `"Impulse"`, and `"Custom"`. When `"Custom"` is
        selected, the user can provide custom parameters using the method
        :meth:`set_custom_parameters()`.
        """
        return self.__time_weighting

    @time_weighting.setter
    def time_weighting(self, weighting: str):
        """Set the time weighting."""
        if weighting not in DICT_TIME_WEIGHTING.keys():
            raise PyAnsysSoundException(
                f"The time weighting must be one of {list(DICT_TIME_WEIGHTING.keys())}."
            )
        self.__time_weighting = weighting

    def set_custom_parameters(
        self,
        time_step: float = 25.0,
        window_size: float = 1000.0,
        analysis_window: str = "RECTANGULAR",
    ):
        """Set the custom parameters for the time weighting.

        Note that using this method automatically switches attribute :attr:`time_weighting` to
        `"Custom"`.

        Parameters
        ----------
        time_step : float, default: 25.0
            The time step in ms.
        window_size : float, default: 1000.0
            The window size in ms.
        analysis_window : str, default: "RECTANGULAR"
            The analysis window to use. Available options are `"RECTANGULAR"`, `"HANN"`,
            `"HAMMING"`, `"BLACKMAN"`, `"BLACKMAN-HARRIS"`, and `"BARTLETT"`.
        """
        if time_step <= 0:
            raise PyAnsysSoundException("The time step must be strictly positive.")

        if window_size <= 0:
            raise PyAnsysSoundException("The window size must be strictly positive.")

        if analysis_window.upper() not in DICT_ANALYSIS_WINDOW.keys():
            raise PyAnsysSoundException(
                f"The analysis window must be one of {list(DICT_ANALYSIS_WINDOW.keys())}."
            )

        # Automatically switch to custom time weighting.
        self.time_weighting = "Custom"

        self.__time_step = time_step
        self.__window_size = window_size
        self.__analysis_window = analysis_window.upper()

    def process(self):
        """Compute the overall level."""
        if self.signal is None:
            raise PyAnsysSoundException(f"No input signal is set. Use {__class__.__name__}.signal.")

        self.__operator.connect(0, self.signal)
        self.__operator.connect(1, DICT_SCALE[self.scale])
        self.__operator.connect(2, float(self.reference_value))
        self.__operator.connect(3, DICT_FREQUENCY_WEIGHTING[self.frequency_weighting])
        self.__operator.connect(4, DICT_TIME_WEIGHTING[self.time_weighting])
        self.__operator.connect(5, self.__time_step / 1000.0)
        self.__operator.connect(6, self.__window_size / 1000.0)
        self.__operator.connect(7, self.__analysis_window)

        self.__operator.run()

        self._output = (
            self.__operator.get_output(0, types.double),
            self.__operator.get_output(1, types.field),
        )

    def get_output(self) -> tuple:
        """Return the maximum level and level over time.

        Returns
        -------
        tuple
            First element (:class:`float`): maximum level.

            Second element (:class:`Field <ansys.dpf.core.field.Field>`): level over time.
        """
        if self._output is None:
            warnings.warn(
                PyAnsysSoundWarning(
                    f"Output is not processed yet. "
                    f"Use the {__class__.__name__}.process() method."
                )
            )

        return self._output

    def get_output_as_nparray(self) -> tuple[np.ndarray]:
        """Return the maximum level, level over time, and time scale.

        Returns
        -------
        numpy.ndarray
            First element: maximum level.

            Second element: level over time.

            Third element: time scale in s.
        """
        output = self.get_output()

        if output is None:
            return (np.nan, np.array([]), np.array([]))

        return (
            np.array(output[0]),
            np.array(output[1].data),
            np.array(output[1].time_freq_support.time_frequencies.data),
        )

    def get_level_max(self) -> float:
        """Return the maximum level.

        Returns
        -------
        float
            The maximum level value over time.
        """
        output = self.get_output()
        return output[0] if output is not None else None

    def get_level_over_time(self) -> np.ndarray:
        """Return the level over time.

        Returns
        -------
        numpy.ndarray
            The level over time.
        """
        return self.get_output_as_nparray()[1]

    def get_time_scale(self) -> np.ndarray:
        """Return the time scale.

        Returns
        -------
        numpy.ndarray
            The time scale in s.
        """
        return self.get_output_as_nparray()[2]

    def plot(self):
        """Plot the level over time."""
        if self._output is None:
            raise PyAnsysSoundException(
                f"Output is not processed yet. Use the {__class__.__name__}.process() method."
            )

        level_over_time = self.get_level_over_time()
        time_scale = self.get_time_scale()
        unit = self.get_output()[1].unit
        time_unit = self.get_output()[1].time_freq_support.time_frequencies.unit

        plt.plot(time_scale, level_over_time)
        plt.xlabel(f"Time ({time_unit})")
        plt.ylabel(f"Level ({unit})")
        plt.title("Level over time")
        plt.grid()
        plt.show()
