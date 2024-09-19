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

import numpy as np
import pytest
from ansys.dpf.core import Field, FieldsContainer

from ansys.sound.core._pyansys_sound import (PyAnsysSoundException,
                                             PyAnsysSoundWarning)
from ansys.sound.core.psychoacoustics import FluctuationStrength
from ansys.sound.core.signal_utilities import LoadWav

EXP_FS_1 = 1.0416046380996704
EXP_FS_2 = 0.9974160194396973
EXP_SPECIFIC_FS_1_0 = 0.09723643958568573
EXP_SPECIFIC_FS_1_9 = 0.15443961322307587
EXP_SPECIFIC_FS_1_40 = 0.17233367264270782
EXP_SPECIFIC_FS_2_15 = 0.26900193095207214
EXP_SPECIFIC_FS_2_17 = 0.2570513188838959
EXP_SPECIFIC_FS_2_40 = 0.11656410992145538
EXP_BARK_0 = 0.5
EXP_BARK_9 = 5.0
EXP_BARK_40 = 20.5
EXP_FREQ_0 = 56.417020507724274
EXP_FREQ_9 = 498.9473684210526
EXP_FREQ_40 = 6875.975124656844

TOTAL_FS_ID = "total"
SPECIFIC_FS_ID = "specific"


def test_fs_instantiation(dpf_sound_test_server):
    fs_computer = FluctuationStrength()
    assert fs_computer != None


def test_fs_process(dpf_sound_test_server):
    fs_computer = FluctuationStrength()

    # No signal -> error
    with pytest.raises(
        PyAnsysSoundException,
        match="No signal found for fluctuation strength computation."
        " Use 'FluctuationStrength.signal'.",
    ):
        fs_computer.process()

    # Get a signal
    wav_loader = LoadWav(pytest.data_path_fluctuating_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal as field container
    fs_computer.signal = fc
    # Compute: no error
    fs_computer.process()

    # Set signal as field
    fs_computer.signal = fc[0]
    # Compute: no error
    fs_computer.process()


def test_fs_get_output(dpf_sound_test_server):
    fs_computer = FluctuationStrength()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_fluctuating_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Fluctuation strength not calculated yet -> warning
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. \
                        Use the 'FluctuationStrength.process\\(\\)' method.",
    ):
        output = fs_computer.get_output()
    assert output == None

    # Set signal
    fs_computer.signal = fc

    # Compute
    fs_computer.process()

    (fs, specific_fs) = fs_computer.get_output()
    assert fs != None
    assert type(fs) == FieldsContainer
    assert specific_fs != None
    assert type(specific_fs) == FieldsContainer


def test_fs_get_fluctuation_strength(dpf_sound_test_server):
    fs_computer = FluctuationStrength()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_fluctuating_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Fluctuation strength not calculated yet -> warning
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. \
                        Use the 'FluctuationStrength.process\\(\\)' method.",
    ):
        output = fs_computer.get_fluctuation_strength()
    assert output == None

    # Set signal as a field
    fs_computer.signal = fc[0]

    # Compute
    fs_computer.process()

    # Request second channel's fluctuation strength while signal is a field (mono) -> error
    with pytest.raises(
        PyAnsysSoundException, match="Specified channel index \\(1\\) does not exist."
    ):
        fs = fs_computer.get_fluctuation_strength(1)

    fs = fs_computer.get_fluctuation_strength(0)
    assert type(fs) == np.float64
    assert fs == pytest.approx(EXP_FS_1)

    # Set signal as a fields container
    fs_computer.signal = fc

    # Compute
    fs_computer.process()

    # Request second channel's fluctuation strength while signal is mono -> error
    with pytest.raises(
        PyAnsysSoundException, match="Specified channel index \\(1\\) does not exist."
    ):
        fs = fs_computer.get_fluctuation_strength(1)

    fs = fs_computer.get_fluctuation_strength(0)
    assert type(fs) == np.float64
    assert fs == pytest.approx(EXP_FS_1)

    # Add a second signal in the fields container
    # Note: No need to re-assign the signal property, as fc is simply an alias for it
    wav_loader = LoadWav(pytest.data_path_fluctuating_tone_in_container)
    wav_loader.process()
    fc.add_field({"channel_number": 1}, wav_loader.get_output()[0])

    # Compute again
    fs_computer.process()

    fs = fs_computer.get_fluctuation_strength(1)
    assert type(fs) == np.float64
    assert fs == pytest.approx(EXP_FS_2)


