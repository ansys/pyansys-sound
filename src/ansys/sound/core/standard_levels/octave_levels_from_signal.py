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

"""Compute octave levels from a time-domain signal input."""

import matplotlib.pyplot as plt
import numpy as np

from ansys.sound.core._pyansys_sound import PyAnsysSoundException

from ._fractional_octave_levels_from_signal_parent import FractionalOctaveLevelsFromSignalParent


class OctaveLevelsFromSignal(FractionalOctaveLevelsFromSignalParent, min_dpf_version="11.0"):
    """Compute octave levels from a time-domain signal input.

    This class computes octave levels from a time-domain signal.

    .. note::
        For consistency with other Ansys Sound applications, octave-band levels are derived from
        one-third-octave levels, and frequency weighting is applied before the conversion. In other
        words, each octave-band level is obtained by summing the 3 one-third-octave levels within
        (in squared units), each weighted with the frequency weighting obtained at the
        one-third-octave-band center frequency. Note that the highest-frequency octave band
        (centered at 16000 Hz) is obtained by only summing the 2 highest one-third-octave bands
        (since the 30th one-third-octave band centered at 20000 Hz is not considered).

    .. seealso::
        :class:`OctaveLevelsFromPSD`, :class:`OneThirdOctaveLevelsFromSignal`

    Examples
    --------
    Compute and plot the octave-band levels from a time-domainsignal.

    >>> from ansys.sound.core.standard_levels import OctaveLevelsFromSignal
    >>> octave_levels_from_signal = OctaveLevelsFromSignal(signal=my_signal, reference_value=2e-5)
    >>> octave_levels_from_signal.process()
    >>> band_levels = octave_levels_from_signal.get_band_levels()
    >>> band_center_frequencies = octave_levels_from_signal.get_frequencies()
    >>> octave_levels_from_signal.plot()

    .. seealso::
        :ref:`calculate_fractional_octave_levels`
            Example demonstrating how to calculate and compare octave and one-third-octave levels.
    """

    def process(self):
        """Compute the octave-band levels."""
        if self.signal is None:
            raise PyAnsysSoundException(
                f"No input signal is set. Use {self.__class__.__name__}.signal."
            )

        one_third_octave_levels, one_third_octave_center_frequencies = (
            self._compute_weighted_one_third_octave_levels()
        )

        # Derive octave-levels from 1/3-octave levels:
        # Squared-unit one-third-octave levels are summed 3 by 3, except for the last octave band
        # where only 2 one-third-octave bands are available and summed.
        octave_count = int(np.ceil(len(one_third_octave_levels) / 3))
        octave_levels = np.zeros(octave_count)
        octave_center_frequencies = np.zeros(octave_count)
        for i in range(octave_count - 1):
            octave_levels[i] = np.sum(one_third_octave_levels[i * 3 : (i + 1) * 3])
            octave_center_frequencies[i] = one_third_octave_center_frequencies[i * 3 + 1]

        octave_levels[-1] = np.sum(one_third_octave_levels[-2:])
        octave_center_frequencies[-1] = one_third_octave_center_frequencies[-1]

        # Set output field using computed levels and center frequencies.
        self._set_output_field(octave_levels, octave_center_frequencies)

    def plot(self):
        """Plot the octave-band levels."""
        levels, frequencies = self.get_output_as_nparray()
        freq_str = [str(f) for f in frequencies]

        if len(self.frequency_weighting) > 0:
            ylabel = (
                f"{self.frequency_weighting}-weighted octave-band level "
                f"(dB{self.frequency_weighting} re {self.reference_value})"
            )
        else:
            ylabel = f"Octave-band level (dB re {self.reference_value})"

        plt.figure()
        plt.bar(freq_str, levels)
        plt.title("Octave-band levels")
        plt.xlabel("Frequency (Hz)")
        plt.ylabel(ylabel)
        plt.xticks(rotation=90)
        plt.grid()
        plt.gca().set_axisbelow(True)  # Ensure bars are in front of grid lines
        plt.tight_layout()
        plt.show()
