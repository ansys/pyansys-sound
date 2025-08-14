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

"""Fractional octave levels from a PSD input."""
import warnings

from ansys.dpf.core import Field, Operator, types
import numpy as np

from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ._standard_levels_parent import DICT_FREQUENCY_WEIGHTING, StandardLevelsParent


class FractionalOctaveLevelsParent(StandardLevelsParent):
    """Abstract base class for fractional octave levels, either from a PSD or a time-domain signal.

    This is the base class for all fractional octave level classes (namely OctaveLevelsFromPSD,
    OneThirdOctaveLevelsFromPSD, OctaveLevelsFromSignal, and OneThirdOctaveLevelsFromSignal) and
    should not be used as is.
    """

    # Class attribute with the name of the DPF Sound operators that computes A, B, or C frequency
    # weightings for a set of frequencies.
    _operator_id_frequency_weighting = "get_frequency_weighting"

    def __init__(
        self,
        reference_value: float = 1.0,
        frequency_weighting: str = "",
    ):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        reference_value : float, default: 1.0
            The reference value for the levels' computation. If the levels are computed with a PSD
            in Pa^2/Hz, the reference value should be 2e-5 (Pa).
        frequency_weighting : str, default: ""
            The frequency weighting to apply to the signal before computing the levels. Available
            options are `""`, `"A"`, `"B"`,  and `"C"`, to get levels in dB (or dBSPL), dBA, dBB,
            and dBC, respectively.
        """
        super().__init__()
        self.reference_value = reference_value
        self.frequency_weighting = frequency_weighting

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

    def get_output(self) -> Field:
        """Return the band levels in dB.

        Returns
        -------
        Field
            The band levels in dB (actual unit depends on :attr:`reference_value` and
            :attr:`frequency_weighting` attributes' values).
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
        """Return the band levels in dB and center frequencies in Hz as a tuple of numpy arrays.

        Returns
        -------
        np.ndarray
            The band levels in dB (actual unit depends on :attr:`reference_value` and
            :attr:`frequency_weighting` attributes' values).
        np.ndarray
            The center frequencies in Hz of the band levels.
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
            The band levels in dB (actual unit depends on :attr:`reference_value` and
            :attr:`frequency_weighting` attributes' values).
        """
        return self.get_output_as_nparray()[0]

    def get_center_frequencies(self) -> np.ndarray:
        """Return the center frequencies in Hz of the band levels as a numpy array.

        Returns
        -------
        np.ndarray
            The center frequencies in Hz of the band levels.
        """
        return self.get_output_as_nparray()[1]

    def _apply_frequency_weighting(self):
        """Apply frequency weighting to the computed levels."""
        if self._output is not None:
            if len(self.frequency_weighting) > 0:
                operator = Operator(self._operator_id_frequency_weighting)
                operator.connect(0, self._output.time_freq_support.time_frequencies.data)
                operator.connect(1, self.frequency_weighting)
                operator.run()
                weights_dB = operator.get_output(0, types.vec_double)
                self._output.data = self._output.data + weights_dB

    def _convert_output_to_dB(self):
        """Convert the output levels to dB."""
        if self._output is not None:
            self._output.data = self._output.data / (self.reference_value**2)
            self._output.data = 10 * np.log10(self._output.data + 1e-12)
