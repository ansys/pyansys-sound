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

"""Sound Composer's control for a source of type spectrum."""
from .._pyansys_sound import PyAnsysSoundException
from ._source_control_parent import SourceControlParent, SpectrumSynthesisMethods


class SourceControlSpectrum(SourceControlParent):
    """Sound Composer's spectrum source's control class.

    This class stores the control parameters used by the Sound Composer for
    generating the sound from a spectrum source.

    It contains the duration in seconds of the sound to generate,
    and the method to use for the sound generation.

    Two sound generation methods are proposed:
    - IFFT: Sound generation method based on the Inverse Fast Fourier Transform of the input
    spectrum, using random phases.
    - Hybrid: sound generation method which combines pure tones generation and IFFT.
    If peaks are detected in the input spectrum, they are generated as pure tones (sine waves).
    The rest is synthesized using the IFFT method.
    """

    def __init__(self, duration: float = 0.0, method: int = 0):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        duration : float, default: 0.0
            Duration of the sound generated from the spectrum source, in seconds.
        method : int, default: 0
            Method to use for the sound generation: 0 for IFFT, 1 for Hybrid.
        """
        super().__init__()
        self.duration = duration
        self.method = method

    def __str__(self) -> str:
        """Return the string representation of the object."""
        return f"Duration: {self.duration} s\nMethod: {self.get_method_name()}"

    @property
    def duration(self) -> float:
        """Duration of the generated sound, in seconds."""
        return self.__duration

    @duration.setter
    def duration(self, duration: float):
        """Set the duration, in seconds."""
        if duration < 0.0:
            raise PyAnsysSoundException("Duration must be positive.")
        self.__duration = duration

    @property
    def method(self) -> int:
        """Method to use for the sound generation: 0 for IFFT, 1 for Hybrid."""
        return self.__method

    @method.setter
    def method(self, method: int):
        """Set the sound generation method: 0 for IFFT, 1 for Hybrid."""
        if method not in [m.value for m in SpectrumSynthesisMethods]:
            available_methods = "\n".join(f"{m.value}: {m.name}" for m in SpectrumSynthesisMethods)
            raise PyAnsysSoundException(
                "Method must be an integer. Available options are:\n" + available_methods
            )
        self.__method = method

    def get_method_name(self) -> str:
        """Get the sound generation method name.

        Returns
        -------
        str
            Name of the sound generation method.
        """
        return SpectrumSynthesisMethods(self.method).name
