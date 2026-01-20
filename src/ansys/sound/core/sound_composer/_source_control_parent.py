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

"""Sound composer's source control."""

from enum import Enum

from ._sound_composer_parent import SoundComposerParent


class SpectrumSynthesisMethods(Enum):
    """Class (enum) providing the list of the available methods to generate a sound from a spectrum.

    .. note::
        The method names used here must all correspond to existing synthesis method identifiers in
        the DPF Sound operators.
    """

    IFFT = "IFFT"
    """IFFT: sound generation method based on the Inverse Fast Fourier Transform of the input
    spectrum, using random phases."""

    Hybrid = "Hybrid"
    """Hybrid: sound generation method that combines generation of pure tones and IFFT.
    If peaks are detected in the input spectrum, they are generated as pure tones (sine waves).
    The rest is synthesized using the IFFT method."""


class SourceControlParent(SoundComposerParent):
    """
    Provides the abstract base class for the Sound Composer's source controls.

    This is the base class of all Sound Composer's source control classes and should not be used as
    is.
    """
