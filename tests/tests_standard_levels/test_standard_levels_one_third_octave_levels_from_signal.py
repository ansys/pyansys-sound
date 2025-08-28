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
from ansys.sound.core.standard_levels import OneThirdOctaveLevelsFromSignal

# Skip entire test module if server < 11.0
if not pytest.SERVERS_VERSION_GREATER_THAN_OR_EQUAL_TO_11_0:
    pytest.skip("Requires server version >= 11.0", allow_module_level=True)

EXP_STR_NOT_SET = (
    "OneThirdOctaveLevelsFromSignal object.\nData\n\tSignal: Not set\n\tReference value: 1.0\n"
    "\tFrequency weighting: None\nOutput levels: Not processed"
)
EXP_STR_ALL_SET = (
    'OneThirdOctaveLevelsFromSignal object.\nData\n\tSignal: "Name of the signal"\n'
    "\tReference value: 2e-05\n\tFrequency weighting: A\nOutput levels: Not processed"
)
EXP_STR_ALL_PROCESSED = (
    'OneThirdOctaveLevelsFromSignal object.\nData\n\tSignal: "Name of the signal"\n'
    "\tReference value: 2e-05\n\tFrequency weighting: A\nOutput levels:\n"
    "\t25.0 Hz:\t-39.9 dBA (re 2e-05)\n"
    "\t31.0 Hz:\t-31.2 dBA (re 2e-05)\n"
    "\t40.0 Hz:\t-18.7 dBA (re 2e-05)\n"
    "\t50.0 Hz:\t-10.6 dBA (re 2e-05)\n"
    "\t63.0 Hz:\t-4.4 dBA (re 2e-05)\n"
    "\t80.0 Hz:\t5.7 dBA (re 2e-05)\n"
    "\t100.0 Hz:\t12.0 dBA (re 2e-05)\n"
    "\t125.0 Hz:\t19.2 dBA (re 2e-05)\n"
    "\t160.0 Hz:\t25.9 dBA (re 2e-05)\n"
    "\t200.0 Hz:\t42.2 dBA (re 2e-05)\n"
    "\t250.0 Hz:\t68.0 dBA (re 2e-05)\n"
    "\t315.0 Hz:\t56.6 dBA (re 2e-05)\n"
    "\t400.0 Hz:\t56.5 dBA (re 2e-05)\n"
    "\t500.0 Hz:\t81.6 dBA (re 2e-05)\n"
    "\t630.0 Hz:\t70.2 dBA (re 2e-05)\n"
    "\t800.0 Hz:\t81.7 dBA (re 2e-05)\n"
    "\t1000.0 Hz:\t74.0 dBA (re 2e-05)\n"
    "\t1250.0 Hz:\t69.3 dBA (re 2e-05)\n"
    "\t1600.0 Hz:\t77.0 dBA (re 2e-05)\n"
    "\t2000.0 Hz:\t79.2 dBA (re 2e-05)\n"
    "\t2500.0 Hz:\t65.3 dBA (re 2e-05)\n"
    "\t3150.0 Hz:\t57.5 dBA (re 2e-05)\n"
    "\t4000.0 Hz:\t56.3 dBA (re 2e-05)\n"
    "\t5000.0 Hz:\t50.1 dBA (re 2e-05)\n"
    "\t6300.0 Hz:\t48.2 dBA (re 2e-05)\n"
    "\t8000.0 Hz:\t44.9 dBA (re 2e-05)\n"
    "\t10000.0 Hz:\t42.4 dBA (re 2e-05)\n"
    "\t12500.0 Hz:\t38.8 dBA (re 2e-05)\n"
    "\t16000.0 Hz:\t27.5 dBA (re 2e-05)"
)
EXP_BAND_COUNT = 29
EXP_LEVEL_DEFAULT_16 = -19.97085
EXP_LEVEL_DEFAULT_15 = -11.47879
EXP_LEVEL_DEFAULT_17 = -25.25151
EXP_LEVEL_DEFAULT_9 = -40.88276
EXP_LEVEL_DEFAULT_21 = -37.67591
EXP_LEVEL_A_PA_16 = 74.00858
EXP_LEVEL_A_PA_15 = 81.70586
EXP_LEVEL_A_PA_17 = 69.30410
EXP_LEVEL_A_PA_9 = 42.24939
EXP_LEVEL_A_PA_21 = 57.50530
EXP_LEVEL_B_PA_16 = 74.00858
EXP_LEVEL_B_PA_15 = 82.46001
EXP_LEVEL_B_PA_17 = 68.73518
EXP_LEVEL_B_PA_9 = 51.05556
EXP_LEVEL_B_PA_21 = 55.90120
EXP_LEVEL_C_PA_16 = 74.00858
EXP_LEVEL_C_PA_15 = 82.51945
EXP_LEVEL_C_PA_17 = 68.69670
EXP_LEVEL_C_PA_9 = 53.06454
EXP_LEVEL_C_PA_21 = 55.80443
EXP_FREQUENCY_16 = 1000.0
EXP_FREQUENCY_15 = 800.0
EXP_FREQUENCY_17 = 1250.0
EXP_FREQUENCY_9 = 200.0
EXP_FREQUENCY_21 = 3150.0


