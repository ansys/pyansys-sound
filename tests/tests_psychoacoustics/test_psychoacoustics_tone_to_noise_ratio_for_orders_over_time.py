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

import pytest
from ansys.dpf.core import Field

from ansys.sound.core._pyansys_sound import (PyAnsysSoundException,
                                             PyAnsysSoundWarning)
from ansys.sound.core.psychoacoustics import ToneToNoiseRatioForOrdersOverTime
from ansys.sound.core.signal_utilities import LoadWav

EXP_TNR_1 = 4.538942
EXP_TNR_2 = 7.559879
EXP_TNR_3 = 2.930925
EXP_TIME = 20.596745485679634
EXP_RPM = 4810.3193359375


EXP_STR = (
    "ToneToNoiseRatioForOrdersOverTime object.\n"
    + "Data\n"
    + f'Signal name: "Acceleration_with_Tacho"\n'
    + f'RPM profile signal name: "Acceleration_with_Tacho_RPM"\n'
    + f"Order list: [2.0, 4.0, 8.0]\n"
)


def test_tone_to_noise_ratio_for_orders_instantiation():
    """Test ToneToNoiseRatioForOrdersOverTime instantiation."""
    tnr_orders = ToneToNoiseRatioForOrdersOverTime()
    assert tnr_orders.signal == None
    assert tnr_orders.profile == None
    assert tnr_orders.order_list == None


def test_tone_to_noise_ratio_for_orders_properties():
    """Test ToneToNoiseRatioForOrdersOverTime properties."""
    tnr_orders = ToneToNoiseRatioForOrdersOverTime()
    tnr_orders.signal = Field()
    assert type(tnr_orders.signal) == Field

    tnr_orders.profile = Field()
    assert type(tnr_orders.profile) == Field

    tnr_orders.order_list = [1.0]
    assert type(tnr_orders.order_list) == list


def test_tone_to_noise_ratio_for_orders___str__():
    """Test __str__ method."""
    wav_loader = LoadWav(pytest.data_path_Acceleration_with_Tacho_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()
    sig = fc[0]
    rpm = fc[1]
    ords = [2.0, 4.0, 8.0]

    tnr_orders = ToneToNoiseRatioForOrdersOverTime(signal=sig, profile=rpm, order_list=ords)

    assert tnr_orders.__str__() == EXP_STR


def test_tone_to_noise_ratio_for_orders_setters_exceptions():
    """Test ToneToNoiseRatioForOrdersOverTime setters' exceptions."""
    tnr_orders = ToneToNoiseRatioForOrdersOverTime()
    with pytest.raises(
        PyAnsysSoundException,
        match="Signal must be provided as a DPF field.",
    ):
        tnr_orders.signal = "Invalid"

    with pytest.raises(
        PyAnsysSoundException,
        match="Profile must be provided as a DPF field.",
    ):
        tnr_orders.profile = "Invalid"

    with pytest.raises(
        PyAnsysSoundException,
        match="Order list must contain at least one order.",
    ):
        tnr_orders.order_list = []

    with pytest.raises(
        PyAnsysSoundException,
        match="Order list must contain strictly positive numbers.",
    ):
        tnr_orders.order_list = [-1.0]


def test_tone_to_noise_ratio_for_orders_process():
    """Test process method."""
    wav_loader = LoadWav(pytest.data_path_Acceleration_with_Tacho_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()
    sig = fc[0]
    rpm = fc[1]
    ords = [2.0, 4.0, 8.0]

    tnr_orders = ToneToNoiseRatioForOrdersOverTime(signal=sig, profile=rpm, order_list=ords)
    tnr_orders.process()


def test_tone_to_noise_ratio_for_orders_process_exception():
    """Test process method's exception."""
    wav_loader = LoadWav(pytest.data_path_Acceleration_with_Tacho_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()
    sig = fc[0]
    rpm = fc[1]

    tnr_orders = ToneToNoiseRatioForOrdersOverTime()
    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "No signal found for tone-to-noise ratio computation. "
            "Use 'ToneToNoiseRatioForOrdersOverTime.signal'."
        ),
    ):
        tnr_orders.process()

    tnr_orders.signal = sig
    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "No profile found for tone-to-noise ratio computation. "
            "Use 'ToneToNoiseRatioForOrdersOverTime.profile'."
        ),
    ):
        tnr_orders.process()

    tnr_orders.profile = rpm
    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "No order list found for tone-to-noise ratio computation. "
            "Use 'ToneToNoiseRatioForOrdersOverTime.order_list'."
        ),
    ):
        tnr_orders.process()


