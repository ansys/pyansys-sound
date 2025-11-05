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

from unittest.mock import patch

import numpy as np
import pytest
from ansys.dpf.core import Field

from ansys.sound.core._pyansys_sound import (PyAnsysSoundException,
                                             PyAnsysSoundWarning)
from ansys.sound.core.psychoacoustics import TonalityAures
from ansys.sound.core.signal_utilities import LoadWav

EXP_TONALITY = 0.211909
EXP_ARRAY_LENGTH = 3247
EXP_TONALITY_OVER_TIME_345 = 0.3239536
EXP_WT_OVER_TIME_345 = 0.641006
EXP_WGR_OVER_TIME_345 = 0.2534436
EXP_TIME_345 = 2.801565
EXP_TONALITY_W1 = 0.0894490
EXP_STR_DEFAULT = (
    "TonalityAures object\n"
    "Data:\n"
    "\tSignal name: Not set\n"
    "\tOverlap: 90.0 %\n"
    "\tAccount for w1 weighting: No\n"
    "Tonality: Not processed"
)
EXP_STR_PROCESSED = (
    "TonalityAures object\n"
    "Data:\n"
    '\tSignal name: "Aircraft-App2"\n'
    "\tOverlap: 50.0 %\n"
    "\tAccount for w1 weighting: Yes\n"
    "\tw1 threshold: 5.0 dB\n"
    "Tonality: 0.09 tu"
)


def test_tonality_aures_instantiation():
    """Test TonalityAures instantiation."""
    tonality = TonalityAures()
    assert tonality.signal is None
    assert tonality.overlap == 90.0
    assert not tonality.account_for_w1
    assert tonality.w1_threshold == 3.0


