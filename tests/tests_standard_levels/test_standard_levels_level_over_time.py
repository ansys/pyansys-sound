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

from ansys.dpf.core import Field
import numpy as np
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ansys.sound.core.signal_utilities import LoadWav
from ansys.sound.core.standard_levels import LevelOverTime

EXP_STR_NOT_SET = (
    "LevelOverTime object.\nData\n\tSignal: Not set\n\tScale type: dB\n\tReference value: 1.0\n"
    "\tFrequency weighting: None\n\tTime weighting: Fast\nMaximum level: Not processed"
)
EXP_STR_ALL_SET = (
    'LevelOverTime object.\nData\n\tSignal: "flute"\n\tScale type: dB\n\tReference value: 1.0\n'
    "\tFrequency weighting: None\n\tTime weighting: Custom\n\tTime step: 100.0 ms\n"
    "\tWindow size: 5000.0 ms\n\tAnalysis window: HANN\nMaximum level: Not processed"
)
if pytest.SERVERS_VERSION_GREATER_THAN_OR_EQUAL_TO_11_0:
    # bug fix in DPF Sound 2026 R1 ID#1288971
    EXP_STR_ALL_PROCESSED = (
        'LevelOverTime object.\nData\n\tSignal: "flute"\n\tScale type: dB\n'
        "\tReference value: 2e-05\n\tFrequency weighting: None\n\tTime weighting: Custom\n"
        "\tTime step: 100.0 ms\n\tWindow size: 5000.0 ms\n\tAnalysis window: HANN\n"
        "Maximum level: 89.2 dB (re. 2e-05 Pa)"
    )
else:
    EXP_STR_ALL_PROCESSED = (
        'LevelOverTime object.\nData\n\tSignal: "flute"\n\tScale type: dB\n'
        "\tReference value: 2e-05\n\tFrequency weighting: None\n\tTime weighting: Custom\n"
        "\tTime step: 100.0 ms\n\tWindow size: 5000.0 ms\n\tAnalysis window: HANN\n"
        "Maximum level: 89.2 dB"
    )

EXP_LEVEL_MAX_DEFAULT = -3.72917
EXP_LEVEL_12 = -16.7062
EXP_TIME_12 = 0.300003
EXP_LEVEL_MAX_RMS = 0.650941
EXP_LEVEL_MAX_SPL = 90.2502
EXP_LEVEL_MAX_A = 89.0532
EXP_LEVEL_MAX_B = 90.0780
EXP_LEVEL_MAX_C = 90.2438
EXP_LEVEL_MAX_SLOW = 88.7946
EXP_LEVEL_MAX_IMPULSE = 90.6944
EXP_LEVEL_MAX_CUSTOM = 89.1737


def test_level_over_time_instantiation():
    """Test LevelOverTime instantiation."""
    level_obj = LevelOverTime()
    assert level_obj.signal == None
    assert level_obj.scale == "dB"
    assert level_obj.reference_value == 1.0
    assert level_obj.frequency_weighting == ""
    assert level_obj.time_weighting == "Fast"


def test_level_over_time_properties():
    """Test LevelOverTime properties."""
    level_obj = LevelOverTime()
    level_obj.signal = Field()
    assert type(level_obj.signal) == Field

    level_obj.scale = "RMS"
    assert level_obj.scale == "RMS"

    level_obj.reference_value = 2e-5
    assert level_obj.reference_value == 2e-5

    level_obj.frequency_weighting = "A"
    assert level_obj.frequency_weighting == "A"

    level_obj.time_weighting = "Slow"
    assert level_obj.time_weighting == "Slow"


