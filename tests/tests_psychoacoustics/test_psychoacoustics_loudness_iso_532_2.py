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
from ansys.sound.core.psychoacoustics import LoudnessISO532_2
from ansys.sound.core.signal_utilities import LoadWav

# Expected values for Acceleration_stereo_nonUnitaryCalib, in Free/Mic conditions
EXP_BIN_LOUDNESS_DICHOTIC_FREE_MIC = 18.90975
EXP_BIN_LOUDNESS_LEVEL_DICHOTIC_FREE_MIC = 82.25344
EXP_MON_LOUDNESS_DICHOTIC_FREE_MIC_LEFT = 9.673014
EXP_MON_LOUDNESS_DICHOTIC_FREE_MIC_RIGHT = 14.93052
EXP_MON_LOUDNESS_LEVEL_DICHOTIC_FREE_MIC_LEFT = 72.58388
EXP_MON_LOUDNESS_LEVEL_DICHOTIC_FREE_MIC_RIGHT = 79.05491
EXP_BIN_SPECIFIC_LOUDNESS_DICHOTIC_FREE_MIC_0 = 0.3092778
EXP_BIN_SPECIFIC_LOUDNESS_DICHOTIC_FREE_MIC_45 = 1.656872
EXP_BIN_SPECIFIC_LOUDNESS_DICHOTIC_FREE_MIC_98 = 0.6377245
EXP_MON_SPECIFIC_LOUDNESS_DICHOTIC_FREE_MIC_L_0 = 0.1548998
EXP_MON_SPECIFIC_LOUDNESS_DICHOTIC_FREE_MIC_L_45 = 0.8625394
EXP_MON_SPECIFIC_LOUDNESS_DICHOTIC_FREE_MIC_L_98 = 0.3725382
EXP_MON_SPECIFIC_LOUDNESS_DICHOTIC_FREE_MIC_R_0 = 0.2467274
EXP_MON_SPECIFIC_LOUDNESS_DICHOTIC_FREE_MIC_R_45 = 1.298307
EXP_MON_SPECIFIC_LOUDNESS_DICHOTIC_FREE_MIC_R_98 = 0.4703090

# Expected values for Acceleration_stereo_nonUnitaryCalib, in Diffuse/Mic conditions
EXP_BIN_LOUDNESS_DICHOTIC_DIFFUSE_MIC = 18.86968
EXP_BIN_LOUDNESS_LEVEL_DICHOTIC_DIFFUSE_MIC = 82.22441
EXP_MON_LOUDNESS_DICHOTIC_DIFFUSE_MIC_LEFT = 9.641939
EXP_MON_LOUDNESS_DICHOTIC_DIFFUSE_MIC_RIGHT = 14.90496
EXP_BIN_SPECIFIC_LOUDNESS_DICHOTIC_DIFFUSE_MIC_0 = 0.3092621
EXP_BIN_SPECIFIC_LOUDNESS_DICHOTIC_DIFFUSE_MIC_45 = 1.639453
EXP_BIN_SPECIFIC_LOUDNESS_DICHOTIC_DIFFUSE_MIC_98 = 0.6317677

# Expected values for Acceleration_stereo_nonUnitaryCalib, in Head condition (field type irrelevant)
EXP_BIN_LOUDNESS_DICHOTIC_HEAD = 14.52840
EXP_BIN_LOUDNESS_LEVEL_DICHOTIC_HEAD = 78.61783
EXP_MON_LOUDNESS_DICHOTIC_HEAD_LEFT = 7.324051
EXP_MON_LOUDNESS_DICHOTIC_HEAD_RIGHT = 11.53435
EXP_BIN_SPECIFIC_LOUDNESS_DICHOTIC_HEAD_0 = 0.3093223
EXP_BIN_SPECIFIC_LOUDNESS_DICHOTIC_HEAD_45 = 1.603330
EXP_BIN_SPECIFIC_LOUDNESS_DICHOTIC_HEAD_98 = 0.5659737

