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

import numpy as np
import pytest
from ansys.dpf.core import (GenericDataContainer, TimeFreqSupport,
                            fields_factory, locations)

from ansys.sound.core._pyansys_sound import PyAnsysSoundException
from ansys.sound.core.examples_helpers._get_example_files import \
    get_absolute_path_for_flute_psd_txt
from ansys.sound.core.psychoacoustics import ProminenceRatio


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


def test_prominence_ratio_instantiation(dpf_sound_test_server):
    pr = ProminenceRatio()
    assert pr != None


def test_prominence_ratio_set_get_psd(dpf_sound_test_server, create_psd_from_txt_data):
    pr = ProminenceRatio()

    psd = create_psd_from_txt_data
    pr.psd = psd
    psd_from_get = pr.psd

    assert len(psd_from_get.data) == 8193
    assert psd_from_get.data[42] == pytest.approx(6.8086340335798055e-09)


def test_prominence_ratio_set_get_frequency_list(dpf_sound_test_server):
    pr = ProminenceRatio()

    frequency_list = [2, 5, 9]
    pr.frequency_list = frequency_list
    frequency_list_from_get = pr.frequency_list

    assert len(frequency_list_from_get) == 3
    assert frequency_list_from_get[2] == 9


def test_prominence_ratio_process(dpf_sound_test_server, create_psd_from_txt_data):
    pr = ProminenceRatio()

    # no signal -> error 1
    with pytest.raises(PyAnsysSoundException) as excinfo:
        pr.process()
    assert str(excinfo.value) == "No PSD found for PR computation. Use 'ProminenceRatio.psd'."

    psd = create_psd_from_txt_data
    pr.psd = psd

    # compute: no error
    pr.process()


def test_prominence_ratio_get_output(dpf_sound_test_server, create_psd_from_txt_data):
    pr = ProminenceRatio()

    psd = create_psd_from_txt_data
    pr.psd = psd

    # no compute: return None
    assert pr.get_output() == None

    # compute: no error
    pr.process()

    pr_container = pr.get_output()
    assert pr_container != None
    assert type(pr_container) == GenericDataContainer


def test_prominence_ratio_get_output_as_nparray(dpf_sound_test_server, create_psd_from_txt_data):
    pr = ProminenceRatio()

    psd = create_psd_from_txt_data
    pr.psd = psd

    # no compute: return None
    assert pr.get_output_as_nparray() == None

    pr.process()

    (
        frequency_Hz,
        pr_db,
        level_db,
        bandwidth_low,
        bandwidth_high,
        pr_max,
    ) = pr.get_output_as_nparray()

    assert type(frequency_Hz) == np.ndarray
    assert frequency_Hz.size == 14
    assert frequency_Hz[0] == pytest.approx(261.09008789)
    assert frequency_Hz[6] == pytest.approx(3671.41113281)

    assert type(pr_db) == np.ndarray
    assert pr_db.size == 14
    assert pr_db[0] == pytest.approx(38.79766083)
    assert pr_db[6] == pytest.approx(2.68530488)

    assert type(level_db) == np.ndarray
    assert level_db.size == 14
    assert level_db[0] == pytest.approx(71.11832306)
    assert level_db[6] == pytest.approx(45.19826385)

    assert type(bandwidth_low) == np.ndarray
    assert bandwidth_low.size == 14
    assert bandwidth_low[0] == pytest.approx(231.48193359)
    assert bandwidth_low[6] == pytest.approx(3652.56958008)

    assert type(bandwidth_high) == np.ndarray
    assert bandwidth_high.size == 14
    assert bandwidth_high[0] == pytest.approx(282.62329102)
    assert bandwidth_high[6] == pytest.approx(3698.32763672)

    assert type(pr_max) == np.ndarray
    assert pr_max.size == 1
    assert pr_max == pytest.approx(44.87330627441406)


