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
from ansys.sound.core.psychoacoustics import LoudnessISO532_1_TimeVarying
from ansys.sound.core.signal_utilities import LoadWav


def test_loudness_iso_532_1_time_varying_instantiation():
    """Test the instantiation of the LoudnessISO532_1_TimeVarying class."""
    time_varying_loudness_computer = LoudnessISO532_1_TimeVarying()
    assert isinstance(time_varying_loudness_computer, LoudnessISO532_1_TimeVarying)
    assert time_varying_loudness_computer.signal == None
    assert time_varying_loudness_computer.field_type == "Free"


def test_loudness_iso_532_1_time_varying_process():
    """Test the process method of the LoudnessISO532_1_TimeVarying class."""
    time_varying_loudness_computer = LoudnessISO532_1_TimeVarying()

    # no signal -> error 1
    with pytest.raises(PyAnsysSoundException) as excinfo:
        time_varying_loudness_computer.process()
    assert (
        str(excinfo.value)
        == "No signal found for loudness versus time computation."
        + " Use `LoudnessISO532_1_TimeVarying.signal`."
    )

    # get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # set signal as field
    time_varying_loudness_computer.signal = fc[0]

    # compute: no error
    time_varying_loudness_computer.process()
    assert time_varying_loudness_computer._output is not None


def test_loudness_iso_532_1_time_varying_get_output():
    """Test the get_output method of the LoudnessISO532_1_TimeVarying class."""
    time_varying_loudness_computer = LoudnessISO532_1_TimeVarying()

    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    time_varying_loudness_computer.signal = fc[0]

    # Loudness not calculated yet -> warning
    with pytest.warns(
        PyAnsysSoundWarning,
        match=(
            "Output is not processed yet. "
            "Use the `LoudnessISO532_1_TimeVarying.process\\(\\)` method."
        ),
    ):
        output = time_varying_loudness_computer.get_output()
    assert output is None

    # Compute
    time_varying_loudness_computer.process()

    (
        instantaneous_loudness,
        N5,
        N10,
        instantaneous_loudness_level,
        L5,
        L10,
    ) = time_varying_loudness_computer.get_output()
    assert isinstance(instantaneous_loudness, Field)
    assert isinstance(N5, float)
    assert isinstance(N10, float)
    assert isinstance(instantaneous_loudness_level, Field)
    assert isinstance(L5, float)
    assert isinstance(L10, float)


def test_loudness_iso_532_1_time_varying_get_output_as_nparray():
    """Test the get_output_as_nparray method of the LoudnessISO532_1_TimeVarying class."""
    time_varying_loudness_computer = LoudnessISO532_1_TimeVarying()

    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    time_varying_loudness_computer.signal = fc[0]

    # Loudness not calculated yet -> warning
    with pytest.warns(
        PyAnsysSoundWarning,
        match=(
            "Output is not processed yet. "
            "Use the `LoudnessISO532_1_TimeVarying.process\\(\\)` method."
        ),
    ):
        (
            instantaneous_loudness,
            N5,
            N10,
            instantaneous_loudness_level,
            L5,
            L10,
            time_scale,
        ) = time_varying_loudness_computer.get_output_as_nparray()
    assert len(instantaneous_loudness) == 0
    assert np.isnan(N5)
    assert np.isnan(N10)
    assert len(instantaneous_loudness_level) == 0
    assert np.isnan(L5)
    assert np.isnan(L10)
    assert len(time_scale) == 0

    # Compute
    time_varying_loudness_computer.process()

    (
        instantaneous_loudness,
        N5,
        N10,
        instantaneous_loudness_level,
        L5,
        L10,
        time_scale,
    ) = time_varying_loudness_computer.get_output_as_nparray()

    assert type(instantaneous_loudness) == np.ndarray
    assert len(instantaneous_loudness) == 1770
    assert instantaneous_loudness[0] == pytest.approx(0.0)
    assert instantaneous_loudness[10] == pytest.approx(0.06577175855636597)
    assert instantaneous_loudness[100] == pytest.approx(5.100262641906738)
    assert type(instantaneous_loudness_level) == np.ndarray
    assert len(instantaneous_loudness_level) == 1770
    assert instantaneous_loudness_level[0] == pytest.approx(3.0)
    assert instantaneous_loudness_level[10] == pytest.approx(15.430279731750488)
    assert instantaneous_loudness_level[100] == pytest.approx(63.505714416503906)
    assert type(time_scale) == np.ndarray
    assert len(time_scale) == 1770
    assert time_scale[0] == 0
    assert time_scale[10] == pytest.approx(0.019999999552965164)
    assert time_scale[42] == pytest.approx(0.08399999886751175)
    assert time_scale[100] == pytest.approx(0.20000000298023224)
    assert time_scale[110] == pytest.approx(0.2199999988079071)
    assert type(N5) == np.ndarray
    assert N5 == pytest.approx(45.12802505493164)
    assert type(N10) == np.ndarray
    assert N10 == pytest.approx(44.12368392944336)
    assert type(L5) == np.ndarray
    assert L5 == pytest.approx(94.95951843261719)
    assert type(L10) == np.ndarray
    assert L10 == pytest.approx(94.63481140136719)

    time_varying_loudness_computer.field_type = "Diffuse"

    # compute
    time_varying_loudness_computer.process()

    _, N5, N10, _, L5, L10, _ = time_varying_loudness_computer.get_output_as_nparray()
    assert N5 == pytest.approx(47.87789)
    assert N10 == pytest.approx(46.89662)
    assert L5 == pytest.approx(95.81287)
    assert L10 == pytest.approx(95.51412)


