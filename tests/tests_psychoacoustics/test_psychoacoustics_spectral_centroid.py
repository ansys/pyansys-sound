# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from ansys.dpf.core import Field
import numpy as np
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ansys.sound.core.psychoacoustics import SpectralCentroid
from ansys.sound.core.signal_utilities import LoadWav

EXP_SPECTRAL_CENTROID = 816.00695


def test_spectral_centroid_instantiation():
    spectral_centroid_computer = SpectralCentroid()
    assert spectral_centroid_computer != None


def test_spectral_centroid_process():
    spectral_centroid_computer = SpectralCentroid()

    # No signal -> error
    with pytest.raises(
        PyAnsysSoundException,
        match="No signal found for spectral centroid computation. Use 'SpectralCentroid.signal'.",
    ):
        spectral_centroid_computer.process()

    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal as field
    spectral_centroid_computer.signal = fc[0]

    # Compute: no error
    spectral_centroid_computer.process()


def test_spectral_centroid_get_output():
    spectral_centroid_computer = SpectralCentroid()

    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    spectral_centroid_computer.signal = fc[0]

    # Spectral centroid not calculated yet -> warning
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. \
                        Use the 'SpectralCentroid.process\\(\\)' method.",
    ):
        spectral_centroid_computer.get_output()

    # Compute
    spectral_centroid_computer.process()

    spectral_centroid = spectral_centroid_computer.get_output()
    assert spectral_centroid != None
    assert type(spectral_centroid) == float
    assert spectral_centroid == pytest.approx(EXP_SPECTRAL_CENTROID)


def test_spectral_centroid_get_spectral_centroid():
    spectral_centroid_computer = SpectralCentroid()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    spectral_centroid_computer.signal = fc[0]

    # Compute
    spectral_centroid_computer.process()

    spectral_centroid = spectral_centroid_computer.get_spectral_centroid()
    assert type(spectral_centroid) == float
    assert spectral_centroid == pytest.approx(EXP_SPECTRAL_CENTROID)


def test_spectral_centroid_get_output_as_nparray():
    spectral_centroid_computer = SpectralCentroid()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    spectral_centroid_computer.signal = fc[0]

    spectral_centroid = spectral_centroid_computer.get_output_as_nparray()
    assert type(spectral_centroid) == np.ndarray
    assert len(spectral_centroid) == 0

    # Compute
    spectral_centroid_computer.process()

    spectral_centroid = spectral_centroid_computer.get_output_as_nparray()
    assert spectral_centroid != None
    assert type(spectral_centroid) == np.ndarray
    assert spectral_centroid[0] == pytest.approx(EXP_SPECTRAL_CENTROID)


def test_spectral_centroid_set_get_signal():
    spectral_centroid_computer = SpectralCentroid()
    field = Field()
    field.data = 42 * np.ones(3)
    spectral_centroid_computer.signal = field
    field_from_get = spectral_centroid_computer.signal

    assert field_from_get.data[0, 2] == 42


def test_spectral_centroid_print():
    spectral_centroid_computer = SpectralCentroid()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    spectral_centroid_computer.signal = fc[0]

    # Compute
    spectral_centroid_computer.process()

    # Check __str__
    str = spectral_centroid_computer.__str__()
    assert (
        str
        == "SpectralCentroid object\nData\n\t Signal name: flute\n\t Spectral centroid: 816.0 Hz\n"  # noqa: E501
    )
