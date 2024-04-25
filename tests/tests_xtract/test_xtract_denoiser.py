from unittest.mock import patch

from ansys.dpf.core import Field, FieldsContainer
import numpy as np
import pytest

from ansys.dpf.sound.pydpf_sound import PyDpfSoundException, PyDpfSoundWarning
from ansys.dpf.sound.signal_utilities import LoadWav
from ansys.dpf.sound.xtract.xtract_denoiser import XtractDenoiser


def test_for_fun():
    assert 1 == 1


def test_xtract_denoiser_instantiation(dpf_sound_test_server):
    xtract_denoiser = XtractDenoiser()
    assert xtract_denoiser != None


def test_xtract_denoiser_process(dpf_sound_test_server):
    assert False