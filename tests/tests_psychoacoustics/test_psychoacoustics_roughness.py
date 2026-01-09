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

from unittest.mock import patch

from ansys.dpf.core import Field
import numpy as np
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ansys.sound.core.psychoacoustics import Roughness
from ansys.sound.core.signal_utilities import LoadWav

EXP_ROUGHNESS = 0.5495809316635132
EXP_BARK_COUNT = 47
EXP_SPECIFIC_ROUGHNESS_0 = 0.0018477396806702018
EXP_SPECIFIC_ROUGHNESS_9 = 0.0060088788159191618
EXP_SPECIFIC_ROUGHNESS_40 = 0.062388259917497635
EXP_TIME_COUNT = 33
EXP_ROUGHNESS_OVER_TIME_5 = 0.4840297
EXP_ROUGHNESS_OVER_TIME_12 = 0.5560241
EXP_ROUGHNESS_OVER_TIME_20 = 0.5688730
EXP_BARK_0 = 0.5
EXP_BARK_9 = 5.0
EXP_BARK_40 = 20.5
EXP_FREQ_0 = 56.417020507724274
EXP_FREQ_9 = 498.9473684210526
EXP_FREQ_40 = 6875.975124656844
EXP_TIME_5 = 0.4644792
EXP_TIME_12 = 1.114750
EXP_TIME_20 = 1.857917
EXP_STR_DEFAULT = (
    "Roughness object\nData:\n\tSignal name: Not set\nOverall roughness: Not processed"
)
EXP_STR = 'Roughness object\nData:\n\tSignal name: ""\nOverall roughness: 0.55 aspers'


def test_roughness_instantiation():
    """Test the instantiation of the Roughness class."""
    roughness_computer = Roughness()
    assert roughness_computer != None


def test_roughness___str__():
    """Test the __str__ method of the Roughness class."""
    roughness_computer = Roughness()
    assert str(roughness_computer) == EXP_STR_DEFAULT

    # Get a signal
    wav_loader = LoadWav(pytest.data_path_rough_noise)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    roughness_computer.signal = fc[0]

    # Compute
    roughness_computer.process()

    assert str(roughness_computer) == EXP_STR


def test_roughness_process():
    """Test the process method of the Roughness class."""
    roughness_computer = Roughness()

    # No signal -> error
    with pytest.raises(
        PyAnsysSoundException,
        match="No signal found for roughness computation. Use `Roughness.signal`.",
    ):
        roughness_computer.process()

    # Get a signal
    wav_loader = LoadWav(pytest.data_path_rough_noise)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal as field
    roughness_computer.signal = fc[0]
    # Compute: no error
    roughness_computer.process()
    assert roughness_computer._output is not None


def test_roughness_get_output():
    """Test the get_output method of the Roughness class."""
    roughness_computer = Roughness()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_rough_noise)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Roughness not calculated yet -> warning
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the `Roughness.process\\(\\)` method.",
    ):
        output = roughness_computer.get_output()
    assert output == None

    # Set signal
    roughness_computer.signal = fc[0]

    # Compute
    roughness_computer.process()

    roughness, specific_roughness, roughness_over_time = roughness_computer.get_output()
    assert roughness == pytest.approx(EXP_ROUGHNESS)
    assert isinstance(specific_roughness, Field)
    assert specific_roughness.data[0] == pytest.approx(EXP_SPECIFIC_ROUGHNESS_0)
    assert specific_roughness.data[9] == pytest.approx(EXP_SPECIFIC_ROUGHNESS_9)
    assert specific_roughness.data[40] == pytest.approx(EXP_SPECIFIC_ROUGHNESS_40)
    assert isinstance(roughness_over_time, Field)
    assert roughness_over_time.data[5] == pytest.approx(EXP_ROUGHNESS_OVER_TIME_5)
    assert roughness_over_time.data[12] == pytest.approx(EXP_ROUGHNESS_OVER_TIME_12)
    assert roughness_over_time.data[20] == pytest.approx(EXP_ROUGHNESS_OVER_TIME_20)