def test_level_over_time_properties_exceptions():
    """Test LevelOverTime properties exceptions."""
    level_obj = LevelOverTime()
    with pytest.raises(PyAnsysSoundException, match="The signal must be provided as a DPF field."):
        level_obj.signal = "InvalidType"

    with pytest.raises(PyAnsysSoundException, match="The scale type must be either 'dB' or 'RMS'."):
        level_obj.scale = "Invalid"

    with pytest.raises(
        PyAnsysSoundException, match="The reference value must be strictly positive."
    ):
        level_obj.reference_value = -1

    with pytest.raises(
        PyAnsysSoundException,
        match="The frequency weighting must be one of \\['', 'A', 'B', 'C'\\].",
    ):
        level_obj.frequency_weighting = "Invalid"

    with pytest.raises(
        PyAnsysSoundException,
        match="The time weighting must be one of \\['Fast', 'Slow', 'Impulse', 'Custom'\\].",
    ):
        level_obj.time_weighting = "Invalid"


def test_level_over_time___str__():
    """Test LevelOverTime __str__ method."""
    level_obj = LevelOverTime()
    assert str(level_obj) == EXP_STR_NOT_SET

    loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    loader.process()
    f_signal = loader.get_output()[0]

    level_obj.signal = f_signal
    level_obj.set_custom_parameters(time_step=100.0, window_size=5000.0, analysis_window="HANN")
    assert str(level_obj) == EXP_STR_ALL_SET

    level_obj.reference_value = 2e-5
    level_obj.process()
    assert str(level_obj) == EXP_STR_ALL_PROCESSED


def test_level_over_time_set_custom_parameters():
    """Test LevelOverTime set_custom_parameters method."""
    level_obj = LevelOverTime()
    level_obj.set_custom_parameters(time_step=100.0, window_size=5000.0, analysis_window="HANN")
    assert level_obj.time_weighting == "Custom"


def test_level_over_time_set_custom_parameters_exceptions():
    """Test LevelOverTime set_custom_parameters method exceptions."""
    level_obj = LevelOverTime()
    with pytest.raises(
        PyAnsysSoundException,
        match="The time step must be strictly positive.",
    ):
        level_obj.set_custom_parameters(time_step=0, window_size=5000.0, analysis_window="HANN")

    with pytest.raises(
        PyAnsysSoundException,
        match="The window size must be strictly positive.",
    ):
        level_obj.set_custom_parameters(time_step=100.0, window_size=0, analysis_window="HANN")

    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "The analysis window must be one of \\['RECTANGULAR', 'HANN', 'HAMMING', 'BLACKMAN', "
            "'BLACKMAN-HARRIS', 'BARTLETT'\\]."
        ),
    ):
        level_obj.set_custom_parameters(
            time_step=100.0, window_size=5000.0, analysis_window="Invalid"
        )


def test_level_over_time_process():
    """Test LevelOverTime process method."""
    loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    loader.process()
    f_signal = loader.get_output()[0]

    level_obj = LevelOverTime(signal=f_signal)
    level_obj.process()
    assert level_obj.get_output() is not None


def test_level_over_time_process_exceptions():
    """Test LevelOverTime process method exceptions."""
    level_obj = LevelOverTime()
    with pytest.raises(
        PyAnsysSoundException,
        match="No input signal is set. Use LevelOverTime.signal.",
    ):
        level_obj.process()


def test_level_over_time_get_output():
    """Test LevelOverTime get_output method."""
    loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    loader.process()
    f_signal = loader.get_output()[0]

    level_obj = LevelOverTime(signal=f_signal)
    level_obj.process()
    output = level_obj.get_output()
    assert len(output) == 2
    assert output[0] == pytest.approx(EXP_LEVEL_MAX_DEFAULT)
    assert type(output[1]) == Field


def test_level_over_time_get_output_warnings():
    """Test LevelOverTime get_output method warnings."""
    level_obj = LevelOverTime()
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the LevelOverTime.process\\(\\) method.",
    ):
        output = level_obj.get_output()
    assert output is None


def test_level_over_time_get_output_as_nparray():
    """Test LevelOverTime get_output_as_nparray method."""
    loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    loader.process()
    f_signal = loader.get_output()[0]

    level_obj = LevelOverTime(signal=f_signal)
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the LevelOverTime.process\\(\\) method.",
    ):
        output = level_obj.get_output_as_nparray()
    assert np.isnan(output[0])
    assert len(output[1]) == 0

    level_obj.process()
    output = level_obj.get_output_as_nparray()
    assert output[0] == pytest.approx(EXP_LEVEL_MAX_DEFAULT)
    assert type(output[1]) == np.ndarray
    assert output[1][12] == pytest.approx(EXP_LEVEL_12)
    assert type(output[2]) == np.ndarray
    assert output[2][12] == pytest.approx(EXP_TIME_12)