def test_loudness_iso_532_1_time_varying_get_loudness_vs_time_sone():
    """Test the get_loudness_sone_vs_time method of the LoudnessISO532_1_TimeVarying class."""
    time_varying_loudness_computer = LoudnessISO532_1_TimeVarying()

    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    time_varying_loudness_computer.signal = fc[0]

    # Compute
    time_varying_loudness_computer.process()

    instantaneous_loudness = time_varying_loudness_computer.get_loudness_sone_vs_time()
    assert type(instantaneous_loudness) == np.ndarray
    assert len(instantaneous_loudness) == 1770
    assert instantaneous_loudness[0] == pytest.approx(0.0)
    assert instantaneous_loudness[10] == pytest.approx(0.06577175855636597)
    assert instantaneous_loudness[100] == pytest.approx(5.100262641906738)


def test_loudness_iso_532_1_time_varying_get_loudness_vs_time_phon():
    """Test the get_loudness_level_phon_vs_time method of the LoudnessISO532_1_TimeVarying class."""
    time_varying_loudness_computer = LoudnessISO532_1_TimeVarying()

    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    time_varying_loudness_computer.signal = fc[0]

    # Compute
    time_varying_loudness_computer.process()

    instantaneous_loudness_level = time_varying_loudness_computer.get_loudness_level_phon_vs_time()
    assert type(instantaneous_loudness_level) == np.ndarray
    assert len(instantaneous_loudness_level) == 1770
    assert instantaneous_loudness_level[0] == pytest.approx(3.0)
    assert instantaneous_loudness_level[10] == pytest.approx(15.430279731750488)
    assert instantaneous_loudness_level[100] == pytest.approx(63.505714416503906)


def test_loudness_iso_532_1_time_varying_get_Nmax_sone():
    """Test the get_Nmax_sone method of the LoudnessISO532_1_TimeVarying class."""
    time_varying_loudness_computer = LoudnessISO532_1_TimeVarying()

    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    time_varying_loudness_computer.signal = fc[0]

    # Compute
    time_varying_loudness_computer.process()

    Nmax = time_varying_loudness_computer.get_Nmax_sone()
    assert Nmax == pytest.approx(46.718074798583984)


def test_loudness_iso_532_1_time_varying_get_N5():
    """Test the get_N5_sone method of the LoudnessISO532_1_TimeVarying class."""
    time_varying_loudness_computer = LoudnessISO532_1_TimeVarying()

    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    time_varying_loudness_computer.signal = fc[0]

    # Compute
    time_varying_loudness_computer.process()

    N5 = time_varying_loudness_computer.get_N5_sone()
    assert N5 == pytest.approx(45.12802505493164)


def test_loudness_iso_532_1_time_varying_get_N10():
    """Test the get_N10_sone method of the LoudnessISO532_1_TimeVarying class."""
    time_varying_loudness_computer = LoudnessISO532_1_TimeVarying()

    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    time_varying_loudness_computer.signal = fc[0]

    # Compute
    time_varying_loudness_computer.process()

    N10 = time_varying_loudness_computer.get_N10_sone()
    assert N10 == pytest.approx(44.12368392944336)


