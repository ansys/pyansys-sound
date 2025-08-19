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

"""Fractional octave levels from a time-domain signal input."""
from ansys.dpf.core import Field, Operator, types

from ansys.sound.core.server_helpers._check_server_version import class_available_from_version

from .._pyansys_sound import PyAnsysSoundException
from ._fractional_octave_levels_parent import FractionalOctaveLevelsParent


@class_available_from_version("11.0")
class FractionalOctaveLevelsFromSignalParent(FractionalOctaveLevelsParent):
    """Abstract base class for fractional octave levels from time-domain signal.

    This is the base class for all fractional octave level classes using a time-domain signal as
    input (namely OctaveLevelsFromSignal and OneThirdOctaveLevelsFromSignal) and should not be used
    as is.
    """

    # Class attribute (string) with the name of the DPF Sound operator allowing fractional-octave
    # level computation from time-domain signal.
    # Attribute value shall be set in subclasses, as it depends on whether you compute octave- or
    # one-third-octave-band levels.
    _operator_id_levels_computation = None

    def __init__(
        self,
        signal: Field = None,
        reference_value: float = 1.0,
        frequency_weighting: str = "",
    ):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        signal : Field, default: None
            The time-domain signal from which the levels are computed.
        reference_value : float, default: 1.0
            The reference value for the levels' computation. If the levels are computed with a PSD
            in Pa^2/Hz, the reference value should be 2e-5 (Pa).
        frequency_weighting : str, default: ""
            The frequency weighting to apply to the signal before computing the levels. Available
            options are `""`, `"A"`, `"B"`,  and `"C"`, to get levels in dB (or dBSPL), dBA, dBB,
            and dBC, respectively.
        """
        super().__init__(reference_value=reference_value, frequency_weighting=frequency_weighting)
        self.signal = signal

    def __str__(self) -> str:
        """Return the string representation of the object."""
        str_name = f'"{self.signal.name}"' if self.signal is not None else "Not set"
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
            f"\tSignal: {str_name}\n"
            f"\tReference value: {self.reference_value}\n"
            f"\tFrequency weighting: {str_frequency_weighting}\n"
            f"Output levels:{str_levels}"
        )

    @property
    def signal(self) -> Field:
        """Input time-domain signal."""
        return self.__signal

    @signal.setter
    def signal(self, signal: Field):
        """Set the signal."""
        if signal is not None:
            if not isinstance(signal, Field):
                raise PyAnsysSoundException("The input signal must be provided as a DPF field.")
        self.__signal = signal

    def process(self):
        """Compute the band levels."""
        # It is necessary to check that this is an instance of a subclass, not the superclass,
        # otherwise the operator instantiation would raise an error. This check is done by testing
        # the value of the class attribute operator_id_levels_computation.
        if self._operator_id_levels_computation is None:
            raise PyAnsysSoundException(
                f"This method cannot be called from class {self.__class__.__name__}. This class is "
                "meant as an abstract class that should not be used directly."
            )

        if self.signal is None:
            raise PyAnsysSoundException(
                f"No input signal is set. Use {self.__class__.__name__}.signal."
            )

        operator = Operator(self._operator_id_levels_computation)

        operator.connect(0, self.signal)
        operator.run()
        self._output = operator.get_output(0, types.field)

        self._convert_output_to_dB()
        self._apply_frequency_weighting()
