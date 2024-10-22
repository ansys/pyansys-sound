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
from ansys.sound.core.psychoacoustics import TonalityDIN45681
from ansys.sound.core.signal_utilities import LoadWav

EXP_DL = 10.73870086669922
EXP_U = 10.73870086669922
EXP_KT = 10.73870086669922
EXP_DLJ3 = 10.73870086669922
EXP_UJ3 = 10.73870086669922
EXP_FTJ3 = 10.73870086669922
EXP_KTJ3 = 10.73870086669922
EXP_TIME3 = 10.73870086669922
EXP_DETAILS3 = 10.73870086669922
EXP_SPECTRUM_NUMBER = 3
EXP_TONE_NUMBER = 2
EXP_TONE_DETAILS21 = 10.73870086669922
EXP_STR = (
    "TonalityDIN45681 object.\n"
    + "Data\n"
    + f"Signal name: \"flute.wav\"\n"
    + f"Window length: 3.0 s\n"
    + f"Overlap: 0.0 %\n"
    + f"Mean difference DL: 1.0 (+/-2.0) dB\n"
    + f"Tonal adjustment Kt: 3.0 dB\n"
)


def test_tonality_din45681_instantiation(dpf_sound_test_server):
    """Test TonalityDIN45681 instantiation."""
    # Test instantiation.
    tonality = TonalityDIN45681()
    assert tonality.signal == None
    assert tonality.window_length == pytest.approx(3.0)
    assert tonality.overlap == pytest.approx(0.0)


def test_tonality_din45681_setters(dpf_sound_test_server):
    """Test TonalityDIN45681 setters."""
    # Test setters.
    tonality = TonalityDIN45681()
    tonality.signal = Field()
    assert type(tonality.signal) == Field

    tonality.window_length = 2.0
    assert tonality.window_length == 2.0

    tonality.overlap = 15.6
    assert tonality.overlap == 15.6


def test_tonality_din45681_setters_exceptions(dpf_sound_test_server):
    """Test TonalityDIN45681 setters' exceptions."""
    tonality = TonalityDIN45681()
    with pytest.raises(
        PyAnsysSoundException,
        match="Signal must be specified as a DPF field.",
    ):
        tonality.signal = "Invalid"

    with pytest.raises(
        PyAnsysSoundException, match="Window length must be strictly positive."
    ):
        tonality.window_length = 0.0


    with pytest.raises(
        PyAnsysSoundException, match="Overlap must be positive and strictly smaller than 100.0 %."
    ):
        tonality.overlap = 100.0


    with pytest.raises(
        PyAnsysSoundException, match="Overlap must be positive and strictly smaller than 100.0 %."
    ):
        tonality.overlap = -1.0


def test_tonality_din45681_process(dpf_sound_test_server):
    """Test process method."""
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_non_unitary_calib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityDIN45681(signal=fc[0])
    tonality.process()


def test_tonality_din45681_process_exception(dpf_sound_test_server):
    """Test process method's exception."""
    tonality = TonalityDIN45681()

    with pytest.raises(
        PyAnsysSoundException,
        match="No input signal defined. Use 'TonalityDIN45681.signal'.",
    ):
        tonality.process()


def test_tonality_din45681_get_output(dpf_sound_test_server):
    """Test get_output method."""
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_non_unitary_calib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityDIN45681(signal=fc[0])
    tonality.process()

    output = tonality.get_output()
    assert output is not None


def test_tonality_din45681_get_output_unprocessed(dpf_sound_test_server):
    """Test get_output method's warning."""
    tonality = TonalityDIN45681()

    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the 'TonalityDIN45681.process()' method.",
    ):
        output = tonality.get_output()
    assert output is None


def test_tonality_din45681_get_output_as_nparray(dpf_sound_test_server):
    """Test get_output_as_nparray method."""
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_non_unitary_calib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityDIN45681(signal=fc[0])
    tonality.process()

    DL, Kt, U, DLj, Uj, fTj, Ktj, time, details = tonality.get_output_as_nparray()
    assert DL == pytest.approx(EXP_DL)
    assert Kt == pytest.approx(EXP_KT)
    assert U == pytest.approx(EXP_U)    
    assert DLj[3] == pytest.approx(EXP_DLJ3)
    assert Uj[3] == pytest.approx(EXP_UJ3)
    assert fTj[3] == pytest.approx(EXP_FTJ3)
    assert Ktj[3] == pytest.approx(EXP_KTJ3)
    assert time[3] == pytest.approx(EXP_TIME3)
    assert details[3] == pytest.approx(EXP_DETAILS3)


def test_tonality_din45681_get_output_as_nparray_unprocessed(dpf_sound_test_server):
    """Test get_output_as_nparray method's warning."""
    tonality = TonalityDIN45681()

    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the 'TonalityDIN45681.process()' method.",
   ):
        DL, Kt, U, DLj, Uj, fTj, Ktj, time, details = tonality.get_output_as_nparray()
    assert np.isnan(DL) == True
    assert np.isnan(Kt) == True
    assert np.isnan(U) == True
    assert len(DLj) == 0
    assert len(Uj) == 0
    assert len(fTj) == 0
    assert len(Ktj) == 0
    assert len(time) == 0
    assert len(details) == 0


