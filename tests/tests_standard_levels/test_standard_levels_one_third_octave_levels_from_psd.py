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

from unittest.mock import patch

from ansys.dpf.core import Field, TimeFreqSupport, fields_factory, locations
import numpy as np
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ansys.sound.core.standard_levels import OneThirdOctaveLevelsFromPSD

# Skip entire test module if server < 11.0
if not pytest.SERVERS_VERSION_GREATER_THAN_OR_EQUAL_TO_11_0:
    pytest.skip("Requires server version >= 11.0", allow_module_level=True)

EXP_STR_NOT_SET = (
    "OneThirdOctaveLevelsFromPSD object.\nData\n\tPSD: Not set\n"
    "\tANSI S1.11-1986 filterbank simulation: No\n\tReference value: 1.0\n"
    "\tFrequency weighting: None\nOutput levels: Not processed"
)
EXP_STR_ALL_SET = (
    'OneThirdOctaveLevelsFromPSD object.\nData\n\tPSD: "Name of the PSD"\n'
    "\tANSI S1.11-1986 filterbank simulation: Yes\n\tReference value: 2e-05\n"
    "\tFrequency weighting: A\nOutput levels: Not processed"
)
EXP_STR_ALL_PROCESSED = (
    'OneThirdOctaveLevelsFromPSD object.\nData\n\tPSD: "Name of the PSD"\n'
    "\tANSI S1.11-1986 filterbank simulation: Yes\n\tReference value: 2e-05\n"
    "\tFrequency weighting: A\nOutput levels:\n"
    "\t25.0 Hz:\t-45.7 dBA (re 2e-05)\n"
    "\t31.5 Hz:\t-36.6 dBA (re 2e-05)\n"
    "\t40.0 Hz:\t-24.7 dBA (re 2e-05)\n"
    "\t50.0 Hz:\t-16.5 dBA (re 2e-05)\n"
    "\t63.0 Hz:\t-10.3 dBA (re 2e-05)\n"
    "\t80.0 Hz:\t-0.3 dBA (re 2e-05)\n"
    "\t100.0 Hz:\t6.2 dBA (re 2e-05)\n"
    "\t125.0 Hz:\t13.3 dBA (re 2e-05)\n"
    "\t160.0 Hz:\t20.2 dBA (re 2e-05)\n"
    "\t200.0 Hz:\t36.8 dBA (re 2e-05)\n"
    "\t250.0 Hz:\t62.4 dBA (re 2e-05)\n"
    "\t315.0 Hz:\t51.2 dBA (re 2e-05)\n"
    "\t400.0 Hz:\t50.9 dBA (re 2e-05)\n"
    "\t500.0 Hz:\t76.0 dBA (re 2e-05)\n"
    "\t630.0 Hz:\t64.7 dBA (re 2e-05)\n"
    "\t800.0 Hz:\t76.1 dBA (re 2e-05)\n"
    "\t1000.0 Hz:\t68.5 dBA (re 2e-05)\n"
    "\t1250.0 Hz:\t63.7 dBA (re 2e-05)\n"
    "\t1600.0 Hz:\t71.5 dBA (re 2e-05)\n"
    "\t2000.0 Hz:\t73.6 dBA (re 2e-05)\n"
    "\t2500.0 Hz:\t59.7 dBA (re 2e-05)\n"
    "\t3150.0 Hz:\t51.9 dBA (re 2e-05)\n"
    "\t4000.0 Hz:\t50.7 dBA (re 2e-05)\n"
    "\t5000.0 Hz:\t44.6 dBA (re 2e-05)\n"
    "\t6300.0 Hz:\t42.6 dBA (re 2e-05)\n"
    "\t8000.0 Hz:\t39.4 dBA (re 2e-05)\n"
    "\t10000.0 Hz:\t36.8 dBA (re 2e-05)\n"
    "\t12500.0 Hz:\t33.2 dBA (re 2e-05)\n"
    "\t16000.0 Hz:\t21.5 dBA (re 2e-05)"
)
EXP_BAND_COUNT = 29
EXP_LEVEL_DEFAULT_16 = -25.79326
EXP_LEVEL_DEFAULT_15 = -17.04219
EXP_LEVEL_DEFAULT_17 = -31.90556
EXP_LEVEL_DEFAULT_9 = -66.85459
EXP_LEVEL_DEFAULT_21 = -43.37958
EXP_LEVEL_ANSI_A_PA_16 = 68.45362
EXP_LEVEL_ANSI_A_PA_15 = 76.14678
EXP_LEVEL_ANSI_A_PA_17 = 63.74951
EXP_LEVEL_ANSI_A_PA_9 = 36.77381
EXP_LEVEL_ANSI_A_PA_21 = 51.94006
EXP_LEVEL_ANSI_B_PA_16 = 68.45362
EXP_LEVEL_ANSI_B_PA_15 = 76.90092
EXP_LEVEL_ANSI_B_PA_17 = 63.18060
EXP_LEVEL_ANSI_B_PA_9 = 45.57998
EXP_LEVEL_ANSI_B_PA_21 = 50.33597
EXP_LEVEL_ANSI_C_PA_16 = 68.45362
EXP_LEVEL_ANSI_C_PA_15 = 76.96037
EXP_LEVEL_ANSI_C_PA_17 = 63.14211
EXP_LEVEL_ANSI_C_PA_9 = 47.58892
EXP_LEVEL_ANSI_C_PA_21 = 50.23919
EXP_FREQUENCY_16 = 1000.0
EXP_FREQUENCY_15 = 800.0
EXP_FREQUENCY_17 = 1250.0
EXP_FREQUENCY_9 = 200.0
EXP_FREQUENCY_21 = 3150.0