# Expected values for flute_nonUnitaryCalib (mono), in Free/Mic conditions
EXP_BIN_LOUDNESS_DIOTIC_FREE_MIC = 58.42287
EXP_BIN_LOUDNESS_LEVEL_DIOTIC_FREE_MIC = 97.44814
EXP_MON_LOUDNESS_DIOTIC_FREE_MIC = 38.94790
EXP_MON_LOUDNESS_LEVEL_DIOTIC_FREE_MIC = 92.04321
EXP_BIN_SPECIFIC_LOUDNESS_DIOTIC_FREE_MIC_0 = 3.350576e-7
EXP_BIN_SPECIFIC_LOUDNESS_DIOTIC_FREE_MIC_45 = 1.477295
EXP_BIN_SPECIFIC_LOUDNESS_DIOTIC_FREE_MIC_98 = 3.738140
EXP_MON_SPECIFIC_LOUDNESS_DIOTIC_FREE_MIC_0 = 2.233678e-7
EXP_MON_SPECIFIC_LOUDNESS_DIOTIC_FREE_MIC_45 = 0.9848462
EXP_MON_SPECIFIC_LOUDNESS_DIOTIC_FREE_MIC_98 = 2.492050

# Expected fc/ERBn values
EXP_ERB_LEN = 372
EXP_ERB_0 = 1.8
EXP_ERB_45 = 6.3
EXP_ERB_98 = 11.6
EXP_FREQ_0 = 49.01015
EXP_FREQ_45 = 222.4797
EXP_FREQ_98 = 570.2265

# Expected string representations
EXP_STR_DEFAULT = (
    "LoudnessISO532_2 object.\nData\n\tSignal name: Not set\n"
    "\tField type: Free\n\tRecording type: Mic (Single microphone)\n"
    "Binaural loudness: Not processed\n"
    "Binaural loudness level: Not processed"
)
EXP_STR_ALLSET = (
    'LoudnessISO532_2 object.\nData\n\tSignal name: "flute"\n'
    "\tListening assumption: Diotic\n"
    "\tField type: Diffuse\n\tRecording type: Head (Head and torso simulator)\n"
    "Binaural loudness: 44.1 sones\n"
    "Binaural loudness level: 93.8 phons"
)


def test_loudness_iso_532_2_instantiation():
    """Test the instantiation of the LoudnessISO532_2 class."""
    loudness_computer = LoudnessISO532_2()
    assert isinstance(loudness_computer, LoudnessISO532_2)
    assert loudness_computer.signal is None
    assert loudness_computer.field_type == "Free"
    assert loudness_computer.recording_type == "Mic"


def test_loudness_iso_532_2_properties():
    """Test the properties of the LoudnessISO532_2 class."""
    loudness_computer = LoudnessISO532_2()

    # Check signal property as a Field
    loudness_computer.signal = Field()
    assert type(loudness_computer.signal) == Field

    # Check signal property as a list of Fields
    loudness_computer.signal = [Field(), Field()]
    assert type(loudness_computer.signal) == list
    assert len(loudness_computer.signal) == 2

    # Check field_type property
    loudness_computer.field_type = "Diffuse"
    assert loudness_computer.field_type == "Diffuse"

    # Check case insensitivity
    loudness_computer.field_type = "diffuse"
    assert loudness_computer.field_type == "diffuse"

    loudness_computer.field_type = "DIFFUSE"
    assert loudness_computer.field_type == "DIFFUSE"

    # Check recording_type property
    loudness_computer.recording_type = "Head"
    assert loudness_computer.recording_type == "Head"

    # Check case insensitivity
    loudness_computer.recording_type = "head"
    assert loudness_computer.recording_type == "head"

    loudness_computer.recording_type = "HEAD"
    assert loudness_computer.recording_type == "HEAD"


