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
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANtaBILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from unittest.mock import patch

from ansys.dpf.core import Field
from ansys.dpf.core.collection import Collection
import numpy as np
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ansys.sound.core.psychoacoustics import TonalityISO1996_2_OverTime
from ansys.sound.core.signal_utilities import LoadWav

EXP_TIME3 = 1.312472
EXP_SEGMENT_COUNT = 96
EXP_SEGMENT3_TA = 15.31328
EXP_SEGMENT3_KT = 6.0
EXP_SEGMENT3_START = 0.787483
EXP_SEGMENT3_END = 1.837483
EXP_SEGMENT3_CB_L = 750.0
EXP_SEGMENT3_CB_U = 916.6667
EXP_SEGMENT3_LPT = 66.82337
EXP_SEGMENT3_LPN = 54.16815
EXP_STR_UNPROCESSED = (
    "TonalityISO1996_2_OverTime object\n"
    "Data:\n"
    f"\tSignal name: Not set\n"
    f"\tIntegration window length: 1000.0 ms\n"
    f"\tOverlap: 75.0 %\n"
    f"\tNoise pause detection threshold: 1.0 dB\n"
    f"\tEffective analysis bandwidth: 5.0 Hz\n"
    f"\tNoise bandwidth in proportion to critical bandwidth: 0.75\n"
    f"Number of segments: Not processed\n"
    f"Maximum tonal audibility: Not processed\n"
    f"Maximum tonal adjustment: Not processed"
)
EXP_STR_PROCESSED = (
    "TonalityISO1996_2_OverTime object\n"
    "Data:\n"
    f'\tSignal name: "Aircraft-App2"\n'
    f"\tIntegration window length: 1000.0 ms\n"
    f"\tOverlap: 75.0 %\n"
    f"\tNoise pause detection threshold: 1.0 dB\n"
    f"\tEffective analysis bandwidth: 5.0 Hz\n"
    f"\tNoise bandwidth in proportion to critical bandwidth: 0.75\n"
    f"Number of segments: 96\n"
    f"Maximum tonal audibility: 25.7 dB\n"
    f"Maximum tonal adjustment: 6.0 dB"
)


def test_tonality_iso_1996_2_over_time_instantiation():
    """Test instantiation."""
    tonality = TonalityISO1996_2_OverTime()
    assert tonality.signal == None
    assert tonality.window_length == pytest.approx(1000.0)
    assert tonality.overlap == pytest.approx(75.0)
    assert tonality.noise_pause_threshold == pytest.approx(1.0)
    assert tonality.effective_analysis_bandwidth == pytest.approx(5.0)
    assert tonality.noise_bandwidth_ratio == pytest.approx(0.75)