def test_roughness_get_roughness():
    """Test the get_roughness method of the Roughness class."""
    roughness_computer = Roughness()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_rough_noise)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Roughness not calculated yet -> warning
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the `Roughness.process\\(\\)` method.",
    ):
        roughness = roughness_computer.get_roughness()
    assert np.isnan(roughness)

    # Set signal
    roughness_computer.signal = fc[0]

    # Compute
    roughness_computer.process()

    roughness = roughness_computer.get_roughness()
    assert type(roughness) == float
    assert roughness == pytest.approx(EXP_ROUGHNESS)


def test_roughness_get_specific_roughness():
    """Test the get_specific_roughness method of the Roughness class."""
    roughness_computer = Roughness()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_rough_noise)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Roughness not calculated yet -> warning
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the `Roughness.process\\(\\)` method.",
    ):
        specific_roughness = roughness_computer.get_specific_roughness()
    assert len(specific_roughness) == 0

    # Set signal
    roughness_computer.signal = fc[0]

    # Compute
    roughness_computer.process()

    specific_roughness = roughness_computer.get_specific_roughness()
    assert type(specific_roughness) == np.ndarray
    assert len(specific_roughness) == EXP_BARK_COUNT
    assert specific_roughness[0] == pytest.approx(EXP_SPECIFIC_ROUGHNESS_0)
    assert specific_roughness[9] == pytest.approx(EXP_SPECIFIC_ROUGHNESS_9)
    assert specific_roughness[40] == pytest.approx(EXP_SPECIFIC_ROUGHNESS_40)


def test_roughness_get_bark_band_indexes():
    """Test the get_bark_band_indexes method of the Roughness class."""
    roughness_computer = Roughness()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_rough_noise)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Roughness not calculated yet -> warning
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the `Roughness.process\\(\\)` method.",
    ):
        bark_scale = roughness_computer.get_bark_band_indexes()
    assert len(bark_scale) == 0

    # Set signal
    roughness_computer.signal = fc[0]

    # Compute
    roughness_computer.process()

    bark_band_indexes = roughness_computer.get_bark_band_indexes()
    assert type(bark_band_indexes) == np.ndarray
    assert len(bark_band_indexes) == EXP_BARK_COUNT
    assert bark_band_indexes[0] == pytest.approx(EXP_BARK_0)
    assert bark_band_indexes[9] == pytest.approx(EXP_BARK_9)
    assert bark_band_indexes[40] == pytest.approx(EXP_BARK_40)


def test_roughness_get_bark_band_frequencies():
    """Test the get_bark_band_frequencies method of the Roughness class."""
    roughness_computer = Roughness()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_rough_noise)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    roughness_computer.signal = fc[0]

    # Compute
    roughness_computer.process()

    bark_band_frequencies = roughness_computer.get_bark_band_frequencies()
    assert type(bark_band_frequencies) == np.ndarray
    assert len(bark_band_frequencies) == EXP_BARK_COUNT
    assert bark_band_frequencies[0] == pytest.approx(EXP_FREQ_0)
    assert bark_band_frequencies[9] == pytest.approx(EXP_FREQ_9)
    assert bark_band_frequencies[40] == pytest.approx(EXP_FREQ_40)


def test_roughness_get_roughness_over_time():
    """Test the get_roughness_over_time method of the Roughness class."""
    roughness_computer = Roughness()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_rough_noise)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Roughness not calculated yet -> warning
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the `Roughness.process\\(\\)` method.",
    ):
        roughness_over_time = roughness_computer.get_roughness_over_time()
    assert len(roughness_over_time) == 0

    # Set signal
    roughness_computer.signal = fc[0]

    # Compute
    roughness_computer.process()

    roughness_over_time = roughness_computer.get_roughness_over_time()
    assert type(roughness_over_time) == np.ndarray
    assert len(roughness_over_time) == EXP_TIME_COUNT
    assert roughness_over_time[5] == pytest.approx(EXP_ROUGHNESS_OVER_TIME_5)
    assert roughness_over_time[12] == pytest.approx(EXP_ROUGHNESS_OVER_TIME_12)
    assert roughness_over_time[20] == pytest.approx(EXP_ROUGHNESS_OVER_TIME_20)


