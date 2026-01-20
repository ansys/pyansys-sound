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

"""Fractional octave levels from a PSD input."""

from ansys.dpf.core import Field, Operator, types
import numpy as np

from .._pyansys_sound import PyAnsysSoundException
from ._fractional_octave_levels_parent import FractionalOctaveLevelsParent


class FractionalOctaveLevelsFromPSDParent(FractionalOctaveLevelsParent, min_dpf_version="11.0"):
    """Abstract base class for fractional octave levels from PSD.

    This is the base class for all fractional octave level classes using a PSD as input (namely
    OctaveLevelsFromPSD and OneThirdOctaveLevelsFromPSD) and should not be used as is.
    """

    # Class attributes (string) with the names of the DPF Sound operators allowing
    # fractional-octave level computation from PSD, whether simulating ANSI S1.11-1986 filterbank
    # or not.
    # Attribute values shall be set in subclasses, as they depend on whether you compute octave- or
    # one-third-octave-band levels.
    _operator_id_levels_computation = None
    _operator_id_levels_computation_ansi = None

    def __init__(
        self,
        psd: Field = None,
        use_ansi_s1_11_1986: bool = False,
        reference_value: float = 1.0,
        frequency_weighting: str = "",
    ):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        psd : Field, default: None
            The power spectral density (PSD), in squared linear unit per Hz  (Pa^2/Hz, for example),
            from which the levels are computed.
        use_ansi_s1_11_1986 : bool, default: False
            Whether to simulate the 1/3-octave filterbank as defined in ANSI S1.11-1986 and
            IEC 61260 standards.
        reference_value : float, default: 1.0
            The reference value for the levels' computation. If the levels are computed with a PSD
            in Pa^2/Hz, the reference value should be 2e-5 (Pa).
        frequency_weighting : str, default: ""
            The frequency weighting to apply to the signal before computing the levels. Available
            options are `""`, `"A"`, `"B"`,  and `"C"`, to get levels in dB (or dBSPL), dBA, dBB,
            and dBC, respectively.
        """
        super().__init__(reference_value=reference_value, frequency_weighting=frequency_weighting)
        self.psd = psd
        self.use_ansi_s1_11_1986 = use_ansi_s1_11_1986

    def __str__(self) -> str:
        """Return the string representation of the object."""
        str_name = f'"{self.psd.name}"' if self.psd is not None else "Not set"
        if len(self.frequency_weighting) > 0:
            str_frequency_weighting = self.frequency_weighting
            str_unit = f"dB{self.frequency_weighting} (re {self.reference_value})"
        else:
            str_frequency_weighting = "None"
            str_unit = f"dB (re {self.reference_value})"

        if self._output is not None:
            levels, frequencies = self.get_output_as_nparray()
            str_levels = "\n\t"
            str_levels += "\n\t".join(
                [f"{f:.1f} Hz:\t{l:.1f} {str_unit}" for (f, l) in zip(frequencies, levels)]
            )
        else:
            str_levels = " Not processed"

        return (
            f"{self.__class__.__name__} object.\n"
            "Data\n"
            f"\tPSD: {str_name}\n"
            f"\tANSI S1.11-1986 filterbank simulation: "
            f"{'Yes' if self.use_ansi_s1_11_1986 else 'No'}\n"
            f"\tReference value: {self.reference_value}\n"
            f"\tFrequency weighting: {str_frequency_weighting}\n"
            f"Output levels:{str_levels}"
        )

    @property
    def psd(self) -> Field:
        """Input power spectral density (PSD), in squared linear unit per Hz."""
        return self.__psd

    @psd.setter
    def psd(self, psd: Field):
        """Set the PSD."""
        if psd is not None:
            if not isinstance(psd, Field):
                raise PyAnsysSoundException("The input PSD must be provided as a DPF field.")
        self.__psd = psd

    @property
    def use_ansi_s1_11_1986(self) -> bool:
        """Whether to simulate the 1/3-octave band filterbank (ANSI S1.11-1986/IEC 61260)."""
        return self.__use_ansi_s1_11_1986

    @use_ansi_s1_11_1986.setter
    def use_ansi_s1_11_1986(self, value: bool):
        """Set the use_ansi_s1_11_1986 flag."""
        self.__use_ansi_s1_11_1986 = value

    def process(self):
        """Compute the band levels."""
        # It is necessary to check that `self` is an instance of a subclass, otherwise the operator
        # instantiation would raise an error. This check is done by testing the values of the class
        # attributes `_operator_id_levels_computation` and `_operator_id_levels_computation_ansi`.
        if (
            self._operator_id_levels_computation is None
            or self._operator_id_levels_computation_ansi is None
        ):
            raise PyAnsysSoundException(
                f"This method cannot be called from class {self.__class__.__name__}. This class is "
                "meant as an abstract class that should not be used directly."
            )

        if self.psd is None:
            raise PyAnsysSoundException(f"No input PSD is set. Use {self.__class__.__name__}.psd.")

        if self.use_ansi_s1_11_1986:
            operator = Operator(self._operator_id_levels_computation_ansi)
        else:
            operator = Operator(self._operator_id_levels_computation)

        operator.connect(0, self.psd)
        operator.run()
        self._output = operator.get_output(0, types.field)

        # Convert to dB
        self._output.data = 10.0 * np.log10(self._output.data / (self.reference_value**2) + 1e-12)

        # Apply frequency weighting
        frequencies = self._output.time_freq_support.time_frequencies.data
        self._output.data += self._get_frequency_weightings(frequencies)
