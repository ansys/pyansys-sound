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
from ansys.sound.core.psychoacoustics import TonalityECMA418_2
from ansys.sound.core.signal_utilities import LoadWav

EXP_TONALITY = 4.9181241989135742
EXP_TONALITY_OVER_TIME = 5.7180857658386230
EXP_FT_OVER_TIME = 795.41015625000000
EXP_TIME = 3.5360000133514404
EXP_STR = (
    "TonalityECMA418_2 object.\n"
    + "Data\n"
    + f'Signal name: "flute"\n'
    + f"Tonality: 4.918124198913574 tuHMS\n"
)


def test_tonality_ecma_418_2_instantiation():
    """Test TonalityECMA418_2 instantiation."""
    tonality = TonalityECMA418_2()
    assert tonality.signal == None


def test_tonality_ecma_418_2_properties():
    """Test TonalityECMA418_2 properties."""
    tonality = TonalityECMA418_2()
    tonality.signal = Field()
    assert type(tonality.signal) == Field


def test_tonality_ecma_418_2___str__():
    """Test __str__ method."""
    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityECMA418_2(signal=fc[0])
    tonality.process()

    assert tonality.__str__() == EXP_STR


def test_tonality_ecma_418_2_setters_exceptions():
    """Test TonalityECMA418_2 setters' exceptions."""
    tonality = TonalityECMA418_2()
    with pytest.raises(
        PyAnsysSoundException,
        match="Signal must be specified as a DPF field.",
    ):
        tonality.signal = "Invalid"


def test_tonality_ecma_418_2_process():
    """Test process method."""
    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityECMA418_2(signal=fc[0])
    tonality.process()


def test_tonality_ecma_418_2_process_exception():
    """Test process method's exception."""
    tonality = TonalityECMA418_2()

    with pytest.raises(
        PyAnsysSoundException,
        match="No input signal defined. Use ``TonalityECMA418_2.signal``.",
    ):
        tonality.process()


def test_tonality_ecma_418_2_get_output():
    """Test get_output method."""
    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityECMA418_2(signal=fc[0])
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
    fc = wav_loader.get_output()

    tonality = TonalityECMA418_2(signal=fc[0])
    tonality.process()

    tonality_float, tonality_over_time, ft_over_time, time = tonality.get_output_as_nparray()

    assert tonality_float == pytest.approx(EXP_TONALITY)
    assert tonality_over_time[225] == pytest.approx(EXP_TONALITY_OVER_TIME)
    assert ft_over_time[225] == pytest.approx(EXP_FT_OVER_TIME)
    assert time[-1] == pytest.approx(EXP_TIME)


def test_tonality_ecma_418_2_get_output_as_nparray_unprocessed():
    """Test get_output_as_nparray method's warning."""
    tonality = TonalityECMA418_2()

    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the ``TonalityECMA418_2.process\\(\\)`` method.",
    ):
        tonality_float, tonality_over_time, ft_over_time, time = tonality.get_output_as_nparray()
    assert np.isnan(tonality_float)
    assert len(tonality_over_time) == 0
    assert len(ft_over_time) == 0
    assert len(time) == 0


def test_tonality_ecma_418_2_get_tonality():
    """Test get_tonality method."""
    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityECMA418_2(signal=fc[0])
    tonality.process()

    tonality_float = tonality.get_tonality()
    assert tonality_float == pytest.approx(EXP_TONALITY)


def test_tonality_ecma_418_2_get_tonality_over_time():
    """Test get_tonality_over_time method."""
    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityECMA418_2(signal=fc[0])
    tonality.process()

    tonality_over_time = tonality.get_tonality_over_time()
    assert tonality_over_time[225] == pytest.approx(EXP_TONALITY_OVER_TIME)


def test_tonality_ecma_418_2_get_tone_frequency_over_time():
    """Test get_tone_frequency_over_time method."""
    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityECMA418_2(signal=fc[0])
    tonality.process()

    ft_over_time = tonality.get_tone_frequency_over_time()
    assert ft_over_time[225] == pytest.approx(EXP_FT_OVER_TIME)


def test_tonality_ecma_418_2_get_time_scale():
    """Test get_time_scale method."""
    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityECMA418_2(signal=fc[0])
    tonality.process()

    time = tonality.get_time_scale()
    assert time[-1] == pytest.approx(EXP_TIME)


@patch("matplotlib.pyplot.show")
def test_tonality_ecma_418_2_plot(mock_show):
    """Test plot method."""
    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityECMA418_2(signal=fc[0])
    tonality.process()

    tonality.plot()


def test_tonality_ecma_418_2_plot_exception():
    """Test plot method's exception."""
    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityECMA418_2(signal=fc[0])

    with pytest.raises(
        PyAnsysSoundException,
        match="Output is not processed yet. Use the ``TonalityECMA418_2.process\\(\\)`` method.",
    ):
        tonality.plot()
