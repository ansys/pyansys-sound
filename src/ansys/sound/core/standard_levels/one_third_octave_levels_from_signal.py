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

"""Compute 1/3-octave levels from a time-domain signal input."""

import matplotlib.pyplot as plt

from ansys.sound.core._pyansys_sound import PyAnsysSoundException

from ._fractional_octave_levels_from_signal_parent import FractionalOctaveLevelsFromSignalParent


class OneThirdOctaveLevelsFromSignal(
    FractionalOctaveLevelsFromSignalParent, min_dpf_version="11.0"
):
    """Compute 1/3-octave levels from a time-domain signal input.

    This class computes 1/3-octave levels from a time-domain signal.

    .. seealso::
        :class:`OneThirdOctaveLevelsFromPSD`, :class:`OctaveLevelsFromSignal`

    Examples
    --------
    Compute and plot the one-third-octave-band levels from a time-domain signal.

    >>> from ansys.sound.core.standard_levels import OneThirdOctaveLevelsFromSignal
    >>> one_third_octave_levels_from_signal = OneThirdOctaveLevelsFromSignal(
    ...     signal=my_signal,
    ...     reference_value=2e-5
    ... )
    >>> one_third_octave_levels_from_signal.process()
    >>> band_levels = one_third_octave_levels_from_signal.get_band_levels()
    >>> band_center_frequencies = one_third_octave_levels_from_signal.get_frequencies()
    >>> one_third_octave_levels_from_signal.plot()

    .. seealso::
        :ref:`calculate_fractional_octave_levels`
            Example demonstrating how to calculate and compare octave and one-third-octave levels.
    """

    def process(self):
        """Compute the one-third-octave-band levels."""
        if self.signal is None:
            raise PyAnsysSoundException(
                f"No input signal is set. Use {self.__class__.__name__}.signal."
            )

        levels, center_frequencies = self._compute_weighted_one_third_octave_levels()

        self._set_output_field(levels, center_frequencies)

    def plot(self):
        """Plot the 1/3-octave-band levels."""
        levels, frequencies = self.get_output_as_nparray()
        freq_str = [str(f) for f in frequencies]

        if len(self.frequency_weighting) > 0:
            ylabel = (
                f"{self.frequency_weighting}-weighted 1/3-octave-band level "
                f"(dB{self.frequency_weighting} re {self.reference_value})"
            )
        else:
            ylabel = f"1/3-octave-band level (dB re {self.reference_value})"

        plt.figure()
        plt.bar(freq_str, levels)
        plt.title("1/3-octave-band levels")
        plt.xlabel("Frequency (Hz)")
        plt.ylabel(ylabel)
        plt.xticks(rotation=90)
        plt.grid()
        plt.gca().set_axisbelow(True)  # Ensure bars are in front of grid lines
        plt.tight_layout()
        plt.show()