@pytest.fixture
def create_psd_from_txt_data():
    path_flute_psd = pytest.data_path_flute_psd_locally

    # Open a txt file for reading
    fid = open(path_flute_psd)

    # skip first line
    fid.readline()

    # read all other lines
    all_lines = fid.readlines()
    # close file
    fid.close()

    amplitudes = []

    for line in all_lines:
        splitted_line = line.split()
        amplitudes.append(float(splitted_line[1]))

    amplitudes = np.array(amplitudes)

    # convert dBSPL / Hz -> Pa^2/Hz
    amplitudes = np.power(10, amplitudes / 10)
    amplitudes = amplitudes * 2.0e-5
    amplitudes = amplitudes * 2.0e-5

    # for now, due to a sharp constraint on regularity of frequencies (1.0e-5) in the operator,
    # we cannot use those written in the file. Let's recreate them
    frequencies = np.linspace(0, 22050, len(amplitudes))

    psd = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
    psd.append(amplitudes, 1)
    support = TimeFreqSupport()
    frequencies_field = fields_factory.create_scalar_field(
        num_entities=1, location=locations.time_freq
    )
    frequencies_field.append(frequencies, 1)
    support.time_frequencies = frequencies_field

    psd.time_freq_support = support

    yield psd


def test_one_third_octave_levels_from_psd_instantiation():
    """Test OneThirdOctaveLevelsFromPSD instantiation."""
    level_obj = OneThirdOctaveLevelsFromPSD()
    assert level_obj.psd == None
    assert level_obj.use_ansi_s1_11_1986 == False
    assert level_obj.reference_value == 1.0
    assert level_obj.frequency_weighting == ""


def test_one_third_octave_levels_from_psd_properties():
    """Test OneThirdOctaveLevelsFromPSD properties."""
    level_obj = OneThirdOctaveLevelsFromPSD()
    level_obj.psd = Field()
    assert type(level_obj.psd) == Field

    level_obj.use_ansi_s1_11_1986 = True
    assert level_obj.use_ansi_s1_11_1986 == True

    level_obj.reference_value = 2e-5
    assert level_obj.reference_value == 2e-5

    level_obj.frequency_weighting = "A"
    assert level_obj.frequency_weighting == "A"


def test_one_third_octave_levels_from_psd_properties_exceptions():
    """Test OneThirdOctaveLevelsFromPSD properties exceptions."""
    level_obj = OneThirdOctaveLevelsFromPSD()
    with pytest.raises(
        PyAnsysSoundException, match="The input PSD must be provided as a DPF field."
    ):
        level_obj.psd = "InvalidType"

    with pytest.raises(
        PyAnsysSoundException, match="The reference value must be strictly positive."
    ):
        level_obj.reference_value = -1

    with pytest.raises(
        PyAnsysSoundException,
        match="The frequency weighting must be one of \\['', 'A', 'B', 'C'\\].",
    ):
        level_obj.frequency_weighting = "Invalid"


def test_one_third_octave_levels_from_psd___str__(create_psd_from_txt_data):
    """Test OneThirdOctaveLevelsFromPSD __str__ method."""
    level_obj = OneThirdOctaveLevelsFromPSD()
    assert str(level_obj) == EXP_STR_NOT_SET

    psd = create_psd_from_txt_data
    psd.name = "Name of the PSD"

    level_obj.psd = psd
    level_obj.use_ansi_s1_11_1986 = True
    level_obj.reference_value = 2e-5
    level_obj.frequency_weighting = "A"
    assert str(level_obj) == EXP_STR_ALL_SET

    level_obj.process()
    assert str(level_obj) == EXP_STR_ALL_PROCESSED


def test_one_third_octave_levels_from_psd_process(create_psd_from_txt_data):
    """Test OneThirdOctaveLevelsFromPSD process method."""
    level_obj = OneThirdOctaveLevelsFromPSD(psd=create_psd_from_txt_data)
    level_obj.process()
    assert level_obj._output is not None


def test_one_third_octave_levels_from_psd_process_exceptions():
    """Test OneThirdOctaveLevelsFromPSD process method exceptions."""
    level_obj = OneThirdOctaveLevelsFromPSD()
    with pytest.raises(
        PyAnsysSoundException,
        match="No input PSD is set. Use OneThirdOctaveLevelsFromPSD.psd.",
    ):
        level_obj.process()


