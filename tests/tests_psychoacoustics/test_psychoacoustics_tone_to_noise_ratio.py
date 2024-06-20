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

from unittest.mock import patch

from ansys.dpf.core import GenericDataContainer, TimeFreqSupport, fields_factory, locations
import numpy as np
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundException
from ansys.sound.core.examples_helpers._get_example_files import get_absolute_path_for_flute_psd_txt
from ansys.sound.core.psychoacoustics import ToneToNoiseRatio


@pytest.fixture
def create_psd_from_txt_data():
    path_flute_psd = get_absolute_path_for_flute_psd_txt()

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

    return psd


def test_tone_to_noise_ratio_instantiation(dpf_sound_test_server):
    tnr = ToneToNoiseRatio()
    assert tnr != None


def test_tone_to_noise_ratio_set_get_psd(dpf_sound_test_server, create_psd_from_txt_data):
    tnr = ToneToNoiseRatio()

    psd = create_psd_from_txt_data
    tnr.psd = psd
    psd_from_get = tnr.psd

    assert len(psd_from_get.data) == 8193
    assert psd_from_get.data[42] == pytest.approx(6.8086340335798055e-09)


def test_tone_to_noise_ratio_set_get_frequency_list(dpf_sound_test_server):
    tnr = ToneToNoiseRatio()

    frequency_list = [2, 5, 9]
    tnr.frequency_list = frequency_list
    frequency_list_from_get = tnr.frequency_list

    assert len(frequency_list_from_get) == 3
    assert frequency_list_from_get[2] == 9


def test_tone_to_noise_ratio_process(dpf_sound_test_server, create_psd_from_txt_data):
    tnr = ToneToNoiseRatio()

    # no signal -> error 1
    with pytest.raises(PyAnsysSoundException) as excinfo:
        tnr.process()
    assert str(excinfo.value) == "No PSD found for TNR computation. Use 'ToneToNoiseRatio.psd'."

    psd = create_psd_from_txt_data
    tnr.psd = psd

    # compute: no error
    tnr.process()


def test_tone_to_noise_ratio_get_output(dpf_sound_test_server, create_psd_from_txt_data):
    tnr = ToneToNoiseRatio()

    psd = create_psd_from_txt_data
    tnr.psd = psd

    # no compute: return None
    assert tnr.get_output() == None

    # compute: no error
    tnr.process()

    tnr_container = tnr.get_output()
    assert tnr_container != None
    assert type(tnr_container) == GenericDataContainer


def test_tone_to_noise_ratio_get_output_as_nparray(dpf_sound_test_server, create_psd_from_txt_data):
    tnr = ToneToNoiseRatio()

    psd = create_psd_from_txt_data
    tnr.psd = psd

    # no compute: return None
    assert tnr.get_output_as_nparray() == None

    tnr.process()

    (
        frequency_Hz,
        tnr_db,
        level_db,
        bandwidth_low,
        bandwidth_high,
        tnr_max,
    ) = tnr.get_output_as_nparray()

    assert type(frequency_Hz) == np.ndarray
    assert frequency_Hz.size == 11
    assert frequency_Hz[0] == pytest.approx(261.090087890625)
    assert frequency_Hz[6] == pytest.approx(1835.70556640625)

    assert type(tnr_db) == np.ndarray
    assert tnr_db.size == 11
    assert tnr_db[0] == pytest.approx(38.04449462890625)
    assert tnr_db[6] == pytest.approx(32.670352935791016)

    assert type(level_db) == np.ndarray
    assert level_db.size == 11
    assert level_db[0] == pytest.approx(71.11832305908203)
    assert level_db[6] == pytest.approx(72.64159843444824)

    assert type(bandwidth_low) == np.ndarray
    assert bandwidth_low.size == 11
    assert bandwidth_low[0] == pytest.approx(231.48193359375)
    assert bandwidth_low[6] == pytest.approx(1808.7890625)

    assert type(bandwidth_high) == np.ndarray
    assert bandwidth_high.size == 11
    assert bandwidth_high[0] == pytest.approx(282.623291015625)
    assert bandwidth_high[6] == pytest.approx(1929.913330078125)

    assert type(tnr_max) == np.ndarray
    assert tnr_max.size == 1
    assert tnr_max == pytest.approx(38.04449462890625)


