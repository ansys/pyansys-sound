from ansys.dpf.sound.pydpf_sound import PyDpfSoundException
import pytest

from ansys.dpf.sound.xtract.xtract_transient_parameters import XtractTransientParameters


def test_xtract_transient_parameters_instantiation(dpf_sound_test_server):
    xtract_transient_parameters = XtractTransientParameters()
    assert xtract_transient_parameters != None


def test_xtract_transient_parameters_getter_setter_upper_threshold(dpf_sound_test_server):
    xtract_transient_parameters = XtractTransientParameters()

    # Invalid value
    with pytest.raises(PyDpfSoundException) as excinfo:
        xtract_transient_parameters.upper_threshold = 150.0
    assert str(excinfo.value) == "Upper threshold must be between 0.0 and 100.0 dB."

    xtract_transient_parameters.upper_threshold = 92.0

    assert xtract_transient_parameters.upper_threshold == 92.0


def test_xtract_transient_parameters_getter_setter_lower_threshold(dpf_sound_test_server):
    xtract_transient_parameters = XtractTransientParameters()

    # Invalid value
    with pytest.raises(PyDpfSoundException) as excinfo:
        xtract_transient_parameters.lower_threshold = 150.0
    assert str(excinfo.value) == "Lower threshold must be between 0.0 and 100.0 dB."

    xtract_transient_parameters.lower_threshold = 92.0

    assert xtract_transient_parameters.lower_threshold == 92.0


def test_xtract_transient_parameters_getter_generic_data_container(dpf_sound_test_server):
    xtract_transient_parameters = XtractTransientParameters()

    gdc = xtract_transient_parameters.get_parameters_as_generic_data_container()
    assert gdc is not None
