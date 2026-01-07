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

"""Sound composer functions.

Helper functions related to the sound composer.
"""

from ._sound_composer_parent import SoundComposerParent
from ._source_control_parent import SourceControlParent, SpectrumSynthesisMethods
from ._source_parent import SourceParent
from .sound_composer import SoundComposer
from .source_audio import SourceAudio
from .source_broadband_noise import SourceBroadbandNoise
from .source_broadband_noise_two_parameters import SourceBroadbandNoiseTwoParameters
from .source_control_spectrum import SourceControlSpectrum
from .source_control_time import SourceControlTime
from .source_harmonics import SourceHarmonics
from .source_harmonics_two_parameters import SourceHarmonicsTwoParameters
from .source_spectrum import SourceSpectrum
from .track import Track

__all__ = (
    "SoundComposer",
    "Track",
    "SoundComposerParent",
    "SourceParent",
    "SourceControlParent",
    "SpectrumSynthesisMethods",
    "SourceSpectrum",
    "SourceControlSpectrum",
    "SourceHarmonicsTwoParameters",
    "SourceBroadbandNoise",
    "SourceBroadbandNoiseTwoParameters",
    "SourceHarmonics",
    "SourceHarmonicsTwoParameters",
    "SourceControlTime",
    "SourceAudio",
)
