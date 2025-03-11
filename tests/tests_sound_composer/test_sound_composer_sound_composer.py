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
from ansys.sound.core.sound_composer import (
    SoundComposer,
    SourceAudio,
    SourceBroadbandNoise,
    SourceBroadbandNoiseTwoParameters,
    SourceHarmonics,
    SourceHarmonicsTwoParameters,
    SourceSpectrum,
    Track,
)
from ansys.sound.core.spectral_processing.power_spectral_density import PowerSpectralDensity

REF_ACOUSTIC_POWER = 4e-10

EXP_LEVEL_OCTAVE_BAND = [71.9, 78.7, 66.2]
EXP_STR_NOT_SET = "Sound Composer object (0 track(s))"
EXP_STR_ALL_SET = (
    "Sound Composer object (7 track(s))\n"
    '\tTrack 1: SourceBroadbandNoise, "BBN", gain = +0.0 dB\n'
    '\tTrack 2: SourceSpectrum, "Spectrum", gain = +0.0 dB\n'
    '\tTrack 3: SourceAudio, "Audio", gain = +10.0 dB\n'
    '\tTrack 4: SourceBroadbandNoiseTwoParameters, "BBN2Params", gain = +0.0 dB\n'
    '\tTrack 5: SourceHarmonics, "Harmo", gain = +0.0 dB\n'
    '\tTrack 6: SourceHarmonicsTwoParameters, "Harmo2Params", gain = +0.0 dB\n'
    '\tTrack 7: SourceHarmonicsTwoParameters, "Harmo2ParamsRpmAsSecondParam", gain = +0.0 dB'
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
    assert isinstance(sound_composer.tracks[0].source, SourceBroadbandNoise)
    assert sound_composer.tracks[0].name == "BBN"
    assert sound_composer.tracks[0].gain == 0.0
    assert sound_composer.tracks[0].filter is None
    assert isinstance(sound_composer.tracks[1].source, SourceSpectrum)
    assert sound_composer.tracks[1].name == "Spectrum"
    assert sound_composer.tracks[1].gain == 0.0
    assert sound_composer.tracks[1].filter is None
    assert isinstance(sound_composer.tracks[2].source, SourceAudio)
    assert sound_composer.tracks[2].name == "Audio"
    assert sound_composer.tracks[2].gain == 10.0
    assert sound_composer.tracks[2].filter is not None
    assert isinstance(sound_composer.tracks[3].source, SourceBroadbandNoiseTwoParameters)
    assert sound_composer.tracks[3].name == "BBN2Params"
    assert sound_composer.tracks[3].gain == 0.0
    assert sound_composer.tracks[3].filter is None
    assert isinstance(sound_composer.tracks[4].source, SourceHarmonics)
    assert sound_composer.tracks[4].name == "Harmo"
    assert sound_composer.tracks[4].gain == 0.0
    assert sound_composer.tracks[4].filter is None
    assert isinstance(sound_composer.tracks[5].source, SourceHarmonicsTwoParameters)
    assert sound_composer.tracks[5].name == "Harmo2Params"
    assert sound_composer.tracks[5].gain == 0.0
    assert sound_composer.tracks[5].filter is None
    assert isinstance(sound_composer.tracks[6].source, SourceHarmonicsTwoParameters)
    assert sound_composer.tracks[6].name == "Harmo2ParamsRpmAsSecondParam"
    assert sound_composer.tracks[6].gain == 0.0
    assert sound_composer.tracks[6].filter is None


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


def test_sound_composer_properties():
    """Test SoundComposer properties."""
    sound_composer = SoundComposer()

    # Test tracks property.
    sound_composer.tracks = [Track()]
    assert len(sound_composer.tracks) == 1
    assert isinstance(sound_composer.tracks[0], Track)


def test_sound_composer_properties_exception():
    """Test SoundComposer properties' exception."""
    sound_composer = SoundComposer()
    with pytest.raises(
        PyAnsysSoundException,
        match="Each item in the track list must be of type `Track`.",
    ):
        sound_composer.tracks = ["InvalidType"]


def test_sound_composer_add_track():
    """Test SoundComposer add_track method."""
    sound_composer = SoundComposer()
    sound_composer.add_track(Track())
    assert len(sound_composer.tracks) == 1
    assert isinstance(sound_composer.tracks[0], Track)


def test_sound_composer_add_track_exception():
    """Test SoundComposer add_track method's exception."""
    sound_composer = SoundComposer()
    with pytest.raises(PyAnsysSoundException, match="Input track object must be of type `Track`."):
        sound_composer.add_track("InvalidType")


def test_sound_composer_load():
    """Test SoundComposer load method."""
    sound_composer = SoundComposer()
    sound_composer.load(project_path=pytest.data_path_sound_composer_project_in_container)

    assert isinstance(sound_composer, SoundComposer)
    assert len(sound_composer.tracks) == 7
    assert isinstance(sound_composer.tracks[0].source, SourceBroadbandNoise)
    assert sound_composer.tracks[0].name == "BBN"
    assert sound_composer.tracks[0].gain == 0.0
    assert sound_composer.tracks[0].filter is None
    assert isinstance(sound_composer.tracks[1].source, SourceSpectrum)
    assert sound_composer.tracks[1].name == "Spectrum"
    assert sound_composer.tracks[1].gain == 0.0
    assert sound_composer.tracks[1].filter is None
    assert isinstance(sound_composer.tracks[2].source, SourceAudio)
    assert sound_composer.tracks[2].name == "Audio"
    assert sound_composer.tracks[2].gain == 10.0
    assert sound_composer.tracks[2].filter is not None
    assert isinstance(sound_composer.tracks[3].source, SourceBroadbandNoiseTwoParameters)
    assert sound_composer.tracks[3].name == "BBN2Params"
    assert sound_composer.tracks[3].gain == 0.0
    assert sound_composer.tracks[3].filter is None
    assert isinstance(sound_composer.tracks[4].source, SourceHarmonics)
    assert sound_composer.tracks[4].name == "Harmo"
    assert sound_composer.tracks[4].gain == 0.0
    assert sound_composer.tracks[4].filter is None
    assert isinstance(sound_composer.tracks[5].source, SourceHarmonicsTwoParameters)
    assert sound_composer.tracks[5].name == "Harmo2Params"
    assert sound_composer.tracks[5].gain == 0.0
    assert sound_composer.tracks[5].filter is None
    assert isinstance(sound_composer.tracks[6].source, SourceHarmonicsTwoParameters)
    assert sound_composer.tracks[6].name == "Harmo2ParamsRpmAsSecondParam"
    assert sound_composer.tracks[6].gain == 0.0
    assert sound_composer.tracks[6].filter is None


def test_sound_composer_save():
    """Test SoundComposer save method."""
    sound_composer = SoundComposer(
        project_path=pytest.data_path_sound_composer_project_in_container
    )
    path_to_save = pytest.temporary_folder + "/test_sound_composer_save.scn"
    sound_composer.save(project_path=path_to_save)


def test_sound_composer_save_load_warnings():
    """Test SoundComposer load & save methods' warnings."""
    sound_composer = SoundComposer()

    with pytest.warns(
        PyAnsysSoundWarning,
        match=(
            "There are no tracks to save. The saved project will be empty. To add tracks before "
            "saving the project, use `SoundComposer.tracks`, `SoundComposer.add_track\\(\\)` or "
            "`SoundComposer.load\\(\\)`."
        ),
    ):
        sound_composer.save(project_path=pytest.temporary_folder + "/test_sound_composer_save.scn")

    with pytest.warns(
        PyAnsysSoundWarning,
        match="The project file `test_sound_composer_save.scn` does not contain any track.",
    ):
        sound_composer.load(project_path=pytest.temporary_folder + "/test_sound_composer_save.scn")
    assert len(sound_composer.tracks) == 0


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
            "There are no tracks to process. Use `SoundComposer.tracks`, "
            "`SoundComposer.add_track\\(\\)` or `SoundComposer.load\\(\\)`."
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

    # Compute the power spectral density over the output signal.
    psd = PowerSpectralDensity(
        input_signal=output,
        fft_size=8192,
        window_type="HANN",
        window_length=8192,
        overlap=0.75,
    )
    psd.process()
    psd_squared, psd_freq = psd.get_PSD_squared_linear_as_nparray()
    delat_f = psd_freq[1] - psd_freq[0]

    # Check the sound power level in the octave bands centered at 250, 1000 and 4000 Hz.
    # Due to the non-deterministic nature of the produced signal, tolerance is set to 3 dB.
    psd_squared_band = psd_squared[
        (psd_freq >= 250 * 2 ** (-1 / 2)) & (psd_freq < 250 * 2 ** (1 / 2))
    ]
    level = 10 * np.log10(psd_squared_band.sum() * delat_f / REF_ACOUSTIC_POWER)
    assert level == pytest.approx(EXP_LEVEL_OCTAVE_BAND[0], abs=3.0)

    psd_squared_band = psd_squared[
        (psd_freq >= 1000 * 2 ** (-1 / 2)) & (psd_freq < 1000 * 2 ** (1 / 2))
    ]
    level = 10 * np.log10(psd_squared_band.sum() * delat_f / REF_ACOUSTIC_POWER)
    assert level == pytest.approx(EXP_LEVEL_OCTAVE_BAND[1], abs=3.0)

    psd_squared_band = psd_squared[
        (psd_freq >= 4000 * 2 ** (-1 / 2)) & (psd_freq < 4000 * 2 ** (1 / 2))
    ]
    level = 10 * np.log10(psd_squared_band.sum() * delat_f / REF_ACOUSTIC_POWER)
    assert level == pytest.approx(EXP_LEVEL_OCTAVE_BAND[2], abs=3.0)


def test_sound_composer_get_output_warning():
    """Test SoundComposer get_output method's exception."""
    sound_composer = SoundComposer()
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the `SoundComposer.process\\(\\)` method.",
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
        match="Output is not processed yet. Use the `SoundComposer.process\\(\\)` method.",
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
        match="Output is not processed yet. Use the `SoundComposer.process\\(\\)` method.",
    ):
        sound_composer.plot()