def test_level_over_time_get_level_max():
    """Test LevelOverTime get_level_max method."""
    loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    loader.process()
    f_signal = loader.get_output()[0]

    level_obj = LevelOverTime(signal=f_signal)
    level_obj.process()
    output = level_obj.get_level_max()
    assert type(output) == float
    assert output == pytest.approx(EXP_LEVEL_MAX_DEFAULT)

    level_obj.scale = "RMS"
    level_obj.process()
    assert level_obj.get_level_max() == pytest.approx(EXP_LEVEL_MAX_RMS)

    level_obj.scale = "dB"
    level_obj.reference_value = 2e-5
    level_obj.process()
    assert level_obj.get_level_max() == pytest.approx(EXP_LEVEL_MAX_SPL)

    level_obj.frequency_weighting = "A"
    level_obj.process()
    assert level_obj.get_level_max() == pytest.approx(EXP_LEVEL_MAX_A)

    level_obj.frequency_weighting = "B"
    level_obj.process()
    assert level_obj.get_level_max() == pytest.approx(EXP_LEVEL_MAX_B)

    level_obj.frequency_weighting = "C"
    level_obj.process()
    assert level_obj.get_level_max() == pytest.approx(EXP_LEVEL_MAX_C)

    level_obj.time_weighting = "Slow"
    level_obj.process()
    assert level_obj.get_level_max() == pytest.approx(EXP_LEVEL_MAX_SLOW)

    level_obj.time_weighting = "Impulse"
    level_obj.process()
    assert level_obj.get_level_max() == pytest.approx(EXP_LEVEL_MAX_IMPULSE)

    level_obj.frequency_weighting = ""
    level_obj.set_custom_parameters(time_step=100.0, window_size=5000.0, analysis_window="HANN")
    level_obj.process()
    assert level_obj.get_level_max() == pytest.approx(EXP_LEVEL_MAX_CUSTOM)


def test_level_over_time_get_level_over_time():
    """Test LevelOverTime get_level_over_time method."""
    loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    loader.process()
    f_signal = loader.get_output()[0]

    level_obj = LevelOverTime(signal=f_signal)
    level_obj.process()
    output = level_obj.get_level_over_time()
    assert type(output) == np.ndarray
    assert output[12] == pytest.approx(EXP_LEVEL_12)


def test_level_over_time_get_time_scale():
    """Test LevelOverTime get_time_scale method."""
    loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    loader.process()
    f_signal = loader.get_output()[0]

    level_obj = LevelOverTime(signal=f_signal)
    level_obj.process()
    output = level_obj.get_time_scale()
    assert type(output) == np.ndarray
    assert output[12] == pytest.approx(EXP_TIME_12)


@patch("matplotlib.pyplot.show")
def test_level_over_time_plot(mock_show):
    """Test LevelOverTime plot method."""
    loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    loader.process()
    f_signal = loader.get_output()[0]

    level_obj = LevelOverTime(signal=f_signal)
    level_obj.process()
    level_obj.plot()

    level_obj.scale = "RMS"
    level_obj.process()
    level_obj.plot()

    level_obj.scale = "dB"
    level_obj.process()
    level_obj.plot()

    level_obj.reference_value = 2e-5
    level_obj.process()
    level_obj.plot()

    level_obj.frequency_weighting = "A"
    level_obj.process()
    level_obj.plot()


def test_level_over_time_plot_exceptions():
    """Test LevelOverTime plot method exceptions."""
    loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    loader.process()
    f_signal = loader.get_output()[0]

    level_obj = LevelOverTime(signal=f_signal)
    with pytest.raises(
        PyAnsysSoundException,
        match="Output is not processed yet. Use the LevelOverTime.process\\(\\) method.",
    ):
        level_obj.plot()
