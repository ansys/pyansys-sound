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

"""Signal utilities functions.

Helper functions related to signal management.
"""

from ._signal_utilities_parent import SignalUtilitiesParent  # isort:skip
from .apply_gain import ApplyGain
from .create_sound_field import CreateSoundField
from .crop_signal import CropSignal
from .load_wav import LoadWav
from .resample import Resample
from .sum_signals import SumSignals
from .write_wav import WriteWav
from .zero_pad import ZeroPad

__all__ = (
    "SignalUtilitiesParent",
    "LoadWav",
    "WriteWav",
    "Resample",
    "ZeroPad",
    "ApplyGain",
    "SumSignals",
    "CropSignal",
    "CreateSoundField",
)
