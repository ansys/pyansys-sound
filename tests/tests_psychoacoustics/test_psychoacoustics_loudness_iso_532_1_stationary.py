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
from ansys.sound.core.psychoacoustics import LoudnessISO532_1_Stationary
from ansys.sound.core.signal_utilities import LoadWav

EXP_LOUDNESS_FREE = 39.58000183105469
EXP_LOUDNESS_DIFFUSE = 42.02
EXP_LOUDNESS_LEVEL_FREE = 93.0669937133789
EXP_LOUDNESS_LEVEL_DIFFUSE = 93.93004
EXP_SPECIFIC_LOUDNESS_FREE_0 = 0.0
EXP_SPECIFIC_LOUDNESS_FREE_9 = 0.15664348006248474
EXP_SPECIFIC_LOUDNESS_FREE_40 = 1.3235466480255127
EXP_BARK_0 = 0.10000000149011612
EXP_BARK_9 = 1.0000000149011612
EXP_BARK_40 = 4.100000061094761
EXP_FREQ_0 = 21.33995930840456
EXP_FREQ_9 = 102.08707043772274
EXP_FREQ_40 = 400.79351405718324


def test_loudness_iso_532_1_stationary_instantiation():
    """Test the instantiation of the LoudnessISO532_1_Stationary class."""
    loudness_computer = LoudnessISO532_1_Stationary()
    assert isinstance(loudness_computer, LoudnessISO532_1_Stationary)
    assert loudness_computer.signal is None
    assert loudness_computer.field_type == "Free"


def test_loudness_iso_532_1_stationary_process():
    """Test the process method of the LoudnessISO532_1_Stationary class."""
    loudness_computer = LoudnessISO532_1_Stationary()

    # No signal -> error
    with pytest.raises(
        PyAnsysSoundException,
        match="No signal found for loudness computation. Use `LoudnessISO532_1_Stationary.signal`.",
    ):
        loudness_computer.process()

    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal as field
    loudness_computer.signal = fc[0]

    # Compute: no error
    loudness_computer.process()
    assert loudness_computer._output is not None


def test_loudness_iso_532_1_stationary_get_output():
    """Test the get_output method of the LoudnessISO532_1_Stationary class."""
    loudness_computer = LoudnessISO532_1_Stationary()

    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    loudness_computer.signal = fc[0]

    # Loudness not calculated yet -> warning
    with pytest.warns(
        PyAnsysSoundWarning,
        match=(
            "Output is not processed yet. "
            "Use the `LoudnessISO532_1_Stationary.process\\(\\)` method."
        ),
    ):
        output = loudness_computer.get_output()
    assert output is None

    # Compute
    loudness_computer.process()

    (loudness, loudness_level, specific_loudness) = loudness_computer.get_output()
    assert isinstance(loudness, float)
    assert loudness == pytest.approx(EXP_LOUDNESS_FREE)
    assert isinstance(loudness_level, float)
    assert loudness_level == pytest.approx(EXP_LOUDNESS_LEVEL_FREE)
    assert isinstance(specific_loudness, Field)
    assert specific_loudness.data[0] == pytest.approx(EXP_SPECIFIC_LOUDNESS_FREE_0)
    assert specific_loudness.data[9] == pytest.approx(EXP_SPECIFIC_LOUDNESS_FREE_9)
    assert specific_loudness.data[40] == pytest.approx(EXP_SPECIFIC_LOUDNESS_FREE_40)


def test_loudness_iso_532_1_stationary_get_loudness_sone():
    """Test the get_loudness_sone method of the LoudnessISO532_1_Stationary class."""
    loudness_computer = LoudnessISO532_1_Stationary()

    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    loudness_computer.signal = fc[0]

    # Compute
    loudness_computer.process()

    loudness = loudness_computer.get_loudness_sone()
    assert isinstance(loudness, np.ndarray)
    assert loudness == pytest.approx(EXP_LOUDNESS_FREE)


def test_loudness_iso_532_1_stationary_get_loudness_level_phon():
    """Test the get_loudness_level_phon method of the LoudnessISO532_1_Stationary class."""
    loudness_computer = LoudnessISO532_1_Stationary()

    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    loudness_computer.signal = fc[0]

    # Compute
    loudness_computer.process()

    loudness_level = loudness_computer.get_loudness_level_phon()
    assert isinstance(loudness_level, np.ndarray)
    assert loudness_level == pytest.approx(EXP_LOUDNESS_LEVEL_FREE)


def test_loudness_iso_532_1_stationary_get_specific_loudness():
    """Test the get_specific_loudness method of the LoudnessISO532_1_Stationary class."""
    loudness_computer = LoudnessISO532_1_Stationary()

    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    loudness_computer.signal = fc[0]

    # Compute
    loudness_computer.process()

    specific_loudness = loudness_computer.get_specific_loudness()
    assert type(specific_loudness) == np.ndarray
    assert len(specific_loudness) == 240
    assert specific_loudness[0] == pytest.approx(EXP_SPECIFIC_LOUDNESS_FREE_0)
    assert specific_loudness[9] == pytest.approx(EXP_SPECIFIC_LOUDNESS_FREE_9)
    assert specific_loudness[40] == pytest.approx(EXP_SPECIFIC_LOUDNESS_FREE_40)


