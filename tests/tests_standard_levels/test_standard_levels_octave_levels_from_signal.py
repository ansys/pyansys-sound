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
from ansys.sound.core.signal_utilities.load_wav import LoadWav
from ansys.sound.core.standard_levels import OctaveLevelsFromSignal

# Skip entire test module if server < 11.0
if not pytest.SERVERS_VERSION_GREATER_THAN_OR_EQUAL_TO_11_0:
    pytest.skip("Requires server version >= 11.0", allow_module_level=True)

EXP_STR_NOT_SET = (
    "OctaveLevelsFromSignal object.\nData\n\tSignal: Not set\n\tReference value: 1.0\n"
    "\tFrequency weighting: None\nOutput levels: Not processed"
)
EXP_STR_ALL_SET = (
    'OctaveLevelsFromSignal object.\nData\n\tSignal: "Name of the signal"\n'
    "\tReference value: 2e-05\n\tFrequency weighting: A\nOutput levels: Not processed"
)
EXP_STR_ALL_PROCESSED = (
    'OctaveLevelsFromSignal object.\nData\n\tSignal: "Name of the signal"\n'
    "\tReference value: 2e-05\n\tFrequency weighting: A\nOutput levels:\n"
    "\t31.5 Hz:\t-18.4 dBA (re 2e-05)\n"
    "\t63.0 Hz:\t6.2 dBA (re 2e-05)\n"
    "\t125.0 Hz:\t26.9 dBA (re 2e-05)\n"
    "\t250.0 Hz:\t68.3 dBA (re 2e-05)\n"
    "\t500.0 Hz:\t81.9 dBA (re 2e-05)\n"
    "\t1000.0 Hz:\t82.6 dBA (re 2e-05)\n"
    "\t2000.0 Hz:\t81.3 dBA (re 2e-05)\n"
    "\t4000.0 Hz:\t60.4 dBA (re 2e-05)\n"
    "\t8000.0 Hz:\t50.6 dBA (re 2e-05)\n"
    "\t16000.0 Hz:\t39.1 dBA (re 2e-05)"
)
EXP_BAND_COUNT = 10
EXP_LEVEL_DEFAULT_0 = -77.09024
EXP_LEVEL_DEFAULT_3 = -17.12080
EXP_LEVEL_DEFAULT_5 = -10.74725
EXP_LEVEL_DEFAULT_7 = -34.6444
EXP_LEVEL_DEFAULT_9 = -50.3817
EXP_LEVEL_A_PA_0 = -18.40589
EXP_LEVEL_A_PA_3 = 68.28658
EXP_LEVEL_A_PA_5 = 82.59591
EXP_LEVEL_A_PA_7 = 60.37881
EXP_LEVEL_A_PA_9 = 39.12920
EXP_LEVEL_B_PA_0 = 2.213288
EXP_LEVEL_B_PA_3 = 75.51890
EXP_LEVEL_B_PA_5 = 83.19813
EXP_LEVEL_B_PA_7 = 58.72937
EXP_LEVEL_B_PA_9 = 37.31334
EXP_LEVEL_C_PA_0 = 14.64082
EXP_LEVEL_C_PA_3 = 76.85878
EXP_LEVEL_C_PA_5 = 83.24699
EXP_LEVEL_C_PA_7 = 58.63037
EXP_LEVEL_C_PA_9 = 37.20627
EXP_FREQUENCY_0 = 31.5
EXP_FREQUENCY_3 = 250.0
EXP_FREQUENCY_5 = 1000.0
EXP_FREQUENCY_7 = 4000.0
EXP_FREQUENCY_9 = 16000.0


def test_octave_levels_from_signal_instantiation():
    """Test OctaveLevelsFromSignal instantiation."""
    level_obj = OctaveLevelsFromSignal()
    assert level_obj.signal == None
    assert level_obj.reference_value == 1.0
    assert level_obj.frequency_weighting == ""


