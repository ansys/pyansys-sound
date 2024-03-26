import pytest

from ansys.dpf.sound.signal_utilities import SignalUtilitiesAbstract


@pytest.mark.dependency()
def test_signal_utilities_abstract_instanciate():
    pydpf_sound = SignalUtilitiesAbstract()
    assert pydpf_sound != None
