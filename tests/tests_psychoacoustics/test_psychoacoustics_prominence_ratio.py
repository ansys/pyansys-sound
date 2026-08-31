# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

from ansys.dpf.core import GenericDataContainer
import numpy as np
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundException
from ansys.sound.core.psychoacoustics import ProminenceRatio

EXP_TONE_COUNT = 14

if pytest.SOUND_VERSION_GREATER_THAN_OR_EQUAL_TO_2027R1:
    # Bug fix (ID#1457510)
    EXP_FREQ_0 = 261.1
    EXP_FREQ_6 = 3671.3999

    EXP_PR_0 = 38.90429
    EXP_PR_6 = 2.689856

    EXP_LEVEL_0 = 71.11819
    EXP_LEVEL_6 = 45.15756

    EXP_BANDWIDTH_LOW_0 = 231.5
    EXP_BANDWIDTH_LOW_6 = 3654.9

    EXP_BANDWIDTH_HIGH_0 = 280.8
    EXP_BANDWIDTH_HIGH_6 = 3698.1

    EXP_PR_MAX = 45.05140
else:
    EXP_FREQ_0 = 261.0901
    EXP_FREQ_6 = 3671.411

    EXP_PR_0 = 38.79766083
    EXP_PR_6 = 2.68530488

    EXP_LEVEL_0 = 71.11832306
    EXP_LEVEL_6 = 45.19826385

    EXP_BANDWIDTH_LOW_0 = 250.0
    EXP_BANDWIDTH_LOW_6 = 3600.0

    EXP_BANDWIDTH_HIGH_0 = 270.0
    EXP_BANDWIDTH_HIGH_6 = 3750.0

    EXP_PR_MAX = 40.0


def test_prominence_ratio_instantiation():
    """Test the instantiation of ProminenceRatio class."""
    pr = ProminenceRatio()
    assert pr != None


def test_prominence_ratio_set_get_psd(create_psd_from_txt_data):
    """Test the psd setter and getter of ProminenceRatio class."""
    pr = ProminenceRatio()

    psd = create_psd_from_txt_data
    pr.psd = psd
    psd_from_get = pr.psd

    assert len(psd_from_get.data) == 8193
    assert psd_from_get.data[42] == pytest.approx(6.8086340335798055e-09)


def test_prominence_ratio_set_get_frequency_list():
    """Test the frequency_list setter and getter of ProminenceRatio class."""
    pr = ProminenceRatio()

    frequency_list = [2, 5, 9]
    pr.frequency_list = frequency_list
    frequency_list_from_get = pr.frequency_list

    assert len(frequency_list_from_get) == 3
    assert frequency_list_from_get[2] == 9


def test_prominence_ratio_process(create_psd_from_txt_data):
    """Test the process method of ProminenceRatio class."""
    pr = ProminenceRatio()

    # no signal -> error 1
    with pytest.raises(PyAnsysSoundException) as excinfo:
        pr.process()
    assert str(excinfo.value) == "No PSD found for PR computation. Use 'ProminenceRatio.psd'."

    psd = create_psd_from_txt_data
    pr.psd = psd

    # compute: no error
    pr.process()


def test_prominence_ratio_get_output(create_psd_from_txt_data):
    """Test the get_output method of ProminenceRatio class."""
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