def test_loudness_iso_532_2_properties_exceptions():
    """Test the exceptions of the properties of the LoudnessISO532_2 class."""
    loudness_computer = LoudnessISO532_2()

    # Check invalid value for signal property
    with pytest.raises(
        PyAnsysSoundException,
        match="Signal must be specified as a DPF field or a list of exactly 2 DPF fields.",
    ):
        loudness_computer.signal = "WrongType"

    # Check incorrect field number in fields container for signal property
    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "The input signal list must contain exactly 2 fields corresponding to the signals "
            "presented at the two ears."
        ),
    ):
        loudness_computer.signal = []

    # Check invalid value for field_type property
    with pytest.raises(
        PyAnsysSoundException,
        match='Invalid field type "Invalid". Available options are "Free" and "Diffuse".',
    ):
        loudness_computer.field_type = "Invalid"

    # Check invalid value for recording_type property
    with pytest.raises(
        PyAnsysSoundException,
        match='Invalid recording type "Invalid". Available options are "Mic" and "Head".',
    ):
        loudness_computer.recording_type = "Invalid"


def test_loudness_iso_532_2___str__():
    """Test the __str__ method of the LoudnessISO532_2 class."""
    loudness_computer = LoudnessISO532_2()

    assert loudness_computer.__str__() == EXP_STR_DEFAULT

    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()

    loudness_computer.signal = fc[0]
    loudness_computer.field_type = "Diffuse"
    loudness_computer.recording_type = "Head"
    loudness_computer.process()

    assert loudness_computer.__str__() == EXP_STR_ALLSET


def test_loudness_iso_532_2_process():
    """Test the process method of the LoudnessISO532_2 class."""
    loudness_computer = LoudnessISO532_2()

    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()

    loudness_computer.signal = fc[0]

    loudness_computer.process()
    assert loudness_computer._output is not None


def test_loudness_iso_532_2_process_exceptions():
    """Test the exceptions of the process method of the LoudnessISO532_2 class."""
    loudness_computer = LoudnessISO532_2()

    with pytest.raises(
        PyAnsysSoundException,
        match="No input signal set. Use `LoudnessISO532_2.signal`.",
    ):
        loudness_computer.process()


def test_loudness_iso_532_2_get_output_diotic_case():
    """Test the get_output method of the LoudnessISO532_2 class, in the diotic case."""
    loudness_computer = LoudnessISO532_2()

    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()

    # A single signal channel -> Diotic case
    loudness_computer.signal = fc[0]

    loudness_computer.process()

    N_bin, LN_bin, N_mon, LN_mon, Nprime_bin, Nprime_mon = loudness_computer.get_output()
    assert N_bin == pytest.approx(EXP_BIN_LOUDNESS_DIOTIC_FREE_MIC)
    assert LN_bin == pytest.approx(EXP_BIN_LOUDNESS_LEVEL_DIOTIC_FREE_MIC)
    assert len(N_mon) == 1
    assert N_mon[0] == pytest.approx(EXP_MON_LOUDNESS_DIOTIC_FREE_MIC)
    assert len(LN_mon) == 1
    assert LN_mon[0] == pytest.approx(EXP_MON_LOUDNESS_LEVEL_DIOTIC_FREE_MIC)
    assert len(Nprime_bin) == EXP_ERB_LEN
    assert Nprime_bin.data[0] == pytest.approx(EXP_BIN_SPECIFIC_LOUDNESS_DIOTIC_FREE_MIC_0)
    assert Nprime_bin.data[45] == pytest.approx(EXP_BIN_SPECIFIC_LOUDNESS_DIOTIC_FREE_MIC_45)
    assert Nprime_bin.data[98] == pytest.approx(EXP_BIN_SPECIFIC_LOUDNESS_DIOTIC_FREE_MIC_98)
    assert len(Nprime_mon) == 1
    assert len(Nprime_mon[0]) == EXP_ERB_LEN
    assert Nprime_mon[0].data[0] == pytest.approx(EXP_MON_SPECIFIC_LOUDNESS_DIOTIC_FREE_MIC_0)
    assert Nprime_mon[0].data[45] == pytest.approx(EXP_MON_SPECIFIC_LOUDNESS_DIOTIC_FREE_MIC_45)
    assert Nprime_mon[0].data[98] == pytest.approx(EXP_MON_SPECIFIC_LOUDNESS_DIOTIC_FREE_MIC_98)


