from unittest.mock import patch

from ansys.dpf.core import Field, FieldsContainer
import numpy as np
import pytest

from ansys.dpf.sound.pydpf_sound import PyDpfSoundException, PyDpfSoundWarning
from ansys.dpf.sound.signal_utilities import LoadWav
from ansys.dpf.sound.xtract.xtract_transient import XtractTransient


def test_xtract_transient_instantiation(dpf_sound_test_server):
    xtract_transient = XtractTransient()
    assert xtract_transient != None

def test_xtract_transient_initialization():
    # Test initialization with default values
    xtract = XtractTransient()
    assert xtract.input_signal is None
    assert xtract.input_parameters is None
    assert xtract.output_transient_signals is None
    assert xtract.output_non_transient_signals is None

    # Test initialization with custom values
    input_signal = FieldsContainer()
    input_parameters = FieldsContainer()
    xtract = XtractTransient(
        input_signal=input_signal,
        input_parameters=input_parameters,
    )
    assert xtract.input_signal == input_signal
    assert xtract.input_parameters == input_parameters
    assert xtract.output_transient_signals is None
    assert xtract.output_non_transient_signals is None

def test_xtract_transient_process():
    # Test the process method
    xtract = XtractTransient()
    # Add your test logic here
    assert False

def test_xtract_transient_get_output():
    # Test the get_output method
    xtract = XtractTransient()
    # Add your test logic here
    assert False

def test_xtract_transient_get_output_as_nparray():
    # Test the get_output_as_nparray method
    xtract = XtractTransient()
    # Add your test logic here
    assert False

def test_xtract_transient_plot_output():
    # Test the plot_output method
    xtract = XtractTransient()
    # Add your test logic here
    assert False
