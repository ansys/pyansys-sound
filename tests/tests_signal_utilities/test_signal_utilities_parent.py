import pytest

from ansys.dpf.sound.signal_utilities import SignalUtilitiesParent


@pytest.mark.dependency()
def test_signal_utilities_parent_instanciate():
    pydpf_sound = SignalUtilitiesParent()
    assert pydpf_sound != None