def test_prominence_ratio_get_output_as_nparray(create_psd_from_txt_data):
    """Test the get_output_as_nparray method of ProminenceRatio class."""
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
    assert frequency_Hz.size == EXP_TONE_COUNT
    assert frequency_Hz[0] == pytest.approx(EXP_FREQ_0)
    assert frequency_Hz[6] == pytest.approx(EXP_FREQ_6)

    assert type(pr_db) == np.ndarray
    assert pr_db.size == EXP_TONE_COUNT
    assert pr_db[0] == pytest.approx(EXP_PR_0)
    assert pr_db[6] == pytest.approx(EXP_PR_6)

    assert type(level_db) == np.ndarray
    assert level_db.size == EXP_TONE_COUNT
    assert level_db[0] == pytest.approx(EXP_LEVEL_0)
    assert level_db[6] == pytest.approx(EXP_LEVEL_6)

    assert type(bandwidth_low) == np.ndarray
    assert bandwidth_low.size == EXP_TONE_COUNT
    assert bandwidth_low[0] == pytest.approx(EXP_BANDWIDTH_LOW_0)
    assert bandwidth_low[6] == pytest.approx(EXP_BANDWIDTH_LOW_6)

    assert type(bandwidth_high) == np.ndarray
    assert bandwidth_high.size == EXP_TONE_COUNT
    assert bandwidth_high[0] == pytest.approx(EXP_BANDWIDTH_HIGH_0)
    assert bandwidth_high[6] == pytest.approx(EXP_BANDWIDTH_HIGH_6)

    assert type(pr_max) == np.ndarray
    assert pr_max.size == 1
    assert pr_max == pytest.approx(EXP_PR_MAX)


def test_prominence_ratio_get_nb_tones(create_psd_from_txt_data):
    """Test getting the number of tones from ProminenceRatio computation."""
    pr = ProminenceRatio()

    psd = create_psd_from_txt_data
    pr.psd = psd

    with pytest.raises(PyAnsysSoundException) as excinfo:
        pr.get_nb_tones()
    assert str(excinfo.value) == "Output is not processed yet. \
                    Use the 'ProminenceRatio.process()' method."

    pr.process()
    assert pr.get_nb_tones() == EXP_TONE_COUNT

    # flat spectrum -> no peaks to detect
    psd.data = np.ones(len(psd.data))
    pr.process()
    assert pr.get_nb_tones() == 0


def test_prominence_ratio_get_peaks_frequencies(create_psd_from_txt_data):
    """Test getting the peaks frequencies from ProminenceRatio computation."""
    pr = ProminenceRatio()

    psd = create_psd_from_txt_data
    pr.psd = psd

    # no compute: return None
    assert pr.get_peaks_frequencies() == None

    pr.process()
    peaks_frequencies = pr.get_peaks_frequencies()
    assert type(peaks_frequencies) == np.ndarray
    assert peaks_frequencies.size == EXP_TONE_COUNT
    assert peaks_frequencies[0] == pytest.approx(EXP_FREQ_0)
    assert peaks_frequencies[6] == pytest.approx(EXP_FREQ_6)


def test_prominence_ratio_get_PR_values(create_psd_from_txt_data):
    """Test getting the prominence ratio values from ProminenceRatio computation."""
    pr = ProminenceRatio()

    psd = create_psd_from_txt_data
    pr.psd = psd

    # no compute: return None
    assert pr.get_PR_values() == None

    pr.process()
    pr_db = pr.get_PR_values()
    assert type(pr_db) == np.ndarray
    assert pr_db.size == EXP_TONE_COUNT
    assert pr_db[0] == pytest.approx(EXP_PR_0)
    assert pr_db[6] == pytest.approx(EXP_PR_6)


def test_prominence_ratio_get_peaks_levels(create_psd_from_txt_data):
    """Test getting the peaks levels from ProminenceRatio computation."""
    pr = ProminenceRatio()

    psd = create_psd_from_txt_data
    pr.psd = psd

    # no compute: return None
    assert pr.get_peaks_levels() == None

    pr.process()
    level_db = pr.get_peaks_levels()
    assert type(level_db) == np.ndarray
    assert level_db.size == EXP_TONE_COUNT
    assert level_db[0] == pytest.approx(EXP_LEVEL_0)
    assert level_db[6] == pytest.approx(EXP_LEVEL_6)