def test_loudness_iso_532_1_stationary_get_bark_band_indexes():
    """Test the _get_bark_band_indexes method of the LoudnessISO532_1_Stationary class."""
    loudness_computer = LoudnessISO532_1_Stationary()

    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal as a fields container
    loudness_computer.signal = fc[0]

    # Compute
    loudness_computer.process()

    bark_band_indexes = loudness_computer.get_bark_band_indexes()
    assert type(bark_band_indexes) == np.ndarray
    assert len(bark_band_indexes) == 240
    assert bark_band_indexes[0] == pytest.approx(EXP_BARK_0)
    assert bark_band_indexes[9] == pytest.approx(EXP_BARK_9)
    assert bark_band_indexes[40] == pytest.approx(EXP_BARK_40)


def test_loudness_iso_532_1_stationary_get_bark_band_frequencies():
    """Test the get_bark_band_frequencies method of the LoudnessISO532_1_Stationary class."""
    loudness_computer = LoudnessISO532_1_Stationary()

    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    loudness_computer.signal = fc[0]

    # Compute
    loudness_computer.process()

    bark_band_frequencies = loudness_computer.get_bark_band_frequencies()
    assert type(bark_band_frequencies) == np.ndarray
    assert len(bark_band_frequencies) == 240
    assert bark_band_frequencies[0] == pytest.approx(EXP_FREQ_0)
    assert bark_band_frequencies[9] == pytest.approx(EXP_FREQ_9)
    assert bark_band_frequencies[40] == pytest.approx(EXP_FREQ_40)


def test_loudness_iso_532_1_stationary_get_output_as_nparray():
    """Test the get_output_as_nparray method of the LoudnessISO532_1_Stationary class."""
    loudness_computer = LoudnessISO532_1_Stationary()

    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    loudness_computer.signal = fc[0]
    loudness_computer.field_type = "Free"

    with pytest.warns(
        PyAnsysSoundWarning,
        match=(
            "Output is not processed yet. Use the `LoudnessISO532_1_Stationary.process\\(\\)` "
            "method."
        ),
    ):
        (
            loudness,
            loudness_level,
            specific_loudness,
            bark_band_indexes,
        ) = loudness_computer.get_output_as_nparray()
    assert np.isnan(loudness)
    assert np.isnan(loudness_level)
    assert len(specific_loudness) == 0
    assert len(bark_band_indexes) == 0

    # Compute
    loudness_computer.process()

    (
        loudness,
        loudness_level,
        specific_loudness,
        bark_band_indexes,
    ) = loudness_computer.get_output_as_nparray()
    assert type(loudness) == np.ndarray
    assert loudness == pytest.approx(EXP_LOUDNESS_FREE)
    assert type(loudness_level) == np.ndarray
    assert loudness_level == pytest.approx(EXP_LOUDNESS_LEVEL_FREE)
    assert type(specific_loudness) == np.ndarray
    assert len(specific_loudness) == 240
    assert specific_loudness[0] == pytest.approx(0.0)
    assert specific_loudness[9] == pytest.approx(EXP_SPECIFIC_LOUDNESS_FREE_9)
    assert specific_loudness[40] == pytest.approx(EXP_SPECIFIC_LOUDNESS_FREE_40)
    assert type(bark_band_indexes) == np.ndarray
    assert len(bark_band_indexes) == 240
    assert bark_band_indexes[0] == pytest.approx(EXP_BARK_0)
    assert bark_band_indexes[9] == pytest.approx(EXP_BARK_9)
    assert bark_band_indexes[40] == pytest.approx(EXP_BARK_40)

    loudness_computer.field_type = "Diffuse"

    # Compute
    loudness_computer.process()

    (
        loudness,
        loudness_level,
        specific_loudness,
        bark_band_indexes,
    ) = loudness_computer.get_output_as_nparray()
    assert loudness == pytest.approx(EXP_LOUDNESS_DIFFUSE)
    assert loudness_level == pytest.approx(EXP_LOUDNESS_LEVEL_DIFFUSE)


@patch("matplotlib.pyplot.show")
def test_loudness_iso_532_1_stationary_plot(mock_show):
    """Test the plot method of the LoudnessISO532_1_Stationary class."""
    loudness_computer = LoudnessISO532_1_Stationary()

    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    loudness_computer.signal = fc[0]

    # Loudness not computed yet -> error
    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "Output is not processed yet. Use the "
            "`LoudnessISO532_1_Stationary.process\\(\\)` method."
        ),
    ):
        loudness_computer.plot()

    # Compute
    loudness_computer.process()

    # Plot
    loudness_computer.plot()


def test_loudness_iso_532_1_stationary_set_get_signal():
    """Test the signal property of the LoudnessISO532_1_Stationary class."""
    loudness_computer = LoudnessISO532_1_Stationary()
    f_signal = Field()
    f_signal.data = 42 * np.ones(3)
    loudness_computer.signal = f_signal
    f_signal_from_get = loudness_computer.signal

    assert f_signal_from_get.data[0, 2] == 42

    # Set invalid value
    with pytest.raises(PyAnsysSoundException, match="Signal must be specified as a DPF field."):
        loudness_computer.signal = "WrongType"


def test_loudness_iso_532_1_stationary_set_get_field_type():
    """Test the field_type property of the LoudnessISO532_1_Stationary class."""
    loudness_computer = LoudnessISO532_1_Stationary()

    # Set value
    loudness_computer.field_type = "Diffuse"
    assert loudness_computer.field_type == "Diffuse"

    # Check case insensitivity
    loudness_computer.field_type = "diffuse"
    assert loudness_computer.field_type == "diffuse"

    loudness_computer.field_type = "DIFFUSE"
    assert loudness_computer.field_type == "DIFFUSE"

    # Set invalid value
    with pytest.raises(
        PyAnsysSoundException,
        match='Invalid field type "Invalid". Available options are "Free" and "Diffuse".',
    ):
        loudness_computer.field_type = "Invalid"