def test_fs_get_specific_fluctuation_strength(dpf_sound_test_server):
    fs_computer = FluctuationStrength()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_fluctuating_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Fluctuation strength not calculated yet -> warning
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. \
                        Use the 'FluctuationStrength.process\\(\\)' method.",
    ):
        output = fs_computer.get_specific_fluctuation_strength()
    assert output == None

    # Set signal
    fs_computer.signal = fc

    # Compute
    fs_computer.process()

    specific_fs = fs_computer.get_specific_fluctuation_strength()

    assert type(specific_fs) == np.ndarray
    assert len(specific_fs) == 47
    assert specific_fs[0] == pytest.approx(EXP_SPECIFIC_FS_1_0)
    assert specific_fs[9] == pytest.approx(EXP_SPECIFIC_FS_1_9)
    assert specific_fs[40] == pytest.approx(EXP_SPECIFIC_FS_1_40)

    # Add a second signal in the fields container
    # Note: No need to re-assign the signal property, as fc is simply an alias for it
    wav_loader = LoadWav(pytest.data_path_fluctuating_tone_in_container)
    wav_loader.process()
    fc.add_field({"channel_number": 1}, wav_loader.get_output()[0])

    # Compute again
    fs_computer.process()

    specific_fs = fs_computer.get_specific_fluctuation_strength(1)

    assert type(specific_fs) == np.ndarray
    assert len(specific_fs) == 47
    assert specific_fs[15] == pytest.approx(EXP_SPECIFIC_FS_2_15)
    assert specific_fs[17] == pytest.approx(EXP_SPECIFIC_FS_2_17)
    assert specific_fs[40] == pytest.approx(EXP_SPECIFIC_FS_2_40)


def test_fs__get_ouptut_parameter(dpf_sound_test_server):
    fs_computer = FluctuationStrength()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_fluctuating_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    fs_computer.signal = fc

    # Fluctuation strength not calculated yet -> warning
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. \
                        Use the 'FluctuationStrength.process\\(\\)' method.",
    ):
        output = fs_computer._get_output_parameter(0, TOTAL_FS_ID)
    assert output == None

    # Compute
    fs_computer.process()

    # Invalid parameter identifier -> error
    with pytest.raises(PyAnsysSoundException, match="ID of output parameter is invalid."):
        param = fs_computer._get_output_parameter(0, "thisIsNotValid")

    # Invalid channel index -> error
    with pytest.raises(
        PyAnsysSoundException, match="Specified channel index \\(1\\) does not exist."
    ):
        param = fs_computer._get_output_parameter(1, TOTAL_FS_ID)

    param = fs_computer._get_output_parameter(0, TOTAL_FS_ID)
    assert type(param) == np.float64
    assert param == pytest.approx(EXP_FS_1)

    param = fs_computer._get_output_parameter(0, SPECIFIC_FS_ID)
    assert type(param) == np.ndarray
    assert len(param) == 47
    assert param[0] == pytest.approx(EXP_SPECIFIC_FS_1_0)
    assert param[9] == pytest.approx(EXP_SPECIFIC_FS_1_9)
    assert param[40] == pytest.approx(EXP_SPECIFIC_FS_1_40)

    # Add a second signal in the fields container
    # Note: No need to re-assign the signal property, as fc is simply an alias for it
    wav_loader = LoadWav(pytest.data_path_fluctuating_tone_in_container)
    wav_loader.process()
    fc.add_field({"channel_number": 1}, wav_loader.get_output()[0])

    # Compute again
    fs_computer.process()

    param = fs_computer._get_output_parameter(1, TOTAL_FS_ID)
    assert type(param) == np.float64
    assert param == pytest.approx(EXP_FS_2)

    param = fs_computer._get_output_parameter(1, SPECIFIC_FS_ID)
    assert type(param) == np.ndarray
    assert len(param) == 47
    assert param[15] == pytest.approx(EXP_SPECIFIC_FS_2_15)
    assert param[17] == pytest.approx(EXP_SPECIFIC_FS_2_17)
    assert param[40] == pytest.approx(EXP_SPECIFIC_FS_2_40)


def test_fs_get_bark_band_indexes(dpf_sound_test_server):
    fs_computer = FluctuationStrength()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_fluctuating_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Fluctuation strength not calculated yet -> warning
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. \
                        Use the 'FluctuationStrength.process\\(\\)' method.",
    ):
        output = fs_computer.get_bark_band_indexes()
    assert output == None

    # Set signal as a fields container
    fs_computer.signal = fc

    # Compute
    fs_computer.process()

    bark_band_indexes = fs_computer.get_bark_band_indexes()
    assert type(bark_band_indexes) == np.ndarray
    assert len(bark_band_indexes) == 47
    assert bark_band_indexes[0] == pytest.approx(EXP_BARK_0)
    assert bark_band_indexes[9] == pytest.approx(EXP_BARK_9)
    assert bark_band_indexes[40] == pytest.approx(EXP_BARK_40)

    # Set signal as a field
    fs_computer.signal = fc[0]

    # Compute
    fs_computer.process()

    bark_band_indexes = fs_computer.get_bark_band_indexes()
    assert type(bark_band_indexes) == np.ndarray
    assert len(bark_band_indexes) == 47
    assert bark_band_indexes[0] == pytest.approx(EXP_BARK_0)
    assert bark_band_indexes[9] == pytest.approx(EXP_BARK_9)
    assert bark_band_indexes[40] == pytest.approx(EXP_BARK_40)


