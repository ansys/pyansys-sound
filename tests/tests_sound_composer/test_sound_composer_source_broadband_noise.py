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

import warnings

from ansys.dpf.core import (
    FieldsContainer,
    Operator,
)
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundWarning

REF_ACOUSTIC_POWER = 4e-10

EXP_LEVEL_OCTAVE_BAND = 41.0
EXP_SPECTRUM_DATA03 = 5.0357002692180686e-06
EXP_STR_NOT_SET = "Broadband noise source: Not set\nSource control: Not set"
EXP_STR_ALL_SET = (
    "Broadband noise source: ''\n"
    "\tSpectrum type: Octave\n"
    "\tSpectrum count: 5\n"
    "\tControl parameter: Speed of wind, m/s\n"
    "\t\t[ 1.   2.   5.3 10.5 27.8]"
    "\nSource control: \n"
    "\tMin: 1.0 m/s\n"
    "\tMax: 10.0 m/s\n"
    "\tDuration: 3.0 s"
)
EXP_STR_ALL_SET_40_VALUES = (
    "Broadband noise source: ''\n"
    "\tSpectrum type: Narrow band (DeltaF: 10.0 Hz)\n"
    "\tSpectrum count: 40\n"
    "\tControl parameter: Speed of wind, m/s\n"
    "\t\t[1. 2. 3. 4. 5. ... 36. 37. 38. 39. 40.]"
    "\nSource control: \n"
    "\tMin: 1.0 m/s\n"
    "\tMax: 10.0 m/s\n"
    "\tDuration: 3.0 s"
)


def test_source_broadband_noise_set_from_generic_data_containers():
    """Test SourceBroadbandNoise set_from_generic_data_containers method."""
    for i in range(1, 1000):
        if i % 100 == 0:
            warnings.warn(PyAnsysSoundWarning(f"Loop iteration {i}"))
        print(i)
        op = Operator("sound_composer_load_source_bbn")
        op.connect(0, pytest.data_path_sound_composer_bbn_source_in_container)
        op.run()
        fc_data: FieldsContainer = op.get_output(0, "fields_container")
