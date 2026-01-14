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
from ansys.sound.core.psychoacoustics import TonalityISOTS20065
from ansys.sound.core.signal_utilities import LoadWav

EXP_DL = 9.737211
EXP_U = 0.8541942
EXP_DLJ3 = 7.597201
EXP_UJ3 = 2.154871
EXP_FTJ3 = 113.0493
EXP_TIME3 = 10.48608
EXP_SPECTRUM_NUMBER = 6
EXP_SPECTRUM1_DECISIVE_DIFFERENCE = 7.895215
EXP_SPECTRUM1_UNCERTAINTY = 1.483663
EXP_SPECTRUM1_DECISIVE_FREQUENCY = 16359.85
EXP_SPECTRUM1_TONE_NUMBER = 4
EXP_SPECTRUM1_TONE3_DIFFERENCE = 4.705133
EXP_SPECTRUM1_TONE3_TYPE = ""
EXP_STR = (
    "TonalityISOTS20065 object.\n"
    "Data\n"
    f'\tSignal name: "Acceleration_with_Tacho"\n'
    f"\tWindow length: 3.0 s\n"
    f"\tOverlap: 0.0 %\n"
    f"Mean tonality (audibility DL): 9.7 (+/-0.9) dB"
)

if pytest.SOUND_VERSION_GREATER_THAN_OR_EQUAL_TO_2026R1:
    # Third-party update (IPP) in DPF Sound 2026 R1
    EXP_SPECTRUM1_TONE3_MASKING_NOISE_LEVEL = 0.6313894
else:  # DPF Sound <= 2025 R2
    EXP_SPECTRUM1_TONE3_MASKING_NOISE_LEVEL = 0.6313946


def test_tonality_iso_ts_20065_instantiation():
    """Test TonalityISOTS20065 instantiation."""
    tonality = TonalityISOTS20065()
    assert tonality.signal == None
    assert tonality.window_length == pytest.approx(3.0)
    assert tonality.overlap == pytest.approx(0.0)


def test_tonality_iso_ts_20065_properties():
    """Test TonalityISOTS20065 properties."""
    tonality = TonalityISOTS20065()
    tonality.signal = Field()
    assert type(tonality.signal) == Field

    tonality.window_length = 2.0
    assert tonality.window_length == 2.0

    tonality.overlap = 15.6
    assert tonality.overlap == 15.6


