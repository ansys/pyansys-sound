# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
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

from ansys.dpf.core import Field, FieldsContainer
import numpy as np
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ansys.sound.core.psychoacoustics import Roughness
from ansys.sound.core.signal_utilities import LoadWav

EXP_ROUGHNESS_1 = 0.5495809316635132
EXP_ROUGHNESS_2 = 0.20937225222587585
EXP_SPECIFIC_ROUGHNESS_1_0 = 0.0018477396806702018
EXP_SPECIFIC_ROUGHNESS_1_9 = 0.0060088788159191618
EXP_SPECIFIC_ROUGHNESS_1_40 = 0.062388259917497635
EXP_SPECIFIC_ROUGHNESS_2_15 = 0.03811583295464516
EXP_SPECIFIC_ROUGHNESS_2_17 = 0.18448638916015625
EXP_SPECIFIC_ROUGHNESS_2_40 = 0.0
EXP_BARK_0 = 0.5
EXP_BARK_9 = 5.0
EXP_BARK_40 = 20.5
EXP_FREQ_0 = 56.417020507724274
EXP_FREQ_9 = 498.9473684210526
EXP_FREQ_40 = 6875.975124656844

TOTAL_ROUGHNESS_ID = "total"
SPECIFIC_ROUGHNESS_ID = "specific"


def test_roughness_instantiation():
    roughness_computer = Roughness()
    assert roughness_computer != None


def test_roughness_process():
    roughness_computer = Roughness()

    # No signal -> error
    with pytest.raises(
        PyAnsysSoundException,
        match="No signal found for roughness computation. Use 'Roughness.signal'.",
    ):
        roughness_computer.process()

    # Get a signal
    wav_loader = LoadWav(pytest.data_path_rough_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal as field container
    roughness_computer.signal = fc
    # Compute: no error
    roughness_computer.process()

    # Set signal as field
    roughness_computer.signal = fc[0]
    # Compute: no error
    roughness_computer.process()


def test_roughness_get_output():
    roughness_computer = Roughness()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_rough_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Roughness not calculated yet -> warning
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. \
                        Use the 'Roughness.process\\(\\)' method.",
    ):
        output = roughness_computer.get_output()
    assert output == None

    # Set signal
    roughness_computer.signal = fc

    # Compute
    roughness_computer.process()

    (roughness, specific_roughness) = roughness_computer.get_output()
    assert roughness != None
    assert type(roughness) == FieldsContainer
    assert specific_roughness != None
    assert type(specific_roughness) == FieldsContainer


def test_roughness_get_roughness():
    roughness_computer = Roughness()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_rough_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Roughness not calculated yet -> warning
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. \
                        Use the 'Roughness.process\\(\\)' method.",
    ):
        output = roughness_computer.get_roughness()
    assert output == None

    # Set signal as a field
    roughness_computer.signal = fc[0]

    # Compute
    roughness_computer.process()

    # Request second channel's roughness while signal is a field (mono) -> error
    with pytest.raises(
        PyAnsysSoundException, match="Specified channel index \\(1\\) does not exist."
    ):
        roughness = roughness_computer.get_roughness(1)

    roughness = roughness_computer.get_roughness(0)
    assert type(roughness) == np.float64
    assert roughness == pytest.approx(EXP_ROUGHNESS_1)

    # Set signal as a fields container
    roughness_computer.signal = fc

    # Compute
    roughness_computer.process()

    # Request second channel's roughness while signal is mono -> error
    with pytest.raises(
        PyAnsysSoundException, match="Specified channel index \\(1\\) does not exist."
    ):
        roughness = roughness_computer.get_roughness(1)

    roughness = roughness_computer.get_roughness(0)
    assert type(roughness) == np.float64
    assert roughness == pytest.approx(EXP_ROUGHNESS_1)

    # Add a second signal in the fields container
    # Note: No need to re-assign the signal property, as fc is simply an alias for it
    wav_loader = LoadWav(pytest.data_path_rough_tone_in_container)
    wav_loader.process()
    fc.add_field({"channel_number": 1}, wav_loader.get_output()[0])

    # Compute again
    roughness_computer.process()

    roughness = roughness_computer.get_roughness(1)
    assert type(roughness) == np.float64
    assert roughness == pytest.approx(EXP_ROUGHNESS_2)


