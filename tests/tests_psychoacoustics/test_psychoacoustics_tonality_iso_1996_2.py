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
import numpy as np
import pytest
import regex as re

from ansys.sound.core._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ansys.sound.core.psychoacoustics import TonalityISO1996_2
from ansys.sound.core.signal_utilities import LoadWav

EXP_TONALITY = 43.122661590576172
EXP_TONAL_ADJ = 6.0
EXP_CB_LOW = 211.32544
EXP_CB_HIGH = 311.32544
EXP_TOTAL_NOISE = 27.298639
EXP_TOTAL_TONAL = 68.343742

EXP_STR_1 = (
    "TonalityISO1996_2 object.\n"
    + "Data\n"
    + f'Signal name: "flute"\n'
    + f"Noise pause detection threshold: 2.0 dB\n"
    + f"Effective analysis bandwidth: 4.0 Hz\n"
    + f"Noise bandwidth in proportion to CBW: 0.8\n"
    + f"Tonal audibility: Not processed\n"
    + f"Tonal adjustment Kt: Not processed\n"
)

EXP_STR_2 = (
    "TonalityISO1996_2 object.\n"
    + "Data\n"
    + f'Signal name: "flute"\n'
    + f"Noise pause detection threshold: 2.0 dB\n"
    + f"Effective analysis bandwidth: 4.0 Hz\n"
    + f"Noise bandwidth in proportion to CBW: 0.8\n"
    + f"Tonal audibility: 43.1 dB\n"
    + f"Tonal adjustment Kt: 6.0 dB\n"
)


def test_tonality_iso_1996_2_instantiation():
    """Test TonalityISO1996_2 instantiation."""
    tonality = TonalityISO1996_2()
    assert tonality.signal == None
    assert tonality.noise_pause_threshold == 1.0
    assert tonality.effective_analysis_bandwidth == 5.0
    assert tonality.noise_bandwidth_ratio == 0.75


def test_tonality_iso_1996_2_properties():
    """Test TonalityISO1996_2 properties."""
    tonality = TonalityISO1996_2()
    tonality.signal = Field()
    assert type(tonality.signal) == Field

    tonality.noise_pause_threshold = 2.0
    assert tonality.noise_pause_threshold == 2.0

    tonality.noise_pause_threshold = 4
    assert tonality.noise_pause_threshold == 4.0

    tonality.effective_analysis_bandwidth = 3.0
    assert tonality.effective_analysis_bandwidth == 3.0


def test_tonality_iso_1996_2___str__():
    """Test __str__ method."""
    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()
    sig = fc[0]

    tonality = TonalityISO1996_2(
        signal=sig,
        noise_pause_threshold=2.0,
        effective_analysis_bandwidth=4.0,
        noise_bandwidth_ratio=0.8,
    )
    assert tonality.__str__() == EXP_STR_1
    tonality.process()
    assert tonality.__str__() == EXP_STR_2


def test_tonality_iso_1996_2_setters_exceptions():
    """Test setters' exceptions."""
    tonality = TonalityISO1996_2()

    with pytest.raises(
        PyAnsysSoundException,
        match="Signal must be specified as a DPF field.",
    ):
        tonality.signal = "signal"

    with pytest.raises(
        PyAnsysSoundException,
        match="Noise pause threshold must be provided as a float value.",
    ):
        tonality.noise_pause_threshold = "-1.0"

    with pytest.raises(
        PyAnsysSoundException,
        match=re.escape("Effective analysis bandwidth must be in the range [0.0; 5.0] Hz."),
    ):
        tonality.effective_analysis_bandwidth = 6.0

    with pytest.raises(
        PyAnsysSoundException,
        match=re.escape(
            "Noise critical bandwidth ratio must be provided as a float value,"
            "in the range [0.75; 2.0]."
        ),
    ):
        tonality.noise_bandwidth_ratio = 3.0


def test_tonality_iso_1996_2_process():
    """Test process method."""
    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()
    sig = fc[0]

    tonality = TonalityISO1996_2(
        signal=sig,
        noise_pause_threshold=2.0,
        effective_analysis_bandwidth=4.0,
        noise_bandwidth_ratio=0.8,
    )
    tonality.process()
    assert tonality._output is not None


def test_tonality_iso_1996_2_process_exception():
    """Test process method's exception."""
    tonality = TonalityISO1996_2()

    with pytest.raises(
        PyAnsysSoundException,
        match="No input signal defined. Use ``TonalityISO1996_2.signal``.",
    ):
        tonality.process()


