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

from ansys.dpf.core import Field, GenericDataContainer
import numpy as np
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ansys.sound.core.signal_utilities.load_wav import LoadWav
from ansys.sound.core.sound_composer import SourceAudio

EXP_AUDIO_DATA17640 = -0.5416082739830017
EXP_STR_NOT_SET = "Audio source: Not set"
EXP_STR_ALL_SET = "Audio source: 'flute'\n\tDuration: 3.5 s\n\tSampling frequency: 44100.0 Hz"
EXP_STR_EMPTY_AUDIO = "Audio source: 'flute'\n\tDuration: N/A\n\tSampling frequency: N/A"


def test_source_audio_instantiation_no_arg():
    """Test SourceAudio instantiation without arguments."""
    # Test instantiation.
    source_audio = SourceAudio()
    assert isinstance(source_audio, SourceAudio)
    assert source_audio.source_audio_data is None


def test_source_audio_instantiation_wav_file():
    """Test SourceAudio instantiation with file argument."""
    # Test instantiation.
    source_audio = SourceAudio(pytest.data_path_flute_nonUnitaryCalib_in_container)
    assert isinstance(source_audio, SourceAudio)
    assert source_audio.source_audio_data is not None


def test_source_audio_instantiation_txt_file():
    """Test SourceAudio instantiation with file argument."""
    # Test instantiation.
    source_audio = SourceAudio(pytest.data_path_flute_nonUnitaryCalib_as_txt_in_container)
    assert isinstance(source_audio, SourceAudio)
    assert source_audio.source_audio_data is not None


def test_source_audio___str___not_set():
    """Test SourceAudio __str__ method when nothing is set."""
    source_audio = SourceAudio()
    assert str(source_audio) == EXP_STR_NOT_SET


def test_source_audio___str___all_set():
    """Test SourceAudio __str__ method when all data are set."""
    source_audio = SourceAudio(pytest.data_path_flute_nonUnitaryCalib_in_container)
    assert str(source_audio) == EXP_STR_ALL_SET


def test_source_audio___str___empty_audio():
    """Test SourceAudio __str__ method when all data are set."""
    source_audio = SourceAudio(pytest.data_path_flute_nonUnitaryCalib_in_container)
    source_audio.source_audio_data.data = []
    source_audio.source_audio_data.time_freq_support.time_frequencies.data = []
    assert str(source_audio) == EXP_STR_EMPTY_AUDIO


def test_source_audio_properties():
    """Test SourceAudio properties."""
    source_audio = SourceAudio()

    # Test source_audio_data property.
    source_audio.source_audio_data = Field()
    assert isinstance(source_audio.source_audio_data, Field)


def test_source_audio_propertiess_exceptions():
    """Test SourceAudio properties' exceptions."""
    source_audio = SourceAudio()

    # Test source_audio_data setter exception (str instead a Field).
    with pytest.raises(
        PyAnsysSoundException, match="Specified audio source data must be provided as a DPF field."
    ):
        source_audio.source_audio_data = "InvalidType"


def test_source_audio_load_from_wave_file():
    """Test SourceAudio load_source_audio_from_text method."""
    source_audio = SourceAudio()
    source_audio.load_from_wave_file(pytest.data_path_flute_nonUnitaryCalib_in_container)
    assert isinstance(source_audio.source_audio_data, Field)
    assert source_audio.source_audio_data.data[17640] == pytest.approx(
        EXP_AUDIO_DATA17640, rel=1e-3
    )


def test_source_audio_load_from_text_file():
    """Test SourceAudio load_source_audio_from_text method."""
    source_audio = SourceAudio()
    source_audio.load_from_text_file(pytest.data_path_flute_nonUnitaryCalib_as_txt_in_container)
    assert isinstance(source_audio.source_audio_data, Field)
    assert source_audio.source_audio_data.data[17640] == pytest.approx(
        EXP_AUDIO_DATA17640, rel=1e-3
    )


def test_source_audio_set_from_generic_data_containers():
    """Test SourceAudio set_from_generic_data_containers method."""
    loader = LoadWav(path_to_wav=pytest.data_path_flute_nonUnitaryCalib_in_container)
    loader.process()
    f_data: Field = loader.get_output()[0]

    source_data = GenericDataContainer()
    source_data.set_property("sound_composer_source", f_data)

    source_audio = SourceAudio()
    source_audio.set_from_generic_data_containers(source_data, None)
    assert isinstance(source_audio.source_audio_data, Field)
    assert len(source_audio.source_audio_data.data) == len(f_data.data)
    assert source_audio.source_audio_data.data[17640] == pytest.approx(EXP_AUDIO_DATA17640)


