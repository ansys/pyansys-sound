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
from ansys.dpf.core import Field, TimeFreqSupport, fields_factory, locations

from ansys.sound.core._pyansys_sound import (PyAnsysSoundException,
                                             PyAnsysSoundWarning)
from ansys.sound.core.standard_levels import OctaveLevelsFromPSD

# Skip entire test module if server < 11.0
if not pytest.SERVERS_VERSION_GREATER_THAN_OR_EQUAL_TO_11_0:
    pytest.skip("Requires server version >= 11.0", allow_module_level=True)

EXP_STR_NOT_SET = (
    "OctaveLevelsFromPSD object.\nData\n\tPSD: Not set\n"
    "\tANSI S1.11-1986 filterbank simulation: No\n\tReference value: 1.0\n"
    "\tFrequency weighting: None\nOutput levels: Not processed"
)
EXP_STR_ALL_SET = (
    'OctaveLevelsFromPSD object.\nData\n\tPSD: "Name of the PSD"\n'
    "\tANSI S1.11-1986 filterbank simulation: Yes\n\tReference value: 2e-05\n"
    "\tFrequency weighting: A\nOutput levels: Not processed"
)
EXP_STR_ALL_PROCESSED = (
    'OctaveLevelsFromPSD object.\nData\n\tPSD: "Name of the PSD"\n'
    "\tANSI S1.11-1986 filterbank simulation: Yes\n\tReference value: 2e-05\n"
    "\tFrequency weighting: A\nOutput levels:\n"
    "\t31.5 Hz:\t-28.6 dBA (re 2e-05)\n"
    "\t63.0 Hz:\t-2.7 dBA (re 2e-05)\n"
    "\t125.0 Hz:\t19.2 dBA (re 2e-05)\n"
    "\t250.0 Hz:\t62.6 dBA (re 2e-05)\n"
    "\t500.0 Hz:\t76.3 dBA (re 2e-05)\n"
    "\t1000.0 Hz:\t77.7 dBA (re 2e-05)\n"
    "\t2000.0 Hz:\t75.8 dBA (re 2e-05)\n"
    "\t4000.0 Hz:\t54.7 dBA (re 2e-05)\n"
    "\t8000.0 Hz:\t44.7 dBA (re 2e-05)\n"
    "\t16000.0 Hz:\t31.3 dBA (re 2e-05)"
)
EXP_BAND_COUNT = 10
EXP_LEVEL_DEFAULT_0 = -83.10991
EXP_LEVEL_DEFAULT_3 = -22.85122
EXP_LEVEL_DEFAULT_5 = -16.37538
EXP_LEVEL_DEFAULT_7 = -40.26398
EXP_LEVEL_DEFAULT_9 = -56.20047
EXP_LEVEL_ANSI_A_PA_0 = -28.55802
EXP_LEVEL_ANSI_A_PA_3 = 62.57908
EXP_LEVEL_ANSI_A_PA_5 = 77.67375
EXP_LEVEL_ANSI_A_PA_7 = 54.73505
EXP_LEVEL_ANSI_A_PA_9 = 31.26837
EXP_LEVEL_ANSI_B_PA_0 = -6.15460
EXP_LEVEL_ANSI_B_PA_3 = 69.89394
EXP_LEVEL_ANSI_B_PA_5 = 77.67375
EXP_LEVEL_ANSI_B_PA_7 = 53.04652
EXP_LEVEL_ANSI_B_PA_9 = 29.44717
EXP_LEVEL_ANSI_C_PA_0 = 7.94025
EXP_LEVEL_ANSI_C_PA_3 = 71.25353
EXP_LEVEL_ANSI_C_PA_5 = 77.67375
EXP_LEVEL_ANSI_C_PA_7 = 52.94557
EXP_LEVEL_ANSI_C_PA_9 = 29.33984
EXP_FREQUENCY_0 = 31.5
EXP_FREQUENCY_3 = 250.0
EXP_FREQUENCY_5 = 1000.0
EXP_FREQUENCY_7 = 4000.0
EXP_FREQUENCY_9 = 16000.0


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


def test_octave_levels_from_psd_instantiation():
    """Test OctaveLevelsFromPSD instantiation."""
    level_obj = OctaveLevelsFromPSD()
    assert level_obj.psd == None
    assert level_obj.use_ansi_s1_11_1986 == False
    assert level_obj.reference_value == 1.0
    assert level_obj.frequency_weighting == ""


def test_octave_levels_from_psd_properties():
    """Test OctaveLevelsFromPSD properties."""
    level_obj = OctaveLevelsFromPSD()
    level_obj.psd = Field()
    assert type(level_obj.psd) == Field

    level_obj.use_ansi_s1_11_1986 = True
    assert level_obj.use_ansi_s1_11_1986 == True

    level_obj.reference_value = 2e-5
    assert level_obj.reference_value == 2e-5

    level_obj.frequency_weighting = "A"
    assert level_obj.frequency_weighting == "A"


