from unittest.mock import patch

from ansys.dpf.core import Field, FieldsContainer, Operator, GenericDataContainer
import numpy as np
import pytest

from ansys.dpf.sound.pydpf_sound import PyDpfSoundException, PyDpfSoundWarning
from ansys.dpf.sound.signal_utilities import LoadWav
from ansys.dpf.sound.xtract.xtract_tonal import XtractTonal


def test_xtract_tonal_instantiation(dpf_sound_test_server):
    xtract_tonal = XtractTonal()
    assert xtract_tonal != None

def test_xtract_tonal_initialization():
    # Test initialization with default values
    xtract = XtractTonal()
    assert xtract.input_signal is None
    assert xtract.input_parameters is None
    assert xtract.output_tonal_signals is None
    assert xtract.output_non_tonal_signals is None

    # Test initialization with custom values
    input_signal = FieldsContainer()
    input_parameters = GenericDataContainer()
    xtract = XtractTonal(
        input_signal=input_signal,
        input_parameters=input_parameters,
    )
    assert xtract.input_signal == input_signal
    assert xtract.input_parameters == input_parameters
    assert xtract.output_tonal_signals is None
    assert xtract.output_non_tonal_signals is None    

def test_xtract_tonal_process(dpf_sound_test_server):
    assert False

def test_xtract_tonal_get_output():
    # Test the get_output method
    xtract = XtractTonal()
    # Add your test logic here
    assert False

def test_xtract_tonal_get_output_as_nparray():
    # Test the get_output_as_nparray method
    xtract = XtractTonal()
    # Add your test logic here
    assert False

def test_xtract_tonal_plot_output():
    # Test the plot_output method
    xtract = XtractTonal()
    # Add your test logic here
    assert False                