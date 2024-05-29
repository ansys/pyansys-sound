import numpy as np
import pytest

from ansys.dpf.sound.pydpf_sound import PyDpfSound, PyDpfSoundWarning


def test_pydpf_sound_instanciate():
    pydpf_sound = PyDpfSound()
    assert pydpf_sound != None


def test_pydpf_sound_process():
    pydpf_sound = PyDpfSound()
    with pytest.warns(PyDpfSoundWarning, match="Nothing to process."):
        pydpf_sound.process()
    assert pydpf_sound.process() == None


def test_pydpf_sound_plot():
    pydpf_sound = PyDpfSound()
    with pytest.warns(PyDpfSoundWarning, match="Nothing to plot."):
        pydpf_sound.plot()

    assert pydpf_sound.plot() == None


def test_pydpf_sound_get_output():
    pydpf_sound = PyDpfSound()
    with pytest.warns(PyDpfSoundWarning, match="Nothing to output."):
        pydpf_sound.get_output()
    out = pydpf_sound.get_output()
    assert out == None


def test_pydpf_sound_get_output_as_nparray():
    pydpf_sound = PyDpfSound()
    with pytest.warns(PyDpfSoundWarning, match="Nothing to output."):
        pydpf_sound.get_output_as_nparray()
    out = pydpf_sound.get_output_as_nparray()
    assert type(out) == type(np.empty(0))
    assert np.size(out) == 0
    assert np.shape(out) == (0,)
