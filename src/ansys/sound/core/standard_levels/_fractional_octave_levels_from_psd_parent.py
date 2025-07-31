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

"""Compute octave levels from a PSD input."""
import warnings

from ansys.dpf.core import Field, Operator, types
import numpy as np

from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ._standard_levels_parent import DICT_FREQUENCY_WEIGHTING, StandardLevelsParent

ID_OCTAVE_LEVELS_FROM_PSD = "compute_octave_levels_from_psd"
ID_OCTAVE_LEVELS_FROM_PSD_ANSI = "compute_octave_levels_from_psd_ansi_s1_11_1986"
ID_GET_FREQUENCY_WEIGHTING = "get_frequency_weighting"


class FractionalOctaveLevelsFromPSDParent(StandardLevelsParent):
    """Abstract base class for fractional octave levels from PSD.

    This is the base class for all fractional octave level from PSD classes and should not be used
    as is.
    """

    # Class operator IDs defined as class attributes
    operator_id_levels_computation = None  # This shall be set in subclasses
    operator_id_levels_computation_ansi = None  # This shall be set in subclasses
    operator_id_frequency_weighting = "get_frequency_weighting"

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
            The power spectral density (PSD) from which the levels are computed.
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
        super().__init__()
        self.psd = psd
        self.use_ansi_s1_11_1986 = use_ansi_s1_11_1986
        self.reference_value = reference_value
        self.frequency_weighting = frequency_weighting

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
        """Input PSD."""
        return self.__psd

    @psd.setter
    def psd(self, psd: Field):
        """Set the PSD."""
        if psd is not None:
            if not isinstance(psd, Field):
                raise PyAnsysSoundException("The PSD must be provided as a DPF field.")
        self.__psd = psd

    @property
    def use_ansi_s1_11_1986(self) -> bool:
        """Whether to simulate the 1/3-octave band filterbank (ANSI S1.11-1986/IEC 61260)."""
        return self.__use_ansi_s1_11_1986

    @use_ansi_s1_11_1986.setter
    def use_ansi_s1_11_1986(self, value: bool):
        """Set the use_ansi_s1_11_1986 flag."""
        self.__use_ansi_s1_11_1986 = value
        return self.__use_ansi_s1_11_1986

    @property
    def reference_value(self) -> float:
        """Reference value for the levels' computation.

        If the levels are computed with a PSD in Pa^2/Hz, the reference value should be 2e-5 (Pa).
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
        """Frequency weighting of the computed levels.

        Available options are `""`, `"A"`, `"B"`, and `"C"`, allowing level calculation in dB (or
        dBSPL), dBA, dBB, and dBC, respectively.
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

    def process(self):
        """Compute the band levels."""
        # It is necessary to check that this is an instance of a subclass, not the superclass,
        # otherwise the operator instantiation would raise an error. This check is done by testing
        # the value of the class attributes operator_id_levels_computation and
        # operator_id_levels_computation_ansi.
        if (
            self.operator_id_levels_computation is not None
            and self.operator_id_levels_computation_ansi is not None
        ):
            if self.psd is None:
                raise PyAnsysSoundException(
                    f"No input PSD is set. Use {self.__class__.__name__}.psd."
                )

            if self.use_ansi_s1_11_1986:
                operator = Operator(self.operator_id_levels_computation_ansi)
            else:
                operator = Operator(self.operator_id_levels_computation)

            operator.connect(0, self.psd)
            operator.run()
            levels: Field = operator.get_output(0, types.field)

            if len(self.frequency_weighting) > 0:
                # Get and apply frequency weighting at the band center frequencies.
                operator = Operator(self.operator_id_frequency_weighting)
                operator.connect(0, levels.time_freq_support.time_frequencies.data)
                operator.connect(1, self.frequency_weighting)
                operator.run()
                weights_dB = operator.get_output(0, types.vec_double)
                weights = 10 ** (weights_dB / 10)
                levels.data = levels.data * weights

            # Convert to dB.
            levels.data = 10 * np.log10(levels.data / (self.reference_value**2) + 1e-12)

            self._output = levels
        else:
            raise PyAnsysSoundException(
                f"This method must only be called from a subclass of {__class__.__name__}."
            )

    def get_output(self) -> Field:
        """Return the octave levels in dB.

        Returns
        -------
        Field
            The octave levels in dB.
        """
        if self._output is None:
            warnings.warn(
                PyAnsysSoundWarning(
                    f"Output is not processed yet. "
                    f"Use the {self.__class__.__name__}.process() method."
                )
            )

        return self._output

    def get_output_as_nparray(self) -> tuple[np.ndarray]:
        """Return the octave levels in dB and center frequencies as a tuple of numpy arrays.

        Returns
        -------
        np.ndarray
            The octave levels in dB.
        np.ndarray
            The center frequencies of the octave bands.
        """
        output = self.get_output()

        if output is None:
            return (np.array([]), np.array([]))

        return np.array(output.data), np.array(output.time_freq_support.time_frequencies.data)

    def get_band_levels(self) -> np.ndarray:
        """Return the band levels in dB as a numpy array.

        Returns
        -------
        np.ndarray
            The band levels in dB.
        """
        return self.get_output_as_nparray()[0]

    def get_center_frequencies(self) -> np.ndarray:
        """Return the center frequencies of the octave bands as a numpy array.

        Returns
        -------
        np.ndarray
            The center frequencies of the octave bands.
        """
        return self.get_output_as_nparray()[1]
