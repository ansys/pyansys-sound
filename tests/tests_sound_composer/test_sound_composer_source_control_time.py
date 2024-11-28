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

from ansys.dpf.core import Field
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundException
from ansys.sound.core.signal_utilities.load_wav import LoadWav
from ansys.sound.core.sound_composer import SourceControlTime

EXP_STR_ALL_SET = "Unit: \nDuration: 20.6 s\nMin - max: 968.8 - 4821.3 "
EXP_STR_NOT_SET = "Not set"


def test_source_control_time_instantiation_no_file(dpf_sound_test_server):
    """Test SourceControlTime instantiation."""
    # Test instantiation.
    control_time = SourceControlTime()
    assert isinstance(control_time, SourceControlTime)


def test_source_control_time_instantiation_wav_file(dpf_sound_test_server):
    """Test SourceControlTime instantiation."""
    # Test instantiation.
    control_time = SourceControlTime(pytest.data_path_rpm_profile_as_wav_in_container)
    assert isinstance(control_time, SourceControlTime)


def test_source_control_time_instantiation_txt_file(dpf_sound_test_server):
    """Test SourceControlTime instantiation."""
    # Test instantiation.
    control_time = SourceControlTime(pytest.data_path_rpm_profile_as_txt_in_container)
    assert isinstance(control_time, SourceControlTime)


def test_source_control_time_properties(dpf_sound_test_server):
    """Test SourceControlTime properties."""
    control_time = SourceControlTime()
    loader = LoadWav(pytest.data_path_rpm_profile_as_wav_in_container)
    loader.process()
    control = loader.get_output()[0]

    # Test control setter.
    control_time.control = control
    assert isinstance(control_time.control, Field)
    assert len(control_time.control.data) > 0


def test_source_control_time_propertiess_exceptions(dpf_sound_test_server):
    """Test SourceControlTime properties' exceptions."""
    control_time = SourceControlTime()

    # Test control setter exception 1 (wrong control type).
    with pytest.raises(
        PyAnsysSoundException,
        match="Specified control profile must be provided as a DPF field.",
    ):
        control_time.control = "WrongType"

    # Test control setter exception 2 (empty control).
    with pytest.raises(
        PyAnsysSoundException,
        match="Specified control profile must have at least one element.",
    ):
        control_time.control = Field()


def test_source_control_time___str__(dpf_sound_test_server):
    """Test SourceControlTime __str__ method."""
    control_time = SourceControlTime(pytest.data_path_rpm_profile_as_wav_in_container)
    assert str(control_time) == EXP_STR_ALL_SET


def test_source_control_time___str___not_set(dpf_sound_test_server):
    """Test SourceControlTime __str__ method."""
    control_time = SourceControlTime()
    assert str(control_time) == EXP_STR_NOT_SET


def test_source_control_time_load_from_wave_file(dpf_sound_test_server):
    """Test SourceControlTime load_from_wave_file method."""
    control_time = SourceControlTime()
    control_time.load_from_wave_file(pytest.data_path_rpm_profile_as_wav_in_container)
    assert isinstance(control_time.control, Field)


def test_source_control_time_load_from_text_file(dpf_sound_test_server):
    """Test SourceControlTime load_from_text_file method."""
    control_time = SourceControlTime()
    control_time.load_from_text_file(pytest.data_path_rpm_profile_as_txt_in_container)
    assert isinstance(control_time.control, Field)


@patch("matplotlib.pyplot.show")
def test_source_audio_plot(dpf_sound_test_server):
    """Test SourceAudio plot method."""
    source_audio = SourceControlTime(pytest.data_path_rpm_profile_as_txt_in_container)
    source_audio.plot()
