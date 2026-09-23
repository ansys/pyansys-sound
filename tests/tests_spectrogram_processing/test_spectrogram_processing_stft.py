# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

from ansys.dpf.core import Field, locations, natures
import numpy as np
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ansys.sound.core.signal_utilities import LoadWav
from ansys.sound.core.spectrogram_processing import Stft

if pytest.SOUND_VERSION_GREATER_THAN_OR_EQUAL_TO_2027R1:
    # bug fix (ID#1515224) in DPF Sound 2027 R1
    EXP_FC_SIZE = 308
    EXP_STFT_SIZE = 154
    EXP_FC_98_0 = -4.276798e-5
    EXP_FC_198_0 = -3.598906e-5
    EXP_FC_298_0 = -4.154918e-5
    TESTED_IDX = 49
    EXP_STFT_100_IDX = -0.0010489814449101686 - 0.0013704965822398663j
    EXP_STFT_200_IDX = 0.0004997600335627794 + 0.0003071507962886244j
    EXP_STFT_300_IDX = -2.9794588044751436e-5 - 0.0004804507188964635j
    EXP_MAGNITUDE_100_IDX = 0.0024407469978254526
    EXP_MAGNITUDE_200_IDX = 0.0008295802586940055
    EXP_MAGNITUDE_300_IDX = 0.0006807651735582324
elif pytest.SOUND_VERSION_GREATER_THAN_OR_EQUAL_TO_2026R1:
    # bug fix (ID#1247009) & third-party update (IPP) in DPF Sound 2026 R1
    EXP_FC_SIZE = 308  # real and complex parts in separate fields
    EXP_STFT_SIZE = 154  # real and complex parts combined (EXP_STFT_SIZE = EXP_FC_SIZE / 2)
    EXP_FC_98_0 = -0.04377303272485733
    EXP_FC_198_0 = -0.03683480620384216
    EXP_FC_298_0 = -0.042525582015514374
    TESTED_IDX = 49  # Not the same index because of the shift in indexes due to bug fix
    EXP_STFT_100_IDX = -1.0736324787139893 - 1.4027032852172852j
    EXP_STFT_200_IDX = 0.5115044116973877 + 0.3143688440322876j
    EXP_STFT_300_IDX = -0.03049476072192192 - 0.4917412996292114j
    EXP_MAGNITUDE_100_IDX = 2.4981045637478467
    EXP_MAGNITUDE_200_IDX = 0.8490754186573622
    EXP_MAGNITUDE_300_IDX = 0.696763139370207
else:  # DPF Sound <= 2025 R2
    EXP_FC_SIZE = 310  # real and complex parts in separate fields
    EXP_STFT_SIZE = 155  # real and complex parts combined (EXP_STFT_SIZE = EXP_FC_SIZE / 2)
    EXP_FC_98_0 = -0.11434437334537506
    EXP_FC_198_0 = -0.09117653965950012
    EXP_FC_298_0 = -0.019828863441944122
    TESTED_IDX = 50
    EXP_STFT_100_IDX = -1.0736324787139893 - 1.4027032852172852j
    EXP_STFT_200_IDX = 0.511505126953125 + 0.3143689036369324j
    EXP_STFT_300_IDX = -0.03049434721469879 - 0.49174121022224426j
    EXP_MAGNITUDE_100_IDX = 2.4981045637478463
    EXP_MAGNITUDE_200_IDX = 0.8490763245706706
    EXP_MAGNITUDE_300_IDX = 0.696762976976946

EXP_PHASE_100_IDX = -2.2240823488563417
EXP_PHASE_200_IDX = 0.5510831859508833
EXP_PHASE_300_IDX = -1.63273084147678

EXP_HALF_NFFT = 1025


@pytest.fixture
def load_flute_wav():
    wav_loader = LoadWav(pytest.data_path_flute)
    wav_loader.process()
    yield wav_loader.get_output()[0]


def test_stft_instantiation():
    """Test the instantiation of Stft class."""
    stft = Stft()
    assert stft != None