def test_prominence_ratio_get_nb_tones(dpf_sound_test_server, create_psd_from_txt_data):
    pr = ProminenceRatio()

    psd = create_psd_from_txt_data
    pr.psd = psd

    with pytest.raises(PyAnsysSoundException) as excinfo:
        pr.get_nb_tones()
    assert (
        str(excinfo.value)
        == "Output is not processed yet. \
                    Use the 'ProminenceRatio.process()' method."
    )

    pr.process()
    assert pr.get_nb_tones() == 14

    # flat spectrum -> no peaks to detect
    psd.data = np.ones(len(psd.data))
    pr.process()
    assert pr.get_nb_tones() == 0


def test_prominence_ratio_get_peaks_frequencies(dpf_sound_test_server, create_psd_from_txt_data):
    pr = ProminenceRatio()

    psd = create_psd_from_txt_data
    pr.psd = psd

    # no compute: return None
    assert pr.get_peaks_frequencies() == None

    pr.process()
    peaks_frequencies = pr.get_peaks_frequencies()
    assert type(peaks_frequencies) == np.ndarray
    assert peaks_frequencies.size == 14
    assert peaks_frequencies[0] == pytest.approx(261.09008789)
    assert peaks_frequencies[6] == pytest.approx(3671.41113281)


def test_prominence_ratio_get_PR_values(dpf_sound_test_server, create_psd_from_txt_data):
    pr = ProminenceRatio()

    psd = create_psd_from_txt_data
    pr.psd = psd

    # no compute: return None
    assert pr.get_PR_values() == None

    pr.process()
    pr_db = pr.get_PR_values()
    assert type(pr_db) == np.ndarray
    assert pr_db.size == 14
    assert pr_db[0] == pytest.approx(38.79766083)
    assert pr_db[6] == pytest.approx(2.68530488)


def test_prominence_ratio_get_peaks_levels(dpf_sound_test_server, create_psd_from_txt_data):
    pr = ProminenceRatio()

    psd = create_psd_from_txt_data
    pr.psd = psd

    # no compute: return None
    assert pr.get_peaks_levels() == None

    pr.process()
    level_db = pr.get_peaks_levels()
    assert type(level_db) == np.ndarray
    assert level_db.size == 14
    assert level_db[0] == pytest.approx(71.11832306)
    assert level_db[6] == pytest.approx(45.19826385)


def test_prominence_ratio_get_peaks_low_frequencies(
    dpf_sound_test_server, create_psd_from_txt_data
):
    pr = ProminenceRatio()

    psd = create_psd_from_txt_data
    pr.psd = psd

    # no compute: return None
    assert pr.get_peaks_low_frequencies() == None

    pr.process()
    bandwidth_low = pr.get_peaks_low_frequencies()
    assert type(bandwidth_low) == np.ndarray
    assert bandwidth_low.size == 14
    assert bandwidth_low[0] == pytest.approx(231.48193359)
    assert bandwidth_low[6] == pytest.approx(3652.56958008)


def test_prominence_ratio_get_peaks_high_frequencies(
    dpf_sound_test_server, create_psd_from_txt_data
):
    pr = ProminenceRatio()

    psd = create_psd_from_txt_data
    pr.psd = psd

    # no compute: return None
    assert pr.get_peaks_high_frequencies() == None

    pr.process()
    bandwidth_high = pr.get_peaks_high_frequencies()
    assert type(bandwidth_high) == np.ndarray
    assert bandwidth_high.size == 14
    assert bandwidth_high[0] == pytest.approx(282.62329102)
    assert bandwidth_high[6] == pytest.approx(3698.32763672)


def test_prominence_ratio_get_max_PR_value(dpf_sound_test_server, create_psd_from_txt_data):
    pr = ProminenceRatio()

    psd = create_psd_from_txt_data
    pr.psd = psd

    # no compute: return None
    assert pr.get_max_PR_value() == None

    pr.process()
    pr_max = pr.get_max_PR_value()
    assert type(pr_max) == np.ndarray
    assert pr_max.size == 1
    assert pr_max == pytest.approx(44.87330627441406)