def test_prominence_ratio_get_peaks_low_frequencies(create_psd_from_txt_data):
    """Test getting the low boundary frequencies from ProminenceRatio computation."""
    pr = ProminenceRatio()

    psd = create_psd_from_txt_data
    pr.psd = psd

    # no compute: return None
    assert pr.get_peaks_low_frequencies() == None

    pr.process()
    bandwidth_low = pr.get_peaks_low_frequencies()
    assert type(bandwidth_low) == np.ndarray
    assert bandwidth_low.size == EXP_TONE_COUNT
    assert bandwidth_low[0] == pytest.approx(EXP_BANDWIDTH_LOW_0)
    assert bandwidth_low[6] == pytest.approx(EXP_BANDWIDTH_LOW_6)


def test_prominence_ratio_get_peaks_high_frequencies(create_psd_from_txt_data):
    """Test getting the high boundary frequencies from ProminenceRatio computation."""
    pr = ProminenceRatio()

    psd = create_psd_from_txt_data
    pr.psd = psd

    # no compute: return None
    assert pr.get_peaks_high_frequencies() == None

    pr.process()
    bandwidth_high = pr.get_peaks_high_frequencies()
    assert type(bandwidth_high) == np.ndarray
    assert bandwidth_high.size == EXP_TONE_COUNT
    assert bandwidth_high[0] == pytest.approx(EXP_BANDWIDTH_HIGH_0)
    assert bandwidth_high[6] == pytest.approx(EXP_BANDWIDTH_HIGH_6)


def test_prominence_ratio_get_max_PR_value(create_psd_from_txt_data):
    """Test getting the maximum prominence ratio value from ProminenceRatio computation."""
    pr = ProminenceRatio()

    psd = create_psd_from_txt_data
    pr.psd = psd

    # no compute: return None
    assert pr.get_max_PR_value() == None

    pr.process()
    pr_max = pr.get_max_PR_value()
    assert type(pr_max) == np.ndarray
    assert pr_max.size == 1
    assert pr_max == pytest.approx(EXP_PR_MAX)


def test_prominence_ratio_get_all_tone_infos(create_psd_from_txt_data):
    """Test getting all tone information from ProminenceRatio computation."""
    pr = ProminenceRatio()

    psd = create_psd_from_txt_data
    pr.psd = psd

    with pytest.raises(PyAnsysSoundException) as excinfo:
        pr.get_single_tone_info(1)
    assert str(excinfo.value) == "Output is not processed yet. \
                    Use the 'ProminenceRatio.process()' method."

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

    assert peaks_frequency == pytest.approx(EXP_FREQ_6)
    assert pr_db == pytest.approx(EXP_PR_6)
    assert level_db == pytest.approx(EXP_LEVEL_6)
    assert bandwidth_low == pytest.approx(EXP_BANDWIDTH_LOW_6)
    assert bandwidth_high == pytest.approx(EXP_BANDWIDTH_HIGH_6)

    # flat PSD -> nothing to detect
    psd.data = np.ones(len(psd.data))
    pr.process()
    with pytest.raises(PyAnsysSoundException) as excinfo:
        pr.get_single_tone_info(1)
    assert str(excinfo.value) == "No peak is detected."


def test_prominence_ratio_get_reference_curve(create_psd_from_txt_data):
    """Test getting the reference curve from ProminenceRatio computation."""
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
def test_prominence_ratio_plot(mock_show, create_psd_from_txt_data):
    """Test the plot method of ProminenceRatio class."""
    pr = ProminenceRatio()

    psd = create_psd_from_txt_data
    pr.psd = psd

    with pytest.raises(PyAnsysSoundException) as excinfo:
        pr.plot()
    assert str(excinfo.value) == "Output is not processed yet. \
                    Use the 'ProminenceRatio.process()' method."

    pr.process()
    pr.plot()


def test_prominence_ratio_with_frequency_list(create_psd_from_txt_data):
    """Test ProminenceRatio computation with a custom frequency list."""
    psd = create_psd_from_txt_data
    frequency_list = [
        261.1,
        524.9,
        786.0,
        1047.1,
        1835.7,
        3404.9,
        3671.4,
        3929.8,
        5765.5,
        6029.3,
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
        assert pr.get_peaks_frequencies()[l_i] == pytest.approx(frequency_list[l_i])
