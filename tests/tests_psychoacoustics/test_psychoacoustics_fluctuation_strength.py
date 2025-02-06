# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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

from unittest.mock import patch

from ansys.dpf.core import Field
import numpy as np
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ansys.sound.core.psychoacoustics import FluctuationStrength
from ansys.sound.core.signal_utilities import LoadWav

EXP_FS = 1.0416046380996704
EXP_SPECIFIC_FS_0 = 0.09723643958568573
EXP_SPECIFIC_FS_9 = 0.15443961322307587
EXP_SPECIFIC_FS_40 = 0.17233367264270782
EXP_BARK_0 = 0.5
EXP_BARK_9 = 5.0
EXP_BARK_40 = 20.5
EXP_FREQ_0 = 56.417020507724274
EXP_FREQ_9 = 498.9473684210526
EXP_FREQ_40 = 6875.975124656844

TOTAL_FS_ID = "total"
SPECIFIC_FS_ID = "specific"


def test_fs_instantiation():
    """Test the instantiation of the FluctuationStrength class."""
    fs_computer = FluctuationStrength()
    assert isinstance(fs_computer, FluctuationStrength)
    assert fs_computer.signal == None


def test_fs_process():
    """Test the process method of the FluctuationStrength class."""
    fs_computer = FluctuationStrength()

    # No signal -> error
    with pytest.raises(
        PyAnsysSoundException,
        match="No signal found for fluctuation strength computation."
        " Use `FluctuationStrength.signal`.",
    ):
        fs_computer.process()

    # Get a signal
    wav_loader = LoadWav(pytest.data_path_fluctuating_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    fs_computer.signal = fc[0]
    # Compute: no error
    fs_computer.process()
    assert fs_computer._output is not None


def test_fs_get_output():
    """Test the get_output method of the FluctuationStrength class."""
    fs_computer = FluctuationStrength()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_fluctuating_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    fs_computer.signal = fc[0]

    # Fluctuation strength not calculated yet -> warning
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the `FluctuationStrength.process\\(\\)` method.",
    ):
        output = fs_computer.get_output()
    assert output is None

    # Compute
    fs_computer.process()

    (fs, specific_fs) = fs_computer.get_output()
    assert isinstance(fs, float)
    assert fs == pytest.approx(EXP_FS)
    assert isinstance(specific_fs, Field)
    assert specific_fs.data[0] == pytest.approx(EXP_SPECIFIC_FS_0)
    assert specific_fs.data[9] == pytest.approx(EXP_SPECIFIC_FS_9)
    assert specific_fs.data[40] == pytest.approx(EXP_SPECIFIC_FS_40)


def test_fs_get_fluctuation_strength():
    """Test the get_fluctuation_strength method of the FluctuationStrength class."""
    fs_computer = FluctuationStrength()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_fluctuating_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    fs_computer.signal = fc[0]

    # Compute
    fs_computer.process()

    fs = fs_computer.get_fluctuation_strength()
    assert isinstance(fs, np.ndarray)
    assert fs == pytest.approx(EXP_FS)