@pytest.mark.parametrize(
    "field_type, recording_type, exp_values",
    [
        (
            "Free",
            "Mic",
            (
                EXP_BIN_LOUDNESS_DICHOTIC_FREE_MIC,
                EXP_BIN_LOUDNESS_LEVEL_DICHOTIC_FREE_MIC,
                EXP_MON_LOUDNESS_DICHOTIC_FREE_MIC_LEFT,
                EXP_MON_LOUDNESS_DICHOTIC_FREE_MIC_RIGHT,
                EXP_BIN_SPECIFIC_LOUDNESS_DICHOTIC_FREE_MIC_0,
                EXP_BIN_SPECIFIC_LOUDNESS_DICHOTIC_FREE_MIC_45,
                EXP_BIN_SPECIFIC_LOUDNESS_DICHOTIC_FREE_MIC_98,
            ),
        ),
        (
            "Diffuse",
            "Mic",
            (
                EXP_BIN_LOUDNESS_DICHOTIC_DIFFUSE_MIC,
                EXP_BIN_LOUDNESS_LEVEL_DICHOTIC_DIFFUSE_MIC,
                EXP_MON_LOUDNESS_DICHOTIC_DIFFUSE_MIC_LEFT,
                EXP_MON_LOUDNESS_DICHOTIC_DIFFUSE_MIC_RIGHT,
                EXP_BIN_SPECIFIC_LOUDNESS_DICHOTIC_DIFFUSE_MIC_0,
                EXP_BIN_SPECIFIC_LOUDNESS_DICHOTIC_DIFFUSE_MIC_45,
                EXP_BIN_SPECIFIC_LOUDNESS_DICHOTIC_DIFFUSE_MIC_98,
            ),
        ),
        (
            "Free",
            "Head",
            (
                EXP_BIN_LOUDNESS_DICHOTIC_HEAD,
                EXP_BIN_LOUDNESS_LEVEL_DICHOTIC_HEAD,
                EXP_MON_LOUDNESS_DICHOTIC_HEAD_LEFT,
                EXP_MON_LOUDNESS_DICHOTIC_HEAD_RIGHT,
                EXP_BIN_SPECIFIC_LOUDNESS_DICHOTIC_HEAD_0,
                EXP_BIN_SPECIFIC_LOUDNESS_DICHOTIC_HEAD_45,
                EXP_BIN_SPECIFIC_LOUDNESS_DICHOTIC_HEAD_98,
            ),
        ),
        (
            "Diffuse",
            "Head",
            (
                EXP_BIN_LOUDNESS_DICHOTIC_HEAD,
                EXP_BIN_LOUDNESS_LEVEL_DICHOTIC_HEAD,
                EXP_MON_LOUDNESS_DICHOTIC_HEAD_LEFT,
                EXP_MON_LOUDNESS_DICHOTIC_HEAD_RIGHT,
                EXP_BIN_SPECIFIC_LOUDNESS_DICHOTIC_HEAD_0,
                EXP_BIN_SPECIFIC_LOUDNESS_DICHOTIC_HEAD_45,
                EXP_BIN_SPECIFIC_LOUDNESS_DICHOTIC_HEAD_98,
            ),
        ),
    ],
)
def test_loudness_iso_532_2_get_output_dichotic_case(field_type, recording_type, exp_values):
    """Test the get_output method of the LoudnessISO532_2 class, in the dichotic case."""
    loudness_computer = LoudnessISO532_2()

    wav_loader = LoadWav(pytest.data_path_Acceleration_stereo_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()

    loudness_computer.signal = fc

    loudness_computer.field_type = field_type
    loudness_computer.recording_type = recording_type

    loudness_computer.process()

    N_bin, LN_bin, N_mon, _, Nprime_bin, _ = loudness_computer.get_output()

    assert N_bin == pytest.approx(exp_values[0])
    assert LN_bin == pytest.approx(exp_values[1])
    assert N_mon[0] == pytest.approx(exp_values[2])
    assert N_mon[1] == pytest.approx(exp_values[3])
    assert len(Nprime_bin) == EXP_ERB_LEN
    assert Nprime_bin.data[0] == pytest.approx(exp_values[4])
    assert Nprime_bin.data[45] == pytest.approx(exp_values[5])
    assert Nprime_bin.data[98] == pytest.approx(exp_values[6])


def test_loudness_iso_532_2_get_output_monaural_outputs():
    """Test the get_output method of the LoudnessISO532_2 class for some other monaural outputs.

    Here we test some other monaural outputs, but without repeating the tests for all cases of
    field and recording types.
    """
    loudness_computer = LoudnessISO532_2()

    wav_loader = LoadWav(pytest.data_path_Acceleration_stereo_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()

    loudness_computer.signal = fc

    loudness_computer.process()

    _, _, _, LN_mon, _, Nprime_mon = loudness_computer.get_output()
    assert LN_mon[0] == pytest.approx(EXP_MON_LOUDNESS_LEVEL_DICHOTIC_FREE_MIC_LEFT)
    assert LN_mon[1] == pytest.approx(EXP_MON_LOUDNESS_LEVEL_DICHOTIC_FREE_MIC_RIGHT)
    assert len(Nprime_mon[0]) == EXP_ERB_LEN
    assert Nprime_mon[0].data[0] == pytest.approx(EXP_MON_SPECIFIC_LOUDNESS_DICHOTIC_FREE_MIC_L_0)
    assert Nprime_mon[0].data[45] == pytest.approx(EXP_MON_SPECIFIC_LOUDNESS_DICHOTIC_FREE_MIC_L_45)
    assert Nprime_mon[0].data[98] == pytest.approx(EXP_MON_SPECIFIC_LOUDNESS_DICHOTIC_FREE_MIC_L_98)
    assert len(Nprime_mon[1]) == EXP_ERB_LEN
    assert Nprime_mon[1].data[0] == pytest.approx(EXP_MON_SPECIFIC_LOUDNESS_DICHOTIC_FREE_MIC_R_0)
    assert Nprime_mon[1].data[45] == pytest.approx(EXP_MON_SPECIFIC_LOUDNESS_DICHOTIC_FREE_MIC_R_45)
    assert Nprime_mon[1].data[98] == pytest.approx(EXP_MON_SPECIFIC_LOUDNESS_DICHOTIC_FREE_MIC_R_98)


def test_loudness_iso_532_2_get_output_warning():
    """Test the get_output method's warning of the LoudnessISO532_2 class."""
    loudness_computer = LoudnessISO532_2()

    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()

    loudness_computer.signal = fc[0]

    # Loudness not calculated yet -> warning
    with pytest.warns(
        PyAnsysSoundWarning,
        match=("Output is not processed yet. " "Use the `LoudnessISO532_2.process\\(\\)` method."),
    ):
        output = loudness_computer.get_output()
    assert output is None


def test_loudness_iso_532_2_get_output_as_nparray():
    """Test the get_output_as_nparray method of the LoudnessISO532_2 class."""
    loudness_computer = LoudnessISO532_2()

    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib)
    wav_loader.process()
    ERBn = wav_loader.get_output()

    loudness_computer.signal = ERBn[0]

    # Loudness not calculated yet -> warning
    with pytest.warns(
        PyAnsysSoundWarning,
        match=("Output is not processed yet. " "Use the `LoudnessISO532_2.process\\(\\)` method."),
    ):
        N_bin, LN_bin, N_mon, LN_mon, Nprime_bin, Nprime_mon, ERBn = (
            loudness_computer.get_output_as_nparray()
        )
    assert np.isnan(N_bin)
    assert np.isnan(LN_bin)
    assert len(N_mon) == 0
    assert len(LN_mon) == 0
    assert len(Nprime_bin) == 0
    assert len(Nprime_mon) == 0
    assert len(ERBn) == 0

    loudness_computer.process()

    N_bin, LN_bin, N_mon, LN_mon, Nprime_bin, Nprime_mon, ERBn = (
        loudness_computer.get_output_as_nparray()
    )
    assert N_bin == pytest.approx(EXP_BIN_LOUDNESS_DIOTIC_FREE_MIC)
    assert LN_bin == pytest.approx(EXP_BIN_LOUDNESS_LEVEL_DIOTIC_FREE_MIC)
    assert len(N_mon) == 1
    assert N_mon[0] == pytest.approx(EXP_MON_LOUDNESS_DIOTIC_FREE_MIC)
    assert len(LN_mon) == 1
    assert LN_mon[0] == pytest.approx(EXP_MON_LOUDNESS_LEVEL_DIOTIC_FREE_MIC)
    assert len(Nprime_bin) == EXP_ERB_LEN
    assert Nprime_bin[0] == pytest.approx(EXP_BIN_SPECIFIC_LOUDNESS_DIOTIC_FREE_MIC_0)
    assert Nprime_bin[45] == pytest.approx(EXP_BIN_SPECIFIC_LOUDNESS_DIOTIC_FREE_MIC_45)
    assert Nprime_bin[98] == pytest.approx(EXP_BIN_SPECIFIC_LOUDNESS_DIOTIC_FREE_MIC_98)
    assert len(Nprime_mon) == EXP_ERB_LEN
    assert Nprime_mon[0] == pytest.approx(EXP_MON_SPECIFIC_LOUDNESS_DIOTIC_FREE_MIC_0)
    assert Nprime_mon[45] == pytest.approx(EXP_MON_SPECIFIC_LOUDNESS_DIOTIC_FREE_MIC_45)
    assert Nprime_mon[98] == pytest.approx(EXP_MON_SPECIFIC_LOUDNESS_DIOTIC_FREE_MIC_98)
    assert len(ERBn) == 372
    assert ERBn[0] == pytest.approx(EXP_ERB_0)
    assert ERBn[45] == pytest.approx(EXP_ERB_45)
    assert ERBn[98] == pytest.approx(EXP_ERB_98)


def test_loudness_iso_532_2_get_binaural_loudness_sone():
    """Test the get_binaural_loudness_sone method of the LoudnessISO532_2 class."""
    loudness_computer = LoudnessISO532_2()

    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()

    loudness_computer.signal = fc[0]

    loudness_computer.process()

    N_bin = loudness_computer.get_binaural_loudness_sone()
    assert N_bin == pytest.approx(EXP_BIN_LOUDNESS_DIOTIC_FREE_MIC)


def test_loudness_iso_532_2_get_binaural_loudness_level_phon():
    """Test the get_binaural_loudness_level_phon method of the LoudnessISO532_2 class."""
    loudness_computer = LoudnessISO532_2()

    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()

    loudness_computer.signal = fc[0]

    loudness_computer.process()

    LN_bin = loudness_computer.get_binaural_loudness_level_phon()
    assert LN_bin == pytest.approx(EXP_BIN_LOUDNESS_LEVEL_DIOTIC_FREE_MIC)


def test_loudness_iso_532_2_get_monaural_loudness_sone():
    """Test the get_monaural_loudness_sone method of the LoudnessISO532_2 class."""
    loudness_computer = LoudnessISO532_2()

    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()

    loudness_computer.signal = fc[0]

    loudness_computer.process()

    N_mon = loudness_computer.get_monaural_loudness_sone()
    assert len(N_mon) == 2
    assert N_mon[0] == pytest.approx(EXP_MON_LOUDNESS_DIOTIC_FREE_MIC)
    assert N_mon[1] == pytest.approx(EXP_MON_LOUDNESS_DIOTIC_FREE_MIC)

    wav_loader.path_to_wav = pytest.data_path_Acceleration_stereo_nonUnitaryCalib
    wav_loader.process()
    fc = wav_loader.get_output()

    loudness_computer.signal = fc

    loudness_computer.process()

    N_mon = loudness_computer.get_monaural_loudness_sone()
    assert len(N_mon) == 2
    assert N_mon[0] == pytest.approx(EXP_MON_LOUDNESS_DICHOTIC_FREE_MIC_LEFT)
    assert N_mon[1] == pytest.approx(EXP_MON_LOUDNESS_DICHOTIC_FREE_MIC_RIGHT)


def test_loudness_iso_532_2_get_monaural_loudness_level_phon():
    """Test the get_monaural_loudness_level_phon method of the LoudnessISO532_2 class."""
    loudness_computer = LoudnessISO532_2()

    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()

    loudness_computer.signal = fc[0]

    loudness_computer.process()

    LN_mon = loudness_computer.get_monaural_loudness_level_phon()
    assert len(LN_mon) == 2
    assert LN_mon[0] == pytest.approx(EXP_MON_LOUDNESS_LEVEL_DIOTIC_FREE_MIC)
    assert LN_mon[1] == pytest.approx(EXP_MON_LOUDNESS_LEVEL_DIOTIC_FREE_MIC)

    wav_loader.path_to_wav = pytest.data_path_Acceleration_stereo_nonUnitaryCalib
    wav_loader.process()
    fc = wav_loader.get_output()

    loudness_computer.signal = fc

    loudness_computer.process()

    LN_mon = loudness_computer.get_monaural_loudness_level_phon()
    assert len(LN_mon) == 2
    assert LN_mon[0] == pytest.approx(EXP_MON_LOUDNESS_LEVEL_DICHOTIC_FREE_MIC_LEFT)
    assert LN_mon[1] == pytest.approx(EXP_MON_LOUDNESS_LEVEL_DICHOTIC_FREE_MIC_RIGHT)


def test_loudness_iso_532_2_get_binaural_specific_loudness():
    """Test the get_binaural_specific_loudness method of the LoudnessISO532_2 class."""
    loudness_computer = LoudnessISO532_2()

    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()

    loudness_computer.signal = fc[0]

    loudness_computer.process()

    Nprime_bin = loudness_computer.get_binaural_specific_loudness()
    assert len(Nprime_bin) == EXP_ERB_LEN
    assert Nprime_bin[0] == pytest.approx(EXP_BIN_SPECIFIC_LOUDNESS_DIOTIC_FREE_MIC_0)
    assert Nprime_bin[45] == pytest.approx(EXP_BIN_SPECIFIC_LOUDNESS_DIOTIC_FREE_MIC_45)
    assert Nprime_bin[98] == pytest.approx(EXP_BIN_SPECIFIC_LOUDNESS_DIOTIC_FREE_MIC_98)


def test_loudness_iso_532_2_get_monaural_specific_loudness():
    """Test the get_specific_loudness_sone method of the LoudnessISO532_2 class."""
    loudness_computer = LoudnessISO532_2()

    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()

    loudness_computer.signal = fc[0]

    loudness_computer.process()

    Nprime_mon = loudness_computer.get_monaural_specific_loudness()
    assert len(Nprime_mon) == 2
    assert len(Nprime_mon[0]) == EXP_ERB_LEN
    assert Nprime_mon[0][0] == pytest.approx(EXP_MON_SPECIFIC_LOUDNESS_DIOTIC_FREE_MIC_0)
    assert Nprime_mon[0][45] == pytest.approx(EXP_MON_SPECIFIC_LOUDNESS_DIOTIC_FREE_MIC_45)
    assert Nprime_mon[0][98] == pytest.approx(EXP_MON_SPECIFIC_LOUDNESS_DIOTIC_FREE_MIC_98)

    wav_loader.path_to_wav = pytest.data_path_Acceleration_stereo_nonUnitaryCalib
    wav_loader.process()
    fc = wav_loader.get_output()

    loudness_computer.signal = fc

    loudness_computer.process()

    Nprime_mon = loudness_computer.get_monaural_specific_loudness()
    assert len(Nprime_mon) == 2
    assert len(Nprime_mon[0]) == EXP_ERB_LEN
    assert Nprime_mon[0][0] == pytest.approx(EXP_MON_SPECIFIC_LOUDNESS_DICHOTIC_FREE_MIC_L_0)
    assert Nprime_mon[0][45] == pytest.approx(EXP_MON_SPECIFIC_LOUDNESS_DICHOTIC_FREE_MIC_L_45)
    assert Nprime_mon[0][98] == pytest.approx(EXP_MON_SPECIFIC_LOUDNESS_DICHOTIC_FREE_MIC_L_98)
    assert len(Nprime_mon[1]) == EXP_ERB_LEN
    assert Nprime_mon[1][0] == pytest.approx(EXP_MON_SPECIFIC_LOUDNESS_DICHOTIC_FREE_MIC_R_0)
    assert Nprime_mon[1][45] == pytest.approx(EXP_MON_SPECIFIC_LOUDNESS_DICHOTIC_FREE_MIC_R_45)
    assert Nprime_mon[1][98] == pytest.approx(EXP_MON_SPECIFIC_LOUDNESS_DICHOTIC_FREE_MIC_R_98)


def test_loudness_iso_532_2_get_erb_center_frequencies():
    """Test the get_erb_center_frequencies method of the LoudnessISO532_2 class."""
    loudness_computer = LoudnessISO532_2()

    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()

    loudness_computer.signal = fc[0]

    loudness_computer.process()

    fc = loudness_computer.get_erb_center_frequencies()
    assert len(fc) == EXP_ERB_LEN
    assert fc[0] == pytest.approx(EXP_FREQ_0)
    assert fc[45] == pytest.approx(EXP_FREQ_45)
    assert fc[98] == pytest.approx(EXP_FREQ_98)


def test_loudness_iso_532_2_get_erbn_numbers():
    """Test the get_erbn_numbers method of the LoudnessISO532_2 class."""
    loudness_computer = LoudnessISO532_2()

    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()

    loudness_computer.signal = fc[0]

    loudness_computer.process()

    erb = loudness_computer.get_erbn_numbers()
    assert len(erb) == EXP_ERB_LEN
    assert erb[0] == pytest.approx(EXP_ERB_0)
    assert erb[45] == pytest.approx(EXP_ERB_45)
    assert erb[98] == pytest.approx(EXP_ERB_98)


@patch("matplotlib.pyplot.show")
def test_loudness_iso_532_2_plot(mock_show):
    """Test the plot method of the LoudnessISO532_2 class."""
    loudness_computer = LoudnessISO532_2()

    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()

    loudness_computer.signal = fc[0]

    loudness_computer.process()

    loudness_computer.plot()


def test_loudness_iso_532_2_plot_exceptions():
    """Test the exceptions of the plot method of the LoudnessISO532_2 class."""
    loudness_computer = LoudnessISO532_2()

    with pytest.raises(
        PyAnsysSoundException,
        match="Output is not processed yet. Use the `LoudnessISO532_2.process\\(\\)` method.",
    ):
        loudness_computer.plot()