def test_tonality_din45681_get_mean_difference(dpf_sound_test_server):
    """Test get_mean_difference method."""
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_non_unitary_calib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityDIN45681(signal=fc[0])
    tonality.process()

    DL = tonality.get_mean_difference()
    assert DL == pytest.approx(EXP_DL)


def test_tonality_din45681_get_uncertainty(dpf_sound_test_server):
    """Test get_uncertainty method."""
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_non_unitary_calib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityDIN45681(signal=fc[0])
    tonality.process()

    U = tonality.get_uncertainty()
    assert U == pytest.approx(EXP_U)


def test_tonality_din45681_get_tonal_adjustment(dpf_sound_test_server):
    """Test get_tonal_adjustment method."""
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_non_unitary_calib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityDIN45681(signal=fc[0])
    tonality.process()

    Kt = tonality.get_tonal_adjustment()
    assert Kt == pytest.approx(EXP_KT)


def test_tonality_din45681_get_decisive_difference_over_time(dpf_sound_test_server):
    """Test get_decisive_difference_over_time method."""
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_non_unitary_calib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityDIN45681(signal=fc[0])
    tonality.process()

    DLj = tonality.get_decisive_difference_over_time()
    assert DLj[3] == pytest.approx(EXP_DLJ3)


def test_tonality_din45681_get_uncertainty_over_time(dpf_sound_test_server):
    """Test get_uncertainty_over_time method."""
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_non_unitary_calib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityDIN45681(signal=fc[0])
    tonality.process()

    Uj = tonality.get_uncertainty_over_time()
    assert Uj[3] == pytest.approx(EXP_UJ3)


def test_tonality_din45681_get_tonal_adjustment_over_time(dpf_sound_test_server):
    """Test get_tonal_adjustment_over_time method."""
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_non_unitary_calib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityDIN45681(signal=fc[0])
    tonality.process()

    Ktj = tonality.get_tonal_adjustment_over_time()
    assert Ktj[3] == pytest.approx(EXP_KTJ3)


def test_tonality_din45681_get_time_scale(dpf_sound_test_server):
    """Test get_time_scale method."""
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_non_unitary_calib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityDIN45681(signal=fc[0])
    tonality.process()

    time = tonality.get_time_scale()
    assert time[3] == pytest.approx(EXP_TIME3)


def test_tonality_din45681_get_spectrum_number(dpf_sound_test_server):
    """Test get_spectrum_number method."""
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_non_unitary_calib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityDIN45681(signal=fc[0])
    tonality.process()

    spectrum_number = tonality.get_spectrum_number()
    assert spectrum_number == EXP_SPECTRUM_NUMBER


def test_tonality_din45681_get_spectrum_details(dpf_sound_test_server):
    """Test get_spectrum_details method."""
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_non_unitary_calib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityDIN45681(signal=fc[0])
    tonality.process()

    details = tonality.get_spectrum_details()
    assert details[3] == pytest.approx(EXP_DETAILS3)


def test_tonality_din45681_get_tone_number(dpf_sound_test_server):
    """Test get_tone_number method."""
    wav_loader = LoadWav(pytest.data_path_flute_non_unitary_calib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityDIN45681(signal=fc[0])
    tonality.process()

    tone_number = tonality.get_tone_number(spectrum_index=2)
    assert tone_number == EXP_TONE_NUMBER


def test_tonality_din45681_get_tone_details(dpf_sound_test_server):
    """Test get_tone_details method."""
    wav_loader = LoadWav(pytest.data_path_flute_non_unitary_calib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityDIN45681(signal=fc[0])
    tonality.process()

    details = tonality.get_tone_details(spectrum_index=2, tone_index=1)
    assert details == pytest.approx(EXP_TONE_DETAILS21)


@patch("matplotlib.pyplot.show")
def test_tonality_din45681_plot(mock_show, dpf_sound_test_server):
    """Test plot method."""
    wav_loader = LoadWav(pytest.data_path_flute_non_unitary_calib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityDIN45681(signal=fc[0])
    tonality.process()

    tonality.plot()


def test_tonality_din45681_plot_exception(dpf_sound_test_server):
    """Test plot method's exception."""
    wav_loader = LoadWav(pytest.data_path_flute_non_unitary_calib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityDIN45681(signal=fc[0])

    with pytest.raises(
        PyAnsysSoundException,
        match="Output is not processed yet. Use the 'TonalityDIN45681.process\\(\\)' method.",
    ):
        tonality.plot()


def test_tonality_din45681___str__(dpf_sound_test_server):
    """Test __str__ method."""
    wav_loader = LoadWav(pytest.data_path_flute_non_unitary_calib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityDIN45681(signal=fc[0])
    tonality.process()

    assert tonality.__str__() == EXP_STR
