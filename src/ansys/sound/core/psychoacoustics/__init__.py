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

"""Psychoacoustics functions.

Helper functions related to the computation of psychoacoustics indicators.
"""

from ._psychoacoustics_parent import PsychoacousticsParent
from .fluctuation_strength import FluctuationStrength
from .loudness_iso_532_1_stationary import LoudnessISO532_1_Stationary
from .loudness_iso_532_1_time_varying import LoudnessISO532_1_TimeVarying
from .prominence_ratio import ProminenceRatio
from .roughness import Roughness
from .sharpness import Sharpness
from .tone_to_noise_ratio import ToneToNoiseRatio

__all__ = (
    "PsychoacousticsParent",
    "LoudnessISO532_1_Stationary",
    "LoudnessISO532_1_TimeVarying",
    "ProminenceRatio",
    "ToneToNoiseRatio",
    "Sharpness",
    "Roughness",
    "FluctuationStrength",
)
