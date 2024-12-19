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
import numpy as np
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ansys.sound.core.sound_composer import SoundComposer, Track

REF_ACOUSTIC_POWER = 4e-10

EXP_STR_NOT_SET = "Sound Composer object (0 track(s))"
EXP_STR_ALL_SET = (
    "Sound Composer object (7 track(s))\n\tTrack 1: SourceAudio, Audio, gain = +0.0 dB"
)


def test_sound_composer_instantiation_no_arg():
    """Test SoundComposer instantiation without arguments."""
    # Test instantiation.
    sound_composer = SoundComposer()
    assert isinstance(sound_composer, SoundComposer)
    assert len(sound_composer.tracks) == 0


def test_sound_composer_instantiation_all_args():
    """Test SoundComposer instantiation with all arguments."""
    # Test instantiation.
    sound_composer = SoundComposer(
        project_path=pytest.data_path_sound_composer_project_in_container
    )
    assert isinstance(sound_composer, SoundComposer)
    assert len(sound_composer.tracks) == 7
    # TODO: added tests for each track's source type, and other attributes.


def test_sound_composer___str___not_set():
    """Test SoundComposer __str__ method when nothing is set."""
    sound_composer = SoundComposer()
    assert str(sound_composer) == EXP_STR_NOT_SET


def test_sound_composer___str___all_set():
    """Test SoundComposer __str__ method when all data are set."""
    sound_composer = SoundComposer(
        project_path=pytest.data_path_sound_composer_project_in_container
    )
    assert str(sound_composer) == EXP_STR_ALL_SET
    # TODO: fix the expected string.


def test_sound_composer_properties():
    """Test SoundComposer properties."""
    sound_composer = SoundComposer()

    # Test tracks property.
    sound_composer.tracks = [Track()]
    assert len(sound_composer.tracks) == 1
    assert isinstance(sound_composer.tracks[0], Track)


def test_sound_composer_add_track():
    """Test SoundComposer add_track method."""
    sound_composer = SoundComposer()
    sound_composer.add_track(Track())
    assert len(sound_composer.tracks) == 1
    assert isinstance(sound_composer.tracks[0], Track)


def test_sound_composer_add_track_exception():
    """Test SoundComposer add_track method's exception."""
    sound_composer = SoundComposer()
    with pytest.raises(PyAnsysSoundException, match="Input track object must be of type Track."):
        sound_composer.add_track("InvalidType")


def test_sound_composer_load():
    """Test SoundComposer load method."""
    sound_composer = SoundComposer()
    sound_composer.load(project_path=pytest.data_path_sound_composer_project_in_container)
    assert len(sound_composer.tracks) == 7
    assert isinstance(sound_composer.tracks[0], Track)
    # TODO: add same tests as in instantiation


def test_sound_composer_process():
    """Test SoundComposer process method (resample needed)."""
    sound_composer = SoundComposer(
        project_path=pytest.data_path_sound_composer_project_in_container
    )
    sound_composer.process()
    assert sound_composer._output is not None


def test_sound_composer_process_warning():
    """Test SoundComposer process method's warning."""
    sound_composer = SoundComposer()
    with pytest.warns(
        PyAnsysSoundWarning,
        match=(
            "There are no track to process. Use SoundComposer.add_track\\(\\) or "
            "SoundComposer.load\\(\\)."
        ),
    ):
        sound_composer.process()
    assert sound_composer._output is None


def test_sound_composer_get_output():
    """Test SoundComposer get_output method."""
    sound_composer = SoundComposer(
        project_path=pytest.data_path_sound_composer_project_in_container
    )
    sound_composer.process()
    output = sound_composer.get_output()
    assert isinstance(output, Field)
    # TODO: add test on output's PSD (cf. source test classes).


def test_sound_composer_get_output_warning():
    """Test SoundComposer get_output method's exception."""
    sound_composer = SoundComposer()
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the SoundComposer.process\\(\\) method.",
    ):
        output = sound_composer.get_output()
    assert output is None


def test_sound_composer_get_output_as_nparray():
    """Test SoundComposer get_output_as_nparray method."""
    sound_composer = SoundComposer(
        project_path=pytest.data_path_sound_composer_project_in_container
    )
    sound_composer.process()
    output = sound_composer.get_output_as_nparray()
    assert isinstance(output, np.ndarray)


def test_sound_composer_get_output_as_nparray_warning():
    """Test SoundComposer get_output_as_nparray method's exception."""
    sound_composer = SoundComposer()
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the SoundComposer.process\\(\\) method.",
    ):
        output = sound_composer.get_output_as_nparray()
    assert len(output) == 0


@patch("matplotlib.pyplot.show")
def test_sound_composer_plot(mock_show):
    """Test SoundComposer plot method."""
    sound_composer = SoundComposer(
        project_path=pytest.data_path_sound_composer_project_in_container
    )
    sound_composer.process()
    sound_composer.plot()


def test_sound_composer_plot_exception():
    """Test SoundComposer plot method's exception."""
    sound_composer = SoundComposer()
    with pytest.raises(
        PyAnsysSoundException,
        match="Output is not processed yet. Use the SoundComposer.process\\(\\) method.",
    ):
        sound_composer.plot()