def test_tone_to_noise_ratio_for_orders_get_output():
    """Test get_output method."""
    wav_loader = LoadWav(pytest.data_path_Acceleration_with_Tacho_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()
    sig = fc[0]
    rpm = fc[1]
    ords = [2.0, 4.0, 8.0]

    tnr_orders = ToneToNoiseRatioForOrdersOverTime(signal=sig, profile=rpm, order_list=ords)
    tnr_orders.process()
    output = tnr_orders.get_output()
    assert output is not None


def test_tone_to_noise_ratio_for_orders_get_output_unprocessed():
    """Test get_output method's warning."""
    tnr_orders = ToneToNoiseRatioForOrdersOverTime()

    with pytest.warns(
        PyAnsysSoundWarning,
        match=(
            "Output is not processed yet. Use the 'ToneToNoiseRatioForOrdersOverTime.process\(\)' method."  # noqa: E501
        ),
    ):
        output = tnr_orders.get_output()
    assert output is None


def test_tone_to_noise_ratio_for_orders_get_output_as_nparray():
    """Test get_output_as_nparray method."""
    wav_loader = LoadWav(pytest.data_path_Acceleration_with_Tacho_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()
    sig = fc[0]
    rpm = fc[1]
    ords = [2.0, 4.0, 8.0]

    tnr_orders = ToneToNoiseRatioForOrdersOverTime(signal=sig, profile=rpm, order_list=ords)
    tnr_orders.process()

    TNRs, TimeScale, RPM_resampled = tnr_orders.get_output_as_nparray()
    assert pytest.approx(TNRs[0][538]) == EXP_TNR_1
    assert pytest.approx(TNRs[1][538]) == EXP_TNR_2
    assert pytest.approx(TNRs[2][330]) == EXP_TNR_3
    assert pytest.approx(TimeScale[-1]) == EXP_TIME
    assert len(RPM_resampled) == len(TNRs[0])


def test_tone_to_noise_ratio_for_orders_get_output_as_nparray_unprocessed():
    """Test get_output_as_nparray method's warning."""
    wav_loader = LoadWav(pytest.data_path_Acceleration_with_Tacho_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()
    sig = fc[0]
    rpm = fc[1]
    ords = [2.0, 4.0, 8.0]

    tnr_orders = ToneToNoiseRatioForOrdersOverTime(signal=sig, profile=rpm, order_list=ords)

    with pytest.warns(
        PyAnsysSoundWarning,
        match=(
            "Output is not processed yet. Use the 'ToneToNoiseRatioForOrdersOverTime.process\(\)' method."  # noqa: E501
        ),
    ):
        TNRs, TimeScale, RPM_resampled = tnr_orders.get_output_as_nparray()

    assert len(TNRs) == 0
    assert len(TimeScale) == 0
    assert len(RPM_resampled) == 0


def test_tone_to_noise_ratio_for_orders_get_time_scale():
    """Test get_time_scale method."""
    wav_loader = LoadWav(pytest.data_path_Acceleration_with_Tacho_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()
    sig = fc[0]
    rpm = fc[1]
    ords = [2.0, 4.0, 8.0]

    tnr_orders = ToneToNoiseRatioForOrdersOverTime(signal=sig, profile=rpm, order_list=ords)
    tnr_orders.process()

    time_scale = tnr_orders.get_time_scale()
    assert len(time_scale) == 555
    assert len(time_scale) == 555
    assert pytest.approx(time_scale[-1]) == EXP_TIME


def test_tone_to_noise_ratio_for_orders_get_time_scale_unprocessed():
    """Test get_time_scale method's exception."""
    tnr_orders = ToneToNoiseRatioForOrdersOverTime()
    time_scale = tnr_orders.get_time_scale()
    assert len(time_scale) == 0


def test_tone_to_noise_ratio_for_orders_get_rpm_scale():
    """Test get_rpm_scale method."""
    wav_loader = LoadWav(pytest.data_path_Acceleration_with_Tacho_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()
    sig = fc[0]
    rpm = fc[1]
    ords = [2.0, 4.0, 8.0]

    tnr_orders = ToneToNoiseRatioForOrdersOverTime(signal=sig, profile=rpm, order_list=ords)
    tnr_orders.process()

    rpm_scale = tnr_orders.get_rpm_scale()
    assert len(rpm_scale) == 555
    assert pytest.approx(rpm_scale[-1]) == EXP_RPM


def test_tone_to_noise_ratio_for_orders_get_rpm_scale_unprocessed():
    """Test get_rpm_scale method's exception."""
    tnr_orders = ToneToNoiseRatioForOrdersOverTime()
    rpm_scale = tnr_orders.get_rpm_scale()
    assert len(rpm_scale) == 0


def test_tone_to_noise_ratio_for_orders_get_order_tone_to_noise_ratio_over_time():
    """Test get_order_tone_to_noise_ratio_over_time method."""
    wav_loader = LoadWav(pytest.data_path_Acceleration_with_Tacho_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()
    sig = fc[0]
    rpm = fc[1]
    ords = [2.0, 4.0, 8.0]

    tnr_orders = ToneToNoiseRatioForOrdersOverTime(signal=sig, profile=rpm, order_list=ords)
    tnr_orders.process()

    TNR_2 = tnr_orders.get_order_tone_to_noise_ratio_over_time(order_index=0)
    TNR_4 = tnr_orders.get_order_tone_to_noise_ratio_over_time(order_index=1)
    TNR_8 = tnr_orders.get_order_tone_to_noise_ratio_over_time(order_index=2)

    assert pytest.approx(TNR_2[538]) == EXP_TNR_1
    assert pytest.approx(TNR_4[538]) == EXP_TNR_2
    assert pytest.approx(TNR_8[330]) == EXP_TNR_3


def test_tone_to_noise_ratio_for_orders_get_order_tone_to_noise_ratio_over_time_exception():
    """Test get_order_tone_to_noise_ratio_over_time method's exception."""
    wav_loader = LoadWav(pytest.data_path_Acceleration_with_Tacho_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()
    sig = fc[0]
    rpm = fc[1]
    ords = [2.0, 4.0, 8.0]

    tnr_orders = ToneToNoiseRatioForOrdersOverTime(signal=sig, profile=rpm, order_list=ords)
    tnr_orders.process()

    with pytest.raises(
        PyAnsysSoundException,
        match="Order index 3 is out of range. Order list has 3 elements.",
    ):
        tnr_orders.get_order_tone_to_noise_ratio_over_time(order_index=3)


def test_tone_to_noise_ratio_for_orders_get_order_tone_to_noise_ratio_over_time_unprocessed():
    """Test get_order_tone_to_noise_ratio_over_time method's exception."""
    tnr_orders = ToneToNoiseRatioForOrdersOverTime()
    TNR = tnr_orders.get_order_tone_to_noise_ratio_over_time(order_index=0)
    assert len(TNR) == 0


@patch("matplotlib.pyplot.show")
def test_tone_to_noise_ratio_for_orders_plot(mock_show):
    """Test plot method."""
    wav_loader = LoadWav(pytest.data_path_Acceleration_with_Tacho_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()
    sig = fc[0]
    rpm = fc[1]
    ords = [2.0, 4.0, 8.0]

    tnr_orders = ToneToNoiseRatioForOrdersOverTime(signal=sig, profile=rpm, order_list=ords)
    tnr_orders.process()

    tnr_orders.plot()


@patch("matplotlib.pyplot.show")
def test_tone_to_noise_ratio_for_orders_plot_with_rpm_axis(mock_show):
    """Test plot method."""
    wav_loader = LoadWav(pytest.data_path_Acceleration_with_Tacho_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()
    sig = fc[0]
    rpm = fc[1]
    ords = [2.0, 4.0, 8.0]

    tnr_orders = ToneToNoiseRatioForOrdersOverTime(signal=sig, profile=rpm, order_list=ords)
    tnr_orders.process()

    tnr_orders.plot(use_rpm_scale=True)


def test_tone_to_noise_ratio_for_orders_plot_exception():
    """Test plot method's exception."""
    wav_loader = LoadWav(pytest.data_path_Acceleration_with_Tacho_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()
    sig = fc[0]
    rpm = fc[1]
    ords = [2.0, 4.0, 8.0]
    tnr_orders = ToneToNoiseRatioForOrdersOverTime(signal=sig, profile=rpm, order_list=ords)

    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "Output is not processed yet. "
            "Use the ``ToneToNoiseRatioForOrdersOverTime.process\\(\\)`` method."
        ),
    ):
        tnr_orders.plot()