def test_tonality_iso_1996_2_get_output():
    """Test get_output method."""
    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()
    sig = fc[0]
    tonality = TonalityISO1996_2(
        signal=sig,
        noise_pause_threshold=2.0,
        effective_analysis_bandwidth=4.0,
        noise_bandwidth_ratio=0.8,
    )
    tonality.process()
    output = tonality.get_output()
    assert output is not None


def test_tonality_iso_1996_2_get_output_unprocessed():
    """Test get_output method's warning."""
    tonality = TonalityISO1996_2()

    with pytest.warns(
        PyAnsysSoundWarning,
        match=(
            "Output is not processed yet. Use the ``TonalityISO1996_2.process\(\)`` method."  # noqa: E501
        ),
    ):
        output = tonality.get_output()
    assert output is None


def test_tonality_iso_1996_2_get_output_as_nparray():
    """Test get_output_as_nparray method."""
    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()
    sig = fc[0]
    tonality = TonalityISO1996_2(
        signal=sig,
        noise_pause_threshold=2.0,
        effective_analysis_bandwidth=4.0,
        noise_bandwidth_ratio=0.8,
    )
    tonality.process()

    tonality, adjustment, details = tonality.get_output_as_nparray()

    assert tonality == pytest.approx(EXP_TONALITY)
    assert adjustment == pytest.approx(EXP_TONAL_ADJ)
    assert details[0] == pytest.approx(EXP_CB_LOW)
    assert details[1] == pytest.approx(EXP_CB_HIGH)
    assert details[2] == pytest.approx(EXP_TOTAL_NOISE)
    assert details[3] == pytest.approx(EXP_TOTAL_TONAL)


def test_tonality_iso_1996_2_get_output_as_nparray_unprocessed():
    """Test get_output_as_nparray method's warning."""
    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()
    sig = fc[0]
    tonality = TonalityISO1996_2(
        signal=sig,
        noise_pause_threshold=2.0,
        effective_analysis_bandwidth=4.0,
        noise_bandwidth_ratio=0.8,
    )

    with pytest.warns(
        PyAnsysSoundWarning,
        match=(
            "Output is not processed yet. Use the ``TonalityISO1996_2.process\(\)`` method."  # noqa: E501
        ),
    ):
        tonality, adjustment, details = tonality.get_output_as_nparray()

    assert np.isnan(tonality)
    assert np.isnan(adjustment)
    assert len(details) == 0


def test_tonality_iso_1996_2_get_tonal_audibility():
    """Test get_tonal_audibility method."""
    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()
    sig = fc[0]
    tonality = TonalityISO1996_2(
        signal=sig,
        noise_pause_threshold=2.0,
        effective_analysis_bandwidth=4.0,
        noise_bandwidth_ratio=0.8,
    )
    tonality.process()
    assert tonality.get_tonal_audibility() == pytest.approx(EXP_TONALITY)


def test_tonality_iso_1996_2_get_tonal_adjustment():
    """Test get_tonal_adjustment method."""
    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()
    sig = fc[0]
    tonality = TonalityISO1996_2(
        signal=sig,
        noise_pause_threshold=2.0,
        effective_analysis_bandwidth=4.0,
        noise_bandwidth_ratio=0.8,
    )

    tonality.process()
    assert tonality.get_tonal_adjustment() == pytest.approx(EXP_TONAL_ADJ)


def test_tonality_iso_1996_2_get_computation_details():
    """Test get_computation_details method."""
    wav_loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()
    sig = fc[0]
    tonality = TonalityISO1996_2(
        signal=sig,
        noise_pause_threshold=2.0,
        effective_analysis_bandwidth=4.0,
        noise_bandwidth_ratio=0.8,
    )
    tonality.process()

    details = tonality.get_computation_details()
    assert details["Lower critical band limit (Hz)"] == pytest.approx(EXP_CB_LOW)
    assert details["Higher critical band limit (Hz)"] == pytest.approx(EXP_CB_HIGH)
    assert details["Total noise level (dBA)"] == pytest.approx(EXP_TOTAL_NOISE)
    assert details["Total tonal level (dBA)"] == pytest.approx(EXP_TOTAL_TONAL)


def test_tonality_iso_1996_2_get_computation_details_unprocessed():
    """Test get_computation_details method's warning."""
    tonality = TonalityISO1996_2()

    with pytest.warns(
        PyAnsysSoundWarning,
        match=(
            "Output is not processed yet. Use the ``TonalityISO1996_2.process\(\)`` method."  # noqa: E501
        ),
    ):
        details = tonality.get_computation_details()

    assert type(details) == dict
    assert len(details) == 0


def test_tonality_iso_1996_2_plot():
    """Test plot method."""
    tonality = TonalityISO1996_2()
    with pytest.warns(
        PyAnsysSoundWarning, match="This method is not implemented for class TonalityISO1996_2."
    ):
        tonality.plot()
