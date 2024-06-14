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

from ansys.dpf.core import Field, FieldsContainer
import numpy as np
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundException
from ansys.sound.core.psychoacoustics import LoudnessISO532_1_TimeVarying
from ansys.sound.core.signal_utilities import LoadWav


def test_loudness_iso_532_1_time_varying_instantiation(dpf_sound_test_server):
    time_varying_loudness_computer = LoudnessISO532_1_TimeVarying()
    assert time_varying_loudness_computer != None


def test_loudness_iso_532_1_time_varying_process(dpf_sound_test_server):
    time_varying_loudness_computer = LoudnessISO532_1_TimeVarying()

    # no signal -> error 1
    with pytest.raises(PyAnsysSoundException) as excinfo:
        time_varying_loudness_computer.process()
    assert (
        str(excinfo.value)
        == "No signal for loudness vs time computation. Use LoudnessISO532_1_TimeVarying.signal"
    )

    # get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # set signal as field container
    time_varying_loudness_computer.signal = fc
    # compute: no error
    time_varying_loudness_computer.process()

    # set signal as field
    time_varying_loudness_computer.signal = fc[0]
    # compute: no error
    time_varying_loudness_computer.process()


def test_loudness_iso_532_1_time_varying_get_output(dpf_sound_test_server):
    time_varying_loudness_computer = LoudnessISO532_1_TimeVarying()
    # get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    output = time_varying_loudness_computer.get_output()
    assert output == None

    # set signal
    time_varying_loudness_computer.signal = fc
    # compute
    time_varying_loudness_computer.process()

    (
        loudnessVsTimeSone,
        N5,
        N10,
        loudnessVsTimePhon,
        L5,
        L10,
    ) = time_varying_loudness_computer.get_output()
    assert loudnessVsTimeSone != None
    assert N5 != None
    assert N10 != None
    assert loudnessVsTimePhon != None
    assert L5 != None
    assert L10 != None


def test_loudness_iso_532_1_time_varying_get_output_as_nparray_from_field_container(
    dpf_sound_test_server,
):
    time_varying_loudness_computer = LoudnessISO532_1_TimeVarying()
    # get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    output = time_varying_loudness_computer.get_output_as_nparray()
    assert output == None

    # set signal
    time_varying_loudness_computer.signal = fc
    # compute
    time_varying_loudness_computer.process()

    (
        loudnessVsTimeSone,
        N5,
        N10,
        loudnessVsTimePhon,
        L5,
        L10,
    ) = time_varying_loudness_computer.get_output_as_nparray()

    assert type(loudnessVsTimeSone) == np.ndarray
    assert len(loudnessVsTimeSone) == 1770
    assert loudnessVsTimeSone[0] == pytest.approx(0.0)
    assert loudnessVsTimeSone[10] == pytest.approx(0.06577175855636597)
    assert loudnessVsTimeSone[100] == pytest.approx(5.100262641906738)
    assert type(loudnessVsTimePhon) == np.ndarray
    assert len(loudnessVsTimePhon) == 1770
    assert loudnessVsTimePhon[0] == pytest.approx(3.0)
    assert loudnessVsTimePhon[10] == pytest.approx(15.430279731750488)
    assert loudnessVsTimePhon[100] == pytest.approx(63.505714416503906)
    assert type(N5) == np.ndarray
    assert len(N5) == 1
    assert N5[0] == pytest.approx(45.12802505493164)
    assert type(N10) == np.ndarray
    assert len(N10) == 1
    assert N10[0] == pytest.approx(44.12368392944336)
    assert type(L5) == np.ndarray
    assert len(L5) == 1
    assert L5[0] == pytest.approx(94.95951843261719)
    assert type(L10) == np.ndarray
    assert len(L10) == 1
    assert L10[0] == pytest.approx(94.63481140136719)


