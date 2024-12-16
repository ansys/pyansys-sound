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

from ansys.dpf.core import Field, Operator, TimeFreqSupport, fields_factory, locations
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ansys.sound.core.signal_utilities import LoadWav
from ansys.sound.core.spectral_processing import Filter

EXP_STR_NOT_SET = (
    "Sampling frequency: 44100.0 Hz\n"
    "Numerator coefficients (B): Not set\n"
    "Denominator coefficients (A): Not set"
)
EXP_STR_ALL_SET = (
    "Sampling frequency: 44100.0 Hz\n"
    "Numerator coefficients (B): [4, 5, 6]\n"
    "Denominator coefficients (A): [1, 2, 3]"
)
EXP_STR_ALL_SET_MORE_COEFFS = (
    "Sampling frequency: 44100.0 Hz\n"
    "Numerator coefficients (B): [106.19685363769531, -113.11087036132812, -77.88863372802734, "
    "-45.08974075317383, -17.067110061645508, ... ]\n"
    "Denominator coefficients (A): [106.19685363769531, -113.11087036132812, -77.88863372802734, "
    "-45.08974075317383, -17.067110061645508, ... ]"
)

EXP_B0 = 106.19685364
EXP_B2 = -77.88863373
EXP_B13 = 2.69651508
EXP_OUTPUT8834 = 1.3717
EXP_OUTPUT13536 = -20.8752
EXP_OUTPUT24189 = 51.0042
EXP_OUTPUT43544 = -17.2570


def test_filter_instantiation_no_arg():
    """Test Filter instantiation without arguments."""
    filter = Filter()
    assert isinstance(filter, Filter)
    assert len(filter.a_coefficients) == 0
    assert len(filter.b_coefficients) == 0
    assert filter.signal is None


def test_filter_instantiation_args():
    """Test Filter instantiation without arguments."""
    # Create a field to use in a suitable Field object (signal).
    fs = 44100.0
    support = TimeFreqSupport()
    f_time = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
    f_time.append([0, 1 / fs, 2 / fs, 3 / fs], 1)
    support.time_frequencies = f_time
    f_signal = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
    f_signal.append([1, 2, 3, 4], 1)
    f_signal.time_freq_support = support

    # Test instantiation.
    with pytest.warns(
        PyAnsysSoundWarning,
        match=(
            "Specified parameters a_coefficients and b_coefficients are ignored because FRF file "
            "is also specified."
        ),
    ):
        filter = Filter(
            a_coefficients=[1, 2, 3],
            b_coefficients=[4, 5, 6],
            sampling_frequency=fs,
            file=pytest.data_path_filter_frf,
            signal=f_signal,
        )
    assert isinstance(filter, Filter)
    assert filter.a_coefficients is not []
    assert filter.b_coefficients is not []
    assert filter.signal is not None


def test_filter___str__():
    """Test Filter __str__ method."""
    filter = Filter()
    assert str(filter) == EXP_STR_NOT_SET

    filter.a_coefficients = [1, 2, 3]
    filter.b_coefficients = [4, 5, 6]
    assert str(filter) == EXP_STR_ALL_SET

    filter.design_FIR_from_FRF_file(file=pytest.data_path_filter_frf)
    filter.a_coefficients = filter.b_coefficients
    assert str(filter) == EXP_STR_ALL_SET_MORE_COEFFS


def test_filter_properties():
    """Test Filter properties."""
    fs = 44100.0

    filter = Filter(sampling_frequency=fs)

    # Test property a_coefficients.
    filter.a_coefficients = [1, 2, 3]
    assert filter.a_coefficients == [1, 2, 3]

    # Test property b_coefficients.
    filter.b_coefficients = [4, 5, 6]
    assert filter.b_coefficients == [4, 5, 6]

    # Test property signal.
    support = TimeFreqSupport()
    f_time = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
    f_time.append([0, 1 / fs, 2 / fs, 3 / fs], 1)
    support.time_frequencies = f_time
    f_signal = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
    f_signal.append([1, 2, 3, 4], 1)
    f_signal.time_freq_support = support
    filter.signal = f_signal
    assert isinstance(filter.signal, Field)


def test_filter_properties_exceptions():
    """Test Filter properties' exceptions."""
    filter = Filter()

    # Test property signal's exception 1 (wrong type).
    with pytest.raises(
        PyAnsysSoundException,
        match="Specified signal must be provided as a DPF field.",
    ):
        filter.signal = "string"

    # Test property signal's exception 2 (wrong number of samples).
    support = TimeFreqSupport()
    f_time = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
    f_time.append([0], 1)
    support.time_frequencies = f_time
    f_signal = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
    f_signal.append([0], 1)
    f_signal.time_freq_support = support
    with pytest.raises(
        PyAnsysSoundException,
        match="Specified signal must have at least two samples.",
    ):
        filter.signal = f_signal

    # Test property signal's exception 3 (wrong sampling frequency).
    f_time.append([1], 1)
    f_signal.append([1], 1)
    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "Specified signal's sampling frequency \\(1.0 Hz\\) must match the filter's sampling "
            "frequency \\(44100.0 Hz\\) that was specified as an instantiation argument of the "
            "class Filter."
        ),
    ):
        filter.signal = f_signal


