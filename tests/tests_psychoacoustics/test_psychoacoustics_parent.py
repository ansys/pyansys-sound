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

import numpy as np
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundException
from ansys.sound.core.psychoacoustics import PsychoacousticsParent


def test_psychoacoustics_parent_instantiation():
    psychoacoustics_parent = PsychoacousticsParent()
    assert psychoacoustics_parent != None


def test_psychoacoustics_convert_bark_to_hertz():
    psychoacoustics_parent = PsychoacousticsParent()

    # Invalid Bark band index -> error
    with pytest.raises(
        PyAnsysSoundException,
        match="Specified Bark band indexes must be between 0.0 and 24.0 Bark.",
    ):
        bark_band_frequencies = psychoacoustics_parent._convert_bark_to_hertz(
            bark_band_indexes=np.array([-1])
        )

    # Check output for some valid indexes
    bark_band_indexes = np.array([0, 0.1, 1, 6, 8.5, 15.3, 24])
    bark_band_frequencies = psychoacoustics_parent._convert_bark_to_hertz(
        bark_band_indexes=bark_band_indexes
    )
    assert type(bark_band_frequencies) == np.ndarray
    assert len(bark_band_frequencies) == len(bark_band_indexes)
    assert bark_band_frequencies[0] == pytest.approx(12.764378478664192)
    assert bark_band_frequencies[1] == pytest.approx(21.33995918005147)
    assert bark_band_frequencies[4] == pytest.approx(975.1181102362203)
    assert bark_band_frequencies[6] == pytest.approx(15334.573030003306)
