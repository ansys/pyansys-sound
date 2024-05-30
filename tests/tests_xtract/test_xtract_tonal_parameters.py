from ansys.dpf.core import GenericDataContainer
from ansys.dpf.sound.pydpf_sound import PyDpfSoundException
import pytest

from ansys.dpf.sound.xtract.xtract_tonal_parameters import XtractTonalParameters


def test_xtract_tonal_parameters_instantiation(dpf_sound_test_server):
    xtract_tonal_parameters = XtractTonalParameters()
    assert xtract_tonal_parameters != None


def test_xtract_tonal_parameters_getter_setter_regularity(dpf_sound_test_server):
    xtract_tonal_parameters = XtractTonalParameters()

    # Invalid value
    with pytest.raises(PyDpfSoundException) as excinfo:
        xtract_tonal_parameters.regularity = 150.0
    assert str(excinfo.value) == "Regularity must be between 0.0 and 1.0."

    xtract_tonal_parameters.upper_threshold = 0.5

    assert xtract_tonal_parameters.upper_threshold == 0.5


def test_xtract_tonal_parameters_getter_setter_maximum_slope(dpf_sound_test_server):
    xtract_tonal_parameters = XtractTonalParameters()

    # Invalid value
    with pytest.raises(PyDpfSoundException) as excinfo:
        xtract_tonal_parameters.maximum_slope = 1500000.0
    assert str(excinfo.value) == "Maximum slope must be between 0.0 and 15000.0 Hz/s."

    xtract_tonal_parameters.maximum_slope = 92.0

    assert xtract_tonal_parameters.maximum_slope == 92.0


def test_xtract_tonal_parameters_getter_setter_minimum_duration(dpf_sound_test_server):
    xtract_tonal_parameters = XtractTonalParameters()

    # Invalid value
    with pytest.raises(PyDpfSoundException) as excinfo:
        xtract_tonal_parameters.minimum_duration = 1500000.0
    assert str(excinfo.value) == "Minimum duration must be between 0.0 and 5.0 s."

    xtract_tonal_parameters.minimum_duration = 2.0

    assert xtract_tonal_parameters.minimum_duration == 2.0


def test_xtract_tonal_parameters_getter_setter_local_emergence(dpf_sound_test_server):
    xtract_tonal_parameters = XtractTonalParameters()

    # Invalid value
    with pytest.raises(PyDpfSoundException) as excinfo:
        xtract_tonal_parameters.local_emergence = 1500000.0
    assert str(excinfo.value) == "Local emergence must be between 0.0 and 100.0 dB."

    xtract_tonal_parameters.local_emergence = 20.0

    assert xtract_tonal_parameters.local_emergence == 20.0


def test_xtract_tonal_parameters_getter_setter_fft_size(dpf_sound_test_server):
    xtract_tonal_parameters = XtractTonalParameters()

    # Invalid value
    with pytest.raises(PyDpfSoundException) as excinfo:
        xtract_tonal_parameters.fft_size = -1500000.0
    assert str(excinfo.value) == "Fft size must be between greater than 0."

    xtract_tonal_parameters.fft_size = 20.0

    assert xtract_tonal_parameters.fft_size == 20.0


def test_xtract_tonal_parameters_getter_setter_regularity(dpf_sound_test_server):
    xtract_tonal_parameters = XtractTonalParameters()

    # Invalid value
    with pytest.raises(PyDpfSoundException) as excinfo:
        xtract_tonal_parameters.regularity = -1500000.0
    assert str(excinfo.value) == "Regularity must be between 0.0 and 1.0."

    xtract_tonal_parameters.regularity = 0.1

    assert xtract_tonal_parameters.regularity == 0.1


def test_xtract_tonal_parameters_getter_intertonal_gap(dpf_sound_test_server):
    xtract_tonal_parameters = XtractTonalParameters()

    # Invalid value
    with pytest.raises(PyDpfSoundException) as excinfo:
        xtract_tonal_parameters.intertonal_gap = -1500000.0
    assert str(excinfo.value) == "Intertonal gap must be between 10.0 and 200.0 Hz."

    xtract_tonal_parameters.intertonal_gap = 15.0

    assert xtract_tonal_parameters.intertonal_gap == 15.0


def test_xtract_tonal_parameters_getter_generic_data_container(dpf_sound_test_server):
    xtract_tonal_parameters = XtractTonalParameters()

    gdc = xtract_tonal_parameters.get_parameters_as_generic_data_container()
    assert gdc is not None
    assert type(gdc) == GenericDataContainer
