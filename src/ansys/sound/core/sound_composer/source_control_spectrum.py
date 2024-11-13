# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
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

"""Sound composer's spectrum source control."""
from dataclasses import dataclass

from .._pyansys_sound import PyAnsysSoundException
from ._source_control_parent import SourceControlParent

METHODS = ("Inverse FFT", "Hybrid")


@dataclass
class SourceControlSpectrum(SourceControlParent):
    """Sound composer's spectrum source control class.

    Parameters
    ----------
    duration : float, default 0.0
        Duration of the spectrum.
    method : int, default 0
        Method of the spectrum. 0 for Inverse FFT, 1 for Hybrid.
    """

    __duration: float = 0.0
    __method: int = 0

    @property
    def duration(self) -> float:
        """Get the duration."""
        return self.__duration

    @duration.setter
    def duration(self, duration: float):
        """Set the duration."""
        if duration < 0.0:
            raise PyAnsysSoundException("Duration must be positive.")
        self.__duration = duration

    @property
    def method(self) -> int:
        """Get the method."""
        return self.__method

    @method.setter
    def method(self, method: int):
        """Set the method."""
        if method not in (0, 1):
            raise PyAnsysSoundException(
                f"Method must be either 0 ({METHODS[0]}) or 1 ({METHODS[1]})."
            )
        self.__method = method

    def __str__(self) -> str:
        """Return the string representation of the object."""
        return f"Duration: {self.duration}\nMethod: {METHODS[self.method]}"