def test_roughness_get_specific_roughness():
    roughness_computer = Roughness()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_rough_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Roughness not calculated yet -> warning
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. \
                        Use the 'Roughness.process\\(\\)' method.",
    ):
        output = roughness_computer.get_specific_roughness()
    assert output == None

    # Set signal
    roughness_computer.signal = fc

    # Compute
    roughness_computer.process()

    specific_roughness = roughness_computer.get_specific_roughness()
    assert type(specific_roughness) == np.ndarray
    assert len(specific_roughness) == 47
    assert specific_roughness[0] == pytest.approx(EXP_SPECIFIC_ROUGHNESS_1_0)
    assert specific_roughness[9] == pytest.approx(EXP_SPECIFIC_ROUGHNESS_1_9)
    assert specific_roughness[40] == pytest.approx(EXP_SPECIFIC_ROUGHNESS_1_40)

    # Add a second signal in the fields container
    # Note: No need to re-assign the signal property, as fc is simply an alias for it
    wav_loader = LoadWav(pytest.data_path_rough_tone_in_container)
    wav_loader.process()
    fc.add_field({"channel_number": 1}, wav_loader.get_output()[0])

    # Compute again
    roughness_computer.process()

    specific_roughness = roughness_computer.get_specific_roughness(1)
    assert type(specific_roughness) == np.ndarray
    assert len(specific_roughness) == 47
    assert specific_roughness[15] == pytest.approx(EXP_SPECIFIC_ROUGHNESS_2_15)
    assert specific_roughness[17] == pytest.approx(EXP_SPECIFIC_ROUGHNESS_2_17)
    assert specific_roughness[40] == pytest.approx(EXP_SPECIFIC_ROUGHNESS_2_40)


def test_roughness_get_ouptut_parameter():
    roughness_computer = Roughness()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_rough_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    roughness_computer.signal = fc

    # Roughness not calculated yet -> warning
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. \
                        Use the 'Roughness.process\\(\\)' method.",
    ):
        output = roughness_computer._get_output_parameter(0, TOTAL_ROUGHNESS_ID)
    assert output == None

    # Compute
    roughness_computer.process()

    # Invalid parameter identifier -> error
    with pytest.raises(PyAnsysSoundException, match="Identifier of output parameter is invalid."):
        param = roughness_computer._get_output_parameter(0, "thisIsNotValid")

    # Invalid channel index -> error
    with pytest.raises(
        PyAnsysSoundException, match="Specified channel index \\(1\\) does not exist."
    ):
        param = roughness_computer._get_output_parameter(1, TOTAL_ROUGHNESS_ID)

    param = roughness_computer._get_output_parameter(0, TOTAL_ROUGHNESS_ID)
    assert type(param) == np.float64
    assert param == pytest.approx(EXP_ROUGHNESS_1)

    param = roughness_computer._get_output_parameter(0, SPECIFIC_ROUGHNESS_ID)
    assert type(param) == np.ndarray
    assert len(param) == 47
    assert param[0] == pytest.approx(EXP_SPECIFIC_ROUGHNESS_1_0)
    assert param[9] == pytest.approx(EXP_SPECIFIC_ROUGHNESS_1_9)
    assert param[40] == pytest.approx(EXP_SPECIFIC_ROUGHNESS_1_40)

    # Add a second signal in the fields container
    # Note: No need to re-assign the signal property, as fc is simply an alias for it
    wav_loader = LoadWav(pytest.data_path_rough_tone_in_container)
    wav_loader.process()
    fc.add_field({"channel_number": 1}, wav_loader.get_output()[0])

    # Compute again
    roughness_computer.process()

    param = roughness_computer._get_output_parameter(1, TOTAL_ROUGHNESS_ID)
    assert type(param) == np.float64
    assert param == pytest.approx(EXP_ROUGHNESS_2)

    param = roughness_computer._get_output_parameter(1, SPECIFIC_ROUGHNESS_ID)
    assert type(param) == np.ndarray
    assert len(param) == 47
    assert param[15] == pytest.approx(EXP_SPECIFIC_ROUGHNESS_2_15)
    assert param[17] == pytest.approx(EXP_SPECIFIC_ROUGHNESS_2_17)
    assert param[40] == pytest.approx(EXP_SPECIFIC_ROUGHNESS_2_40)


def test_roughness_get_bark_band_indexes():
    roughness_computer = Roughness()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_rough_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Roughness not calculated yet -> warning
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. \
                        Use the 'Roughness.process\\(\\)' method.",
    ):
        output = roughness_computer.get_bark_band_indexes()
    assert output == None

    # Set signal as a fields container
    roughness_computer.signal = fc

    # Compute
    roughness_computer.process()

    bark_band_indexes = roughness_computer.get_bark_band_indexes()
    assert type(bark_band_indexes) == np.ndarray
    assert len(bark_band_indexes) == 47
    assert bark_band_indexes[0] == pytest.approx(EXP_BARK_0)
    assert bark_band_indexes[9] == pytest.approx(EXP_BARK_9)
    assert bark_band_indexes[40] == pytest.approx(EXP_BARK_40)

    # Set signal as a field
    roughness_computer.signal = fc[0]

    # Compute
    roughness_computer.process()

    bark_band_indexes = roughness_computer.get_bark_band_indexes()
    assert type(bark_band_indexes) == np.ndarray
    assert len(bark_band_indexes) == 47
    assert bark_band_indexes[0] == pytest.approx(EXP_BARK_0)
    assert bark_band_indexes[9] == pytest.approx(EXP_BARK_9)
    assert bark_band_indexes[40] == pytest.approx(EXP_BARK_40)