def test_tonality_aures___str__():
    """Test TonalityAures __str__ method."""
    tonality = TonalityAures()
    assert str(tonality) == EXP_STR_DEFAULT

    wav_loader = LoadWav(pytest.data_path_aircraft_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality.signal = fc[0]
    tonality.overlap = 50.0
    tonality.account_for_w1 = True
    tonality.w1_threshold = 5.0
    tonality.process()
    assert str(tonality) == EXP_STR_PROCESSED


def test_tonality_aures_properties():
    """Test TonalityAures properties."""
    tonality = TonalityAures()

    tonality.signal = Field()
    assert type(tonality.signal) == Field

    tonality.overlap = 50.0
    assert tonality.overlap == 50.0

    tonality.account_for_w1 = True
    assert tonality.account_for_w1

    tonality.w1_threshold = 5.0
    assert tonality.w1_threshold == 5.0


def test_tonality_aures_properties_exceptions():
    """Test TonalityAures properties exceptions."""
    tonality = TonalityAures()

    with pytest.raises(PyAnsysSoundException, match="Signal must be specified as a DPF field."):
        tonality.signal = "Invalid"

    with pytest.raises(
        PyAnsysSoundException,
        match="Overlap must be greater than or equal to 0 %, and strictly smaller than 100 %.",
    ):
        tonality.overlap = -1.0

    with pytest.raises(
        PyAnsysSoundException,
        match="Threshold for the bandwidth weighting must be greater than or equal to 0 dB.",
    ):
        tonality.w1_threshold = -1.0


def test_tonality_aures_process():
    """Test TonalityAures process method."""
    tonality = TonalityAures()

    wav_loader = LoadWav(pytest.data_path_aircraft_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality.signal = fc[0]
    tonality.process()
    assert tonality.get_output() is not None


def test_tonality_aures_process_exception():
    """Test TonalityAures process method's exception."""
    tonality = TonalityAures()

    with pytest.raises(
        PyAnsysSoundException,
        match="No input signal is set. Use TonalityAures.signal.",
    ):
        tonality.process()


def test_tonality_aures_get_output():
    """Test TonalityAures get_output method."""
    tonality = TonalityAures()

    wav_loader = LoadWav(pytest.data_path_aircraft_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality.signal = fc[0]
    tonality.process()
    output = tonality.get_output()
    assert len(output) == 4
    assert output[0] == pytest.approx(EXP_TONALITY)
    assert len(output[1].data) == EXP_ARRAY_LENGTH
    assert output[1].data[345] == pytest.approx(EXP_TONALITY_OVER_TIME_345)
    assert output[2].data[345] == pytest.approx(EXP_WT_OVER_TIME_345)
    assert output[3].data[345] == pytest.approx(EXP_WGR_OVER_TIME_345)


def test_tonality_aures_get_output_warning():
    """Test TonalityAures get_output method's warning."""
    tonality = TonalityAures()

    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the TonalityAures.process\\(\\) method.",
    ):
        output = tonality.get_output()
    assert output is None


def test_tonality_aures_get_output_as_nparray():
    """Test TonalityAures get_output_as_nparray method."""
    tonality = TonalityAures()

    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the TonalityAures.process\\(\\) method.",
    ):
        output = tonality.get_output_as_nparray()
    assert len(output) == 5
    assert len(output[0]) == 0
    assert len(output[1]) == 0
    assert len(output[2]) == 0
    assert len(output[3]) == 0
    assert len(output[4]) == 0

    wav_loader = LoadWav(pytest.data_path_aircraft_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality.signal = fc[0]
    tonality.process()
    output = tonality.get_output_as_nparray()
    assert len(output) == 5
    assert type(output[0]) == np.ndarray
    assert len(output[0]) == 1
    assert output[0][0] == pytest.approx(EXP_TONALITY)
    assert type(output[1]) == np.ndarray
    assert len(output[1]) == EXP_ARRAY_LENGTH
    assert output[1][345] == pytest.approx(EXP_TONALITY_OVER_TIME_345)
    assert type(output[2]) == np.ndarray
    assert len(output[2]) == EXP_ARRAY_LENGTH
    assert output[2][345] == pytest.approx(EXP_WT_OVER_TIME_345)
    assert type(output[3]) == np.ndarray
    assert len(output[3]) == EXP_ARRAY_LENGTH
    assert output[3][345] == pytest.approx(EXP_WGR_OVER_TIME_345)
    assert type(output[4]) == np.ndarray
    assert len(output[4]) == EXP_ARRAY_LENGTH
    assert output[4][345] == pytest.approx(EXP_TIME_345)


def test_tonality_aures_get_tonality():
    """Test TonalityAures get_tonality method."""
    tonality = TonalityAures()

    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the TonalityAures.process\\(\\) method.",
    ):
        output = tonality.get_tonality()
    assert np.isnan(output)

    wav_loader = LoadWav(pytest.data_path_aircraft_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality.signal = fc[0]
    tonality.process()
    output = tonality.get_tonality()
    assert type(output) == np.float64
    assert output == pytest.approx(EXP_TONALITY)


def test_tonality_aures_get_tonality_over_time():
    """Test TonalityAures get_tonality_over_time method."""
    tonality = TonalityAures()

    wav_loader = LoadWav(pytest.data_path_aircraft_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality.signal = fc[0]
    tonality.process()
    output = tonality.get_tonality_over_time()
    assert type(output) == np.ndarray
    assert len(output) == EXP_ARRAY_LENGTH
    assert output[345] == pytest.approx(EXP_TONALITY_OVER_TIME_345)


def test_tonality_aures_get_tonal_weighting_over_time():
    """Test TonalityAures get_tonal_weighting_over_time method."""
    tonality = TonalityAures()

    wav_loader = LoadWav(pytest.data_path_aircraft_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality.signal = fc[0]
    tonality.process()
    output = tonality.get_tonal_weighting_over_time()
    assert type(output) == np.ndarray
    assert len(output) == EXP_ARRAY_LENGTH
    assert output[345] == pytest.approx(EXP_WT_OVER_TIME_345)


def test_tonality_aures_get_loudness_weighting_over_time():
    """Test TonalityAures get_loudness_weighting_over_time method."""
    tonality = TonalityAures()

    wav_loader = LoadWav(pytest.data_path_aircraft_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality.signal = fc[0]
    tonality.process()
    output = tonality.get_loudness_weighting_over_time()
    assert type(output) == np.ndarray
    assert len(output) == EXP_ARRAY_LENGTH
    assert output[345] == pytest.approx(EXP_WGR_OVER_TIME_345)


def test_tonality_aures_get_time_scale():
    """Test TonalityAures get_time_scale method."""
    tonality = TonalityAures()

    wav_loader = LoadWav(pytest.data_path_aircraft_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality.signal = fc[0]
    tonality.process()
    output = tonality.get_time_scale()
    assert type(output) == np.ndarray
    assert len(output) == EXP_ARRAY_LENGTH
    assert output[345] == pytest.approx(EXP_TIME_345)


@patch("matplotlib.pyplot.show")
def test_tonality_aures_plot(mock_show):
    """Test TonalityAures plot method."""
    tonality = TonalityAures()

    wav_loader = LoadWav(pytest.data_path_aircraft_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality.signal = fc[0]
    tonality.process()
    tonality.plot()


def test_tonality_aures_plot_exception():
    """Test TonalityAures plot method's exception."""
    tonality = TonalityAures()

    with pytest.raises(
        PyAnsysSoundException,
        match="Output is not processed yet. Use the TonalityAures.process\\(\\) method.",
    ):
        tonality.plot()
