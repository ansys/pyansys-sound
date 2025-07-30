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
import matplotlib.pyplot as plt
import numpy as np

from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ._standard_levels_parent import DICT_FREQUENCY_WEIGHTING, StandardLevelsParent

ID_OCTAVE_LEVELS_FROM_PSD = "compute_octave_levels_from_psd"
ID_OCTAVE_LEVELS_FROM_PSD_ANSI = "compute_octave_levels_from_psd_ansi_s1_11_1986"
ID_GET_FREQUENCY_WEIGHTING = "get_frequency_weighting"


class OctaveLevelsFromPSD(StandardLevelsParent):
    """Compute octave levels from a PSD input.

    This class converts a PSD input signal into octave levels.
    """

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
            The power spectral density (PSD) from which the octave levels are computed.
        use_ansi_s1_11_1986 : bool, default: False
            Whether to simulate the 1/3-octave filterbank as defined in ANSI S1.11-1986 and
            IEC 61260 standards.
        reference_value : float, default: 1.0
            The reference value for the level computation. If the overall level is computed with a
            signal in Pa, the reference value should be 2e-5.
        frequency_weighting : str, default: ""
            The frequency weighting to apply to the signal before computing the level. Available
            options are `""`, `"A"`, `"B"`,  and `"C"`, respectively to get level in dBSPL, dB(A),
            dB(B), and dB(C).
        """
        super().__init__()
        self.psd = psd
        self.use_ansi_s1_11_1986 = use_ansi_s1_11_1986
        self.reference_value = reference_value
        self.frequency_weighting = frequency_weighting

    def __str__(self) -> str:
        """Return the string representation of the object."""
        output = self.get_output()

        str_name = f'"{self.signal.name}"' if self.signal is not None else "Not set"
        str_frequency_weighting = (
            self.frequency_weighting if len(self.frequency_weighting) > 0 else "None"
        )
        str_level = f"{output:.1f}" if output is not None else "Not processed"

        return (
            f"{__class__.__name__} object.\n"
            "Data\n"
            f"\tSignal: {str_name}\n"
            f"\tScale type: {self.scale}\n"
            f"\tReference value: {self.reference_value}\n"
            f"\tFrequency weighting: {str_frequency_weighting}\n"
            f"Output level value: {str_level}"
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
        """Whether to simulate the octave band filterbank (ANSI S1.11-1986/IEC 61260)."""
        return self.__use_ansi_s1_11_1986

    @use_ansi_s1_11_1986.setter
    def use_ansi_s1_11_1986(self, value: bool):
        """Set the use_ansi_s1_11_1986 flag."""
        self.__use_ansi_s1_11_1986 = value
        return self.__use_ansi_s1_11_1986

    @property
    def reference_value(self) -> float:
        """Reference value for the level computation.

        If the overall level is computed with a sound pressure signal in Pa, the reference value
        should be 2e-5.
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
        is 2e-5 Pa, these options allow level calculation in dBSPL, dB(A), dB(B), and dB(C),
        respectively.
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
        """Compute the overall level."""
        if self.psd is None:
            raise PyAnsysSoundException(f"No input PSD is set. Use {__class__.__name__}.psd.")

        if self.use_ansi_s1_11_1986:
            operator = Operator(ID_OCTAVE_LEVELS_FROM_PSD_ANSI)
        else:
            operator = Operator(ID_OCTAVE_LEVELS_FROM_PSD)

        operator.connect(0, self.psd)
        operator.run()
        levels: Field = operator.get_output(0, types.field)

        if self.frequency_weighting != "":
            # Get and apply frequency weighting at the band center frequencies.
            operator = Operator(ID_GET_FREQUENCY_WEIGHTING)
            operator.connect(0, levels.time_freq_support.time_frequencies.data)
            operator.connect(1, self.frequency_weighting)
            operator.run()
            levels.data = levels.data * operator.get_output(0, types.vec_double)

        # Convert to dB.
        levels.data = 10 * np.log10(levels.data / (self.reference_value**2))

        self._output = levels

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
                    f"Use the {__class__.__name__}.process() method."
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

        return np.array(output.data), np.array([self.time_freq_support.time_frequencies.data])

    def get_one_third_octave_levels(self) -> np.ndarray:
        """Return the octave levels in dB as a numpy array.

        Returns
        -------
        np.ndarray
            The octave levels in dB.
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

    def plot(self):
        """Plot the octave-band levels."""
        levels, frequencies = self.get_output_as_nparray()
        freq_str = [str(f) for f in frequencies]

        if self.use_ansi_s1_11_1986:
            title = "Octave-band levels (ANSI S1.11-1986)"
        else:
            title = "Octave-band levels"

        plt.figure()
        plt.bar(freq_str, levels)
        plt.title(title)
        plt.xlabel("Frequency (Hz)")
        plt.ylabel("Octave-band level (dB)")
        plt.grid(axis="y")
        plt.gca().set_axisbelow(True)  # Ensure bars are in front of grid lines
        plt.show()
