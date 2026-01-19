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

"""Fractional octave levels from a time-domain signal input."""

from ansys.dpf.core import Field, Operator, TimeFreqSupport, fields_factory, locations, types
import numpy as np

from .._pyansys_sound import PyAnsysSoundException
from ._fractional_octave_levels_parent import FractionalOctaveLevelsParent


class FractionalOctaveLevelsFromSignalParent(FractionalOctaveLevelsParent, min_dpf_version="11.0"):
    """Abstract base class for fractional octave levels from time-domain signal.

    This is the base class for all fractional octave level classes using a time-domain signal as
    input (namely OctaveLevelsFromSignal and OneThirdOctaveLevelsFromSignal) and should not be used
    as is.
    """

    # Class attribute (string) with the name of the DPF Sound operator allowing one-third-octave
    # level computation from time-domain signal.
    _operator_id_levels_computation = "compute_one_third_octave_levels_from_signal"

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

    def _compute_weighted_one_third_octave_levels(self) -> tuple[np.ndarray, np.ndarray]:
        """Compute 1/3-octave-band levels and apply frequency weighting.

        Computes the 1/3-octave-band levels using :attr:`signal` as input and applies the frequency
        weighting specified in :attr:`frequency_weighting`.

        Returns
        -------
        numpy.ndarray
            The weighted 1/3-octave-band levels in squared units.
        numpy.ndarray
            The 1/3-octave-band center frequencies in Hz.
        """
        operator = Operator(self._operator_id_levels_computation)
        operator.connect(0, self.signal)
        operator.run()
        field_levels = operator.get_output(0, types.field)

        center_frequencies = np.array(field_levels.time_freq_support.time_frequencies.data)
        levels = np.array(field_levels.data)

        # Retrieve frequency weighting at 1/3-octave-band center frequencies.
        weights_dB = self._get_frequency_weightings(center_frequencies)

        # Convert weights to squared unit, and apply them to computed 1/3-octave levels.
        weights = 10.0 ** (weights_dB / 10.0)
        levels *= weights

        return levels, center_frequencies

    def _set_output_field(self, levels: np.ndarray, center_frequencies: np.ndarray):
        """Set the output field using the specified levels and center frequencies.

        Populates the `_output` attribute with a DPF field built with the specified levels, after
        conversion to dB, and the specified center frequencies as support.

        Parameters
        ----------
        levels : numpy.ndarray
            The computed levels to include in the output field, in squared unit. These will be
            converted to dB in the set field.
        center_frequencies : numpy.ndarray
            The center frequencies corresponding to the computed levels, in Hz.
        """
        # Convert to dB.
        octave_levels_dB = 10.0 * np.log10(levels / (self.reference_value**2) + 1e-12)

        # Create output field.
        field_center_frequencies = fields_factory.create_scalar_field(
            num_entities=1, location=locations.time_freq
        )
        field_center_frequencies.append(center_frequencies, 1)
        support = TimeFreqSupport()
        support.time_frequencies = field_center_frequencies

        self._output = fields_factory.create_scalar_field(
            num_entities=1, location=locations.time_freq
        )
        self._output.append(octave_levels_dB, 1)
        self._output.time_freq_support = support