def test_stft_process(load_flute_wav):
    """Test the process method of Stft class."""
    stft = Stft()

    # Error 1
    with pytest.raises(PyAnsysSoundException) as excinfo:
        stft.process()
    assert str(excinfo.value) == "No signal found for STFT. Use 'Stft.signal'."

    # Testing input fields container (no error expected)
    stft.signal = load_flute_wav
    try:
        stft.process()
    except:
        # Should not fail
        assert False


def test_stft_get_output(load_flute_wav):
    """Test the get_output method of Stft class."""
    stft = Stft(signal=load_flute_wav)

    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. \
                    Use the 'Stft.process\\(\\)' method.",
    ):
        fc_out = stft.get_output()
    assert fc_out is None

    stft.process()
    fc_out = stft.get_output()

    assert len(fc_out) == EXP_FC_SIZE
    assert len(fc_out[100].data) == stft.fft_size
    assert fc_out[100].data[0] == pytest.approx(EXP_FC_98_0)
    assert fc_out[200].data[0] == pytest.approx(EXP_FC_198_0)
    assert fc_out[300].data[0] == pytest.approx(EXP_FC_298_0)

@pytest.mark.skipif(
    pytest.SOUND_VERSION_GREATER_THAN_OR_EQUAL_TO_2027R1,
    reason="Incorrect STFT values' warning is only produced in versions prior to 2027.1",
)
def test_stft_get_output_version_warning(load_flute_wav):
    """Test the version warning of the get_output method of Stft class."""
    stft = Stft(signal=load_flute_wav)

    with pytest.warns(
        PyAnsysSoundWarning,
        match=(
            "Output STFT is not scaled for RMS spectrum in Sound version prior to 2027.1.0. You can "
            "scale it by dividing the STFT values by the sum of the window values."
        )
    ):
        fc_out = stft.get_output()
    assert fc_out is None


def test_stft_get_output_as_np_array(load_flute_wav):
    """Test the get_output_as_nparray method of Stft class."""
    stft = Stft(signal=load_flute_wav)

    stft.process()
    arr = stft.get_output_as_nparray()

    assert np.shape(arr) == (stft.fft_size, EXP_STFT_SIZE)
    assert type(arr[100, 0]) == np.complex128
    assert arr[100, TESTED_IDX].real == pytest.approx(EXP_STFT_100_IDX.real)
    assert arr[100, TESTED_IDX].imag == pytest.approx(EXP_STFT_100_IDX.imag)
    assert arr[200, TESTED_IDX].real == pytest.approx(EXP_STFT_200_IDX.real)
    assert arr[200, TESTED_IDX].imag == pytest.approx(EXP_STFT_200_IDX.imag)
    assert arr[300, TESTED_IDX].real == pytest.approx(EXP_STFT_300_IDX.real)
    assert arr[300, TESTED_IDX].imag == pytest.approx(EXP_STFT_300_IDX.imag)


def test_stft_get_magnitude(load_flute_wav):
    """Test the get_magnitude method of Stft class."""
    stft = Stft(signal=load_flute_wav)

    stft.process()
    magnitude = stft.get_magnitude()

    assert magnitude.shape == (EXP_HALF_NFFT, EXP_STFT_SIZE)
    assert type(magnitude[100, 0]) == np.float64
    assert magnitude[100, TESTED_IDX] == pytest.approx(EXP_MAGNITUDE_100_IDX)
    assert magnitude[200, TESTED_IDX] == pytest.approx(EXP_MAGNITUDE_200_IDX)
    assert magnitude[300, TESTED_IDX] == pytest.approx(EXP_MAGNITUDE_300_IDX)


def test_stft_get_phase(load_flute_wav):
    """Test the get_phase method of Stft class."""
    stft = Stft(signal=load_flute_wav)

    stft.process()
    phase = stft.get_phase()

    assert phase.shape == (EXP_HALF_NFFT, EXP_STFT_SIZE)
    assert type(phase[100, 0]) == np.float64
    assert phase[100, TESTED_IDX] == pytest.approx(EXP_PHASE_100_IDX)
    assert phase[200, TESTED_IDX] == pytest.approx(EXP_PHASE_200_IDX)
    assert phase[300, TESTED_IDX] == pytest.approx(EXP_PHASE_300_IDX)


