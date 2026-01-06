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

"""Psychoacoustics functions.

Helper functions related to the computation of psychoacoustics indicators.
"""

from ._psychoacoustics_parent import FIELD_DIFFUSE, FIELD_FREE, PsychoacousticsParent
from .fluctuation_strength import FluctuationStrength
from .loudness_ansi_s3_4 import LoudnessANSI_S3_4
from .loudness_iso_532_1_stationary import LoudnessISO532_1_Stationary
from .loudness_iso_532_1_time_varying import LoudnessISO532_1_TimeVarying
from .loudness_iso_532_2 import LoudnessISO532_2
from .prominence_ratio import ProminenceRatio
from .prominence_ratio_for_orders_over_time import ProminenceRatioForOrdersOverTime
from .roughness import Roughness
from .sharpness import Sharpness
from .sharpness_din_45692 import SharpnessDIN45692
from .sharpness_din_45692_over_time import SharpnessDIN45692OverTime
from .sharpness_over_time import SharpnessOverTime
from .spectral_centroid import SpectralCentroid
from .tonality_aures import TonalityAures
from .tonality_din_45681 import TonalityDIN45681
from .tonality_ecma_418_2 import TonalityECMA418_2
from .tonality_iso_1996_2 import TonalityISO1996_2
from .tonality_iso_1996_2_over_time import TonalityISO1996_2_OverTime
from .tonality_iso_ts_20065 import TonalityISOTS20065
from .tone_to_noise_ratio import ToneToNoiseRatio
from .tone_to_noise_ratio_for_orders_over_time import ToneToNoiseRatioForOrdersOverTime

__all__ = (
    "PsychoacousticsParent",
    "LoudnessISO532_1_Stationary",
    "LoudnessISO532_1_TimeVarying",
    "LoudnessISO532_2",
    "LoudnessANSI_S3_4",
    "ProminenceRatio",
    "ToneToNoiseRatio",
    "Sharpness",
    "SharpnessDIN45692",
    "SharpnessDIN45692OverTime",
    "SharpnessOverTime",
    "Roughness",
    "FluctuationStrength",
    "TonalityDIN45681",
    "TonalityISOTS20065",
    "TonalityISO1996_2_OverTime",
    "TonalityAures",
    "SpectralCentroid",
    "TonalityECMA418_2",
    "ToneToNoiseRatioForOrdersOverTime",
    "TonalityISO1996_2",
    "ProminenceRatioForOrdersOverTime",
    "FIELD_FREE",
    "FIELD_DIFFUSE",
)