def test_tone_to_noise_ratio_get_nb_tones(dpf_sound_test_server, create_psd_from_txt_data):
    tnr = ToneToNoiseRatio()

    psd = create_psd_from_txt_data
    tnr.psd = psd

    with pytest.raises(PyAnsysSoundException) as excinfo:
        tnr.get_nb_tones()
    assert (
        str(excinfo.value)
        == "Output is not processed yet. Use the 'ToneToNoiseRatio.process()' method."
    )

    tnr.process()
    assert tnr.get_nb_tones() == 11

    # flat spectrum -> no peaks to detect
    psd.data = np.ones(len(psd.data))
    tnr.process()
    assert tnr.get_nb_tones() == 0


def test_tone_to_noise_ratio_get_peaks_frequencies(dpf_sound_test_server, create_psd_from_txt_data):
    tnr = ToneToNoiseRatio()

    psd = create_psd_from_txt_data
    tnr.psd = psd

    # no compute: return None
    assert tnr.get_peaks_frequencies() == None

    tnr.process()
    peaks_frequencies = tnr.get_peaks_frequencies()
    assert type(peaks_frequencies) == np.ndarray
    assert peaks_frequencies.size == 11
    assert peaks_frequencies[0] == pytest.approx(261.090087890625)
    assert peaks_frequencies[6] == pytest.approx(1835.70556640625)


def test_tone_to_noise_ratio_get_TNR_values(dpf_sound_test_server, create_psd_from_txt_data):
    tnr = ToneToNoiseRatio()

    psd = create_psd_from_txt_data
    tnr.psd = psd

    # no compute: return None
    assert tnr.get_TNR_values() == None

    tnr.process()
    tnr_db = tnr.get_TNR_values()
    assert type(tnr_db) == np.ndarray
    assert tnr_db.size == 11
    assert tnr_db[0] == pytest.approx(38.04449462890625)
    assert tnr_db[6] == pytest.approx(32.670352935791016)


def test_tone_to_noise_ratio_get_peaks_levels(dpf_sound_test_server, create_psd_from_txt_data):
    tnr = ToneToNoiseRatio()

    psd = create_psd_from_txt_data
    tnr.psd = psd

    # no compute: return None
    assert tnr.get_peaks_levels() == None

    tnr.process()
    level_db = tnr.get_peaks_levels()
    assert type(level_db) == np.ndarray
    assert level_db.size == 11
    assert level_db[0] == pytest.approx(71.11832305908203)
    assert level_db[6] == pytest.approx(72.64159843444824)


def test_tone_to_noise_ratio_get_peaks_low_frequencies(
    dpf_sound_test_server, create_psd_from_txt_data
):
    tnr = ToneToNoiseRatio()

    psd = create_psd_from_txt_data
    tnr.psd = psd

    # no compute: return None
    assert tnr.get_peaks_low_frequencies() == None

    tnr.process()
    bandwidth_low = tnr.get_peaks_low_frequencies()
    assert type(bandwidth_low) == np.ndarray
    assert bandwidth_low.size == 11
    assert bandwidth_low[0] == pytest.approx(231.48193359375)
    assert bandwidth_low[6] == pytest.approx(1808.7890625)


def test_tone_to_noise_ratio_get_peaks_high_frequencies(
    dpf_sound_test_server, create_psd_from_txt_data
):
    tnr = ToneToNoiseRatio()

    psd = create_psd_from_txt_data
    tnr.psd = psd

    # no compute: return None
    assert tnr.get_peaks_high_frequencies() == None

    tnr.process()
    bandwidth_high = tnr.get_peaks_high_frequencies()
    assert type(bandwidth_high) == np.ndarray
    assert bandwidth_high.size == 11
    assert bandwidth_high[0] == pytest.approx(282.623291015625)
    assert bandwidth_high[6] == pytest.approx(1929.913330078125)


def test_tone_to_noise_ratio_get_max_TNR_value(dpf_sound_test_server, create_psd_from_txt_data):
    tnr = ToneToNoiseRatio()

    psd = create_psd_from_txt_data
    tnr.psd = psd

    # no compute: return None
    assert tnr.get_max_TNR_value() == None

    tnr.process()
    tnr_max = tnr.get_max_TNR_value()
    assert type(tnr_max) == np.ndarray
    assert tnr_max.size == 1
    assert tnr_max == pytest.approx(38.04449462890625)


