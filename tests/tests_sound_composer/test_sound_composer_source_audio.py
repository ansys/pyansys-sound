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

from ansys.dpf.core import Field, TimeFreqSupport, fields_factory, locations
import numpy as np
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ansys.sound.core.sound_composer import SourceAudio
from ansys.sound.core.spectral_processing import PowerSpectralDensity

EXP_AUDIO_DATA17640 = -0.5416082739830017
EXP_STR_NOT_SET = "Audio source: Not set"
EXP_STR_ALL_SET = (
    "Audio source: 'flute'\n\tDuration: 3.5 s\n\tSampling frequency: 44100.0 Hz"
)


def test_source_audio_instantiation_no_arg(dpf_sound_test_server):
    """Test SourceAudio instantiation without arguments."""
    # Test instantiation.
    source_audio = SourceAudio()
    assert isinstance(source_audio, SourceAudio)
    assert source_audio.source_audio_data is None


def test_source_audio_instantiation_file_arg(dpf_sound_test_server):
    """Test SourceAudio instantiation with file argument."""
    # Test instantiation.
    source_audio = SourceAudio(pytest.data_path_flute_nonUnitaryCalib_in_container)
    assert isinstance(source_audio, SourceAudio)
    assert source_audio.source_audio_data is not None


def test_source_audio___str___not_set(dpf_sound_test_server):
    """Test SourceAudio __str__ method when nothing is set."""
    source_audio = SourceAudio()
    assert str(source_audio) == EXP_STR_NOT_SET


def test_source_audio___str___all_set(dpf_sound_test_server):
    """Test SourceAudio __str__ method when all data are set."""
    source_audio = SourceAudio(pytest.data_path_flute_nonUnitaryCalib_in_container)
    assert str(source_audio) == EXP_STR_ALL_SET


def test_source_audio_properties(dpf_sound_test_server):
    """Test SourceAudio properties."""
    source_audio = SourceAudio()

    # Test source_audio_data property.
    source_audio.source_audio_data = Field()
    assert isinstance(source_audio.source_audio_data, Field)


def test_source_audio_propertiess_exceptions(dpf_sound_test_server):
    """Test SourceAudio properties' exceptions."""
    source_audio = SourceAudio()

    # Test source_audio_data setter exception (str instead a Field).
    with pytest.raises(
        PyAnsysSoundException, match="Specified audio source data must be provided as a DPF field."
    ):
        source_audio.source_audio_data = "InvalidType"


def test_source_audio_load_source_audio_from_text(dpf_sound_test_server):
    """Test SourceAudio load_source_audio_from_text method."""
    source_audio = SourceAudio()
    source_audio.load_source_audio_from_text(
        pytest.data_path_flute_nonUnitaryCalib_as_txt_in_container
    )
    assert isinstance(source_audio.source_audio_data, Field)
    assert source_audio.source_audio_data.data[17640] == pytest.approx(EXP_AUDIO_DATA17640, rel=1e-3)


def test_source_audio_process_no_resample(dpf_sound_test_server):
    """Test SourceAudio process method (no resample needed)."""
    source_audio = SourceAudio(pytest.data_path_flute_nonUnitaryCalib_in_container)
    source_audio.process()
    assert source_audio._output is not None


def test_source_audio_process_resample(dpf_sound_test_server):
    """Test SourceAudio process method (resample)."""
    source_audio = SourceAudio(pytest.data_path_flute_nonUnitaryCalib_in_container)
    source_audio.process(48000)
    assert source_audio._output is not None


def test_source_audio_process_exceptions(dpf_sound_test_server):
    """Test SourceAudio process method exceptions."""
    source_audio = SourceAudio()
    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "Source's audio data is not set. Use ``SourceAudio.source_audio_data`` "
            "or method ``SourceAudio.load_source_audio_from_text\\(\\)``."
        ),
    ):
        source_audio.process()


def test_source_audio_get_output(dpf_sound_test_server):
    """Test SourceAudio get_output method."""
    source_audio = SourceAudio(pytest.data_path_flute_nonUnitaryCalib_in_container)
    source_audio.process(sampling_frequency=44100.0)

    output_signal = source_audio.get_output()
    time = output_signal.time_freq_support.time_frequencies.data
    fs = 1.0 / (time[1] - time[0])
    assert isinstance(output_signal, Field)
    assert fs == pytest.approx(44100.0)
    assert output_signal.data[17640] == pytest.approx(EXP_AUDIO_DATA17640)


def test_source_audio_get_output_unprocessed(dpf_sound_test_server):
    """Test SourceAudio get_output method's exception."""
    source_audio = SourceAudio()
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the ``SourceAudio.process\\(\\)`` method.",
    ):
        output = source_audio.get_output()
    assert output is None


def test_source_audio_get_output_as_nparray(dpf_sound_test_server):
    """Test SourceAudio get_output_as_nparray method."""
    source_audio = SourceAudio(pytest.data_path_flute_nonUnitaryCalib_in_container)
    source_audio.process(sampling_frequency=44100.0)

    output_signal = source_audio.get_output_as_nparray()
    assert isinstance(output_signal, np.ndarray)
    assert output_signal[17640] == pytest.approx(EXP_AUDIO_DATA17640)


def test_source_audio_get_output_as_nparray_unprocessed(dpf_sound_test_server):
    """Test SourceAudio get_output_as_nparray method's exception."""
    source_audio = SourceAudio()
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the ``SourceAudio.process\\(\\)`` method.",
    ):
        output = source_audio.get_output_as_nparray()
    assert len(output) == 0


@patch("matplotlib.pyplot.show")
def test_source_audio_plot(dpf_sound_test_server):
    """Test SourceAudio plot method."""
    source_audio = SourceAudio(pytest.data_path_flute_nonUnitaryCalib_in_container)
    source_audio.process()
    source_audio.plot()


@patch("matplotlib.pyplot.show")
def test_source_audio_plot_no_name(dpf_sound_test_server):
    """Test SourceAudio plot method."""
    source_audio = SourceAudio(pytest.data_path_flute_nonUnitaryCalib_in_container)
    source_audio.source_audio_data.name = ""
    source_audio.process()
    source_audio.plot()


def test_source_audio_plot_exceptions(dpf_sound_test_server):
    """Test SourceAudio plot method's exception."""
    source_audio = SourceAudio()
    with pytest.raises(
        PyAnsysSoundException,
        match="Output is not processed yet. Use the ``SourceAudio.process\\(\\)`` method.",
    ):
        source_audio.plot()
