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
from ansys.sound.core.psychoacoustics import TonalityECMA418_2
from ansys.sound.core.signal_utilities import LoadWav

EXP_TONALITY_FREE_1ST = 4.918124
EXP_TONALITY_DIFFUSE_1ST = 4.722795
EXP_TONALITY_FREE_3RD = 4.077500
EXP_TONALITY_DIFFUSE_3RD = 3.963325
EXP_TONALITY_OVER_TIME_FREE_1ST = 5.718086
EXP_TONALITY_OVER_TIME_DIFFUSE_1ST = 5.254110
EXP_TONALITY_OVER_TIME_FREE_3RD = 4.776258
EXP_TONALITY_OVER_TIME_DIFFUSE_3RD = 4.448931
EXP_FT_OVER_TIME_FREE_1ST = 795.4102
EXP_FT_OVER_TIME_DIFFUSE_1ST = 533.2031
EXP_FT_OVER_TIME_FREE_3RD = 791.0156
EXP_FT_OVER_TIME_DIFFUSE_3RD = 527.3438
EXP_TIME_TONALITY = 3.536000
EXP_TIME_TONE_FREQUENCY_1ST = 3.237333
EXP_STR_UNPROCESSED = (
    "TonalityECMA418_2 object.\n"
    "Data\n"
    "\tSignal name: Signal not set\n"
    "\tField type: None\n"
    "\tEdition of the standard: None\n"
    "Tonality: Not processed\n"
)
EXP_STR_1ST_EDITION_FREE = (
    "TonalityECMA418_2 object.\n"
    "Data\n"
    '\tSignal name: "flute"\n'
    "\tField type: Free\n"
    "\tEdition of the standard: 1st\n"
    "Tonality: 4.92 tuHMS\n"
)
EXP_STR_3RD_EDITION_DIFFUSE = (
    "TonalityECMA418_2 object.\n"
    "Data\n"
    '\tSignal name: "flute"\n'
    "\tField type: Diffuse\n"
    "\tEdition of the standard: 3rd\n"
    "Tonality: 3.96 tuHMS\n"
)


def test_tonality_ecma_418_2_instantiation():
    """Test TonalityECMA418_2 instantiation."""
    tonality = TonalityECMA418_2()
    assert type(tonality) is TonalityECMA418_2


def test_tonality_ecma_418_2_properties():
    """Test TonalityECMA418_2 properties."""
    tonality = TonalityECMA418_2()

    # signal property
    tonality.signal = Field()
    assert type(tonality.signal) is Field

    # field_type property
    tonality.field_type = "Free"
    assert tonality.field_type is "Free"

    # field_type property (case insensitivity)
    tonality.field_type = "FReE"
    assert tonality.field_type is "FReE"

    # edition property
    tonality.edition = "1st"
    assert tonality.edition is "1st"

    # edition property (case insensitivity)
    tonality.edition = "1ST"
    assert tonality.edition is "1ST"


@pytest.mark.skipif(
    not pytest.SERVERS_VERSION_GREATER_THAN_OR_EQUAL_TO_11_0,
    reason="Diffuse field and 3rd edition not allowed before server version 11.0",
)
def test_tonality_ecma_418_2_properties_11_0():
    """Test TonalityECMA418_2 properties' additional values allowed from server version 11.0."""
    tonality = TonalityECMA418_2()

    tonality.field_type = "Diffuse"
    assert tonality.field_type is "Diffuse"

    tonality.edition = "3rd"
    assert tonality.edition is "3rd"


def test_tonality_ecma_418_2_setters_exceptions():
    """Test TonalityECMA418_2 setters' exceptions."""
    tonality = TonalityECMA418_2()

    with pytest.raises(
        PyAnsysSoundException,
        match="Signal must be specified as a DPF field.",
    ):
        tonality.signal = "Invalid"

    with pytest.raises(
        PyAnsysSoundException,
        match='Invalid field type "Invalid". Available options are "Free" and "Diffuse".',
    ):
        tonality.field_type = "Invalid"

    with pytest.raises(
        PyAnsysSoundException,
        match='Invalid edition "Invalid". Available options are "1st" and "3rd".',
    ):
        tonality.edition = "Invalid"


@pytest.mark.skipif(
    pytest.SERVERS_VERSION_GREATER_THAN_OR_EQUAL_TO_11_0,
    reason="Server-version errors are only triggered prior to version 11.0",
)
def test_tonality_ecma_418_2_setters_exceptions_lower_than_11_0():
    """Test TonalityECMA418_2 setters' exceptions related to diffuse field and 3rd edition."""
    tonality = TonalityECMA418_2()

    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "Computing ECMA-418-2 tonality in diffuse field requires version 2026 R1 of "
            "DPF Sound or higher. Please use free field instead."
        ),
    ):
        tonality.field_type = "Diffuse"

    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "The 3rd edition of ECMA-418-2 tonality requires version 2026 R1 of DPF Sound "
            "or higher. Please use the 1st edition instead."
        ),
    ):
        tonality.edition = "3rd"