def test_source_audio_get_as_generic_data_containers():
    """Test SourceAudio get_as_generic_data_containers method."""
    # Source data undefined => warning.
    source_audio = SourceAudio()
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Cannot create source generic data container because there is no source data.",
    ):
        source_data, _ = source_audio.get_as_generic_data_containers()
    assert source_data is None

    # Source data is defined.
    source_audio.load_from_wave_file(
        pytest.data_path_flute_nonUnitaryCalib_in_container,
    )
    source_data, source_control_data = source_audio.get_as_generic_data_containers()

    assert isinstance(source_data, GenericDataContainer)
    assert isinstance(source_data.get_property("sound_composer_source"), Field)
    assert source_control_data is None


def test_source_audio_process_no_resample():
    """Test SourceAudio process method (no resample needed)."""
    source_audio = SourceAudio(pytest.data_path_flute_nonUnitaryCalib_in_container)
    source_audio.process()
    assert source_audio._output is not None


def test_source_audio_process_resample():
    """Test SourceAudio process method (resample)."""
    source_audio = SourceAudio(pytest.data_path_flute_nonUnitaryCalib_in_container)
    source_audio.process(48000)
    assert source_audio._output is not None


def test_source_audio_process_exceptions():
    """Test SourceAudio process method exceptions."""
    # Test process method exception1 (missing audio).
    source_audio = SourceAudio()
    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "Source's audio data is not set. Use ``SourceAudio.source_audio_data`` "
            "or method ``SourceAudio.load_source_audio_from_text\\(\\)``."
        ),
    ):
        source_audio.process()

    # Test process method exception2 (invalid sampling frequency value).
    source_audio = SourceAudio()
    with pytest.raises(
        PyAnsysSoundException, match="Sampling frequency must be strictly positive."
    ):
        source_audio.process(sampling_frequency=0.0)


def test_source_audio_get_output():
    """Test SourceAudio get_output method."""
    source_audio = SourceAudio(pytest.data_path_flute_nonUnitaryCalib_in_container)
    source_audio.process(sampling_frequency=44100.0)

    output_signal = source_audio.get_output()
    time = output_signal.time_freq_support.time_frequencies.data
    fs = 1.0 / (time[1] - time[0])
    assert isinstance(output_signal, Field)
    assert fs == pytest.approx(44100.0)
    assert output_signal.data[17640] == pytest.approx(EXP_AUDIO_DATA17640)


def test_source_audio_get_output_unprocessed():
    """Test SourceAudio get_output method's exception."""
    source_audio = SourceAudio()
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the ``SourceAudio.process\\(\\)`` method.",
    ):
        output = source_audio.get_output()
    assert output is None


def test_source_audio_get_output_as_nparray():
    """Test SourceAudio get_output_as_nparray method."""
    source_audio = SourceAudio(pytest.data_path_flute_nonUnitaryCalib_in_container)
    source_audio.process(sampling_frequency=44100.0)

    output_signal = source_audio.get_output_as_nparray()
    assert isinstance(output_signal, np.ndarray)
    assert output_signal[17640] == pytest.approx(EXP_AUDIO_DATA17640)


def test_source_audio_get_output_as_nparray_unprocessed():
    """Test SourceAudio get_output_as_nparray method's exception."""
    source_audio = SourceAudio()
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the ``SourceAudio.process\\(\\)`` method.",
    ):
        output = source_audio.get_output_as_nparray()
    assert len(output) == 0


@patch("matplotlib.pyplot.show")
def test_source_audio_plot(mock_show):
    """Test SourceAudio plot method."""
    source_audio = SourceAudio(pytest.data_path_flute_nonUnitaryCalib_in_container)
    source_audio.process()
    source_audio.plot()


@patch("matplotlib.pyplot.show")
def test_source_audio_plot_no_name(mock_show):
    """Test SourceAudio plot method."""
    source_audio = SourceAudio(pytest.data_path_flute_nonUnitaryCalib_in_container)
    source_audio.source_audio_data.name = ""
    source_audio.process()
    source_audio.plot()


def test_source_audio_plot_exceptions():
    """Test SourceAudio plot method's exception."""
    source_audio = SourceAudio()
    with pytest.raises(
        PyAnsysSoundException,
        match="Output is not processed yet. Use the ``SourceAudio.process\\(\\)`` method.",
    ):
        source_audio.plot()