def test_fs_get_specific_fluctuation_strength():
    """Test the get_specific_fluctuation_strength method of the FluctuationStrength class."""
    fs_computer = FluctuationStrength()

    # Get a signal
    wav_loader = LoadWav(pytest.data_path_fluctuating_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    fs_computer.signal = fc[0]

    # Compute
    fs_computer.process()

    specific_fs = fs_computer.get_specific_fluctuation_strength()

    assert type(specific_fs) == np.ndarray
    assert len(specific_fs) == 47
    assert specific_fs[0] == pytest.approx(EXP_SPECIFIC_FS_0)
    assert specific_fs[9] == pytest.approx(EXP_SPECIFIC_FS_9)
    assert specific_fs[40] == pytest.approx(EXP_SPECIFIC_FS_40)


def test_fs_get_bark_band_indexes():
    """Test the get_bark_band_indexes method of the FluctuationStrength class."""
    fs_computer = FluctuationStrength()

    # Get a signal
    wav_loader = LoadWav(pytest.data_path_fluctuating_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    fs_computer.signal = fc[0]

    # Compute
    fs_computer.process()

    bark_band_indexes = fs_computer.get_bark_band_indexes()
    assert type(bark_band_indexes) == np.ndarray
    assert len(bark_band_indexes) == 47
    assert bark_band_indexes[0] == pytest.approx(EXP_BARK_0)
    assert bark_band_indexes[9] == pytest.approx(EXP_BARK_9)
    assert bark_band_indexes[40] == pytest.approx(EXP_BARK_40)


def test_fs_get_bark_band_frequencies():
    """Test the get_bark_band_frequencies method of the FluctuationStrength class."""
    fs_computer = FluctuationStrength()

    # Get a signal
    wav_loader = LoadWav(pytest.data_path_fluctuating_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    fs_computer.signal = fc[0]

    # Compute
    fs_computer.process()

    bark_band_frequencies = fs_computer.get_bark_band_frequencies()
    assert type(bark_band_frequencies) == np.ndarray
    assert len(bark_band_frequencies) == 47
    assert bark_band_frequencies[0] == pytest.approx(EXP_FREQ_0)
    assert bark_band_frequencies[9] == pytest.approx(EXP_FREQ_9)
    assert bark_band_frequencies[40] == pytest.approx(EXP_FREQ_40)


def test_fs_get_output_as_nparray():
    """Test the get_output_as_nparray method of the FluctuationStrength class."""
    fs_computer = FluctuationStrength()

    # Get a signal
    wav_loader = LoadWav(pytest.data_path_fluctuating_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    fs_computer.signal = fc[0]

    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the `FluctuationStrength.process\\(\\)` method.",
    ):
        fs, specific_fs, bark_band_indexes = fs_computer.get_output_as_nparray()
    assert np.isnan(fs)
    assert len(specific_fs) == 0
    assert len(bark_band_indexes) == 0

    # Compute
    fs_computer.process()

    fs, specific_fs, bark_band_indexes = fs_computer.get_output_as_nparray()

    assert type(fs) == np.ndarray
    assert fs == pytest.approx(EXP_FS)
    assert type(specific_fs) == np.ndarray
    assert len(specific_fs) == 47
    assert specific_fs[0] == pytest.approx(EXP_SPECIFIC_FS_0)
    assert specific_fs[9] == pytest.approx(EXP_SPECIFIC_FS_9)
    assert specific_fs[40] == pytest.approx(EXP_SPECIFIC_FS_40)
    assert type(bark_band_indexes) == np.ndarray
    assert len(bark_band_indexes) == 47
    assert bark_band_indexes[0] == pytest.approx(EXP_BARK_0)
    assert bark_band_indexes[9] == pytest.approx(EXP_BARK_9)
    assert bark_band_indexes[40] == pytest.approx(EXP_BARK_40)


@patch("matplotlib.pyplot.show")
def test_fs_plot(mock_show):
    """Test the plot method of the FluctuationStrength class."""
    fs_computer = FluctuationStrength()

    # Get a signal
    wav_loader = LoadWav(pytest.data_path_fluctuating_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    fs_computer.signal = fc[0]

    # Fluctuation strength not computed yet -> error
    with pytest.raises(
        PyAnsysSoundException,
        match="Output is not processed yet. Use the `FluctuationStrength.process\\(\\)` method.",
    ):
        fs_computer.plot()

    # Compute
    fs_computer.process()

    # Plot
    fs_computer.plot()


def test_fs_set_get_signal():
    """Test the set and get signal methods of the FluctuationStrength class."""
    fs_computer = FluctuationStrength()
    f_signal = Field()
    f_signal.data = 42 * np.ones(3)
    fs_computer.signal = f_signal
    f_signal_from_property = fs_computer.signal

    assert f_signal_from_property.data[0, 2] == 42

    # Set invalid value
    with pytest.raises(PyAnsysSoundException, match="Signal must be specified as a DPF field."):
        fs_computer.signal = "WrongType"
