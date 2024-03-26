import pytest

from ansys.dpf.sound.signal_utilities import SignalUtilities


@pytest.mark.dependency()
def test_signal_utilities_instanciate():
    pydpf_sound = SignalUtilities()
    assert pydpf_sound != None