def test_tonality_ecma_418_2___str__():
    """Test __str__ method."""
    tonality = TonalityECMA418_2()
    assert tonality.__str__() == EXP_STR_UNPROCESSED

    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    wav_loader.process()
    signal = wav_loader.get_output()

    tonality.signal = signal[0]
    tonality.field_type = "Free"
    tonality.edition = "1st"

    tonality.process()

    assert tonality.__str__() == EXP_STR_1ST_EDITION_FREE


@pytest.mark.skipif(
    not pytest.SERVERS_VERSION_GREATER_THAN_OR_EQUAL_TO_11_0,
    reason="Diffuse field and 3rd edition not allowed before server version 11.0",
)
def test_tonality_ecma_418_2___str___11_0():
    """Test __str__ method with diffuse field and 3rd edition."""
    tonality = TonalityECMA418_2()

    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    wav_loader.process()
    signal = wav_loader.get_output()

    tonality.signal = signal[0]
    tonality.field_type = "Diffuse"
    tonality.edition = "3rd"

    tonality.process()

    assert tonality.__str__() == EXP_STR_3RD_EDITION_DIFFUSE


def test_tonality_ecma_418_2_process():
    """Test process method."""
    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    wav_loader.process()
    signal = wav_loader.get_output()

    tonality = TonalityECMA418_2(signal[0], "Free", "1st")
    tonality.process()

    # Case insensitivity
    tonality.field_type = "fReE"
    tonality.edition = "1ST"

    tonality.process()


def test_tonality_ecma_418_2_process_exceptions():
    """Test process method's exception."""
    tonality = TonalityECMA418_2()
    tonality.field_type = "Free"
    tonality.edition = "1st"

    with pytest.raises(
        PyAnsysSoundException,
        match="No input signal defined. Use ``TonalityECMA418_2.signal``.",
    ):
        tonality.process()

    tonality = TonalityECMA418_2()
    tonality.signal = Field()
    tonality.edition = "1st"

    with pytest.raises(
        PyAnsysSoundException,
        match="No field type specified. Use ``TonalityECMA418_2.field_type``.",
    ):
        tonality.process()

    tonality = TonalityECMA418_2()
    tonality.signal = Field()
    tonality.field_type = "Free"

    with pytest.raises(
        PyAnsysSoundException,
        match="No edition of the standard specified. Use ``TonalityECMA418_2.edition``.",
    ):
        tonality.process()


def test_tonality_ecma_418_2_get_output():
    """Test get_output method."""
    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    wav_loader.process()
    signal = wav_loader.get_output()

    tonality = TonalityECMA418_2(signal[0], "Free", "1st")
    tonality.process()

    output = tonality.get_output()
    assert output is not None


def test_tonality_ecma_418_2_get_output_unprocessed():
    """Test get_output method's warning."""
    tonality = TonalityECMA418_2()

    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the ``TonalityECMA418_2.process\\(\\)`` method.",
    ):
        output = tonality.get_output()
    assert output is None


def test_tonality_ecma_418_2_get_output_as_nparray():
    """Test get_output_as_nparray method."""
    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    wav_loader.process()
    signal = wav_loader.get_output()

    tonality = TonalityECMA418_2(signal[0])

    tonality.field_type = "Free"
    tonality.edition = "1st"
    tonality.process()

    tonality_value, tonality_over_time, ft_over_time, time_tonality, time_tone = (
        tonality.get_output_as_nparray()
    )

    assert tonality_value == pytest.approx(EXP_TONALITY_FREE_1ST)
    assert tonality_over_time[225] == pytest.approx(EXP_TONALITY_OVER_TIME_FREE_1ST)
    assert ft_over_time[225] == pytest.approx(EXP_FT_OVER_TIME_FREE_1ST)
    assert time_tonality[-1] == pytest.approx(EXP_TIME_TONALITY)
    assert time_tone[-1] == pytest.approx(EXP_TIME_TONE_FREQUENCY_1ST)


