from unittest.mock import patch

from ansys.dpf.core import Field, FieldsContainer
import numpy as np
import pytest

from ansys.dpf.sound.psychoacoustics import LoudnessVsTime
from ansys.dpf.sound.pydpf_sound import PyDpfSoundException
from ansys.dpf.sound.signal_utilities import LoadWav


@pytest.mark.dependency()
def test_loudness_vs_time_instantiation(dpf_sound_test_server):
    loudnessVsTimeComputer = LoudnessVsTime()
    assert loudnessVsTimeComputer != None


@pytest.mark.dependency(depends=["test_loudness_vs_time_instantiation"])
def test_loudness_vs_time_process(dpf_sound_test_server):
    loudnessVsTimeComputer = LoudnessVsTime()

    # no signal -> error 1
    with pytest.raises(PyDpfSoundException) as excinfo:
        loudnessVsTimeComputer.process()
    assert (
        str(excinfo.value)
        == "No signal for loudness vs time computation. Use LoudnessVsTime.signal"
    )

    # get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # set signal as field container
    loudnessVsTimeComputer.signal = fc
    # compute: no error
    loudnessVsTimeComputer.process()

    # set signal as field
    loudnessVsTimeComputer.signal = fc[0]
    # compute: no error
    loudnessVsTimeComputer.process()


@pytest.mark.dependency(depends=["test_loudness_vs_time_process"])
def test_loudness_vs_time_get_output(dpf_sound_test_server):
    loudnessVsTimeComputer = LoudnessVsTime()
    # get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    output = loudnessVsTimeComputer.get_output()
    assert output == None

    # set signal
    loudnessVsTimeComputer.signal = fc
    # compute
    loudnessVsTimeComputer.process()

    (loudnessVsTimeSone, N5, N10, loudnessVsTimePhon, L5, L10) = loudnessVsTimeComputer.get_output()
    assert loudnessVsTimeSone != None
    assert N5 != None
    assert N10 != None
    assert loudnessVsTimePhon != None
    assert L5 != None
    assert L10 != None


@pytest.mark.dependency(depends=["test_loudness_vs_time_process"])
def test_loudness_vs_time_get_output_as_nparray_from_field_container(dpf_sound_test_server):
    loudnessVsTimeComputer = LoudnessVsTime()
    # get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    output = loudnessVsTimeComputer.get_output_as_nparray()
    assert output == None

    # set signal
    loudnessVsTimeComputer.signal = fc
    # compute
    loudnessVsTimeComputer.process()

    (
        loudnessVsTimeSone,
        N5,
        N10,
        loudnessVsTimePhon,
        L5,
        L10,
    ) = loudnessVsTimeComputer.get_output_as_nparray()
    assert len(loudnessVsTimeSone) == 1770
    assert loudnessVsTimeSone[0] == 0.0
    assert loudnessVsTimeSone[10] == 0.06577175855636597
    assert loudnessVsTimeSone[100] == 5.100262641906738
    assert len(loudnessVsTimePhon) == 1770
    assert loudnessVsTimePhon[0] == 3.0
    assert loudnessVsTimePhon[10] == 15.430279731750488
    assert loudnessVsTimePhon[100] == 63.505714416503906
    assert len(N5) == 1
    assert N5[0] == 45.12802505493164
    assert len(N10) == 1
    assert N10[0] == 44.12368392944336
    assert len(L5) == 1
    assert L5[0] == 94.95951843261719
    assert len(L10) == 1
    assert L10[0] == 94.63481140136719


@pytest.mark.dependency(depends=["test_loudness_vs_time_process"])
def test_loudness_vs_time_get_output_as_nparray_from_field(dpf_sound_test_server):
    loudnessVsTimeComputer = LoudnessVsTime()
    # get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # set signal
    loudnessVsTimeComputer.signal = fc[0]
    # compute
    loudnessVsTimeComputer.process()

    (
        loudnessVsTimeSone,
        N5,
        N10,
        loudnessVsTimePhon,
        L5,
        L10,
    ) = loudnessVsTimeComputer.get_output_as_nparray()
    assert len(loudnessVsTimeSone) == 1770
    assert loudnessVsTimeSone[0] == 0.0
    assert loudnessVsTimeSone[10] == 0.06577175855636597
    assert loudnessVsTimeSone[100] == 5.100262641906738
    assert len(loudnessVsTimePhon) == 1770
    assert loudnessVsTimePhon[0] == 3.0
    assert loudnessVsTimePhon[10] == 15.430279731750488
    assert loudnessVsTimePhon[100] == 63.505714416503906
    assert len(N5) == 1
    assert N5[0] == 45.12802505493164
    assert len(N10) == 1
    assert N10[0] == 44.12368392944336
    assert len(L5) == 1
    assert L5[0] == 94.95951843261719
    assert len(L10) == 1
    assert L10[0] == 94.63481140136719


pytest.mark.dependency(depends=["test_loudness_vs_time_process"])