def test_loudness_iso_532_1_time_varying_get_output_as_nparray_from_field(dpf_sound_test_server):
    time_varying_loudness_computer = LoudnessISO532_1_TimeVarying()
    # get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # set signal
    time_varying_loudness_computer.signal = fc[0]
    # compute
    time_varying_loudness_computer.process()

    (
        loudnessVsTimeSone,
        N5,
        N10,
        loudnessVsTimePhon,
        L5,
        L10,
    ) = time_varying_loudness_computer.get_output_as_nparray()
    assert type(loudnessVsTimeSone) == np.ndarray
    assert len(loudnessVsTimeSone) == 1770
    assert loudnessVsTimeSone[0] == pytest.approx(0.0)
    assert loudnessVsTimeSone[10] == pytest.approx(0.06577175855636597)
    assert loudnessVsTimeSone[100] == pytest.approx(5.100262641906738)
    assert type(loudnessVsTimePhon) == np.ndarray
    assert len(loudnessVsTimePhon) == 1770
    assert loudnessVsTimePhon[0] == pytest.approx(3.0)
    assert loudnessVsTimePhon[10] == pytest.approx(15.430279731750488)
    assert loudnessVsTimePhon[100] == pytest.approx(63.505714416503906)
    assert type(N5) == np.ndarray
    assert len(N5) == 1
    assert N5[0] == pytest.approx(45.12802505493164)
    assert type(N10) == np.ndarray
    assert len(N10) == 1
    assert N10[0] == pytest.approx(44.12368392944336)
    assert type(L5) == np.ndarray
    assert len(L5) == 1
    assert L5[0] == pytest.approx(94.95951843261719)
    assert type(L10) == np.ndarray
    assert len(L10) == 1
    assert L10[0] == pytest.approx(94.63481140136719)


def test_loudness_iso_532_1_time_varying_get_loudness_vs_time_sone(dpf_sound_test_server):
    time_varying_loudness_computer = LoudnessISO532_1_TimeVarying()
    # get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    output = time_varying_loudness_computer.get_loudness_sone_vs_time()
    assert output == None

    # set signal
    time_varying_loudness_computer.signal = fc
    # compute
    time_varying_loudness_computer.process()

    loudnessVsTimeSone = time_varying_loudness_computer.get_loudness_sone_vs_time(0)
    assert type(loudnessVsTimeSone) == np.ndarray
    assert len(loudnessVsTimeSone) == 1770
    assert loudnessVsTimeSone[0] == pytest.approx(0.0)
    assert loudnessVsTimeSone[10] == pytest.approx(0.06577175855636597)
    assert loudnessVsTimeSone[100] == pytest.approx(5.100262641906738)