@pytest.mark.skipif(
    not pytest.SERVERS_VERSION_GREATER_THAN_OR_EQUAL_TO_11_0,
    reason="Diffuse field and 3rd edition not allowed before server version 11.0",
)
def test_tonality_ecma_418_2_get_output_as_nparray_11_0():
    """Test get_output_as_nparray method with diffuse field and 3rd edition."""
    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    wav_loader.process()
    signal = wav_loader.get_output()

    tonality = TonalityECMA418_2(signal[0])

    tonality.field_type = "Diffuse"
    tonality.edition = "1st"
    tonality.process()

    tonality_value, tonality_over_time, ft_over_time, time_tonality, time_tone_frequency = (
        tonality.get_output_as_nparray()
    )

    assert tonality_value == pytest.approx(EXP_TONALITY_DIFFUSE_1ST)
    assert tonality_over_time[225] == pytest.approx(EXP_TONALITY_OVER_TIME_DIFFUSE_1ST)
    assert ft_over_time[225] == pytest.approx(EXP_FT_OVER_TIME_DIFFUSE_1ST)
    assert time_tonality[-1] == pytest.approx(EXP_TIME_TONALITY)
    assert time_tone_frequency[-1] == pytest.approx(EXP_TIME_TONE_FREQUENCY_1ST)

    tonality.field_type = "Free"
    tonality.edition = "3rd"
    tonality.process()

    tonality_value, tonality_over_time, ft_over_time, time_tonality, time_tone_frequency = (
        tonality.get_output_as_nparray()
    )

    assert tonality_value == pytest.approx(EXP_TONALITY_FREE_3RD)
    assert tonality_over_time[225] == pytest.approx(EXP_TONALITY_OVER_TIME_FREE_3RD)
    assert ft_over_time[225] == pytest.approx(EXP_FT_OVER_TIME_FREE_3RD)
    assert time_tonality[-1] == pytest.approx(EXP_TIME_TONALITY)
    # Bug fix (untracked): in 1st edition, time arrays would be different for tonality and tone
    # frequency. No longer the case in 3rd edition.
    assert time_tone_frequency[-1] == pytest.approx(EXP_TIME_TONALITY)

    tonality.field_type = "Diffuse"
    tonality.edition = "3rd"
    tonality.process()

    tonality_value, tonality_over_time, ft_over_time, time_tonality, time_tone_frequency = (
        tonality.get_output_as_nparray()
    )

    assert tonality_value == pytest.approx(EXP_TONALITY_DIFFUSE_3RD)
    assert tonality_over_time[225] == pytest.approx(EXP_TONALITY_OVER_TIME_DIFFUSE_3RD)
    assert ft_over_time[225] == pytest.approx(EXP_FT_OVER_TIME_DIFFUSE_3RD)


def test_tonality_ecma_418_2_get_output_as_nparray_unprocessed():
    """Test get_output_as_nparray method's warning."""
    tonality = TonalityECMA418_2()

    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the ``TonalityECMA418_2.process\\(\\)`` method.",
    ):
        tonality_value, tonality_over_time, ft_over_time, time_tonality, time_tones = (
            tonality.get_output_as_nparray()
        )
    assert np.isnan(tonality_value)
    assert len(tonality_over_time) == 0
    assert len(ft_over_time) == 0
    assert len(time_tonality) == 0
    assert len(time_tones) == 0


def test_tonality_ecma_418_2_get_tonality():
    """Test get_tonality method."""
    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    wav_loader.process()
    signal = wav_loader.get_output()

    tonality = TonalityECMA418_2(signal[0], "Free", "1st")
    tonality.process()

    tonality_value = tonality.get_tonality()
    assert tonality_value == pytest.approx(EXP_TONALITY_FREE_1ST)


def test_tonality_ecma_418_2_get_tonality_over_time():
    """Test get_tonality_over_time method."""
    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    wav_loader.process()
    signal = wav_loader.get_output()

    tonality = TonalityECMA418_2(signal[0], "Free", "1st")
    tonality.process()

    tonality_over_time = tonality.get_tonality_over_time()
    assert tonality_over_time[225] == pytest.approx(EXP_TONALITY_OVER_TIME_FREE_1ST)


def test_tonality_ecma_418_2_get_tone_frequency_over_time():
    """Test get_tone_frequency_over_time method."""
    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    wav_loader.process()
    signal = wav_loader.get_output()

    tonality = TonalityECMA418_2(signal[0], "Free", "1st")
    tonality.process()

    ft_over_time = tonality.get_tone_frequency_over_time()
    assert ft_over_time[225] == pytest.approx(EXP_FT_OVER_TIME_FREE_1ST)


def test_tonality_ecma_418_2_get_tonality_time_scale():
    """Test get_tonality_time_scale method."""
    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    wav_loader.process()
    signal = wav_loader.get_output()

    tonality = TonalityECMA418_2(signal[0], "Free", "1st")
    tonality.process()

    time = tonality.get_tonality_time_scale()
    assert time[-1] == pytest.approx(EXP_TIME_TONALITY)


def test_tonality_ecma_418_2_get_tone_frequency_time_scale():
    """Test get_tone_frequency_time_scale method."""
    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    wav_loader.process()
    signal = wav_loader.get_output()

    tonality = TonalityECMA418_2(signal[0], "Free", "1st")
    tonality.process()

    time = tonality.get_tone_frequency_time_scale()
    assert time[-1] == pytest.approx(EXP_TIME_TONE_FREQUENCY_1ST)


@patch("matplotlib.pyplot.show")
def test_tonality_ecma_418_2_plot(mock_show):
    """Test plot method."""
    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    wav_loader.process()
    signal = wav_loader.get_output()

    tonality = TonalityECMA418_2(signal[0], "Free", "1st")
    tonality.process()

    tonality.plot()


def test_tonality_ecma_418_2_plot_exception():
    """Test plot method's exception."""
    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    wav_loader.process()
    signal = wav_loader.get_output()

    tonality = TonalityECMA418_2(signal[0], "Free", "1st")

    with pytest.raises(
        PyAnsysSoundException,
        match="Output is not processed yet. Use the ``TonalityECMA418_2.process\\(\\)`` method.",
    ):
        tonality.plot()