def test_fs_get_bark_band_frequencies(dpf_sound_test_server):
    fs_computer = FluctuationStrength()
    # Get a signal
    # assert pytest.data_path_flute_in_container == 'toto'
    wav_loader = LoadWav(pytest.data_path_fluctuating_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    fs_computer.signal = fc

    # Compute
    fs_computer.process()

    bark_band_frequencies = fs_computer.get_bark_band_frequencies()
    assert type(bark_band_frequencies) == np.ndarray
    assert len(bark_band_frequencies) == 47
    assert bark_band_frequencies[0] == pytest.approx(EXP_FREQ_0)
    assert bark_band_frequencies[9] == pytest.approx(EXP_FREQ_9)
    assert bark_band_frequencies[40] == pytest.approx(EXP_FREQ_40)


def test_fs_get_output_as_nparray_from_fields_container(dpf_sound_test_server):
    fs_computer = FluctuationStrength()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_fluctuating_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Fluctuation strength not calculated yet -> warning
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. \
                        Use the 'FluctuationStrength.process\\(\\)' method.",
    ):
        output = fs_computer.get_output_as_nparray()
    assert output == None

    # Set signal
    fs_computer.signal = fc

    # Compute
    fs_computer.process()

    (fs, specific_fs) = fs_computer.get_output_as_nparray()

    assert type(fs) == np.ndarray
    assert len(fs) == 1
    assert fs[0] == pytest.approx(EXP_FS_1)
    assert type(specific_fs) == np.ndarray
    assert len(specific_fs) == 47
    assert specific_fs[0] == pytest.approx(EXP_SPECIFIC_FS_1_0)
    assert specific_fs[9] == pytest.approx(EXP_SPECIFIC_FS_1_9)
    assert specific_fs[40] == pytest.approx(EXP_SPECIFIC_FS_1_40)


def test_fs_get_output_as_nparray_from_field(dpf_sound_test_server):
    fs_computer = FluctuationStrength()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_fluctuating_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    fs_computer.signal = fc[0]

    # Compute
    fs_computer.process()

    (fs, specific_fs) = fs_computer.get_output_as_nparray()

    assert type(fs) == np.ndarray
    assert len(fs) == 1
    assert fs[0] == pytest.approx(EXP_FS_1)
    assert type(specific_fs) == np.ndarray
    assert len(specific_fs) == 47
    assert specific_fs[0] == pytest.approx(EXP_SPECIFIC_FS_1_0)
    assert specific_fs[9] == pytest.approx(EXP_SPECIFIC_FS_1_9)
    assert specific_fs[40] == pytest.approx(EXP_SPECIFIC_FS_1_40)


@patch("matplotlib.pyplot.show")
def test_fs_plot_from_fields_container(mock_show, dpf_sound_test_server):
    fs_computer = FluctuationStrength()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_fluctuating_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    fs_computer.signal = fc

    # Fluctuation strength not computed yet -> error
    with pytest.raises(
        PyAnsysSoundException,
        match="Output is not processed yet. \
                    Use the 'FluctuationStrength.process\\(\\)' method.",
    ):
        fs_computer.plot()

    # Compute
    fs_computer.process()

    # Plot
    fs_computer.plot()

    # Add a second signal in the fields container
    wav_loader = LoadWav(pytest.data_path_fluctuating_tone_in_container)
    wav_loader.process()
    fc.add_field({"channel_number": 1}, wav_loader.get_output()[0])

    # Compute
    fs_computer.process()

    # Plot
    fs_computer.plot()


@patch("matplotlib.pyplot.show")
def test_fs_plot_from_field(mock_show, dpf_sound_test_server):
    fs_computer = FluctuationStrength()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_fluctuating_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    fs_computer.signal = fc[0]

    # Compute
    fs_computer.process()

    # Plot
    fs_computer.plot()


def test_fs_set_get_signal(dpf_sound_test_server):
    fs_computer = FluctuationStrength()
    fc = FieldsContainer()
    fc.labels = ["channel"]
    f = Field()
    f.data = 42 * np.ones(3)
    fc.add_field({"channel": 0}, f)
    fc.name = "testField"
    fs_computer.signal = fc
    fc_from_get = fs_computer.signal

    assert fc_from_get.name == "testField"
    assert len(fc_from_get) == 1
    assert fc_from_get[0].data[0, 2] == 42
