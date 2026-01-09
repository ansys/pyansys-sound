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

from ansys.dpf.core import Field
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ansys.sound.core.psychoacoustics import LoudnessANSI_S3_4
from ansys.sound.core.signal_utilities import LoadWav

EXP_LOUDNESS_FREE = 58.98927
EXP_LOUDNESS_LEVEL_FREE = 97.42931
EXP_LOUDNESS_DIFFUSE = 59.16265
EXP_LOUDNESS_LEVEL_DIFFUSE = 97.46850
EXP_STR_DEFAULT = (
    "LoudnessANSI_S3_4 object\nData:\n\tSignal name: Not set\n\tField type: Free\n"
    "Loudness: Not processed\nLoudness level: Not processed"
)
EXP_STR = (
    'LoudnessANSI_S3_4 object\nData:\n\tSignal name: "flute"\n\tField type: Diffuse\n'
    "Loudness: 59.2 sones\nLoudness level: 97.5 phons"
)


def test_loudness_ansi_s3_4_instantiation():
    """Test instantiation of LoudnessANSI_S3_4 class."""
    loudness_computer = LoudnessANSI_S3_4()
    assert loudness_computer.signal is None
    assert loudness_computer.field_type == "Free"


def test_loudness_ansi_s3_4___str__():
    """Test string representation of LoudnessANSI_S3_4 class."""
    loudness_computer = LoudnessANSI_S3_4()
    assert str(loudness_computer) == EXP_STR_DEFAULT

    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()

    loudness_computer.signal = fc[0]
    loudness_computer.field_type = "Diffuse"
    loudness_computer.process()
    assert str(loudness_computer) == EXP_STR


def test_loudness_ansi_s3_4_properties():
    """Test properties of LoudnessANSI_S3_4 class."""
    loudness_computer = LoudnessANSI_S3_4()

    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()

    loudness_computer.signal = fc[0]
    assert isinstance(loudness_computer.signal, Field)

    loudness_computer.field_type = "Diffuse"
    assert loudness_computer.field_type == "Diffuse"


def test_loudness_ansi_s3_4_properties_exceptions():
    """Test exceptions of LoudnessANSI_S3_4 class."""
    loudness_computer = LoudnessANSI_S3_4()

    with pytest.raises(PyAnsysSoundException, match="Signal must be specified as a DPF field."):
        loudness_computer.signal = "WrongType"

    with pytest.raises(
        PyAnsysSoundException,
        match='Invalid field type "InvalidFieldType". Available options are "Free" and "Diffuse".',
    ):
        loudness_computer.field_type = "InvalidFieldType"


def test_loudness_ansi_s3_4_process():
    """Test process method of LoudnessANSI_S3_4 class."""
    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()

    loudness_computer = LoudnessANSI_S3_4(signal=fc[0])
    loudness_computer.process()
    assert loudness_computer._output is not None


def test_loudness_ansi_s3_4_process_exceptions():
    """Test exceptions of LoudnessANSI_S3_4 class."""
    loudness_computer = LoudnessANSI_S3_4()

    with pytest.raises(
        PyAnsysSoundException,
        match="Signal is not set. Use `LoudnessANSI_S3_4.signal`.",
    ):
        loudness_computer.process()


def test_loudness_ansi_s3_4_get_output():
    """Test get_output method of LoudnessANSI_S3_4 class."""
    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()

    loudness_computer = LoudnessANSI_S3_4(signal=fc[0], field_type="Free")
    loudness_computer.process()
    loudness, loudness_level = loudness_computer.get_output()
    assert loudness == pytest.approx(EXP_LOUDNESS_FREE)
    assert loudness_level == pytest.approx(EXP_LOUDNESS_LEVEL_FREE)

    loudness_computer.field_type = "Diffuse"
    loudness_computer.process()
    loudness, loudness_level = loudness_computer.get_output()
    assert loudness == pytest.approx(EXP_LOUDNESS_DIFFUSE)
    assert loudness_level == pytest.approx(EXP_LOUDNESS_LEVEL_DIFFUSE)


def test_loudness_ansi_s3_4_get_output_warning():
    """Test exceptions of LoudnessANSI_S3_4 class."""
    loudness_computer = LoudnessANSI_S3_4()

    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the `LoudnessANSI_S3_4.process\\(\\)` method.",
    ):
        loudness_computer.get_output()


def test_loudness_ansi_s3_4_get_output_as_nparray():
    """Test get_output_as_nparray method of LoudnessANSI_S3_4 class."""
    loudness_computer = LoudnessANSI_S3_4()

    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the `LoudnessANSI_S3_4.process\\(\\)` method.",
    ):
        loudness, loudness_level = loudness_computer.get_output_as_nparray()
    assert len(loudness) == 0
    assert len(loudness_level) == 0

    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()

    loudness_computer.signal = fc[0]
    loudness_computer.field_type = "Free"
    loudness_computer.process()
    loudness, loudness_level = loudness_computer.get_output_as_nparray()
    assert loudness == pytest.approx(EXP_LOUDNESS_FREE)
    assert loudness_level == pytest.approx(EXP_LOUDNESS_LEVEL_FREE)

    loudness_computer.field_type = "Diffuse"
    loudness_computer.process()
    loudness, loudness_level = loudness_computer.get_output_as_nparray()
    assert loudness == pytest.approx(EXP_LOUDNESS_DIFFUSE)
    assert loudness_level == pytest.approx(EXP_LOUDNESS_LEVEL_DIFFUSE)


def test_loudness_ansi_s3_4_get_loudness_sone():
    """Test get_loudness_sone method of LoudnessANSI_S3_4 class."""
    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()

    loudness_computer = LoudnessANSI_S3_4(signal=fc[0], field_type="Free")

    loudness_computer.process()
    assert loudness_computer.get_loudness_sone() == pytest.approx(EXP_LOUDNESS_FREE)

    loudness_computer.field_type = "Diffuse"
    loudness_computer.process()
    assert loudness_computer.get_loudness_sone() == pytest.approx(EXP_LOUDNESS_DIFFUSE)


def test_loudness_ansi_s3_4_get_loudness_level_phon():
    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()

    loudness_computer = LoudnessANSI_S3_4(signal=fc[0], field_type="Free")

    loudness_computer.process()
    assert loudness_computer.get_loudness_level_phon() == pytest.approx(EXP_LOUDNESS_LEVEL_FREE)

    loudness_computer.field_type = "Diffuse"
    loudness_computer.process()
    assert loudness_computer.get_loudness_level_phon() == pytest.approx(EXP_LOUDNESS_LEVEL_DIFFUSE)
