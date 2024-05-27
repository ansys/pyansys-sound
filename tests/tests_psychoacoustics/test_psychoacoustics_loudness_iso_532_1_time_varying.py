from unittest.mock import patch

from ansys.dpf.core import Field, FieldsContainer
import numpy as np
import pytest

from ansys.dpf.sound.psychoacoustics import LoudnessISO532_1_TimeVarying
from ansys.dpf.sound.pydpf_sound import PyDpfSoundException
from ansys.dpf.sound.signal_utilities import LoadWav


@pytest.mark.dependency()
def test_loudness_532_1_time_varying_instantiation(dpf_sound_test_server):
    time_varying_loudness_computer = LoudnessISO532_1_TimeVarying()
    assert time_varying_loudness_computer != None


@pytest.mark.dependency(depends=["test_loudness_532_1_time_varying_instantiation"])
def test_loudness_532_1_time_varying_process(dpf_sound_test_server):
    time_varying_loudness_computer = LoudnessISO532_1_TimeVarying()

    # no signal -> error 1
    with pytest.raises(PyDpfSoundException) as excinfo:
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


@pytest.mark.dependency(depends=["test_loudness_532_1_time_varying_process"])
def test_loudness_532_1_time_varying_get_output(dpf_sound_test_server):
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


@pytest.mark.dependency(depends=["test_loudness_532_1_time_varying_process"])
def test_loudness_532_1_time_varying_get_output_as_nparray_from_field_container(
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


@pytest.mark.dependency(depends=["test_loudness_532_1_time_varying_process"])
def test_loudness_532_1_time_varying_get_output_as_nparray_from_field(dpf_sound_test_server):
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


pytest.mark.dependency(depends=["test_loudness_532_1_time_varying_process"])


def test_loudness_532_1_time_varying_get_loudness_vs_time_sone(dpf_sound_test_server):
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


pytest.mark.dependency(depends=["test_loudness_532_1_time_varying_process"])


def test_loudness_532_1_time_varying_get_loudness_vs_time_sone_from_multichannel_fc(
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


pytest.mark.dependency(depends=["test_loudness_532_1_time_varying_process"])


def test_loudness_532_1_time_varying_get_loudness_vs_time_phon(dpf_sound_test_server):
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


pytest.mark.dependency(depends=["test_loudness_532_1_time_varying_process"])


def test_loudness_532_1_time_varying_get_loudness_vs_time_from_multichannel_fc(
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


pytest.mark.dependency(depends=["test_loudness_532_1_time_varying_process"])


def test_loudness_532_1_time_varying_get_N5(dpf_sound_test_server):
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

    N5 = time_varying_loudness_computer.get_N5_sone()
    assert N5 == pytest.approx(45.12802505493164)


pytest.mark.dependency(depends=["test_loudness_532_1_time_varying_process"])


def test_loudness_532_1_time_varying_get_N5_from_field(dpf_sound_test_server):
    time_varying_loudness_computer = LoudnessISO532_1_TimeVarying()
    # get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # set signal
    time_varying_loudness_computer.signal = fc[0]
    # compute
    time_varying_loudness_computer.process()

    N5 = time_varying_loudness_computer.get_N5_sone()
    assert N5 == pytest.approx(45.12802505493164)


pytest.mark.dependency(depends=["test_loudness_532_1_time_varying_process"])


def test_loudness_532_1_time_varying_get_N10(dpf_sound_test_server):
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


pytest.mark.dependency(depends=["test_loudness_532_1_time_varying_process"])


def test_loudness_532_1_time_varying_get_N10_from_field(dpf_sound_test_server):
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


pytest.mark.dependency(depends=["test_loudness_532_1_time_varying_process"])


def test_loudness_532_1_time_varying_get_L5(dpf_sound_test_server):
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


pytest.mark.dependency(depends=["test_loudness_532_1_time_varying_process"])


def test_loudness_532_1_time_varying_get_L5_from_field(dpf_sound_test_server):
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


pytest.mark.dependency(depends=["test_loudness_532_1_time_varying_process"])


def test_loudness_532_1_time_varying_get_L10(dpf_sound_test_server):
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


pytest.mark.dependency(depends=["test_loudness_532_1_time_varying_process"])


def test_loudness_532_1_time_varying_get_L10_from_field(dpf_sound_test_server):
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


@patch("matplotlib.pyplot.show")
@pytest.mark.dependency(depends=["test_loudness_532_1_time_varying_process"])
def test_loudness_532_1_time_varying_plot_from_field_container(mock_show, dpf_sound_test_server):
    time_varying_loudness_computer = LoudnessISO532_1_TimeVarying()
    # get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # set signal
    time_varying_loudness_computer.signal = fc
    # compute
    time_varying_loudness_computer.process()

    # plot
    time_varying_loudness_computer.plot()


@patch("matplotlib.pyplot.show")
@pytest.mark.dependency(depends=["test_loudness_532_1_time_varying_process"])
def test_loudness_532_1_time_varying_plot_from_field(mock_show, dpf_sound_test_server):
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


@pytest.mark.dependency(depends=["test_loudness_532_1_time_varying_instantiation"])
def test_loudness_532_1_time_varying_set_get_signal(dpf_sound_test_server):
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