def test_one_third_octave_levels_from_psd_get_output(create_psd_from_txt_data):
    """Test OneThirdOctaveLevelsFromPSD get_output method."""
    level_obj = OneThirdOctaveLevelsFromPSD(psd=create_psd_from_txt_data)
    level_obj.process()
    output = level_obj.get_output()
    assert isinstance(output, Field)


def test_one_third_octave_levels_from_psd_get_output_warnings():
    """Test OneThirdOctaveLevelsFromPSD get_output method warnings."""
    level_obj = OneThirdOctaveLevelsFromPSD()
    with pytest.warns(
        PyAnsysSoundWarning,
        match=(
            "Output is not processed yet. Use the OneThirdOctaveLevelsFromPSD.process\\(\\) method."
        ),
    ):
        output = level_obj.get_output()
    assert output is None


def test_one_third_octave_levels_from_psd_get_output_as_nparray(create_psd_from_txt_data):
    """Test OneThirdOctaveLevelsFromPSD get_output_as_nparray method."""
    level_obj = OneThirdOctaveLevelsFromPSD(psd=create_psd_from_txt_data)
    with pytest.warns(
        PyAnsysSoundWarning,
        match=(
            "Output is not processed yet. Use the OneThirdOctaveLevelsFromPSD.process\\(\\) method."
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


def test_one_third_octave_levels_from_psd_get_band_levels(create_psd_from_txt_data):
    """Test OneThirdOctaveLevelsFromPSD get_band_levels method."""
    level_obj = OneThirdOctaveLevelsFromPSD(psd=create_psd_from_txt_data)
    level_obj.process()
    levels = level_obj.get_band_levels()
    assert isinstance(levels, np.ndarray)
    assert len(levels) == EXP_BAND_COUNT
    assert levels[16] == pytest.approx(EXP_LEVEL_DEFAULT_16)
    assert levels[15] == pytest.approx(EXP_LEVEL_DEFAULT_15)
    assert levels[17] == pytest.approx(EXP_LEVEL_DEFAULT_17)
    assert levels[9] == pytest.approx(EXP_LEVEL_DEFAULT_9)
    assert levels[21] == pytest.approx(EXP_LEVEL_DEFAULT_21)

    level_obj.use_ansi_s1_11_1986 = True
    level_obj.frequency_weighting = "A"
    level_obj.reference_value = 2e-5
    level_obj.process()

    levels = level_obj.get_band_levels()
    assert levels[16] == pytest.approx(EXP_LEVEL_ANSI_A_PA_16)
    assert levels[15] == pytest.approx(EXP_LEVEL_ANSI_A_PA_15)
    assert levels[17] == pytest.approx(EXP_LEVEL_ANSI_A_PA_17)
    assert levels[9] == pytest.approx(EXP_LEVEL_ANSI_A_PA_9)
    assert levels[21] == pytest.approx(EXP_LEVEL_ANSI_A_PA_21)

    level_obj.frequency_weighting = "B"
    level_obj.process()

    levels = level_obj.get_band_levels()
    assert levels[16] == pytest.approx(EXP_LEVEL_ANSI_B_PA_16)
    assert levels[15] == pytest.approx(EXP_LEVEL_ANSI_B_PA_15)
    assert levels[17] == pytest.approx(EXP_LEVEL_ANSI_B_PA_17)
    assert levels[9] == pytest.approx(EXP_LEVEL_ANSI_B_PA_9)
    assert levels[21] == pytest.approx(EXP_LEVEL_ANSI_B_PA_21)

    level_obj.frequency_weighting = "C"
    level_obj.process()

    levels = level_obj.get_band_levels()
    assert levels[16] == pytest.approx(EXP_LEVEL_ANSI_C_PA_16)
    assert levels[15] == pytest.approx(EXP_LEVEL_ANSI_C_PA_15)
    assert levels[17] == pytest.approx(EXP_LEVEL_ANSI_C_PA_17)
    assert levels[9] == pytest.approx(EXP_LEVEL_ANSI_C_PA_9)
    assert levels[21] == pytest.approx(EXP_LEVEL_ANSI_C_PA_21)


def test_one_third_octave_levels_from_psd_get_frequencies(create_psd_from_txt_data):
    """Test OneThirdOctaveLevelsFromPSD get_frequencies method."""
    level_obj = OneThirdOctaveLevelsFromPSD(psd=create_psd_from_txt_data)
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
def test_one_third_octave_levels_from_psd_plot(mock_show, create_psd_from_txt_data):
    """Test OneThirdOctaveLevelsFromPSD plot method."""
    level_obj = OneThirdOctaveLevelsFromPSD(psd=create_psd_from_txt_data)
    level_obj.process()
    level_obj.plot()

    level_obj.use_ansi_s1_11_1986 = True
    level_obj.frequency_weighting = "A"
    level_obj.reference_value = 2e-5
    level_obj.process()
    level_obj.plot()