def test_filter_get_sampling_frequency():
    """Test Filter get_sampling_frequency method."""
    fs = 48000.0

    filter = Filter(sampling_frequency=fs)
    assert filter.get_sampling_frequency() == fs


def test_filter_design_FIR_from_FRF_file():
    """Test Filter design_FIR_from_FRF method."""
    filter = Filter()
    filter.design_FIR_from_FRF_file(file=pytest.data_path_filter_frf)
    assert len(filter.a_coefficients) == 1
    assert filter.a_coefficients[0] == pytest.approx(1.0)
    assert filter.b_coefficients[0] == pytest.approx(EXP_B0)
    assert filter.b_coefficients[2] == pytest.approx(EXP_B2)
    assert filter.b_coefficients[13] == pytest.approx(EXP_B13)

    # Load wrong-header file (DPF error).
    with pytest.raises(Exception):
        filter.design_FIR_from_FRF_file(file=pytest.data_path_filter_frf_wrong_header)


def test_filter_design_FIR_from_FRF():
    """Test Filter design_FIR_from_FRF method."""
    op = Operator("load_FRF_from_txt")
    op.connect(0, pytest.data_path_filter_frf)
    op.run()
    frf = op.get_output(0, "field")

    filter = Filter()
    filter.design_FIR_from_FRF(frf=frf)
    assert len(filter.a_coefficients) == 1
    assert filter.a_coefficients[0] == pytest.approx(1.0)
    assert filter.b_coefficients[0] == pytest.approx(EXP_B0)
    assert filter.b_coefficients[2] == pytest.approx(EXP_B2)
    assert filter.b_coefficients[13] == pytest.approx(EXP_B13)


def test_filter_process():
    """Test Filter process method."""
    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc_signal = wav_loader.get_output()

    filter = Filter(signal=fc_signal[0])
    filter.a_coefficients = [1.0]
    filter.b_coefficients = [1.0, 0.5]

    filter.process()
    assert filter._output is not None


def test_filter_process_exceptions():
    """Test Filter process method's exceptions."""
    fs = 44100.0

    filter = Filter(sampling_frequency=fs)

    # Test process method exception1 (missing signal).
    with pytest.raises(
        PyAnsysSoundException,
        match="Input signal is not set. Use Filter.signal.",
    ):
        filter.process()

    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc_signal = wav_loader.get_output()
    filter.signal = fc_signal[0]

    # Test process method exception2 (missing a coefficients).
    filter.b_coefficients = [1, 2, 3]
    filter.a_coefficients = []
    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "Filter's denominator coefficients \\(a_coefficients\\) cannot be empty. Use "
            "Filter.a_coefficients, or the methods Filter.design_FIR_from_FRF\\(\\) or "
            "Filter.design_FIR_from_FRF_file\\(\\)."
        ),
    ):
        filter.process()

    # Test process method exception3 (missing b coefficients).
    filter.b_coefficients = []
    filter.a_coefficients = [1, 2, 3]
    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "Filter's numerator coefficients \\(b_coefficients\\) cannot be empty. Use "
            "Filter.b_coefficients, or the methods Filter.design_FIR_from_FRF\\(\\) or "
            "Filter.design_FIR_from_FRF_file\\(\\)."
        ),
    ):
        filter.process()


def test_filter_get_output():
    """Test Filter get_output method."""
    filter = Filter(file=pytest.data_path_filter_frf)
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the Filter.process\\(\\) method.",
    ):
        output = filter.get_output()
    assert output is None

    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc_signal = wav_loader.get_output()

    filter.signal = fc_signal[0]
    filter.process()
    output = filter.get_output()

    assert output.data[8834] == pytest.approx(EXP_OUTPUT8834)
    assert output.data[13536] == pytest.approx(EXP_OUTPUT13536)
    assert output.data[24189] == pytest.approx(EXP_OUTPUT24189)
    assert output.data[43544] == pytest.approx(EXP_OUTPUT43544)


def test_filter_get_output_as_nparray():
    """Test Filter get_output_asnparray method."""
    filter = Filter(file=pytest.data_path_filter_frf)
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the Filter.process\\(\\) method.",
    ):
        output = filter.get_output_as_nparray()
    assert len(output) == 0

    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc_signal = wav_loader.get_output()

    filter.signal = fc_signal[0]
    filter.process()
    output_nparray = filter.get_output_as_nparray()

    assert output_nparray[8834] == pytest.approx(EXP_OUTPUT8834)
    assert output_nparray[13536] == pytest.approx(EXP_OUTPUT13536)
    assert output_nparray[24189] == pytest.approx(EXP_OUTPUT24189)
    assert output_nparray[43544] == pytest.approx(EXP_OUTPUT43544)


@patch("matplotlib.pyplot.show")
def test_filter_plot(mock_show):
    """Test SourceAudio plot method."""
    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc_signal = wav_loader.get_output()

    filter = Filter(file=pytest.data_path_filter_frf, signal=fc_signal[0])
    filter.process()
    filter.plot()


def test_filter_plot_exception():
    """Test SourceAudio plot method's exception."""
    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc_signal = wav_loader.get_output()

    filter = Filter(file=pytest.data_path_filter_frf, signal=fc_signal[0])

    with pytest.raises(
        PyAnsysSoundException,
        match="Output is not processed yet. Use the Filter.process\\(\\) method.",
    ):
        filter.plot()
