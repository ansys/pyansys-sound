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

from ansys.dpf.core import Field
import numpy as np
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ansys.sound.core.signal_utilities import LoadWav, SumSignals


def test_sum_signals_instantiation():
    sum_gain = SumSignals()
    assert sum_gain != None


def test_sum_signals_process():
    sum_gain = SumSignals()
    wav_loader = LoadWav(pytest.data_path_white_noise)

    # Error 1
    with pytest.raises(PyAnsysSoundException) as excinfo:
        sum_gain.process()
    assert (
        str(excinfo.value)
        == "No signal to apply gain on. Use the 'SumSignals.set_signal()' method."
    )

    wav_loader.process()
    fc = wav_loader.get_output()

    # Testing input fields container (no error expected)
    sum_gain.signals = fc
    sum_gain.process()


def test_sum_signals_get_output():
    wav_loader = LoadWav(pytest.data_path_white_noise)
    wav_loader.process()
    fc_signal = wav_loader.get_output()
    sum_gain = SumSignals(signals=fc_signal)

    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. \
                        Use the 'SumSignals.process\\(\\)' method.",
    ):
        fc_out = sum_gain.get_output()

    sum_gain.process()
    f_out = sum_gain.get_output()

    assert len(f_out) == 480000
    assert f_out.data[1000] == 0.033935546875
    assert f_out.data[3456] == 0.22674560546875
    assert f_out.data[30000] == -0.72344970703125
    assert f_out.data[60000] == -0.13690185546875


def test_sum_signals_get_output_as_np_array():
    wav_loader = LoadWav(pytest.data_path_white_noise)
    wav_loader.process()
    fc_signal = wav_loader.get_output()
    sum_gain = SumSignals(signals=fc_signal)

    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. \
                        Use the 'SumSignals.process\\(\\)' method.",
    ):
        fc_out = sum_gain.get_output()

    sum_gain.process()
    out = sum_gain.get_output_as_nparray()

    assert len(out) == 480000
    assert out[1000] == 0.033935546875
    assert out[3456] == 0.22674560546875
    assert out[30000] == -0.72344970703125
    assert out[60000] == -0.13690185546875


def test_sum_signals_set_get_signals():
    """Test set and get signals."""
    sum_gain = SumSignals()

    signal = Field()
    signal.data = 42 * np.ones(3)
    signals = [signal, signal, signal]
    sum_gain.signals = signals
    signals_from_get = sum_gain.signals

    assert type(signals_from_get) == list
    assert type(signals_from_get[0]) == Field
    assert signals_from_get[0].data[0, 2] == 42


def test_sum_signals_set_signals_exceptions():
    """Test exceptions for signals setter."""
    sum_signals = SumSignals()

    with pytest.raises(
        PyAnsysSoundException,
        match="Input signals must be specified as a list of DPF fields.",
    ):
        sum_signals.signals = "WrongType"

    assert sum_signals.signals is None

    with pytest.raises(
        PyAnsysSoundException,
        match="Input signals must be specified as a list of DPF fields.",
    ):
        sum_signals.signals = [Field(), "WrongType", Field()]

    assert sum_signals.signals is None