def test_loudness_iso_532_1_time_varying_get_loudness_vs_time_sone_from_multichannel_fc(
    dpf_sound_test_server,
):
    time_varying_loudness_computer = LoudnessISO532_1_TimeVarying()
    # get a signal
    wav_loader = LoadWav(pytest.data_path_white_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # set signal
    time_varying_loudness_computer.signal = fc
    # compute
    time_varying_loudness_computer.process()

    loudnessVsTimeSone = time_varying_loudness_computer.get_loudness_sone_vs_time(0)
    assert type(loudnessVsTimeSone) == np.ndarray
    assert len(loudnessVsTimeSone) == 5000
    assert loudnessVsTimeSone[0] == pytest.approx(0.0)
    assert loudnessVsTimeSone[10] == pytest.approx(22.091352462768555)
    assert loudnessVsTimeSone[100] == pytest.approx(38.29069900512695)


def test_loudness_iso_532_1_time_varying_get_loudness_vs_time_phon(dpf_sound_test_server):
    time_varying_loudness_computer = LoudnessISO532_1_TimeVarying()
    # get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    output = time_varying_loudness_computer.get_loudness_level_phon_vs_time()
    assert output == None

    # set signal
    time_varying_loudness_computer.signal = fc
    # compute
    time_varying_loudness_computer.process()

    loudnessVsTimePhon = time_varying_loudness_computer.get_loudness_level_phon_vs_time(0)
    assert type(loudnessVsTimePhon) == np.ndarray
    assert len(loudnessVsTimePhon) == 1770
    assert loudnessVsTimePhon[0] == pytest.approx(3.0)
    assert loudnessVsTimePhon[10] == pytest.approx(15.430279731750488)
    assert loudnessVsTimePhon[100] == pytest.approx(63.505714416503906)


def test_loudness_iso_532_1_time_varying_get_loudness_vs_time_from_multichannel_fc(
    dpf_sound_test_server,
):
    time_varying_loudness_computer = LoudnessISO532_1_TimeVarying()
    # get a signal
    wav_loader = LoadWav(pytest.data_path_white_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # set signal
    time_varying_loudness_computer.signal = fc
    # compute
    time_varying_loudness_computer.process()

    loudnessVsTimePhon = time_varying_loudness_computer.get_loudness_level_phon_vs_time(0)
    assert type(loudnessVsTimePhon) == np.ndarray
    assert len(loudnessVsTimePhon) == 5000
    assert loudnessVsTimePhon[0] == pytest.approx(3.0)
    assert loudnessVsTimePhon[10] == pytest.approx(84.65409851074219)
    assert loudnessVsTimePhon[100] == pytest.approx(92.58921813964844)


def test_loudness_iso_532_1_time_varying_get_N5(dpf_sound_test_server):
    time_varying_loudness_computer = LoudnessISO532_1_TimeVarying()
    # get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    output = time_varying_loudness_computer.get_N5_sone()
    assert output == None

    # set signal
    time_varying_loudness_computer.signal = fc
    # compute
    time_varying_loudness_computer.process()

    # Test errors
    with pytest.raises(
        PyAnsysSoundException,
        match=r"Specified channel index \(2\) does not exist.",
    ):
        N5 = time_varying_loudness_computer.get_N5_sone(channel_index=2)

    N5 = time_varying_loudness_computer.get_N5_sone()
    assert N5 == pytest.approx(45.12802505493164)


def test_loudness_iso_532_1_time_varying_get_N5_from_field(dpf_sound_test_server):
    time_varying_loudness_computer = LoudnessISO532_1_TimeVarying()
    # get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # set signal
    time_varying_loudness_computer.signal = fc[0]

    # compute
    time_varying_loudness_computer.process()

    # Test errors
    with pytest.raises(
        PyAnsysSoundException,
        match=r"Specified channel index \(2\) does not exist.",
    ):
        N5 = time_varying_loudness_computer.get_N5_sone(channel_index=2)

    N5 = time_varying_loudness_computer.get_N5_sone()
    assert N5 == pytest.approx(45.12802505493164)


def test_loudness_iso_532_1_time_varying_get_N10(dpf_sound_test_server):
    time_varying_loudness_computer = LoudnessISO532_1_TimeVarying()
    # get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    output = time_varying_loudness_computer.get_N10_sone()
    assert output == None

    # set signal
    time_varying_loudness_computer.signal = fc
    # compute
    time_varying_loudness_computer.process()

    N10 = time_varying_loudness_computer.get_N10_sone()
    assert N10 == pytest.approx(44.12368392944336)


def test_loudness_iso_532_1_time_varying_get_N10_from_field(dpf_sound_test_server):
    time_varying_loudness_computer = LoudnessISO532_1_TimeVarying()
    # get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # set signal
    time_varying_loudness_computer.signal = fc[0]
    # compute
    time_varying_loudness_computer.process()

    N10 = time_varying_loudness_computer.get_N10_sone()
    assert N10 == pytest.approx(44.12368392944336)


def test_loudness_iso_532_1_time_varying_get_L5(dpf_sound_test_server):
    time_varying_loudness_computer = LoudnessISO532_1_TimeVarying()
    # get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    output = time_varying_loudness_computer.get_L5_phon()
    assert output == None

    # set signal
    time_varying_loudness_computer.signal = fc
    # compute
    time_varying_loudness_computer.process()

    L5 = time_varying_loudness_computer.get_L5_phon()
    assert L5 == pytest.approx(94.95951843261719)


def test_loudness_iso_532_1_time_varying_get_L5_from_field(dpf_sound_test_server):
    time_varying_loudness_computer = LoudnessISO532_1_TimeVarying()
    # get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # set signal
    time_varying_loudness_computer.signal = fc[0]
    # compute
    time_varying_loudness_computer.process()

    L5 = time_varying_loudness_computer.get_L5_phon()
    assert L5 == pytest.approx(94.95951843261719)


def test_loudness_iso_532_1_time_varying_get_L10(dpf_sound_test_server):
    time_varying_loudness_computer = LoudnessISO532_1_TimeVarying()
    # get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    output = time_varying_loudness_computer.get_L10_phon()
    assert output == None

    # set signal
    time_varying_loudness_computer.signal = fc
    # compute
    time_varying_loudness_computer.process()

    L10 = time_varying_loudness_computer.get_L10_phon()
    assert L10 == pytest.approx(94.63481140136719)


def test_loudness_iso_532_1_time_varying_get_L10_from_field(dpf_sound_test_server):
    time_varying_loudness_computer = LoudnessISO532_1_TimeVarying()
    # get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # set signal
    time_varying_loudness_computer.signal = fc[0]
    # compute
    time_varying_loudness_computer.process()

    L10 = time_varying_loudness_computer.get_L10_phon()
    assert L10 == pytest.approx(94.63481140136719)


def test_loudness_iso_532_1_time_varying_get_time_scale(dpf_sound_test_server):
    time_varying_loudness_computer = LoudnessISO532_1_TimeVarying()
    # get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # set signal
    time_varying_loudness_computer.signal = fc[0]

    assert time_varying_loudness_computer.get_time_scale() == None

    time_varying_loudness_computer.process()
    time_scale = time_varying_loudness_computer.get_time_scale()

    assert len(time_scale) == 1770
    assert time_scale[0] == 0
    assert time_scale[10] == pytest.approx(0.019999999552965164)
    assert time_scale[42] == pytest.approx(0.08399999886751175)
    assert time_scale[100] == pytest.approx(0.20000000298023224)
    assert time_scale[110] == pytest.approx(0.2199999988079071)


@patch("matplotlib.pyplot.show")
def test_loudness_iso_532_1_time_varying_plot_from_field_container(
    mock_show, dpf_sound_test_server
):
    time_varying_loudness_computer = LoudnessISO532_1_TimeVarying()

    # Load a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    time_varying_loudness_computer.signal = fc

    # Plot before process -> error
    with pytest.raises(
        PyAnsysSoundException,
        match="Output has not been processed yet, use LoudnessISO532_1_TimeVarying.process().",
    ):
        time_varying_loudness_computer.plot()

    # Compute
    time_varying_loudness_computer.process()

    # Plot
    time_varying_loudness_computer.plot()

    # Add a second signal in the fields container
    # Note: No need to re-assign the signal property, as fc is simply an alias for it
    wav_loader = LoadWav(pytest.data_path_flute2_in_container)
    wav_loader.process()
    fc.add_field({"channel_number": 1}, wav_loader.get_output()[0])

    # Compute again
    time_varying_loudness_computer.process()

    # Plot
    time_varying_loudness_computer.plot()


@patch("matplotlib.pyplot.show")
def test_loudness_iso_532_1_time_varying_plot_from_field(mock_show, dpf_sound_test_server):
    time_varying_loudness_computer = LoudnessISO532_1_TimeVarying()
    # get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # set signal
    time_varying_loudness_computer.signal = fc[0]
    # compute
    time_varying_loudness_computer.process()

    # plot
    time_varying_loudness_computer.plot()


def test_loudness_iso_532_1_time_varying_set_get_signal(dpf_sound_test_server):
    time_varying_loudness_computer = LoudnessISO532_1_TimeVarying()
    fc = FieldsContainer()
    fc.labels = ["channel"]
    f = Field()
    f.data = 42 * np.ones(3)
    fc.add_field({"channel": 0}, f)
    fc.name = "testField"
    time_varying_loudness_computer.signal = fc
    fc_from_get = time_varying_loudness_computer.signal

    assert fc_from_get.name == "testField"
    assert len(fc_from_get) == 1
    assert fc_from_get[0].data[0, 2] == 42