def test_tonality_iso_ts_20065___str__():
    """Test __str__ method."""
    wav_loader = LoadWav(pytest.data_path_Acceleration_with_Tacho_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityISOTS20065(signal=fc[0])
    tonality.process()

    assert tonality.__str__() == EXP_STR


def test_tonality_iso_ts_20065_setters_exceptions():
    """Test TonalityISOTS20065 setters' exceptions."""
    tonality = TonalityISOTS20065()
    with pytest.raises(
        PyAnsysSoundException,
        match="Signal must be specified as a DPF field.",
    ):
        tonality.signal = "Invalid"

    with pytest.raises(PyAnsysSoundException, match="Window length must be strictly positive."):
        tonality.window_length = 0.0

    with pytest.raises(
        PyAnsysSoundException, match="Overlap must be positive and strictly smaller than 100.0 %."
    ):
        tonality.overlap = 100.0

    with pytest.raises(
        PyAnsysSoundException, match="Overlap must be positive and strictly smaller than 100.0 %."
    ):
        tonality.overlap = -1.0


def test_tonality_iso_ts_20065_process():
    """Test process method."""
    wav_loader = LoadWav(pytest.data_path_Acceleration_with_Tacho_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityISOTS20065(signal=fc[0])
    tonality.process()


def test_tonality_iso_ts_20065_process_exception():
    """Test process method's exception."""
    tonality = TonalityISOTS20065()

    with pytest.raises(
        PyAnsysSoundException,
        match="No input signal defined. Use `TonalityISOTS20065.signal`.",
    ):
        tonality.process()


def test_tonality_iso_ts_20065_get_output():
    """Test get_output method."""
    wav_loader = LoadWav(pytest.data_path_Acceleration_with_Tacho_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityISOTS20065(signal=fc[0])
    tonality.process()

    output = tonality.get_output()
    assert output is not None


def test_tonality_iso_ts_20065_get_output_unprocessed():
    """Test get_output method's warning."""
    tonality = TonalityISOTS20065()

    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the `TonalityISOTS20065.process\\(\\)` method.",
    ):
        output = tonality.get_output()
    assert output is None


def test_tonality_iso_ts_20065_get_output_as_nparray():
    """Test get_output_as_nparray method."""
    wav_loader = LoadWav(pytest.data_path_Acceleration_with_Tacho_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityISOTS20065(signal=fc[0])
    tonality.process()

    DL, U, DLj, Uj, fTj, time = tonality.get_output_as_nparray()
    assert DL == pytest.approx(EXP_DL)
    assert U == pytest.approx(EXP_U)
    assert DLj[3] == pytest.approx(EXP_DLJ3)
    assert Uj[3] == pytest.approx(EXP_UJ3)
    assert fTj[3] == pytest.approx(EXP_FTJ3)
    assert time[3] == pytest.approx(EXP_TIME3)


def test_tonality_iso_ts_20065_get_output_as_nparray_unprocessed():
    """Test get_output_as_nparray method's warning."""
    tonality = TonalityISOTS20065()

    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the `TonalityISOTS20065.process\\(\\)` method.",
    ):
        DL, U, DLj, Uj, fTj, time = tonality.get_output_as_nparray()
    assert np.isnan(DL)
    assert np.isnan(U)
    assert len(DLj) == 0
    assert len(Uj) == 0
    assert len(fTj) == 0
    assert len(time) == 0


def test_tonality_iso_ts_20065_get_mean_audibility():
    """Test get_mean_audibility method."""
    wav_loader = LoadWav(pytest.data_path_Acceleration_with_Tacho_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityISOTS20065(signal=fc[0])
    tonality.process()

    DL = tonality.get_mean_audibility()
    assert DL == pytest.approx(EXP_DL)


def test_tonality_iso_ts_20065_get_uncertainty():
    """Test get_uncertainty method."""
    wav_loader = LoadWav(pytest.data_path_Acceleration_with_Tacho_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityISOTS20065(signal=fc[0])
    tonality.process()

    U = tonality.get_uncertainty()
    assert U == pytest.approx(EXP_U)


def test_tonality_iso_ts_20065_get_decisive_audibility_over_time():
    """Test get_decisive_audibility_over_time method."""
    wav_loader = LoadWav(pytest.data_path_Acceleration_with_Tacho_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityISOTS20065(signal=fc[0])
    tonality.process()

    DLj = tonality.get_decisive_audibility_over_time()
    assert DLj[3] == pytest.approx(EXP_DLJ3)


def test_tonality_iso_ts_20065_get_uncertainty_over_time():
    """Test get_uncertainty_over_time method."""
    wav_loader = LoadWav(pytest.data_path_Acceleration_with_Tacho_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityISOTS20065(signal=fc[0])
    tonality.process()

    Uj = tonality.get_uncertainty_over_time()
    assert Uj[3] == pytest.approx(EXP_UJ3)


def test_tonality_iso_ts_20065_get_time_scale():
    """Test get_time_scale method."""
    wav_loader = LoadWav(pytest.data_path_Acceleration_with_Tacho_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityISOTS20065(signal=fc[0])
    tonality.process()

    time = tonality.get_time_scale()
    assert time[3] == pytest.approx(EXP_TIME3)


def test_tonality_iso_ts_20065_get_spectrum_number():
    """Test get_spectrum_number method."""
    wav_loader = LoadWav(pytest.data_path_Acceleration_with_Tacho_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityISOTS20065(signal=fc[0])
    tonality.process()

    spectrum_number = tonality.get_spectrum_number()
    assert spectrum_number == EXP_SPECTRUM_NUMBER


def test_tonality_iso_ts_20065_get_spectrum_details():
    """Test get_spectrum_details method."""
    wav_loader = LoadWav(pytest.data_path_Acceleration_with_Tacho_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityISOTS20065(signal=fc[0])
    tonality.process()

    decicive_audibility, uncertainty, decisive_frequency = tonality.get_spectrum_details(
        spectrum_index=1
    )
    assert decicive_audibility == pytest.approx(EXP_SPECTRUM1_DECISIVE_DIFFERENCE)
    assert uncertainty == pytest.approx(EXP_SPECTRUM1_UNCERTAINTY)
    assert decisive_frequency == pytest.approx(EXP_SPECTRUM1_DECISIVE_FREQUENCY)


def test_tonality_iso_ts_20065_get_tone_number():
    """Test get_tone_number method."""
    wav_loader = LoadWav(pytest.data_path_Acceleration_with_Tacho_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityISOTS20065(signal=fc[0])
    tonality.process()

    tone_number = tonality.get_tone_number(spectrum_index=1)
    assert tone_number == EXP_SPECTRUM1_TONE_NUMBER


def test_tonality_iso_ts_20065_get_tone_details():
    """Test get_tone_details method."""
    wav_loader = LoadWav(pytest.data_path_Acceleration_with_Tacho_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityISOTS20065(signal=fc[0])
    tonality.process()

    details = tonality.get_tone_details(spectrum_index=1, tone_index=3)
    assert details[0] == pytest.approx(EXP_SPECTRUM1_TONE3_DIFFERENCE)
    assert details[3] == pytest.approx(EXP_SPECTRUM1_TONE3_TYPE)
    assert details[7] == pytest.approx(EXP_SPECTRUM1_TONE3_MASKING_NOISE_LEVEL)


def test_tonality_iso_ts_20065_get_tone_details_exception():
    """Test get_tone_details method's exception."""
    wav_loader = LoadWav(pytest.data_path_Acceleration_with_Tacho_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityISOTS20065(signal=fc[0])
    tonality.process()

    with pytest.raises(
        PyAnsysSoundException,
        match="Tone index 10 is out of bounds \\(total tone count in specified spectrum is 6\\).",
    ):
        tonality.get_tone_details(spectrum_index=1, tone_index=10)


@patch("matplotlib.pyplot.show")
def test_tonality_iso_ts_20065_plot(mock_show):
    """Test plot method."""
    wav_loader = LoadWav(pytest.data_path_Acceleration_with_Tacho_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityISOTS20065(signal=fc[0])
    tonality.process()

    tonality.plot()


def test_tonality_iso_ts_20065_plot_exception():
    """Test plot method's exception."""
    wav_loader = LoadWav(pytest.data_path_Acceleration_with_Tacho_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityISOTS20065(signal=fc[0])

    with pytest.raises(
        PyAnsysSoundException,
        match="Output is not processed yet. Use the `TonalityISOTS20065.process\\(\\)` method.",
    ):
        tonality.plot()


def test_tonality_iso_ts_20065___check_spectrum_index():
    """Test __check_spectrum_index method."""
    wav_loader = LoadWav(pytest.data_path_Acceleration_with_Tacho_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityISOTS20065(signal=fc[0])
    tonality.process()

    with pytest.raises(
        PyAnsysSoundException,
        match="Spectrum index 10 is out of bounds \\(total spectrum count is 6\\).",
    ):
        tonality._TonalityISOTS20065__check_spectrum_index(spectrum_index=10)
