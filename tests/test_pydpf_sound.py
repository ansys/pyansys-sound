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

import numpy as np
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSound, PyAnsysSoundWarning


@pytest.mark.dependency()
def test_pyansys_sound_instanciate():
    pyansys_sound = PyAnsysSound()
    assert pyansys_sound != None


@pytest.mark.dependency(depends=["test_pyansys_sound_instanciate"])
def test_pyansys_sound_process():
    pyansys_sound = PyAnsysSound()
    with pytest.warns(PyAnsysSoundWarning, match="There is nothing to process."):
        pyansys_sound.process()
    assert pyansys_sound.process() == None


@pytest.mark.dependency(depends=["test_pyansys_sound_instanciate"])
def test_pyansys_sound_plot():
    pyansys_sound = PyAnsysSound()
    with pytest.warns(PyAnsysSoundWarning, match="There is nothing to plot."):
        pyansys_sound.plot()

    assert pyansys_sound.plot() == None


@pytest.mark.dependency(depends=["test_pyansys_sound_instanciate"])
def test_pyansys_sound_get_output():
    pyansys_sound = PyAnsysSound()
    with pytest.warns(PyAnsysSoundWarning, match="There is nothing to output."):
        pyansys_sound.get_output()
    out = pyansys_sound.get_output()
    assert out == None


@pytest.mark.dependency(depends=["test_pyansys_sound_instanciate"])
def test_pyansys_sound_get_output_as_nparray():
    pyansys_sound = PyAnsysSound()
    with pytest.warns(PyAnsysSoundWarning, match="There is nothing to output."):
        pyansys_sound.get_output_as_nparray()
    out = pyansys_sound.get_output_as_nparray()
    assert type(out) == type(np.empty(0))
    assert np.size(out) == 0
    assert np.shape(out) == (0,)
