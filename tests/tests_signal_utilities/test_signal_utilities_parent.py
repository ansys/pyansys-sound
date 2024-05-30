import pytest

from ansys.sound.core.signal_utilities import SignalUtilitiesParent


@pytest.mark.dependency()
def test_signal_utilities_parent_instanciate():
    pyansys_sound = SignalUtilitiesParent()
    assert pyansys_sound != None
