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

"""Compute the overall level."""

from ansys.dpf.core import Field, Operator, types

from .._pyansys_sound import PyAnsysSoundException
from ._overall_level_parent import OverallLevelParent
from ._standard_levels_parent import DICT_FREQUENCY_WEIGHTING, DICT_SCALE

ID_COMPUTE_OVERALL_LEVEL = "compute_overall_level"


class OverallLevel(OverallLevelParent):
    """Compute the overall level.

    This class computes the overall level of a signal.

    .. seealso::
        :class:`LevelOverTime`, :class:`OctaveLevelsFromSignal`,
        :class:`OneThirdOctaveLevelsFromSignal`

    Examples
    --------
    Compute the overall SPL of an acoustic signal.

    >>> from ansys.sound.core.standard_levels import OverallLevel
    >>> overall_level = OverallLevel(signal=signal, reference_value=2e-5, scale="dB")
    >>> overall_level.process()
    >>> level_value = overall_level.get_level()

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
            options are `""`, `"A"`, `"B"`,  and `"C"`, respectively to get level in dB (or dBSPL),
            dBA, dBB, and dBC. Note that the frequency weighting is only applied if the attribute
            :attr:`scale` is set to `"dB"`.
        """
        super().__init__(
            scale=scale,
            reference_value=reference_value,
            frequency_weighting=frequency_weighting,
        )
        self.signal = signal
        self.__operator = Operator(ID_COMPUTE_OVERALL_LEVEL)

    def __str__(self) -> str:
        """Return the string representation of the object."""
        str_name = f'"{self.signal.name}"' if self.signal is not None else "Not set"
        if self.scale == "RMS":
            str_frequency_weighting = "Not applicable"
            unit = self.signal.unit if isinstance(self.signal.unit, str) else self.signal.unit[1]
        elif len(self.frequency_weighting) > 0:
            str_frequency_weighting = self.frequency_weighting
            unit = f"dB{self.frequency_weighting} re. {self.reference_value}"
        else:
            str_frequency_weighting = "None"
            unit = f"dB re. {self.reference_value}"
        str_level = f"{self._output:.1f} {unit}" if self._output is not None else "Not processed"

        return (
            f"{__class__.__name__} object.\n"
            "Data\n"
            f"\tSignal: {str_name}\n"
            f"\tScale type: {self.scale}\n"
            + (f"\tReference value: {self.reference_value}\n" if self.scale == "dB" else "")
            + f"\tFrequency weighting: {str_frequency_weighting}\n"
            f"Output level value: {str_level}"
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

    def process(self):
        """Compute the overall level."""
        if self.signal is None:
            raise PyAnsysSoundException(f"No input signal is set. Use {__class__.__name__}.signal.")

        self.__operator.connect(0, self.signal)
        self.__operator.connect(1, DICT_SCALE[self.scale])
        self.__operator.connect(2, float(self.reference_value))
        self.__operator.connect(3, DICT_FREQUENCY_WEIGHTING[self.frequency_weighting])

        self.__operator.run()

        self._output = self.__operator.get_output(0, types.double)
