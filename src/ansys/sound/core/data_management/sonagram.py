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
from ansys.dpf.core import FieldsContainer
import numpy as np

from .._pyansys_sound import PyAnsysSoundException


class Sonagram(FieldsContainer):
    """PyAnsys Sound class to store sound data.

    Probably redundant with Stft, maybe not worth it
    add Nfft, window type, and overlap as ppts
    add specific getters for magnitude & phase
    """

    def __init__(
        self,
    ):
        """TODO."""
        super().__init__()

    def __str__(self):
        """Return the string representation of the object."""
        return (
            f"Sonagram object:"
            f"\n\tDuration: {self.duration:.2f} s"
            f"\n\tMaximum frequency: {self.f_max:.1f} Hz"
        )

    @property
    def frequencies(self) -> np.ndarray:
        """Array of frequencies in Hz where the PSD is defined."""
        if len(self) == 0:
            raise PyAnsysSoundException("Empty sonagram. Cannot retrieve frequency array.")

        return np.array(self[0].time_freq_support.time_frequencies.data)

    @property
    def time(self) -> np.ndarray:
        """Array of times in s where the sound is defined."""
        return np.array(self.time_freq_support.time_frequencies.data)

    @property
    def fs(self) -> float:
        """Sampling frequency in Hz."""
        if len(self.time) < 2:
            raise PyAnsysSoundException("Not enough time points to determine sampling frequency.")

        return 1 / (self.time[1] - self.time[0])

    def update(self) -> None:
        """Update the sound data."""
        # Nothing to update here for now
        # TODO:
        # - check at least one field is present
        # - check all fields are the same size and have the same time frequency support
        # - check support is regularly spaced
        pass

    def get_as_nparray(self) -> list[np.ndarray]:
        """Get the sound data as a NumPy array."""
        return np.array(self.data)

    @classmethod
    def create(cls, object: FieldsContainer) -> "Sonagram":
        """TODO."""
        object.__class__ = cls
        object.update()
        return object

    def plot(self):
        """Plot the sound data."""
        pass
