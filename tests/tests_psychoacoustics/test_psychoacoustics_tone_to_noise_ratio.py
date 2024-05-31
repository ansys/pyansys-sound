from unittest.mock import patch

from ansys.dpf.core import GenericDataContainer, TimeFreqSupport, fields_factory, locations
import numpy as np
import pytest

from ansys.dpf.sound.examples_helpers._get_example_files import get_absolute_path_for_flute_psd_txt
from ansys.dpf.sound.psychoacoustics import ToneToNoiseRatio
from ansys.dpf.sound.pydpf_sound import PyDpfSoundException


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
    trn = ToneToNoiseRatio()
    assert trn != None


def test_tone_to_noise_ratio_set_get_psd(dpf_sound_test_server, create_psd_from_txt_data):
    trn = ToneToNoiseRatio()

    psd = create_psd_from_txt_data
    trn.psd = psd
    psd_from_get = trn.psd

    assert len(psd_from_get.data) == 8193
    assert psd_from_get.data[42] == pytest.approx(6.8086340335798055e-09)


def test_tone_to_noise_ratio_set_get_frequency_list(dpf_sound_test_server):
    trn = ToneToNoiseRatio()

    frequency_list = [2, 5, 9]
    trn.frequency_list = frequency_list
    frequency_list_from_get = trn.frequency_list

    assert len(frequency_list_from_get) == 3
    assert frequency_list_from_get[2] == 9


def test_tone_to_noise_ratio_process(dpf_sound_test_server, create_psd_from_txt_data):
    trn = ToneToNoiseRatio()

    # no signal -> error 1
    with pytest.raises(PyDpfSoundException) as excinfo:
        trn.process()
    assert str(excinfo.value) == "No PSD for TNR computation. Use ToneToNoiseRatio.psd."

    psd = create_psd_from_txt_data
    trn.psd = psd

    # compute: no error
    trn.process()


def test_tone_to_noise_ratio_get_output(dpf_sound_test_server, create_psd_from_txt_data):
    trn = ToneToNoiseRatio()

    psd = create_psd_from_txt_data
    trn.psd = psd

    # no compute: return None
    assert trn.get_output() == None

    # compute: no error
    trn.process()

    tnr_container = trn.get_output()
    assert tnr_container != None
    assert type(tnr_container) == GenericDataContainer


def test_tone_to_noise_ratio_get_output_as_nparray(dpf_sound_test_server, create_psd_from_txt_data):
    trn = ToneToNoiseRatio()

    psd = create_psd_from_txt_data
    trn.psd = psd

    # no compute: return None
    assert trn.get_output_as_nparray() == None

    trn.process()

    (
        frequency_Hz,
        tnr_db,
        level_db,
        bandwidth_low,
        bandwidth_high,
        tnr_max,
    ) = trn.get_output_as_nparray()

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
    trn = ToneToNoiseRatio()

    psd = create_psd_from_txt_data
    trn.psd = psd

    with pytest.raises(PyDpfSoundException) as excinfo:
        trn.get_nb_tones()
    assert (
        str(excinfo.value) == "Output has not been processed yet, use ToneToNoiseRatio.process()."
    )

    trn.process()
    assert trn.get_nb_tones() == 11

    # flat spectrum -> no peaks to detect
    psd.data = np.ones(len(psd.data))
    trn.process()
    assert trn.get_nb_tones() == 0


def test_tone_to_noise_ratio_get_peaks_frequencies(dpf_sound_test_server, create_psd_from_txt_data):
    trn = ToneToNoiseRatio()

    psd = create_psd_from_txt_data
    trn.psd = psd

    # no compute: return None
    assert trn.get_peaks_frequencies() == None

    trn.process()
    peaks_frequencies = trn.get_peaks_frequencies()
    assert type(peaks_frequencies) == np.ndarray
    assert peaks_frequencies.size == 11
    assert peaks_frequencies[0] == pytest.approx(261.090087890625)
    assert peaks_frequencies[6] == pytest.approx(1835.70556640625)


def test_tone_to_noise_ratio_get_TNR_values(dpf_sound_test_server, create_psd_from_txt_data):
    trn = ToneToNoiseRatio()

    psd = create_psd_from_txt_data
    trn.psd = psd

    # no compute: return None
    assert trn.get_TNR_values() == None

    trn.process()
    tnr_db = trn.get_TNR_values()
    assert type(tnr_db) == np.ndarray
    assert tnr_db.size == 11
    assert tnr_db[0] == pytest.approx(38.04449462890625)
    assert tnr_db[6] == pytest.approx(32.670352935791016)