def test_one_third_octave_levels_from_signal_instantiation():
    """Test OneThirdOctaveLevelsFromSignal instantiation."""
    level_obj = OneThirdOctaveLevelsFromSignal()
    assert level_obj.signal == None
    assert level_obj.reference_value == 1.0
    assert level_obj.frequency_weighting == ""


def test_one_third_octave_levels_from_signal_properties():
    """Test OneThirdOctaveLevelsFromSignal properties."""
    level_obj = OneThirdOctaveLevelsFromSignal()
    level_obj.signal = Field()
    assert type(level_obj.signal) == Field

    level_obj.reference_value = 2e-5
    assert level_obj.reference_value == 2e-5

    level_obj.frequency_weighting = "A"
    assert level_obj.frequency_weighting == "A"


def test_one_third_octave_levels_from_signal_properties_exceptions():
    """Test OneThirdOctaveLevelsFromSignal properties exceptions."""
    level_obj = OneThirdOctaveLevelsFromSignal()
    with pytest.raises(
        PyAnsysSoundException, match="The input signal must be provided as a DPF field."
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


def test_one_third_octave_levels_from_signal___str__():
    """Test OneThirdOctaveLevelsFromSignal __str__ method."""
    level_obj = OneThirdOctaveLevelsFromSignal()
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


def test_one_third_octave_levels_from_signal_process():
    """Test OneThirdOctaveLevelsFromSignal process method."""
    loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    loader.process()
    signal = loader.get_output()[0]

    level_obj = OneThirdOctaveLevelsFromSignal(signal=signal)
    level_obj.process()
    assert level_obj._output is not None


def test_one_third_octave_levels_from_signal_process_exceptions():
    """Test OneThirdOctaveLevelsFromSignal process method exceptions."""
    level_obj = OneThirdOctaveLevelsFromSignal()
    with pytest.raises(
        PyAnsysSoundException,
        match="No input signal is set. Use OneThirdOctaveLevelsFromSignal.signal.",
    ):
        level_obj.process()


def test_one_third_octave_levels_from_signal_get_output():
    """Test OneThirdOctaveLevelsFromSignal get_output method."""
    loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    loader.process()
    signal = loader.get_output()[0]

    level_obj = OneThirdOctaveLevelsFromSignal(signal=signal)
    level_obj.process()
    output = level_obj.get_output()
    assert isinstance(output, Field)


def test_one_third_octave_levels_from_signal_get_output_warnings():
    """Test OneThirdOctaveLevelsFromSignal get_output method warnings."""
    level_obj = OneThirdOctaveLevelsFromSignal()
    with pytest.warns(
        PyAnsysSoundWarning,
        match=(
            "Output is not processed yet. Use the OneThirdOctaveLevelsFromSignal.process\\(\\) "
            "method."
        ),
    ):
        output = level_obj.get_output()
    assert output is None


def test_one_third_octave_levels_from_signal_get_output_as_nparray():
    """Test OneThirdOctaveLevelsFromSignal get_output_as_nparray method."""
    loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    loader.process()
    signal = loader.get_output()[0]

    level_obj = OneThirdOctaveLevelsFromSignal(signal=signal)
    with pytest.warns(
        PyAnsysSoundWarning,
        match=(
            "Output is not processed yet. Use the OneThirdOctaveLevelsFromSignal.process\\(\\) "
            "method."
        ),
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


def test_one_third_octave_levels_from_signal_get_band_levels():
    """Test OneThirdOctaveLevelsFromSignal get_band_levels method."""
    loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    loader.process()
    signal = loader.get_output()[0]

    level_obj = OneThirdOctaveLevelsFromSignal(signal=signal)
    level_obj.process()
    levels = level_obj.get_band_levels()
    assert isinstance(levels, np.ndarray)
    assert len(levels) == EXP_BAND_COUNT
    assert levels[16] == pytest.approx(EXP_LEVEL_DEFAULT_16)
    assert levels[15] == pytest.approx(EXP_LEVEL_DEFAULT_15)
    assert levels[17] == pytest.approx(EXP_LEVEL_DEFAULT_17)
    assert levels[9] == pytest.approx(EXP_LEVEL_DEFAULT_9)
    assert levels[21] == pytest.approx(EXP_LEVEL_DEFAULT_21)

    level_obj.frequency_weighting = "A"
    level_obj.reference_value = 2e-5
    level_obj.process()

    levels = level_obj.get_band_levels()
    assert levels[16] == pytest.approx(EXP_LEVEL_A_PA_16)
    assert levels[15] == pytest.approx(EXP_LEVEL_A_PA_15)
    assert levels[17] == pytest.approx(EXP_LEVEL_A_PA_17)
    assert levels[9] == pytest.approx(EXP_LEVEL_A_PA_9)
    assert levels[21] == pytest.approx(EXP_LEVEL_A_PA_21)

    level_obj.frequency_weighting = "B"
    level_obj.process()

    levels = level_obj.get_band_levels()
    assert levels[16] == pytest.approx(EXP_LEVEL_B_PA_16)
    assert levels[15] == pytest.approx(EXP_LEVEL_B_PA_15)
    assert levels[17] == pytest.approx(EXP_LEVEL_B_PA_17)
    assert levels[9] == pytest.approx(EXP_LEVEL_B_PA_9)
    assert levels[21] == pytest.approx(EXP_LEVEL_B_PA_21)

    level_obj.frequency_weighting = "C"
    level_obj.process()

    levels = level_obj.get_band_levels()
    assert levels[16] == pytest.approx(EXP_LEVEL_C_PA_16)
    assert levels[15] == pytest.approx(EXP_LEVEL_C_PA_15)
    assert levels[17] == pytest.approx(EXP_LEVEL_C_PA_17)
    assert levels[9] == pytest.approx(EXP_LEVEL_C_PA_9)
    assert levels[21] == pytest.approx(EXP_LEVEL_C_PA_21)


def test_one_third_octave_levels_from_signal_get_frequencies():
    """Test OneThirdOctaveLevelsFromSignal get_frequencies method."""
    loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    loader.process()
    signal = loader.get_output()[0]

    level_obj = OneThirdOctaveLevelsFromSignal(signal=signal)
    level_obj.process()
    frequencies = level_obj.get_center_frequencies()
    assert isinstance(frequencies, np.ndarray)
    assert len(frequencies) == EXP_BAND_COUNT
    assert frequencies[16] == pytest.approx(EXP_FREQUENCY_16)
    assert frequencies[15] == pytest.approx(EXP_FREQUENCY_15)
    assert frequencies[17] == pytest.approx(EXP_FREQUENCY_17)
    assert frequencies[9] == pytest.approx(EXP_FREQUENCY_9)
    assert frequencies[21] == pytest.approx(EXP_FREQUENCY_21)


@patch("matplotlib.pyplot.show")
def test_one_third_octave_levels_from_signal_plot(mock_show):
    """Test OneThirdOctaveLevelsFromSignal plot method."""
    loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    loader.process()
    signal = loader.get_output()[0]

    level_obj = OneThirdOctaveLevelsFromSignal(signal=signal)
    level_obj.process()
    level_obj.plot()

    level_obj.frequency_weighting = "A"
    level_obj.reference_value = 2e-5
    level_obj.process()
    level_obj.plot()
