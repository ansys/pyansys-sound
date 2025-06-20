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

"""PyAnsys Sound class to store sound data."""
from ansys.dpf.core import Field
import matplotlib.pyplot as plt
import numpy as np

from .._pyansys_sound import PyAnsysSoundException


# class PSD(Field, metaclass=NoExtraAttributesMeta):
class PSD(Field):
    """PyAnsys Sound class to store sound data.

    Add Nfft, window type, and overlap as ppts, but then probably redundant with
    PowerSpectralDensity.
    """

    def __init__(
        self,
    ):
        """TODO."""
        super().__init__()

    def __str__(self):
        """Return the string representation of the object."""
        if len(self.frequencies) > 0:
            properties_str = (
                f":\n\tFrequency resolution: {self.delta_f:.2f} Hz"
                f"\n\tMaximum frequency: {self.f_max:.1f} Hz"
            )
        else:
            properties_str = ""
        return f"PSD object{properties_str}"

    @property
    def frequencies(self) -> np.ndarray:
        """Array of frequencies in Hz where the PSD is defined."""
        return np.array(self.time_freq_support.time_frequencies.data)

    @property
    def delta_f(self) -> float:
        """Frequency resolution in Hz of the PSD."""
        if len(self.frequencies) < 2:
            raise PyAnsysSoundException(
                "Not enough frequency points to determine frequency resolution."
            )

        return self.frequencies[1] - self.frequencies[0]

    @property
    def f_max(self) -> float:
        """Maximum frequency in Hz."""
        return self.frequencies[-1]

    def update(self) -> None:
        """Update the sound data."""
        # Nothing to update here for now
        # TODO:
        # - check support is regularly spaced
        pass

    def get_as_nparray(self) -> list[np.ndarray]:
        """Get the sound data as a NumPy array."""
        return (np.array(self.data), self.frequencies)

    @classmethod
    def create(cls, object: Field) -> "PSD":
        """TODO."""
        object.__class__ = cls
        object.update()
        return object

    def plot(self):
        """Plot the PSD data."""
        plt.plot(self.time_freq_support.time_frequencies.data, self.data)

        plt.xlabel("Frequency (Hz)")
        plt.ylabel("Amplitude (dB/Hz)")
        plt.title(self.name)
        plt.show()
