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
import matplotlib.pyplot as plt

from ._fractional_octave_levels_from_psd_parent import FractionalOctaveLevelsFromPSDParent


class OctaveLevelsFromPSD(FractionalOctaveLevelsFromPSDParent):
    """Compute octave levels from a PSD input.

    This class converts a PSD input into octave levels.
    """

    # Override the operator IDs for octave levels computation
    _operator_id_levels_computation = "compute_octave_levels_from_psd"
    _operator_id_levels_computation_ansi = "compute_octave_levels_from_psd_ansi_s1_11_1986"

    def plot(self):
        """Plot the octave-band levels."""
        levels, frequencies = self.get_output_as_nparray()
        freq_str = [str(f) for f in frequencies]

        if self.use_ansi_s1_11_1986:
            title = "Octave-band levels (ANSI S1.11-1986)"
        else:
            title = "Octave-band levels"

        if len(self.frequency_weighting) > 0:
            ylabel = (
                f"{self.frequency_weighting}-weighted octave-band level "
                f"(dB{self.frequency_weighting} re {self.reference_value})"
            )
        else:
            ylabel = f"Octave-band level (dB re {self.reference_value})"

        plt.figure()
        plt.bar(freq_str, levels)
        plt.title(title)
        plt.xlabel("Frequency (Hz)")
        plt.ylabel(ylabel)
        plt.xticks(rotation=90)
        plt.grid()
        plt.gca().set_axisbelow(True)  # Ensure bars are in front of grid lines
        plt.tight_layout()
        plt.show()