def test_octave_levels_from_signal_properties():
    """Test OctaveLevelsFromSignal properties."""
    level_obj = OctaveLevelsFromSignal()
    level_obj.signal = Field()
    assert type(level_obj.signal) == Field

    level_obj.reference_value = 2e-5
    assert level_obj.reference_value == 2e-5

    level_obj.frequency_weighting = "A"
    assert level_obj.frequency_weighting == "A"


def test_octave_levels_from_signal_properties_exceptions():
    """Test OctaveLevelsFromSignal properties exceptions."""
    level_obj = OctaveLevelsFromSignal()
    with pytest.raises(
        PyAnsysSoundException,
        match="The input signal must be provided as a DPF field.",
    ):
        level_obj.signal = "InvalidType"

    with pytest.raises(
        PyAnsysSoundException, match="The reference value must be strictly positive."
    ):
        level_obj.reference_value = -1

    with pytest.raises(
        PyAnsysSoundException,
        match="The frequency weighting must be one of \\['', 'A', 'B', 'C'\\].",
    ):
        level_obj.frequency_weighting = "Invalid"


def test_octave_levels_from_signal___str__():
    """Test OctaveLevelsFromSignal __str__ method."""
    level_obj = OctaveLevelsFromSignal()
    assert str(level_obj) == EXP_STR_NOT_SET

    loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    loader.process()
    signal = loader.get_output()[0]
    signal.name = "Name of the signal"

    level_obj.signal = signal
    level_obj.reference_value = 2e-5
    level_obj.frequency_weighting = "A"
    assert str(level_obj) == EXP_STR_ALL_SET

    level_obj.process()
    assert str(level_obj) == EXP_STR_ALL_PROCESSED


def test_octave_levels_from_signal_process():
    """Test OctaveLevelsFromSignal process method."""
    loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    loader.process()
    signal = loader.get_output()[0]

    level_obj = OctaveLevelsFromSignal(signal=signal)
    level_obj.process()
    assert level_obj._output is not None


def test_octave_levels_from_signal_process_exceptions():
    """Test OctaveLevelsFromSignal process method exceptions."""
    level_obj = OctaveLevelsFromSignal()
    with pytest.raises(
        PyAnsysSoundException,
        match="No input signal is set. Use OctaveLevelsFromSignal.signal.",
    ):
        level_obj.process()


def test_octave_levels_from_signal_get_output():
    """Test OctaveLevelsFromSignal get_output method."""
    loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    loader.process()
    signal = loader.get_output()[0]

    level_obj = OctaveLevelsFromSignal(signal=signal)
    level_obj.process()
    output = level_obj.get_output()
    assert isinstance(output, Field)


def test_octave_levels_from_signal_get_output_warnings():
    """Test OctaveLevelsFromSignal get_output method warnings."""
    level_obj = OctaveLevelsFromSignal()
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the OctaveLevelsFromSignal.process\\(\\) method.",
    ):
        output = level_obj.get_output()
    assert output is None


def test_octave_levels_from_signal_get_output_as_nparray():
    """Test OctaveLevelsFromSignal get_output_as_nparray method."""
    loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    loader.process()
    signal = loader.get_output()[0]

    level_obj = OctaveLevelsFromSignal(signal=signal)
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the OctaveLevelsFromSignal.process\\(\\) method.",
    ):
        levels, frequencies = level_obj.get_output_as_nparray()
    assert isinstance(levels, np.ndarray)
    assert len(levels) == 0
    assert isinstance(frequencies, np.ndarray)
    assert len(frequencies) == 0

    level_obj.process()
    levels, frequencies = level_obj.get_output_as_nparray()
    assert isinstance(levels, np.ndarray)
    assert len(levels) == EXP_BAND_COUNT
    assert isinstance(frequencies, np.ndarray)
    assert len(frequencies) == EXP_BAND_COUNT


