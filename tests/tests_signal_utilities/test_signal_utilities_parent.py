import pytest

from ansys.dpf.sound.signal_utilities import SignalUtilitiesParent


@pytest.mark.dependency()
def test_signal_utilities_parent_instantiate():
    signal_utilities = SignalUtilitiesParent()
    assert signal_utilities != None