def test_tone_to_noise_ratio_get_all_tone_infos(dpf_sound_test_server, create_psd_from_txt_data):
    tnr = ToneToNoiseRatio()

    psd = create_psd_from_txt_data
    tnr.psd = psd

    with pytest.raises(PyAnsysSoundException) as excinfo:
        tnr.get_single_tone_info(1)
    assert (
        str(excinfo.value)
        == "Output is not processed yet. Use the 'ToneToNoiseRatio.process()' method."
    )

    tnr.process()
    with pytest.raises(PyAnsysSoundException) as excinfo:
        tnr.get_single_tone_info(14)
    assert str(excinfo.value) == "Tone index is out of bound. It must be between 0 and 10."

    (
        peaks_frequency,
        tnr_db,
        level_db,
        bandwidth_low,
        bandwidth_high,
    ) = tnr.get_single_tone_info(6)

    assert peaks_frequency == pytest.approx(1835.70556640625)
    assert tnr_db == pytest.approx(32.670352935791016)
    assert level_db == pytest.approx(72.64159843444824)
    assert bandwidth_low == pytest.approx(1808.7890625)
    assert bandwidth_high == pytest.approx(1929.913330078125)

    # flat PSD -> nothing to detect
    psd.data = np.ones(len(psd.data))
    tnr.process()
    with pytest.raises(PyAnsysSoundException) as excinfo:
        tnr.get_single_tone_info(1)
    assert str(excinfo.value) == "No peak is detected."


def test_tone_to_noise_ratio_get_reference_curve(dpf_sound_test_server, create_psd_from_txt_data):
    tnr = ToneToNoiseRatio()

    psd = create_psd_from_txt_data

    with pytest.raises(PyAnsysSoundException) as excinfo:
        tnr.get_reference_curve()
    assert str(excinfo.value) == "No PSD set. Use 'ToneToNoiseRatio.psd'."

    tnr.psd = psd
    ref_curve = tnr.get_reference_curve()

    assert type(ref_curve) == np.ndarray
    assert ref_curve.size == 8193
    assert ref_curve[0] == 0
    assert ref_curve[33] == 0
    assert ref_curve[34] == pytest.approx(16.650725265104406)
    assert ref_curve[42] == pytest.approx(15.886278055051882)
    assert ref_curve[371] == pytest.approx(8.00505997697306)
    assert ref_curve[372] == pytest.approx(8.0)
    assert ref_curve[4168] == pytest.approx(8.0)
    assert ref_curve[4169] == 0
    assert ref_curve[5896] == 0


@patch("matplotlib.pyplot.show")
def test_tone_to_noise_ratio_plot(dpf_sound_test_server, create_psd_from_txt_data):
    tnr = ToneToNoiseRatio()

    psd = create_psd_from_txt_data
    tnr.psd = psd

    with pytest.raises(PyAnsysSoundException) as excinfo:
        tnr.plot()
    assert (
        str(excinfo.value)
        == "Output is not processed yet. Use the 'ToneToNoiseRatio.process()' method."
    )

    tnr.process()
    tnr.plot()


def test_tone_to_noise_ratio_with_frequency_list(dpf_sound_test_server, create_psd_from_txt_data):
    psd = create_psd_from_txt_data
    frequency_list = [
        261.090087890625,
        524.871826171875,
        785.9619140625,
        1047.052001953125,
        1310.833740234375,
        1571.923828125,
        1835.70556640625,
        2096.795654296875,
        2360.577392578125,
    ]
    frequency_list_rounded = [
        261.0,
        524.0,
        785.0,
        1047.0,
        1310.0,
        1571.0,
        1835.0,
        2096.0,
        2360.0,
    ]
    tnr = ToneToNoiseRatio(psd, frequency_list=frequency_list_rounded)

    tnr.process()

    assert len(frequency_list) == len(tnr.get_peaks_frequencies())
    for l_i in range(len(frequency_list)):
        assert frequency_list[l_i] == pytest.approx(tnr.get_peaks_frequencies()[l_i])