def test_loudness_vs_time_get_loudness_vs_time_sone(dpf_sound_test_server):
    loudnessVsTimeComputer = LoudnessVsTime()
    # get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    output = loudnessVsTimeComputer.get_loudness_vs_time_sone()
    assert output == None

    # set signal
    loudnessVsTimeComputer.signal = fc
    # compute
    loudnessVsTimeComputer.process()

    loudnessVsTimeSone = loudnessVsTimeComputer.get_loudness_vs_time_sone()
    assert len(loudnessVsTimeSone) == 1
    assert len(loudnessVsTimeSone[0].data) == 1770
    assert loudnessVsTimeSone[0].data[0] == 0.0
    assert loudnessVsTimeSone[0].data[10] == 0.06577175855636597


pytest.mark.dependency(depends=["test_loudness_vs_time_process"])


def test_loudness_vs_time_get_loudness_vs_time_phon(dpf_sound_test_server):
    loudnessVsTimeComputer = LoudnessVsTime()
    # get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    output = loudnessVsTimeComputer.get_loudness_vs_time_phon()
    assert output == None

    # set signal
    loudnessVsTimeComputer.signal = fc
    # compute
    loudnessVsTimeComputer.process()

    loudnessVsTimePhon = loudnessVsTimeComputer.get_loudness_vs_time_phon()
    assert len(loudnessVsTimePhon) == 1
    assert len(loudnessVsTimePhon[0].data) == 1770
    assert loudnessVsTimePhon[0].data[0] == 3.0
    assert loudnessVsTimePhon[0].data[10] == 15.430279731750488


pytest.mark.dependency(depends=["test_loudness_vs_time_process"])


def test_loudness_vs_time_get_N5(dpf_sound_test_server):
    loudnessVsTimeComputer = LoudnessVsTime()
    # get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    output = loudnessVsTimeComputer.get_N5_sone()
    assert output == None

    # set signal
    loudnessVsTimeComputer.signal = fc
    # compute
    loudnessVsTimeComputer.process()

    N5 = loudnessVsTimeComputer.get_N5_sone()
    assert len(N5) == 1
    assert N5[0].data[0] == 45.12802505493164


pytest.mark.dependency(depends=["test_loudness_vs_time_process"])


def test_loudness_vs_time_get_N10(dpf_sound_test_server):
    loudnessVsTimeComputer = LoudnessVsTime()
    # get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    output = loudnessVsTimeComputer.get_N10_sone()
    assert output == None

    # set signal
    loudnessVsTimeComputer.signal = fc
    # compute
    loudnessVsTimeComputer.process()

    N10 = loudnessVsTimeComputer.get_N10_sone()
    assert len(N10) == 1
    assert N10[0].data[0] == 44.12368392944336


pytest.mark.dependency(depends=["test_loudness_vs_time_process"])


def test_loudness_vs_time_get_L5(dpf_sound_test_server):
    loudnessVsTimeComputer = LoudnessVsTime()
    # get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    output = loudnessVsTimeComputer.get_L5_sone()
    assert output == None

    # set signal
    loudnessVsTimeComputer.signal = fc
    # compute
    loudnessVsTimeComputer.process()

    L5 = loudnessVsTimeComputer.get_L5_sone()
    assert len(L5) == 1
    assert L5[0].data[0] == 94.95951843261719


pytest.mark.dependency(depends=["test_loudness_vs_time_process"])


def test_loudness_vs_time_get_L10(dpf_sound_test_server):
    loudnessVsTimeComputer = LoudnessVsTime()
    # get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    output = loudnessVsTimeComputer.get_L10_sone()
    assert output == None

    # set signal
    loudnessVsTimeComputer.signal = fc
    # compute
    loudnessVsTimeComputer.process()

    L10 = loudnessVsTimeComputer.get_L10_sone()
    assert len(L10) == 1
    assert L10[0].data[0] == 94.63481140136719


@patch("matplotlib.pyplot.show")
@pytest.mark.dependency(depends=["test_loudness_vs_time_process"])
def test_loudness_vs_time_plot_from_field_container(mock_show, dpf_sound_test_server):
    loudnessVsTimeComputer = LoudnessVsTime()
    # get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # set signal
    loudnessVsTimeComputer.signal = fc
    # compute
    loudnessVsTimeComputer.process()

    # plot
    loudnessVsTimeComputer.plot()


@patch("matplotlib.pyplot.show")
@pytest.mark.dependency(depends=["test_loudness_vs_time_process"])
def test_loudness_vs_time_plot_from_field(mock_show, dpf_sound_test_server):
    loudnessVsTimeComputer = LoudnessVsTime()
    # get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # set signal
    loudnessVsTimeComputer.signal = fc[0]
    # compute
    loudnessVsTimeComputer.process()

    # plot
    loudnessVsTimeComputer.plot()


@pytest.mark.dependency(depends=["test_loudness_vs_time_instantiation"])
def test_loudness_vs_time_set_get_signal(dpf_sound_test_server):
    loudnessVsTimeComputer = LoudnessVsTime()
    fc = FieldsContainer()
    fc.labels = ["channel"]
    f = Field()
    f.data = 42 * np.ones(3)
    fc.add_field({"channel": 0}, f)
    fc.name = "testField"
    loudnessVsTimeComputer.signal = fc
    fc_from_get = loudnessVsTimeComputer.signal

    assert fc_from_get.name == "testField"
    assert len(fc_from_get) == 1
    assert fc_from_get[0].data[0, 2] == 42
