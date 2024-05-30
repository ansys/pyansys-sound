import numpy as np
import pytest

from ansys.sound.core.pyansys_sound import PyAnsysSound, PyAnsysSoundWarning


@pytest.mark.dependency()
def test_pyansys_sound_instanciate():
    pyansys_sound = PyAnsysSound()
    assert pyansys_sound != None


@pytest.mark.dependency(depends=["test_pyansys_sound_instanciate"])
def test_pyansys_sound_process():
    pyansys_sound = PyAnsysSound()
    with pytest.warns(PyAnsysSoundWarning, match="Nothing to process."):
        pyansys_sound.process()
    assert pyansys_sound.process() == None


@pytest.mark.dependency(depends=["test_pyansys_sound_instanciate"])
def test_pyansys_sound_plot():
    pyansys_sound = PyAnsysSound()
    with pytest.warns(PyAnsysSoundWarning, match="Nothing to plot."):
        pyansys_sound.plot()

    assert pyansys_sound.plot() == None


@pytest.mark.dependency(depends=["test_pyansys_sound_instanciate"])
def test_pyansys_sound_get_output():
    pyansys_sound = PyAnsysSound()
    with pytest.warns(PyAnsysSoundWarning, match="Nothing to output."):
        pyansys_sound.get_output()
    out = pyansys_sound.get_output()
    assert out == None


@pytest.mark.dependency(depends=["test_pyansys_sound_instanciate"])
def test_pyansys_sound_get_output_as_nparray():
    pyansys_sound = PyAnsysSound()
    with pytest.warns(PyAnsysSoundWarning, match="Nothing to output."):
        pyansys_sound.get_output_as_nparray()
    out = pyansys_sound.get_output_as_nparray()
    assert type(out) == type(np.empty(0))
    assert np.size(out) == 0
    assert np.shape(out) == (0,)
