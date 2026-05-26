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

"""Compute the overall level from a PSD input."""

from ansys.dpf.core import Field, Operator, types

from .._pyansys_sound import PyAnsysSoundException
from ._standard_levels_parent import DICT_FREQUENCY_WEIGHTING, DICT_SCALE
from .overall_level import OverallLevel

ID_COMPUTE_OVERALL_LEVEL_FROM_PSD = "compute_overall_level_from_psd"


class OverallLevelFromPSD(OverallLevel, min_sound_version="2027.1.0"):
    """Compute the overall level from a power spectral density (PSD) input.

    This class computes the overall level from a PSD, on a decibel scale or a linear,
    root-mean-square (RMS) scale.

    .. seealso::
        :class:`OverallLevel`, :class:`OneThirdOctaveLevelsFromPSD`,
        :class:`OctaveLevelsFromPSD`, :class:`PowerSpectralDensity`

    Examples
    --------
    Compute the overall level from a PSD.

    >>> from ansys.sound.core.standard_levels import OverallLevelFromPSD
    >>> level = OverallLevelFromPSD(psd=my_psd, reference_value=2e-5)
    >>> level.process()
    >>> level_dB = level.get_level()
    """

    def __init__(
        self,
        psd: Field = None,
        scale: str = "dB",
        reference_value: float = 1.0,
        frequency_weighting: str = "",
    ):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        psd : Field, default: None
            The input power spectral density (PSD), in unit^2/Hz.
        scale : str, default: "dB"
            The scale type of the output level. Available options are `"dB"` and `"RMS"`.
        reference_value : float, default: 1.0
            The reference value for the level computation. If the PSD is computed from a signal
            in Pa, the reference value should be 2e-5 (Pa).
        frequency_weighting : str, default: ""
            The frequency weighting to apply before computing the level. Available options are
            `""`, `"A"`, `"B"`, and `"C"`, respectively to get level in dB (or dBSPL), dBA, dBB,
            and dBC. Note that the frequency weighting is only applied if the attribute
            :attr:`scale` is set to `"dB"`.
        """
        super().__init__(
            signal=None,
            scale=scale,
            reference_value=reference_value,
            frequency_weighting=frequency_weighting,
        )
        self.psd = psd
        self.__operator = Operator(ID_COMPUTE_OVERALL_LEVEL_FROM_PSD)

    def __str__(self) -> str:
        """Return the string representation of the object."""
        str_name = f'"{self.psd.name}"' if self.psd is not None else "Not set"
        if self.scale == "RMS":
            str_frequency_weighting = "Not applicable"
            unit = "(RMS)"
            if self.psd is not None:
                psd_unit = self.psd.unit if isinstance(self.psd.unit, str) else self.psd.unit[1]
                if psd_unit.endswith("^2/Hz"):
                    unit = self.psd.unit[:-6]
        elif len(self.frequency_weighting) > 0:
            str_frequency_weighting = self.frequency_weighting
            unit = f"dB{self.frequency_weighting} (re {self.reference_value})"
        else:
            str_frequency_weighting = "None"
            unit = f"dB (re {self.reference_value})"
        str_level = f"{self._output:.1f} {unit}" if self._output is not None else "Not processed"

        return (
            f"{__class__.__name__} object.\n"
            "Data\n"
            f"\tPSD: {str_name}\n"
            f"\tScale type: {self.scale}\n"
            + (f"\tReference value: {self.reference_value}\n" if self.scale == "dB" else "")
            + f"\tFrequency weighting: {str_frequency_weighting}\n"
            f"Output level value: {str_level}"
        )

    @property
    def psd(self) -> Field:
        """Input power spectral density (PSD)."""
        return self.__psd

    @psd.setter
    def psd(self, psd: Field):
        """Set the PSD."""
        if psd is not None:
            if not isinstance(psd, Field):
                raise PyAnsysSoundException("The input PSD must be provided as a DPF field.")
        self.__psd = psd

    @property
    def signal(self) -> Field:
        """Not applicable for this class. Use :attr:`psd` instead."""
        raise PyAnsysSoundException(
            f"'{__class__.__name__}' does not use a signal input. Use the 'psd' attribute instead."
        )

    @signal.setter
    def signal(self, signal: Field):
        """Block setting signal on this class."""
        if signal is not None:
            raise PyAnsysSoundException(
                f"'{__class__.__name__}' does not use a signal input. "
                "Use the 'psd' attribute instead."
            )

    def process(self):
        """Compute the overall level from the PSD."""
        if self.psd is None:
            raise PyAnsysSoundException(f"No input PSD is set. Use {__class__.__name__}.psd.")

        self.__operator.connect(0, self.psd)
        self.__operator.connect(1, DICT_SCALE[self.scale])
        self.__operator.connect(2, float(self.reference_value))
        self.__operator.connect(3, DICT_FREQUENCY_WEIGHTING[self.frequency_weighting])

        self.__operator.run()

        self._output = self.__operator.get_output(0, types.double)
