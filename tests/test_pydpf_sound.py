from ansys.dpf.core import FieldsContainer
import numpy as np
import pytest

from ansys.dpf.sound.pydpf_sound import PyDpfSound


@pytest.mark.dependency()
def test_pydpf_sound_instanciate():
    pydpf_sound = PyDpfSound()
    assert pydpf_sound != None


@pytest.mark.dependency(depends=["test_pydpf_sound_instanciate"])
def test_pydpf_sound_compute():
    pydpf_sound = PyDpfSound()
    assert pydpf_sound.compute() == None


@pytest.mark.dependency(depends=["test_pydpf_sound_instanciate"])
def test_pydpf_sound_plot():
    pydpf_sound = PyDpfSound()
    assert pydpf_sound.plot() == None


@pytest.mark.dependency(depends=["test_pydpf_sound_instanciate"])
def test_pydpf_sound_get_output():
    pydpf_sound = PyDpfSound()
    out = pydpf_sound.get_output()
    assert type(out) == type(FieldsContainer)


@pytest.mark.dependency(depends=["test_pydpf_sound_instanciate"])
def test_pydpf_sound_get_output_as_nparray():
    pydpf_sound = PyDpfSound()
    out = pydpf_sound.get_output_as_nparray()
    assert type(out) == type(np.empty(0))
    assert np.size(out) == 0
    assert np.shape(out) == (0,)