def test_octave_levels_from_psd_properties_exceptions():
    """Test OctaveLevelsFromPSD properties exceptions."""
    level_obj = OctaveLevelsFromPSD()
    with pytest.raises(
        PyAnsysSoundException,
        match="The input PSD must be provided as a DPF field.",
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


def test_octave_levels_from_psd___str__(create_psd_from_txt_data):
    """Test OctaveLevelsFromPSD __str__ method."""
    level_obj = OctaveLevelsFromPSD()
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


def test_octave_levels_from_psd_process(create_psd_from_txt_data):
    """Test OctaveLevelsFromPSD process method."""
    level_obj = OctaveLevelsFromPSD(psd=create_psd_from_txt_data)
    level_obj.process()
    assert level_obj._output is not None


def test_octave_levels_from_psd_process_exceptions():
    """Test OctaveLevelsFromPSD process method exceptions."""
    level_obj = OctaveLevelsFromPSD()
    with pytest.raises(
        PyAnsysSoundException,
        match="No input PSD is set. Use OctaveLevelsFromPSD.psd.",
    ):
        level_obj.process()


def test_octave_levels_from_psd_get_output(create_psd_from_txt_data):
    """Test OctaveLevelsFromPSD get_output method."""
    level_obj = OctaveLevelsFromPSD(psd=create_psd_from_txt_data)
    level_obj.process()
    output = level_obj.get_output()
    assert isinstance(output, Field)


def test_octave_levels_from_psd_get_output_warnings():
    """Test OctaveLevelsFromPSD get_output method warnings."""
    level_obj = OctaveLevelsFromPSD()
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the OctaveLevelsFromPSD.process\\(\\) method.",
    ):
        output = level_obj.get_output()
    assert output is None


def test_octave_levels_from_psd_get_output_as_nparray(create_psd_from_txt_data):
    """Test OctaveLevelsFromPSD get_output_as_nparray method."""
    level_obj = OctaveLevelsFromPSD(psd=create_psd_from_txt_data)
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the OctaveLevelsFromPSD.process\\(\\) method.",
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


def test_octave_levels_from_psd_get_band_levels(create_psd_from_txt_data):
    """Test OctaveLevelsFromPSD get_band_levels method."""
    level_obj = OctaveLevelsFromPSD(psd=create_psd_from_txt_data)
    level_obj.process()
    levels = level_obj.get_band_levels()
    assert isinstance(levels, np.ndarray)
    assert len(levels) == EXP_BAND_COUNT
    assert levels[0] == pytest.approx(EXP_LEVEL_DEFAULT_0)
    assert levels[3] == pytest.approx(EXP_LEVEL_DEFAULT_3)
    assert levels[5] == pytest.approx(EXP_LEVEL_DEFAULT_5)
    assert levels[7] == pytest.approx(EXP_LEVEL_DEFAULT_7)
    assert levels[9] == pytest.approx(EXP_LEVEL_DEFAULT_9)

    level_obj.use_ansi_s1_11_1986 = True
    level_obj.frequency_weighting = "A"
    level_obj.reference_value = 2e-5
    level_obj.process()

    levels = level_obj.get_band_levels()
    assert levels[0] == pytest.approx(EXP_LEVEL_ANSI_A_PA_0)
    assert levels[3] == pytest.approx(EXP_LEVEL_ANSI_A_PA_3)
    assert levels[5] == pytest.approx(EXP_LEVEL_ANSI_A_PA_5)
    assert levels[7] == pytest.approx(EXP_LEVEL_ANSI_A_PA_7)
    assert levels[9] == pytest.approx(EXP_LEVEL_ANSI_A_PA_9)

    level_obj.frequency_weighting = "B"
    level_obj.process()

    levels = level_obj.get_band_levels()
    assert levels[0] == pytest.approx(EXP_LEVEL_ANSI_B_PA_0)
    assert levels[3] == pytest.approx(EXP_LEVEL_ANSI_B_PA_3)
    assert levels[5] == pytest.approx(EXP_LEVEL_ANSI_B_PA_5)
    assert levels[7] == pytest.approx(EXP_LEVEL_ANSI_B_PA_7)
    assert levels[9] == pytest.approx(EXP_LEVEL_ANSI_B_PA_9)

    level_obj.frequency_weighting = "C"
    level_obj.process()

    levels = level_obj.get_band_levels()
    assert levels[0] == pytest.approx(EXP_LEVEL_ANSI_C_PA_0)
    assert levels[3] == pytest.approx(EXP_LEVEL_ANSI_C_PA_3)
    assert levels[5] == pytest.approx(EXP_LEVEL_ANSI_C_PA_5)
    assert levels[7] == pytest.approx(EXP_LEVEL_ANSI_C_PA_7)
    assert levels[9] == pytest.approx(EXP_LEVEL_ANSI_C_PA_9)


def test_octave_levels_from_psd_get_frequencies(create_psd_from_txt_data):
    """Test OctaveLevelsFromPSD get_frequencies method."""
    level_obj = OctaveLevelsFromPSD(psd=create_psd_from_txt_data)
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
def test_octave_levels_from_psd_plot(mock_show, create_psd_from_txt_data):
    """Test OctaveLevelsFromPSD plot method."""
    level_obj = OctaveLevelsFromPSD(psd=create_psd_from_txt_data)
    level_obj.process()
    level_obj.plot()

    level_obj.use_ansi_s1_11_1986 = True
    level_obj.frequency_weighting = "A"
    level_obj.reference_value = 2e-5
    level_obj.process()
    level_obj.plot()