def test_roughness_get_bark_band_frequencies():
    roughness_computer = Roughness()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_rough_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    roughness_computer.signal = fc

    # Compute
    roughness_computer.process()

    bark_band_frequencies = roughness_computer.get_bark_band_frequencies()
    assert type(bark_band_frequencies) == np.ndarray
    assert len(bark_band_frequencies) == 47
    assert bark_band_frequencies[0] == pytest.approx(EXP_FREQ_0)
    assert bark_band_frequencies[9] == pytest.approx(EXP_FREQ_9)
    assert bark_band_frequencies[40] == pytest.approx(EXP_FREQ_40)


def test_roughness_get_output_as_nparray_from_fields_container():
    roughness_computer = Roughness()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_rough_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Roughness not calculated yet -> warning
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. \
                        Use the 'Roughness.process\\(\\)' method.",
    ):
        output = roughness_computer.get_output_as_nparray()
    assert output == None

    # Set signal
    roughness_computer.signal = fc

    # Compute
    roughness_computer.process()

    (roughness, specific_roughness) = roughness_computer.get_output_as_nparray()
    assert type(roughness) == np.ndarray
    assert len(roughness) == 1
    assert roughness[0] == pytest.approx(EXP_ROUGHNESS_1)
    assert type(specific_roughness) == np.ndarray
    assert len(specific_roughness) == 47
    assert specific_roughness[0] == pytest.approx(EXP_SPECIFIC_ROUGHNESS_1_0)
    assert specific_roughness[9] == pytest.approx(EXP_SPECIFIC_ROUGHNESS_1_9)
    assert specific_roughness[40] == pytest.approx(EXP_SPECIFIC_ROUGHNESS_1_40)


def test_roughness_get_output_as_nparray_from_field():
    roughness_computer = Roughness()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_rough_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    roughness_computer.signal = fc[0]

    # Compute
    roughness_computer.process()

    (roughness, specific_roughness) = roughness_computer.get_output_as_nparray()
    assert type(roughness) == np.ndarray
    assert len(roughness) == 1
    assert roughness[0] == pytest.approx(EXP_ROUGHNESS_1)
    assert type(specific_roughness) == np.ndarray
    assert len(specific_roughness) == 47
    assert specific_roughness[0] == pytest.approx(EXP_SPECIFIC_ROUGHNESS_1_0)
    assert specific_roughness[9] == pytest.approx(EXP_SPECIFIC_ROUGHNESS_1_9)
    assert specific_roughness[40] == pytest.approx(EXP_SPECIFIC_ROUGHNESS_1_40)


@patch("matplotlib.pyplot.show")
def test_roughness_plot_from_fields_container(mock_show):
    roughness_computer = Roughness()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_rough_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    roughness_computer.signal = fc

    # Roughness not computed yet -> error
    with pytest.raises(
        PyAnsysSoundException,
        match="Output is not processed yet. \
                    Use the 'Roughness.process\\(\\)' method.",
    ):
        roughness_computer.plot()

    # Compute
    roughness_computer.process()

    # Plot
    roughness_computer.plot()

    # Add a second signal in the fields container
    # Note: No need to re-assign the signal property, as fc is simply an alias for it
    wav_loader = LoadWav(pytest.data_path_rough_tone_in_container)
    wav_loader.process()
    fc.add_field({"channel_number": 1}, wav_loader.get_output()[0])

    # Compute
    roughness_computer.process()

    # Plot
    roughness_computer.plot()


@patch("matplotlib.pyplot.show")
def test_roughness_plot_from_field(mock_show):
    roughness_computer = Roughness()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_rough_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    roughness_computer.signal = fc[0]

    # Compute
    roughness_computer.process()

    # Plot
    roughness_computer.plot()


def test_roughness_set_get_signal():
    roughness_computer = Roughness()
    fc = FieldsContainer()
    fc.labels = ["channel"]
    f = Field()
    f.data = 42 * np.ones(3)
    fc.add_field({"channel": 0}, f)
    fc.name = "testField"
    roughness_computer.signal = fc
    fc_from_get = roughness_computer.signal

    assert fc_from_get.name == "testField"
    assert len(fc_from_get) == 1
    assert fc_from_get[0].data[0, 2] == 42