def test_stft_set_get_signal():
    """Test the signal setter and getter of Stft class."""
    stft = Stft()
    signal = Field(nentities=1, nature=natures.scalar, location=locations.time_freq)
    signal.data = 42 * np.ones(3)
    stft.signal = signal
    signal = stft.signal

    assert len(signal.data) == 3
    assert signal.data[2] == 42

    # Error
    with pytest.raises(
        PyAnsysSoundException,
        match="Input signal must be provided as a DPF Field.",
    ):
        stft.signal = 2


def test_stft_set_get_fft_size():
    """Test the fft_size setter and getter of Stft class."""
    stft = Stft()

    # Error
    with pytest.raises(PyAnsysSoundException) as excinfo:
        stft.fft_size = -12.0
    assert str(excinfo.value) == "FFT size must be greater than 0.0."

    stft.fft_size = 1234.0
    assert stft.fft_size == 1234.0


def test_stft_set_get_window_overlap():
    """Test the window_overlap setter and getter of Stft class."""
    stft = Stft()

    # Error
    with pytest.raises(PyAnsysSoundException) as excinfo:
        stft.window_overlap = -12.0
    assert str(excinfo.value) == "Window overlap must be between 0.0 and 1.0."

    stft.window_overlap = 0.5
    assert stft.window_overlap == 0.5


def test_stft_set_get_window_type():
    """Test the window_type setter and getter of Stft class."""
    stft = Stft()

    # Error
    with pytest.raises(PyAnsysSoundException) as excinfo:
        stft.window_type = "InvalidWindow"
    assert (
        str(excinfo.value)
        == "Window type is invalid. Options are 'TRIANGULAR', 'BLACKMAN', 'BLACKMANHARRIS', "
        "'HAMMING', 'HANN', 'GAUSS', 'FLATTOP', 'RECTANGULAR', and 'BARTLETT'."
    )

    stft.window_type = "GAUSS"
    assert stft.window_type == "GAUSS"


@patch("matplotlib.pyplot.show")
def test_stft_plot(mock_show, load_flute_wav):
    """Test the plot method of Stft class."""
    stft = Stft(signal=load_flute_wav)
    stft.process()
    stft.plot()
    mock_show.assert_called_once()


def test_stft_plot_exceptions(load_flute_wav):
    """Test the plot method of Stft class."""
    stft = Stft(signal=load_flute_wav)
    with pytest.raises(
        PyAnsysSoundException,
        match="Output is not processed yet. Use the `Stft.process\\(\\)` method.",
    ):
        stft.plot()
    stft.process()


@patch("matplotlib.pyplot.show")
def test_stft_plot_custom(mock_show, load_flute_wav):
    """Test the plot_custom method of Stft class."""
    stft = Stft(signal=load_flute_wav)
    stft.process()
    stft.plot_custom(display_phase=True)
    mock_show.assert_called_once()
    mock_show.reset_mock()
    stft.plot_custom(display_phase=False)
    mock_show.assert_called_once()
    mock_show.reset_mock()
    stft.plot_custom(display_phase=False, display_in_dB=False)
    mock_show.assert_called_once()
    mock_show.reset_mock()
    stft.plot_custom(display_phase=False, display_in_dB=True, reference_value=2e-5)
    mock_show.assert_called_once()
    mock_show.reset_mock()
    stft.plot_custom(
        display_phase=False,
        display_in_dB=True,
        reference_value=2e-5,
        max_magnitude=80.0,
        min_magnitude=0.0,
        max_frequency=5000.0,
        min_frequency=0.0,
        title="Custom STFT plot with all options"
    )
    mock_show.assert_called_once()


def test_stft_plot_custom_exceptions(load_flute_wav):
    """Test the plot_custom method of Stft class for exceptions."""
    stft = Stft(signal=load_flute_wav)
    with pytest.raises(
        PyAnsysSoundException,
        match="Output is not processed yet. Use the `Stft.process\\(\\)` method.",
    ):
        stft.plot_custom()

    stft.process()
    with pytest.raises(
        PyAnsysSoundException,
        match="Reference value for dB conversion must be strictly greater than 0.",
    ):
        stft.plot_custom(reference_value=0.0)