def test_tone_to_noise_ratio_get_peaks_levels(dpf_sound_test_server, create_psd_from_txt_data):
    trn = ToneToNoiseRatio()

    psd = create_psd_from_txt_data
    trn.psd = psd

    # no compute: return None
    assert trn.get_peaks_levels() == None

    trn.process()
    level_db = trn.get_peaks_levels()
    assert type(level_db) == np.ndarray
    assert level_db.size == 11
    assert level_db[0] == pytest.approx(71.11832305908203)
    assert level_db[6] == pytest.approx(72.64159843444824)


def test_tone_to_noise_ratio_get_peaks_low_frequencies(
    dpf_sound_test_server, create_psd_from_txt_data
):
    trn = ToneToNoiseRatio()

    psd = create_psd_from_txt_data
    trn.psd = psd

    # no compute: return None
    assert trn.get_peaks_low_frequencies() == None

    trn.process()
    bandwidth_low = trn.get_peaks_low_frequencies()
    assert type(bandwidth_low) == np.ndarray
    assert bandwidth_low.size == 11
    assert bandwidth_low[0] == pytest.approx(231.48193359375)
    assert bandwidth_low[6] == pytest.approx(1808.7890625)


def test_tone_to_noise_ratio_get_peaks_high_frequencies(
    dpf_sound_test_server, create_psd_from_txt_data
):
    trn = ToneToNoiseRatio()

    psd = create_psd_from_txt_data
    trn.psd = psd

    # no compute: return None
    assert trn.get_peaks_high_frequencies() == None

    trn.process()
    bandwidth_high = trn.get_peaks_high_frequencies()
    assert type(bandwidth_high) == np.ndarray
    assert bandwidth_high.size == 11
    assert bandwidth_high[0] == pytest.approx(282.623291015625)
    assert bandwidth_high[6] == pytest.approx(1929.913330078125)


def test_tone_to_noise_ratio_get_max_TNR_value(dpf_sound_test_server, create_psd_from_txt_data):
    trn = ToneToNoiseRatio()

    psd = create_psd_from_txt_data
    trn.psd = psd

    # no compute: return None
    assert trn.get_max_TNR_value() == None

    trn.process()
    tnr_max = trn.get_max_TNR_value()
    assert type(tnr_max) == np.ndarray
    assert tnr_max.size == 1
    assert tnr_max == pytest.approx(38.04449462890625)


def test_tone_to_noise_ratio_get_all_tone_infos(dpf_sound_test_server, create_psd_from_txt_data):
    trn = ToneToNoiseRatio()

    psd = create_psd_from_txt_data
    trn.psd = psd

    with pytest.raises(PyDpfSoundException) as excinfo:
        trn.get_single_tone_info(1)
    assert (
        str(excinfo.value) == "Output has not been processed yet, use ToneToNoiseRatio.process()."
    )

    trn.process()
    with pytest.raises(PyDpfSoundException) as excinfo:
        trn.get_single_tone_info(14)
    assert str(excinfo.value) == "Out of bound index. tone_index must be between 0 and 10."

    (
        peaks_frequency,
        tnr_db,
        level_db,
        bandwidth_low,
        bandwidth_high,
    ) = trn.get_single_tone_info(6)

    assert peaks_frequency == pytest.approx(1835.70556640625)
    assert tnr_db == pytest.approx(32.670352935791016)
    assert level_db == pytest.approx(72.64159843444824)
    assert bandwidth_low == pytest.approx(1808.7890625)
    assert bandwidth_high == pytest.approx(1929.913330078125)

    # flat PSD -> nothing to detect
    psd.data = np.ones(len(psd.data))
    trn.process()
    with pytest.raises(PyDpfSoundException) as excinfo:
        trn.get_single_tone_info(1)
    assert str(excinfo.value) == "No peak detected."


def test_tone_to_noise_ratio_get_reference_curve(dpf_sound_test_server, create_psd_from_txt_data):
    trn = ToneToNoiseRatio()

    psd = create_psd_from_txt_data

    with pytest.raises(PyDpfSoundException) as excinfo:
        trn.get_reference_curve()
    assert str(excinfo.value) == "No PSD set. Use ToneToNoiseRatio.psd."

    trn.psd = psd
    ref_curve = trn.get_reference_curve()

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
    trn = ToneToNoiseRatio()

    psd = create_psd_from_txt_data
    trn.psd = psd

    with pytest.raises(PyDpfSoundException) as excinfo:
        trn.plot()
    assert (
        str(excinfo.value) == "Output has not been processed yet, use ToneToNoiseRatio.process()."
    )

    trn.process()
    trn.plot()


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
    trn = ToneToNoiseRatio(psd, frequency_list=frequency_list_rounded)

    trn.process()

    assert len(frequency_list) == len(trn.get_peaks_frequencies())
    for l_i in range(len(frequency_list)):
        assert frequency_list[l_i] == pytest.approx(trn.get_peaks_frequencies()[l_i])
