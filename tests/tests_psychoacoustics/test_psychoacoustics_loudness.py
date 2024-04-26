from unittest.mock import patch

import pytest

from ansys.dpf.sound.psychoacoustics.loudness import Loudness
from ansys.dpf.sound.pydpf_sound import PyDpfSoundException
from ansys.dpf.sound.signal_utilities import LoadWav


@pytest.mark.dependency()
def test_loudness_instantiation(dpf_sound_test_server):
    loudnessComputer = Loudness()
    assert loudnessComputer != None


@pytest.mark.dependency(depends=["test_loudness_instantiation"])
def test_loudness_process(dpf_sound_test_server):
    loudnessComputer = Loudness()

    # no signal -> error 1
    with pytest.raises(PyDpfSoundException) as excinfo:
        loudnessComputer.process()
    assert str(excinfo.value) == "No signal for loudness computation. Use Loudness.signal"

    # get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # set signal as field container
    loudnessComputer.signal = fc
    # compute: no error
    loudnessComputer.process()

    # set signal as field
    loudnessComputer.signal = fc[0]
    # compute: no error
    loudnessComputer.process()


@pytest.mark.dependency(depends=["test_loudness_process"])
def test_loudness_get_output(dpf_sound_test_server):
    loudnessComputer = Loudness()
    # get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    output = loudnessComputer.get_output()
    assert output == None

    # set signal
    loudnessComputer.signal = fc
    # compute
    loudnessComputer.process()

    (loudnessSone, loudnessPhon, SpecificLoudness) = loudnessComputer.get_output()
    assert loudnessSone
    assert loudnessPhon != None
    assert SpecificLoudness != None


pytest.mark.dependency(depends=["test_loudness_process"])


def test_loudness_get_loudness_sone(dpf_sound_test_server):
    loudnessComputer = Loudness()
    # get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    output = loudnessComputer.get_loudness_sone()
    assert output == None

    # set signal
    loudnessComputer.signal = fc
    # compute
    loudnessComputer.process()

    loudnessSone = loudnessComputer.get_loudness_sone()
    assert loudnessSone


pytest.mark.dependency(depends=["test_loudness_process"])


def test_loudness_get_loudness_phon(dpf_sound_test_server):
    loudnessComputer = Loudness()
    # get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    output = loudnessComputer.get_loudness_phon()
    assert output == None

    # set signal
    loudnessComputer.signal = fc
    # compute
    loudnessComputer.process()

    loudnessPhon = loudnessComputer.get_loudness_phon()
    assert loudnessPhon


@pytest.mark.dependency(depends=["test_loudness_process"])
def test_loudness_get_specific_loudness(dpf_sound_test_server):
    loudnessComputer = Loudness()
    # get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    output = loudnessComputer.get_specific_loudness()
    assert output == None

    # set signal
    loudnessComputer.signal = fc
    # compute
    loudnessComputer.process()

    specificLoudness = loudnessComputer.get_specific_loudness()
    assert specificLoudness


@pytest.mark.dependency(depends=["test_loudness_process"])
def test_loudness_get_output_as_nparray_from_field_container(dpf_sound_test_server):
    loudnessComputer = Loudness()
    # get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    output = loudnessComputer.get_output_as_nparray()
    assert output == None

    # set signal
    loudnessComputer.signal = fc
    # compute
    loudnessComputer.process()

    (loudnessSone, loudnessPhon, SpecificLoudness) = loudnessComputer.get_output_as_nparray()
    assert len(loudnessSone) == 1
    assert loudnessSone[0] == 39.58000183105469
    assert len(loudnessPhon) == 1
    assert loudnessPhon[0] == 93.0669937133789
    assert len(SpecificLoudness) == 240
    assert SpecificLoudness[0] == 0
    assert SpecificLoudness[9] == 0.15664348006248474
    assert SpecificLoudness[40] == 1.3235466480255127


@pytest.mark.dependency(depends=["test_loudness_process"])
def test_loudness_get_output_as_nparray_from_field(dpf_sound_test_server):
    loudnessComputer = Loudness()
    # get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # set signal
    loudnessComputer.signal = fc[0]
    # compute
    loudnessComputer.process()

    (loudnessSone, loudnessPhon, SpecificLoudness) = loudnessComputer.get_output_as_nparray()
    assert len(loudnessSone) == 1
    assert loudnessSone[0] == 39.58000183105469
    assert len(loudnessPhon) == 1
    assert loudnessPhon[0] == 93.0669937133789
    assert len(SpecificLoudness) == 240
    assert SpecificLoudness[0] == 0
    assert SpecificLoudness[9] == 0.15664348006248474
    assert SpecificLoudness[40] == 1.3235466480255127


@patch("matplotlib.pyplot.show")
@pytest.mark.dependency(depends=["test_loudness_process"])
def test_loudness_plot_from_field_container(mock_show, dpf_sound_test_server):
    loudnessComputer = Loudness()
    # get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # set signal
    loudnessComputer.signal = fc
    # compute
    loudnessComputer.process()

    # plot
    loudnessComputer.plot()


@patch("matplotlib.pyplot.show")
@pytest.mark.dependency(depends=["test_loudness_process"])
def test_loudness_plot_from_field(mock_show, dpf_sound_test_server):
    loudnessComputer = Loudness()
    # get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # set signal
    loudnessComputer.signal = fc[0]
    # compute
    loudnessComputer.process()

    # plot
    loudnessComputer.plot()
