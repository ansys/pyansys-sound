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

import numpy as np
import pytest

from ansys.sound.core._pyansys_sound import (PyAnsysSoundException,
                                             PyAnsysSoundWarning)
from ansys.sound.core.psychoacoustics import PsychoacousticsParent
from ansys.sound.core.psychoacoustics.loudness_iso_532_1_stationary import \
    LoudnessISO532_1_Stationary
from ansys.sound.core.signal_utilities.load_wav import LoadWav


def test_psychoacoustics_parent_instantiation(dpf_sound_test_server):
    psychoacoustics_parent = PsychoacousticsParent()
    assert psychoacoustics_parent != None


def test_psychoacoustics_convert_bark_to_hertz(dpf_sound_test_server):
    psychoacoustics_parent = PsychoacousticsParent()

    # Invalid Bark band index -> error
    with pytest.raises(
        PyAnsysSoundException,
        match="Specified Bark band indexes must be between 0.0 and 24.0 Bark.",
    ):
        bark_band_frequencies = psychoacoustics_parent._convert_bark_to_hertz(
            bark_band_indexes=np.array([-1])
        )

    # Check output for some valid indexes
    bark_band_indexes = np.array([0, 0.1, 1, 6, 8.5, 15.3, 24])
    bark_band_frequencies = psychoacoustics_parent._convert_bark_to_hertz(
        bark_band_indexes=bark_band_indexes
    )
    assert type(bark_band_frequencies) == np.ndarray
    assert len(bark_band_frequencies) == len(bark_band_indexes)
    assert bark_band_frequencies[0] == pytest.approx(12.764378478664192)
    assert bark_band_frequencies[1] == pytest.approx(21.33995918005147)
    assert bark_band_frequencies[4] == pytest.approx(975.1181102362203)
    assert bark_band_frequencies[6] == pytest.approx(15334.573030003306)


def test_psychoacoustics_parent_check_channel_index(dpf_sound_test_server):
    # We need to instantiate either of the child classes (loudness here), otherwise we cannot
    # achieve complete test coverage of the method.
    loudness = LoudnessISO532_1_Stationary()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal as a field
    loudness.signal = fc[0]

    # Nothing computed -> false
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the "
        "'LoudnessISO532_1_Stationary.process\\(\\)' method.",
    ):
        valid_status = loudness._check_channel_index(0)
    assert valid_status == False

    loudness.process()

    # Check unexisting channel (field case)
    with pytest.raises(
        PyAnsysSoundException, match="Specified channel index \\(1\\) does not exist."
    ):
        loudness._check_channel_index(1)

    # Set signal as a fields container
    loudness.signal = fc
    loudness.process()

    # Check unexisting channel (fields container case)
    with pytest.raises(
        PyAnsysSoundException, match="Specified channel index \\(1\\) does not exist."
    ):
        loudness._check_channel_index(1)

    # Check existing channel (0)
    assert loudness._check_channel_index(0) == True