def test_roughness_get_time_scale():
    """Test the get_time_scale method of the Roughness class."""
    roughness_computer = Roughness()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_rough_noise)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    roughness_computer.signal = fc[0]

    # Compute
    roughness_computer.process()

    time_scale = roughness_computer.get_time_scale()
    assert type(time_scale) == np.ndarray
    assert len(time_scale) == EXP_TIME_COUNT
    assert time_scale[5] == pytest.approx(EXP_TIME_5)
    assert time_scale[12] == pytest.approx(EXP_TIME_12)
    assert time_scale[20] == pytest.approx(EXP_TIME_20)


def test_roughness_get_output_as_nparray():
    """Test the get_output_as_nparray method of the Roughness class."""
    roughness_computer = Roughness()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_rough_noise)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    roughness_computer.signal = fc[0]

    # Roughness not calculated yet -> warning
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the `Roughness.process\\(\\)` method.",
    ):
        roughness, specific_roughness, bark_scale, roughness_over_time, time_scale = (
            roughness_computer.get_output_as_nparray()
        )
    assert np.isnan(roughness)
    assert len(specific_roughness) == 0
    assert len(bark_scale) == 0
    assert len(roughness_over_time) == 0
    assert len(time_scale) == 0

    # Compute
    roughness_computer.process()

    roughness, specific_roughness, bark_scale, roughness_over_time, time_scale = (
        roughness_computer.get_output_as_nparray()
    )
    assert roughness == pytest.approx(EXP_ROUGHNESS)
    assert isinstance(specific_roughness, np.ndarray)
    assert specific_roughness[0] == pytest.approx(EXP_SPECIFIC_ROUGHNESS_0)
    assert specific_roughness[9] == pytest.approx(EXP_SPECIFIC_ROUGHNESS_9)
    assert specific_roughness[40] == pytest.approx(EXP_SPECIFIC_ROUGHNESS_40)
    assert isinstance(bark_scale, np.ndarray)
    assert bark_scale[0] == pytest.approx(EXP_BARK_0)
    assert bark_scale[9] == pytest.approx(EXP_BARK_9)
    assert bark_scale[40] == pytest.approx(EXP_BARK_40)
    assert isinstance(roughness_over_time, np.ndarray)
    assert roughness_over_time[5] == pytest.approx(EXP_ROUGHNESS_OVER_TIME_5)
    assert roughness_over_time[12] == pytest.approx(EXP_ROUGHNESS_OVER_TIME_12)
    assert roughness_over_time[20] == pytest.approx(EXP_ROUGHNESS_OVER_TIME_20)
    assert isinstance(time_scale, np.ndarray)
    assert time_scale[5] == pytest.approx(EXP_TIME_5)
    assert time_scale[12] == pytest.approx(EXP_TIME_12)
    assert time_scale[20] == pytest.approx(EXP_TIME_20)


@patch("matplotlib.pyplot.show")
def test_roughness_plot(mock_show):
    """Test the plot method."""
    roughness_computer = Roughness()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_rough_noise)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    roughness_computer.signal = fc[0]

    # Roughness not computed yet -> error
    with pytest.raises(
        PyAnsysSoundException,
        match="Output is not processed yet. Use the `Roughness.process\\(\\)` method.",
    ):
        roughness_computer.plot()

    # Compute
    roughness_computer.process()

    # Plot
    roughness_computer.plot()


def test_roughness_set_get_signal():
    """Test the setter and getter of the signal property."""
    roughness_computer = Roughness()
    f_signal = Field()
    f_signal.data = 42 * np.ones(3)

    roughness_computer.signal = f_signal
    assert isinstance(roughness_computer.signal, Field)
    assert len(roughness_computer.signal.data[0]) == 3
    assert roughness_computer.signal.data[0][0] == 42

    # Set invalid value
    with pytest.raises(PyAnsysSoundException, match="Signal must be specified as a DPF field."):
        roughness_computer.signal = "WrongType"