def test_octave_levels_from_signal_get_band_levels():
    """Test OctaveLevelsFromSignal get_band_levels method."""
    loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    loader.process()
    signal = loader.get_output()[0]

    level_obj = OctaveLevelsFromSignal(signal=signal)
    level_obj.process()
    levels = level_obj.get_band_levels()
    assert isinstance(levels, np.ndarray)
    assert len(levels) == EXP_BAND_COUNT
    assert levels[0] == pytest.approx(EXP_LEVEL_DEFAULT_0)
    assert levels[3] == pytest.approx(EXP_LEVEL_DEFAULT_3)
    assert levels[5] == pytest.approx(EXP_LEVEL_DEFAULT_5)
    assert levels[7] == pytest.approx(EXP_LEVEL_DEFAULT_7)
    assert levels[9] == pytest.approx(EXP_LEVEL_DEFAULT_9)

    level_obj.frequency_weighting = "A"
    level_obj.reference_value = 2e-5
    level_obj.process()

    levels = level_obj.get_band_levels()
    assert levels[0] == pytest.approx(EXP_LEVEL_A_PA_0)
    assert levels[3] == pytest.approx(EXP_LEVEL_A_PA_3)
    assert levels[5] == pytest.approx(EXP_LEVEL_A_PA_5)
    assert levels[7] == pytest.approx(EXP_LEVEL_A_PA_7)
    assert levels[9] == pytest.approx(EXP_LEVEL_A_PA_9)

    level_obj.frequency_weighting = "B"
    level_obj.process()

    levels = level_obj.get_band_levels()
    assert levels[0] == pytest.approx(EXP_LEVEL_B_PA_0)
    assert levels[3] == pytest.approx(EXP_LEVEL_B_PA_3)
    assert levels[5] == pytest.approx(EXP_LEVEL_B_PA_5)
    assert levels[7] == pytest.approx(EXP_LEVEL_B_PA_7)
    assert levels[9] == pytest.approx(EXP_LEVEL_B_PA_9)

    level_obj.frequency_weighting = "C"
    level_obj.process()

    levels = level_obj.get_band_levels()
    assert levels[0] == pytest.approx(EXP_LEVEL_C_PA_0)
    assert levels[3] == pytest.approx(EXP_LEVEL_C_PA_3)
    assert levels[5] == pytest.approx(EXP_LEVEL_C_PA_5)
    assert levels[7] == pytest.approx(EXP_LEVEL_C_PA_7)
    assert levels[9] == pytest.approx(EXP_LEVEL_C_PA_9)


def test_octave_levels_from_signal_get_frequencies():
    """Test OctaveLevelsFromSignal get_frequencies method."""
    loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    loader.process()
    signal = loader.get_output()[0]

    level_obj = OctaveLevelsFromSignal(signal=signal)
    level_obj.process()
    frequencies = level_obj.get_center_frequencies()
    assert isinstance(frequencies, np.ndarray)
    assert len(frequencies) == EXP_BAND_COUNT
    assert frequencies[0] == pytest.approx(EXP_FREQUENCY_0)
    assert frequencies[3] == pytest.approx(EXP_FREQUENCY_3)
    assert frequencies[5] == pytest.approx(EXP_FREQUENCY_5)
    assert frequencies[7] == pytest.approx(EXP_FREQUENCY_7)
    assert frequencies[9] == pytest.approx(EXP_FREQUENCY_9)


@patch("matplotlib.pyplot.show")
def test_octave_levels_from_signal_plot(mock_show):
    """Test OctaveLevelsFromSignal plot method."""
    loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    loader.process()
    signal = loader.get_output()[0]

    level_obj = OctaveLevelsFromSignal(signal=signal)
    level_obj.process()
    level_obj.plot()

    level_obj.frequency_weighting = "A"
    level_obj.reference_value = 2e-5
    level_obj.process()
    level_obj.plot()
