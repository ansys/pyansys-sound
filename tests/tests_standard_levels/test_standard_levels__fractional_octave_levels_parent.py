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

import pytest

from ansys.sound.core.standard_levels import FractionalOctaveLevelsParent

# Skip entire test module if server < 11.0
if not pytest.SERVERS_VERSION_GREATER_THAN_OR_EQUAL_TO_11_0:
    pytest.skip("Requires server version >= 11.0", allow_module_level=True)

# Note: This class' methods and properties are mostly tested in subclasses' tests. Here are only
# tested the class' protected methods.

EXP_A_WEIGHTS_100 = -19.14515
EXP_A_WEIGHTS_1000 = 0.0
EXP_A_WEIGHTS_4000 = 0.964229
EXP_A_WEIGHTS_10000 = -2.488333
EXP_B_WEIGHTS_100 = -5.647791
EXP_B_WEIGHTS_1000 = 0.0
EXP_B_WEIGHTS_4000 = -0.7242990
EXP_B_WEIGHTS_10000 = -4.295534
EXP_C_WEIGHTS_100 = -0.2997242
EXP_C_WEIGHTS_1000 = 0.0
EXP_C_WEIGHTS_4000 = -0.8252422
EXP_C_WEIGHTS_10000 = -4.4022


def test__fractional_octave_levels_parent__get_frequency_weightings():
    """Test FractionalOctaveLevelsParent _get_frequency_weightings method."""
    level_obj = FractionalOctaveLevelsParent()

    assert level_obj._operator_id_frequency_weighting == "get_frequency_weighting"

    frequencies = [100, 1000, 4000, 10000]

    # Check A-weighted levels
    level_obj.frequency_weighting = "A"
    weights = level_obj._get_frequency_weightings(frequencies)
    assert weights[0] == pytest.approx(EXP_A_WEIGHTS_100)
    assert weights[1] == pytest.approx(EXP_A_WEIGHTS_1000)
    assert weights[2] == pytest.approx(EXP_A_WEIGHTS_4000)
    assert weights[3] == pytest.approx(EXP_A_WEIGHTS_10000)

    # Check B-weighted levels
    level_obj.frequency_weighting = "B"
    weights = level_obj._get_frequency_weightings(frequencies)
    assert weights[0] == pytest.approx(EXP_B_WEIGHTS_100)
    assert weights[1] == pytest.approx(EXP_B_WEIGHTS_1000)
    assert weights[2] == pytest.approx(EXP_B_WEIGHTS_4000)
    assert weights[3] == pytest.approx(EXP_B_WEIGHTS_10000)

    # Check C-weighted levels
    level_obj.frequency_weighting = "C"
    weights = level_obj._get_frequency_weightings(frequencies)
    assert weights[0] == pytest.approx(EXP_C_WEIGHTS_100)
    assert weights[1] == pytest.approx(EXP_C_WEIGHTS_1000)
    assert weights[2] == pytest.approx(EXP_C_WEIGHTS_4000)
    assert weights[3] == pytest.approx(EXP_C_WEIGHTS_10000)

    # Check unweighted levels
    level_obj.frequency_weighting = ""
    weights = level_obj._get_frequency_weightings(frequencies)
    assert weights[0] == 0.0
    assert weights[1] == 0.0
    assert weights[2] == 0.0
    assert weights[3] == 0.0