def test_prominence_ratio_get_all_tone_infos(dpf_sound_test_server, create_psd_from_txt_data):
    pr = ProminenceRatio()

    psd = create_psd_from_txt_data
    pr.psd = psd

    with pytest.raises(PyAnsysSoundException) as excinfo:
        pr.get_single_tone_info(1)
    assert (
        str(excinfo.value)
        == "Output is not processed yet. \
                    Use the 'ProminenceRatio.process()' method."
    )

    pr.process()
    with pytest.raises(PyAnsysSoundException) as excinfo:
        pr.get_single_tone_info(14)
    assert str(excinfo.value) == "Tone index is out of bound. It must be between 0 and 13."

    (
        peaks_frequency,
        pr_db,
        level_db,
        bandwidth_low,
        bandwidth_high,
    ) = pr.get_single_tone_info(6)

    assert peaks_frequency == pytest.approx(3671.41113281)
    assert pr_db == pytest.approx(2.68530488)
    assert level_db == pytest.approx(45.19826385)
    assert bandwidth_low == pytest.approx(3652.56958008)
    assert bandwidth_high == pytest.approx(3698.32763672)

    # flat PSD -> nothing to detect
    psd.data = np.ones(len(psd.data))
    pr.process()
    with pytest.raises(PyAnsysSoundException) as excinfo:
        pr.get_single_tone_info(1)
    assert str(excinfo.value) == "No peak is detected."


def test_prominence_ratio_get_reference_curve(dpf_sound_test_server, create_psd_from_txt_data):
    pr = ProminenceRatio()

    psd = create_psd_from_txt_data

    with pytest.raises(PyAnsysSoundException) as excinfo:
        pr.get_reference_curve()
    assert str(excinfo.value) == "No PSD set. Use 'ProminenceRatio.psd'."

    pr.psd = psd
    ref_curve = pr.get_reference_curve()

    assert type(ref_curve) == np.ndarray
    assert ref_curve.size == 8193
    assert ref_curve[0] == 0
    assert ref_curve[33] == 0
    assert ref_curve[34] == pytest.approx(19.38502432785643)
    assert ref_curve[42] == pytest.approx(18.467320594299977)
    assert ref_curve[371] == pytest.approx(9.006074402128524)
    assert ref_curve[372] == pytest.approx(9.0)
    assert ref_curve[4168] == pytest.approx(9.0)
    assert ref_curve[4169] == 0
    assert ref_curve[5896] == 0


@patch("matplotlib.pyplot.show")
def test_prominence_ratio_plot(dpf_sound_test_server, create_psd_from_txt_data):
    pr = ProminenceRatio()

    psd = create_psd_from_txt_data
    pr.psd = psd

    with pytest.raises(PyAnsysSoundException) as excinfo:
        pr.plot()
    assert (
        str(excinfo.value)
        == "Output is not processed yet. \
                    Use the 'ProminenceRatio.process()' method."
    )

    pr.process()
    pr.plot()


def test_prominence_ratio_with_frequency_list(dpf_sound_test_server, create_psd_from_txt_data):
    psd = create_psd_from_txt_data
    frequency_list = [
        261.090087890625,
        524.871826171875,
        785.9619140625,
        1047.052001953125,
        1835.70556640625,
        3404.937744140625,
        3671.4111328125,
        3929.8095703125,
        5765.51513671875,
        6029.296875,
    ]
    frequency_list_rounded = [
        261.0,
        524.0,
        785.0,
        1047.0,
        1835.0,
        3404.0,
        3671.0,
        3929.0,
        5765.0,
        6029.0,
    ]
    pr = ProminenceRatio(psd, frequency_list=frequency_list_rounded)

    pr.process()

    assert len(frequency_list) == len(pr.get_peaks_frequencies())
    for l_i in range(len(frequency_list)):
        assert frequency_list[l_i] == pytest.approx(pr.get_peaks_frequencies()[l_i])