def test_tonality_iso_1996_2_over_time___str__():
    """Test __str__ method."""
    tonality = TonalityISO1996_2_OverTime()
    assert tonality.__str__() == EXP_STR_UNPROCESSED

    wav_loader = LoadWav(pytest.data_path_aircraft_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality.signal = fc[0]
    tonality.process()
    assert tonality.__str__() == EXP_STR_PROCESSED


def test_tonality_iso_1996_2_over_time_properties():
    """Test properties."""
    tonality = TonalityISO1996_2_OverTime()
    tonality.signal = Field()
    assert type(tonality.signal) == Field

    tonality.window_length = 500.0
    assert tonality.window_length == 500.0

    tonality.overlap = 15.6
    assert tonality.overlap == 15.6

    tonality.noise_pause_threshold = 2.0
    assert tonality.noise_pause_threshold == 2.0

    tonality.effective_analysis_bandwidth = 10.0
    assert tonality.effective_analysis_bandwidth == 10.0

    tonality.noise_bandwidth_ratio = 1.5
    assert tonality.noise_bandwidth_ratio == 1.5


def test_tonality_iso_1996_2_over_time_setters_exceptions():
    """Test setters' exceptions."""
    tonality = TonalityISO1996_2_OverTime()
    with pytest.raises(
        PyAnsysSoundException,
        match="Signal must be specified as a DPF field.",
    ):
        tonality.signal = "Invalid"

    with pytest.raises(
        PyAnsysSoundException, match="Integration window length must be greater than 0 ms."
    ):
        tonality.window_length = 0.0

    with pytest.raises(
        PyAnsysSoundException,
        match="Overlap must be greater than or equal to 0 %, and strictly smaller than 100 %",
    ):
        tonality.overlap = 100.0

    with pytest.raises(
        PyAnsysSoundException,
        match="Noise pause detection threshold must be greater than 0 dB.",
    ):
        tonality.noise_pause_threshold = 0.0

    with pytest.raises(
        PyAnsysSoundException,
        match="Effective analysis bandwidth must be greater than 0 Hz.",
    ):
        tonality.effective_analysis_bandwidth = 0.0

    with pytest.raises(
        PyAnsysSoundException,
        match="Noise bandwidth ratio must be between 0.75 and 2.",
    ):
        tonality.noise_bandwidth_ratio = 0.0


def test_tonality_iso_1996_2_over_time_process():
    """Test process method."""
    wav_loader = LoadWav(pytest.data_path_aircraft_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityISO1996_2_OverTime(signal=fc[0])
    tonality.process()


def test_tonality_iso_1996_2_over_time_process_exception():
    """Test process method's exception."""
    tonality = TonalityISO1996_2_OverTime()

    with pytest.raises(
        PyAnsysSoundException,
        match="No input signal is set. Use ``TonalityISO1996_2_OverTime.signal``.",
    ):
        tonality.process()


def test_tonality_iso_1996_2_over_time_get_output():
    """Test get_output method."""
    wav_loader = LoadWav(pytest.data_path_aircraft_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityISO1996_2_OverTime(signal=fc[0])
    tonality.process()

    output = tonality.get_output()
    assert isinstance(output[0], Field)
    assert isinstance(output[1], Field)
    assert isinstance(output[2], Collection)


def test_tonality_iso_1996_2_over_time_get_output_unprocessed():
    """Test get_output method's warning."""
    tonality = TonalityISO1996_2_OverTime()

    with pytest.warns(
        PyAnsysSoundWarning,
        match=(
            "Output is not processed yet. Use the ``TonalityISO1996_2_OverTime.process\\(\\)`` "
            "method."
        ),
    ):
        output = tonality.get_output()
    assert output is None


def test_tonality_iso_1996_2_over_time_get_output_as_nparray():
    """Test get_output_as_nparray method."""
    wav_loader = LoadWav(pytest.data_path_aircraft_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityISO1996_2_OverTime(signal=fc[0])
    tonality.process()

    ta, Kt, time = tonality.get_output_as_nparray()
    assert len(ta) == len(Kt) == len(time) == EXP_SEGMENT_COUNT
    assert ta[3] == pytest.approx(EXP_SEGMENT3_TA)
    assert Kt[3] == pytest.approx(EXP_SEGMENT3_KT)
    assert time[3] == pytest.approx(EXP_TIME3)


def test_tonality_iso_1996_2_over_time_get_output_as_nparray_unprocessed():
    """Test get_output_as_nparray method's warning."""
    tonality = TonalityISO1996_2_OverTime()

    with pytest.warns(
        PyAnsysSoundWarning,
        match=(
            "Output is not processed yet. Use the ``TonalityISO1996_2_OverTime.process\\(\\)`` "
            "method."
        ),
    ):
        ta, Kt, time = tonality.get_output_as_nparray()
    assert len(ta) == len(Kt) == len(time) == 0


def test_tonality_iso_1996_2_over_time_get_tonal_audibility_over_time():
    """Test get_tonal_audibility_over_time method."""
    wav_loader = LoadWav(pytest.data_path_aircraft_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityISO1996_2_OverTime(signal=fc[0])
    tonality.process()

    assert tonality.get_tonal_audibility_over_time()[3] == pytest.approx(EXP_SEGMENT3_TA)


def test_tonality_iso_1996_2_over_time_get_tonal_adjustment_over_time():
    """Test get_tonal_adjustment_over_time method."""
    wav_loader = LoadWav(pytest.data_path_aircraft_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityISO1996_2_OverTime(signal=fc[0])
    tonality.process()

    assert tonality.get_tonal_adjustment_over_time()[3] == pytest.approx(EXP_SEGMENT3_KT)


def test_tonality_iso_1996_2_over_time_get_time_scale():
    """Test get_time_scale method."""
    wav_loader = LoadWav(pytest.data_path_aircraft_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityISO1996_2_OverTime(signal=fc[0])
    tonality.process()

    assert tonality.get_time_scale()[3] == pytest.approx(EXP_TIME3)


def test_tonality_iso_1996_2_over_time_get_segment_count():
    """Test get_segment_count method."""
    wav_loader = LoadWav(pytest.data_path_aircraft_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityISO1996_2_OverTime(signal=fc[0])
    tonality.process()

    assert tonality.get_segment_count() == EXP_SEGMENT_COUNT


def test_tonality_iso_1996_2_over_time_get_segment_details():
    """Test get_segment_details method."""
    wav_loader = LoadWav(pytest.data_path_aircraft_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityISO1996_2_OverTime(signal=fc[0])
    tonality.process()

    dict_details = tonality.get_segment_details(segment_index=3)
    assert dict_details["segment_start_time_s"] == pytest.approx(EXP_SEGMENT3_START)
    assert dict_details["segment_end_time_s"] == pytest.approx(EXP_SEGMENT3_END)
    assert dict_details["lower_critical_band_limit_Hz"] == pytest.approx(EXP_SEGMENT3_CB_L)
    assert dict_details["higher_critical_band_limit_Hz"] == pytest.approx(EXP_SEGMENT3_CB_U)
    assert dict_details["total_tonal_level_dBA"] == pytest.approx(EXP_SEGMENT3_LPT)
    assert dict_details["total_noise_level_dBA"] == pytest.approx(EXP_SEGMENT3_LPN)


def test_tonality_iso_1996_2_over_time_get_segment_details_exceptions():
    """Test get_segment_details method's exception."""
    wav_loader = LoadWav(pytest.data_path_aircraft_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityISO1996_2_OverTime(signal=fc[0])

    with pytest.warns(
        PyAnsysSoundWarning,
        match=(
            "Output is not processed yet. Use the ``TonalityISO1996_2_OverTime.process\\(\\)`` "
            "method."
        ),
    ):
        dict_details = tonality.get_segment_details(segment_index=0)
    assert np.isnan(dict_details["segment_start_time_s"])
    assert np.isnan(dict_details["segment_end_time_s"])
    assert np.isnan(dict_details["lower_critical_band_limit_Hz"])
    assert np.isnan(dict_details["higher_critical_band_limit_Hz"])
    assert np.isnan(dict_details["total_tonal_level_dBA"])
    assert np.isnan(dict_details["total_noise_level_dBA"])

    tonality.process()

    with pytest.raises(
        PyAnsysSoundException,
        match="Segment index 96 is out of range. It must be between 0 and 95.",
    ):
        tonality.get_segment_details(segment_index=96)


@patch("matplotlib.pyplot.show")
def test_tonality_iso_1996_2_over_time_plot(mock_show):
    """Test plot method."""
    wav_loader = LoadWav(pytest.data_path_aircraft_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityISO1996_2_OverTime(signal=fc[0])
    tonality.process()

    tonality.plot()


def test_tonality_iso_1996_2_over_time_plot_exception():
    """Test plot method's exception."""
    wav_loader = LoadWav(pytest.data_path_aircraft_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    tonality = TonalityISO1996_2_OverTime(signal=fc[0])

    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "Output is not processed yet. Use the ``TonalityISO1996_2_OverTime.process\\(\\)`` "
            "method."
        ),
    ):
        tonality.plot()
