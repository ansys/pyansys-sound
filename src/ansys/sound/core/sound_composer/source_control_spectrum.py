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
from .._pyansys_sound import PyAnsysSoundException
from ._source_control_parent import SourceControlParent


class SourceControlSpectrum(SourceControlParent):
    """Sound composer's spectrum source control class.

    This class stores parameters for a spectrum source control, namely its duration in s and
    method used.
    """

    def __init__(self, duration: float = 0.0, method: int = 1):
        """
        Create a ``SourceControlSpectrum`` object.

        Parameters
        ----------
        duration : float, default 0.0
            Duration of the spectrum source control in s.
        method : int, default 1
            Method of the spectrum source control. 1 for inverse FFT, 2 for hybrid.
        """
        super().__init__()
        self.duration = duration
        self.method = method

    def __str__(self) -> str:
        """Return the string representation of the object."""
        return (
            f"Duration: {self.duration} s\n"
            f"Method: {self._spectrum_synthesis_methods(self.method).name}"
        )

    @property
    def duration(self) -> float:
        """Spectrum source control duration in s."""
        return self.__duration

    @duration.setter
    def duration(self, duration: float):
        """Set the duration."""
        if duration < 0.0:
            raise PyAnsysSoundException("Duration must be positive.")
        self.__duration = duration

    @property
    def method(self) -> int:
        """Spectrum source synthesis method, 1 for inverse FFT, 2 for hybrid."""
        return self.__method

    @method.setter
    def method(self, method: int):
        """Set the method."""
        if method not in (1, 2):
            raise PyAnsysSoundException(
                f"Method must be either 1 ({self._spectrum_synthesis_methods(1).name}) "
                f"or 2 ({self._spectrum_synthesis_methods(2).name})."
            )
        self.__method = method
