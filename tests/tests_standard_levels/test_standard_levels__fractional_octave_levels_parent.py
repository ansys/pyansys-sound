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

from ansys.dpf.core import TimeFreqSupport, fields_factory, locations
import pytest

from ansys.sound.core.standard_levels import FractionalOctaveLevelsParent

# Skip entire test module if server < 11.0
if not pytest.SERVERS_VERSION_GREATER_THAN_OR_EQUAL_TO_11_0:
    pytest.skip("Requires server version >= 11.0", allow_module_level=True)

# Note: This class' methods and properties are mostly tested in subclasses' tests. Here are only
# tested the class' protected methods.

EXP_A_WEIGHTED_LEVEL_100 = -9.145153
EXP_A_WEIGHTED_LEVEL_1000 = 25.000000
EXP_A_WEIGHTED_LEVEL_4000 = 50.964229
EXP_A_WEIGHTED_LEVEL_10000 = 77.51167
EXP_B_WEIGHTED_LEVEL_100 = 4.352209
EXP_B_WEIGHTED_LEVEL_1000 = 25.000000
EXP_B_WEIGHTED_LEVEL_4000 = 49.27570
EXP_B_WEIGHTED_LEVEL_10000 = 75.70450
EXP_C_WEIGHTED_LEVEL_100 = 9.700276
EXP_C_WEIGHTED_LEVEL_1000 = 25.000000
EXP_C_WEIGHTED_LEVEL_4000 = 49.174800
EXP_C_WEIGHTED_LEVEL_10000 = 75.597800
EXP_DB_LEVEL_0_01 = -20.000000
EXP_DB_LEVEL_0_5 = -3.010300
EXP_DB_LEVEL_1 = 4.343331e-12
EXP_DB_LEVEL_5 = 6.989700


def test__fractional_octave_levels_parent__apply_frequency_weighting():
    """Test FractionalOctaveLevelsParent _apply_frequency_weighting method."""
    level_obj = FractionalOctaveLevelsParent()

    assert level_obj._operator_id_frequency_weighting == "get_frequency_weighting"

    # Artificially create band levels
    support = TimeFreqSupport()
    center_frequencies = fields_factory.create_scalar_field(
        num_entities=1, location=locations.time_freq
    )
    center_frequencies.append([100, 1000, 4000, 10000], 1)
    support.time_frequencies = center_frequencies
    levels_unweighted = fields_factory.create_scalar_field(
        num_entities=1, location=locations.time_freq
    )
    levels_unweighted.append([10, 25, 50, 80], 1)
    levels_unweighted.time_freq_support = support

    # Check A-weighted levels
    level_obj._output = levels_unweighted.deep_copy()
    level_obj.frequency_weighting = "A"
    level_obj._apply_frequency_weighting()
    assert level_obj._output.data[0] == pytest.approx(EXP_A_WEIGHTED_LEVEL_100)
    assert level_obj._output.data[1] == pytest.approx(EXP_A_WEIGHTED_LEVEL_1000)
    assert level_obj._output.data[2] == pytest.approx(EXP_A_WEIGHTED_LEVEL_4000)
    assert level_obj._output.data[3] == pytest.approx(EXP_A_WEIGHTED_LEVEL_10000)

    # Check B-weighted levels
    level_obj._output = levels_unweighted.deep_copy()
    level_obj.frequency_weighting = "B"
    level_obj._apply_frequency_weighting()
    assert level_obj._output.data[0] == pytest.approx(EXP_B_WEIGHTED_LEVEL_100)
    assert level_obj._output.data[1] == pytest.approx(EXP_B_WEIGHTED_LEVEL_1000)
    assert level_obj._output.data[2] == pytest.approx(EXP_B_WEIGHTED_LEVEL_4000)
    assert level_obj._output.data[3] == pytest.approx(EXP_B_WEIGHTED_LEVEL_10000)

    # Check C-weighted levels
    level_obj._output = levels_unweighted.deep_copy()
    level_obj.frequency_weighting = "C"
    level_obj._apply_frequency_weighting()
    assert level_obj._output.data[0] == pytest.approx(EXP_C_WEIGHTED_LEVEL_100)
    assert level_obj._output.data[1] == pytest.approx(EXP_C_WEIGHTED_LEVEL_1000)
    assert level_obj._output.data[2] == pytest.approx(EXP_C_WEIGHTED_LEVEL_4000)
    assert level_obj._output.data[3] == pytest.approx(EXP_C_WEIGHTED_LEVEL_10000)

    # Check unweighted levels
    level_obj._output = levels_unweighted.deep_copy()
    level_obj.frequency_weighting = ""
    level_obj._apply_frequency_weighting()
    assert level_obj._output.data[0] == 10.0
    assert level_obj._output.data[1] == 25.0
    assert level_obj._output.data[2] == 50.0
    assert level_obj._output.data[3] == 80.0


def test__fractional_octave_levels_parent__convert_output_to_dB():
    """Test FractionalOctaveLevelsParent _convert_output_to_dB method."""
    level_obj = FractionalOctaveLevelsParent()

    # Artificially create band levels
    support = TimeFreqSupport()
    center_frequencies = fields_factory.create_scalar_field(
        num_entities=1, location=locations.time_freq
    )
    center_frequencies.append([100, 1000, 4000, 10000], 1)
    support.time_frequencies = center_frequencies
    levels_unweighted = fields_factory.create_scalar_field(
        num_entities=1, location=locations.time_freq
    )
    levels_unweighted.append([0.01, 0.5, 1, 5], 1)
    levels_unweighted.time_freq_support = support

    # Check dB conversion
    level_obj._output = levels_unweighted
    level_obj._convert_output_to_dB()
    assert level_obj._output.data[0] == pytest.approx(EXP_DB_LEVEL_0_01)
    assert level_obj._output.data[1] == pytest.approx(EXP_DB_LEVEL_0_5)
    assert level_obj._output.data[2] == pytest.approx(EXP_DB_LEVEL_1)
    assert level_obj._output.data[3] == pytest.approx(EXP_DB_LEVEL_5)
