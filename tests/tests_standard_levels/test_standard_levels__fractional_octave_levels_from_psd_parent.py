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

from ansys.sound.core._pyansys_sound import PyAnsysSoundException
from ansys.sound.core.standard_levels import FractionalOctaveLevelsFromPSDParent

# Skip entire test module if server < 11.0
if not pytest.SERVERS_VERSION_GREATER_THAN_OR_EQUAL_TO_11_0:
    pytest.skip("Requires server version >= 11.0", allow_module_level=True)


def test__fractional_octave_levels_from_psd_parent_process_exceptions():
    """Test FractionalOctaveLevelsFromPSDParent process method exceptions.

    This class' tests are covered by the tests of subclasses OctaveLevelsFromPSD and
    OneThirdOctaveLevelsFromPSD. Here is only tested the single path that cannot be tested in these
    subclasses, which is the exception thrown when calling process() from an instance of this
    parent class.
    """
    level_obj = FractionalOctaveLevelsFromPSDParent()

    assert level_obj._operator_id_levels_computation is None
    assert level_obj._operator_id_levels_computation_ansi is None

    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "This method cannot be called from class FractionalOctaveLevelsFromPSDParent. "
            "This class is meant as an abstract class that should not be used directly."
        ),
    ):
        level_obj.process()