def test_loudness_iso_532_1_time_varying_get_Lmax_phon():
    """Test the get_Lmax_phon method of the LoudnessISO532_1_TimeVarying class."""
    time_varying_loudness_computer = LoudnessISO532_1_TimeVarying()

    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    time_varying_loudness_computer.signal = fc[0]

    # Compute
    time_varying_loudness_computer.process()

    Lmax = time_varying_loudness_computer.get_Lmax_phon()
    assert Lmax == pytest.approx(95.45909118652344)


def test_loudness_iso_532_1_time_varying_get_L5():
    """Test the get_L5_phon method of the LoudnessISO532_1_TimeVarying class."""
    time_varying_loudness_computer = LoudnessISO532_1_TimeVarying()

    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    time_varying_loudness_computer.signal = fc[0]

    # Compute
    time_varying_loudness_computer.process()

    L5 = time_varying_loudness_computer.get_L5_phon()
    assert L5 == pytest.approx(94.95951843261719)


def test_loudness_iso_532_1_time_varying_get_L10():
    """Test the get_L10_phon method of the LoudnessISO532_1_TimeVarying class."""
    time_varying_loudness_computer = LoudnessISO532_1_TimeVarying()

    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    time_varying_loudness_computer.signal = fc[0]

    # Compute
    time_varying_loudness_computer.process()

    L10 = time_varying_loudness_computer.get_L10_phon()
    assert L10 == pytest.approx(94.63481140136719)


def test_loudness_iso_532_1_time_varying_get_time_scale():
    """Test the get_time_scale method of the LoudnessISO532_1_TimeVarying class."""
    time_varying_loudness_computer = LoudnessISO532_1_TimeVarying()

    # Get a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    time_varying_loudness_computer.signal = fc[0]

    # Compute
    time_varying_loudness_computer.process()

    time_scale = time_varying_loudness_computer.get_time_scale()
    assert len(time_scale) == 1770
    assert time_scale[0] == 0
    assert time_scale[10] == pytest.approx(0.019999999552965164)
    assert time_scale[42] == pytest.approx(0.08399999886751175)
    assert time_scale[100] == pytest.approx(0.20000000298023224)
    assert time_scale[110] == pytest.approx(0.2199999988079071)


@patch("matplotlib.pyplot.show")
def test_loudness_iso_532_1_time_varying_plot(mock_show):
    """Test the plot method of the LoudnessISO532_1_TimeVarying class."""
    time_varying_loudness_computer = LoudnessISO532_1_TimeVarying()

    # Load a signal
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    time_varying_loudness_computer.signal = fc[0]

    # Plot before process -> error
    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "Output is not processed yet. Use the "
            "`LoudnessISO532_1_TimeVarying.process\\(\\)` method."
        ),
    ):
        time_varying_loudness_computer.plot()

    # Compute
    time_varying_loudness_computer.process()

    # Plot
    time_varying_loudness_computer.plot()


def test_loudness_iso_532_1_time_varying_set_get_signal():
    """Test the set and get signal methods of the LoudnessISO532_1_TimeVarying class."""
    time_varying_loudness_computer = LoudnessISO532_1_TimeVarying()
    f_signal = Field()
    f_signal.data = 42 * np.ones(3)
    time_varying_loudness_computer.signal = f_signal
    f_signal_from_get = time_varying_loudness_computer.signal

    assert f_signal_from_get.data[0, 2] == 42

    # Set invalid value
    with pytest.raises(PyAnsysSoundException, match="Signal must be specified as a DPF field."):
        time_varying_loudness_computer.signal = "WrongType"


def test_loudness_iso_532_1_time_varying_set_get_field_type():
    """Test the field_type property of the LoudnessISO532_1_TimeVarying class."""
    time_varying_loudness_computer = LoudnessISO532_1_TimeVarying()

    # Set value
    time_varying_loudness_computer.field_type = "Diffuse"
    assert time_varying_loudness_computer.field_type == "Diffuse"

    # Check case insensitivity
    time_varying_loudness_computer.field_type = "diffuse"
    assert time_varying_loudness_computer.field_type == "diffuse"

    time_varying_loudness_computer.field_type = "DIFFUSE"
    assert time_varying_loudness_computer.field_type == "DIFFUSE"

    # Set invalid value
    with pytest.raises(
        PyAnsysSoundException,
        match='Invalid field type "Invalid". Available options are "Free" and "Diffuse".',
    ):
        time_varying_loudness_computer.field_type = "Invalid"
