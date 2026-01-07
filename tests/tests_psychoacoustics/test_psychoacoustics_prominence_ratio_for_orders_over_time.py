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
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ansys.sound.core.psychoacoustics import ProminenceRatioForOrdersOverTime
from ansys.sound.core.signal_utilities import LoadWav

EXP_PR_1 = 1.8085632324218750
EXP_PR_2 = 7.3899965286254883
EXP_PR_3 = 1.7300876379013062
EXP_TIME = 20.596745485679634
EXP_RPM = 4810.3193359375


EXP_STR = (
    "ProminenceRatioForOrdersOverTime object.\n"
    + "Data\n"
    + f'Signal name: "Acceleration_with_Tacho"\n'
    + f'RPM profile signal name: "Acceleration_with_Tacho_RPM"\n'
    + f"Order list: [2.0, 4.0, 16.0]\n"
)


def test_prominence_ratio_for_orders_instantiation():
    """Test ProminenceRatioForOrdersOverTime instantiation."""
    pr_orders = ProminenceRatioForOrdersOverTime()
    assert pr_orders.signal == None
    assert pr_orders.profile == None
    assert pr_orders.order_list == None


def test_prominence_ratio_for_orders_properties():
    """Test ProminenceRatioForOrdersOverTime properties."""
    pr_orders = ProminenceRatioForOrdersOverTime()
    pr_orders.signal = Field()
    assert type(pr_orders.signal) == Field

    pr_orders.profile = Field()
    assert type(pr_orders.profile) == Field

    pr_orders.order_list = [1.0]
    assert type(pr_orders.order_list) == list


def test_prominence_ratio_for_orders___str__():
    """Test __str__ method."""
    wav_loader = LoadWav(pytest.data_path_Acceleration_with_Tacho_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()
    sig = fc[0]
    rpm = fc[1]
    ords = [2.0, 4.0, 16.0]

    pr_orders = ProminenceRatioForOrdersOverTime(signal=sig, profile=rpm, order_list=ords)

    assert pr_orders.__str__() == EXP_STR


def test_prominence_ratio_for_orders_setters_exceptions():
    """Test ProminenceRatioForOrdersOverTime setters' exceptions."""
    pr_orders = ProminenceRatioForOrdersOverTime()
    with pytest.raises(
        PyAnsysSoundException,
        match="Signal must be provided as a DPF field.",
    ):
        pr_orders.signal = "Invalid"

    with pytest.raises(
        PyAnsysSoundException,
        match="Profile must be provided as a DPF field.",
    ):
        pr_orders.profile = "Invalid"

    with pytest.raises(
        PyAnsysSoundException,
        match="Order list must contain at least one order.",
    ):
        pr_orders.order_list = []

    with pytest.raises(
        PyAnsysSoundException,
        match="Order list must contain strictly positive numbers.",
    ):
        pr_orders.order_list = [-1.0]


def test_prominence_ratio_for_orders_process():
    """Test process method."""
    wav_loader = LoadWav(pytest.data_path_Acceleration_with_Tacho_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()
    sig = fc[0]
    rpm = fc[1]
    ords = [2.0, 4.0, 16.0]

    pr_orders = ProminenceRatioForOrdersOverTime(signal=sig, profile=rpm, order_list=ords)
    pr_orders.process()


def test_prominence_ratio_for_orders_process_exception():
    """Test process method's exception."""
    wav_loader = LoadWav(pytest.data_path_Acceleration_with_Tacho_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()
    sig = fc[0]
    rpm = fc[1]

    pr_orders = ProminenceRatioForOrdersOverTime()
    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "No signal found for prominence ratio computation. "
            "Use 'ProminenceRatioForOrdersOverTime.signal'."
        ),
    ):
        pr_orders.process()

    pr_orders.signal = sig
    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "No profile found for prominence ratio computation. "
            "Use 'ProminenceRatioForOrdersOverTime.profile'."
        ),
    ):
        pr_orders.process()

    pr_orders.profile = rpm
    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "No order list found for prominence ratio computation. "
            "Use 'ProminenceRatioForOrdersOverTime.order_list'."
        ),
    ):
        pr_orders.process()


def test_prominence_ratio_for_orders_get_output():
    """Test get_output method."""
    wav_loader = LoadWav(pytest.data_path_Acceleration_with_Tacho_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()
    sig = fc[0]
    rpm = fc[1]
    ords = [2.0, 4.0, 16.0]

    pr_orders = ProminenceRatioForOrdersOverTime(signal=sig, profile=rpm, order_list=ords)
    pr_orders.process()
    output = pr_orders.get_output()
    assert output is not None


def test_prominence_ratio_for_orders_get_output_unprocessed():
    """Test get_output method's warning."""
    pr_orders = ProminenceRatioForOrdersOverTime()

    with pytest.warns(
        PyAnsysSoundWarning,
        match=(
            "Output is not processed yet. Use the 'ProminenceRatioForOrdersOverTime.process\(\)' method."  # noqa: E501
        ),
    ):
        output = pr_orders.get_output()
    assert output is None


def test_prominence_ratio_for_orders_get_output_as_nparray():
    """Test get_output_as_nparray method."""
    wav_loader = LoadWav(pytest.data_path_Acceleration_with_Tacho_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()
    sig = fc[0]
    rpm = fc[1]
    ords = [2.0, 4.0, 16.0]

    pr_orders = ProminenceRatioForOrdersOverTime(signal=sig, profile=rpm, order_list=ords)
    pr_orders.process()

    PRs, TimeScale, RPM_resampled = pr_orders.get_output_as_nparray()
    assert pytest.approx(PRs[0][538]) == EXP_PR_1
    assert pytest.approx(PRs[1][538]) == EXP_PR_2
    assert pytest.approx(PRs[2][269]) == EXP_PR_3
    assert pytest.approx(TimeScale[-1]) == EXP_TIME
    assert len(RPM_resampled) == len(PRs[0])


def test_prominence_ratio_for_orders_get_output_as_nparray_unprocessed():
    """Test get_output_as_nparray method's warning."""
    wav_loader = LoadWav(pytest.data_path_Acceleration_with_Tacho_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()
    sig = fc[0]
    rpm = fc[1]
    ords = [2.0, 4.0, 16.0]

    pr_orders = ProminenceRatioForOrdersOverTime(signal=sig, profile=rpm, order_list=ords)

    with pytest.warns(
        PyAnsysSoundWarning,
        match=(
            "Output is not processed yet. Use the 'ProminenceRatioForOrdersOverTime.process\(\)' method."  # noqa: E501
        ),
    ):
        PRs, TimeScale, RPM_resampled = pr_orders.get_output_as_nparray()

    assert len(PRs) == 0
    assert len(TimeScale) == 0
    assert len(RPM_resampled) == 0


def test_prominence_ratio_for_orders_get_time_scale():
    """Test get_time_scale method."""
    wav_loader = LoadWav(pytest.data_path_Acceleration_with_Tacho_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()
    sig = fc[0]
    rpm = fc[1]
    ords = [2.0, 4.0, 16.0]

    pr_orders = ProminenceRatioForOrdersOverTime(signal=sig, profile=rpm, order_list=ords)
    pr_orders.process()

    time_scale = pr_orders.get_time_scale()
    assert len(time_scale) == 555
    assert len(time_scale) == 555
    assert pytest.approx(time_scale[-1]) == EXP_TIME


def test_prominence_ratio_for_orders_get_time_scale_unprocessed():
    """Test get_time_scale method's exception."""
    pr_orders = ProminenceRatioForOrdersOverTime()
    time_scale = pr_orders.get_time_scale()
    assert len(time_scale) == 0


def test_prominence_ratio_for_orders_get_rpm_scale():
    """Test get_rpm_scale method."""
    wav_loader = LoadWav(pytest.data_path_Acceleration_with_Tacho_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()
    sig = fc[0]
    rpm = fc[1]
    ords = [2.0, 4.0, 16.0]

    pr_orders = ProminenceRatioForOrdersOverTime(signal=sig, profile=rpm, order_list=ords)
    pr_orders.process()

    rpm_scale = pr_orders.get_rpm_scale()
    assert len(rpm_scale) == 555
    assert pytest.approx(rpm_scale[-1]) == EXP_RPM


def test_prominence_ratio_for_orders_get_rpm_scale_unprocessed():
    """Test get_rpm_scale method's exception."""
    pr_orders = ProminenceRatioForOrdersOverTime()
    rpm_scale = pr_orders.get_rpm_scale()
    assert len(rpm_scale) == 0


def test_prominence_ratio_for_orders_get_order_prominence_ratio_over_time():
    """Test get_order_prominence_ratio_over_time method."""
    wav_loader = LoadWav(pytest.data_path_Acceleration_with_Tacho_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()
    sig = fc[0]
    rpm = fc[1]
    ords = [2.0, 4.0, 16.0]

    pr_orders = ProminenceRatioForOrdersOverTime(signal=sig, profile=rpm, order_list=ords)
    pr_orders.process()

    PR_2 = pr_orders.get_order_prominence_ratio_over_time(order_index=0)
    PR_4 = pr_orders.get_order_prominence_ratio_over_time(order_index=1)
    PR_8 = pr_orders.get_order_prominence_ratio_over_time(order_index=2)

    assert pytest.approx(PR_2[538]) == EXP_PR_1
    assert pytest.approx(PR_4[538]) == EXP_PR_2
    assert pytest.approx(PR_8[269]) == EXP_PR_3


def test_prominence_ratio_for_orders_get_order_prominence_ratio_over_time_exception():
    """Test get_order_prominence_ratio_over_time method's exception."""
    wav_loader = LoadWav(pytest.data_path_Acceleration_with_Tacho_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()
    sig = fc[0]
    rpm = fc[1]
    ords = [2.0, 4.0, 16.0]

    pr_orders = ProminenceRatioForOrdersOverTime(signal=sig, profile=rpm, order_list=ords)
    pr_orders.process()

    with pytest.raises(
        PyAnsysSoundException,
        match="Order index 3 is out of range. Order list has 3 elements.",
    ):
        pr_orders.get_order_prominence_ratio_over_time(order_index=3)


def test_prominence_ratio_for_orders_get_order_prominence_ratio_over_time_unprocessed():
    """Test get_order_prominence_ratio_over_time method's exception."""
    pr_orders = ProminenceRatioForOrdersOverTime()
    PR = pr_orders.get_order_prominence_ratio_over_time(order_index=0)
    assert len(PR) == 0


@patch("matplotlib.pyplot.show")
def test_prominence_ratio_for_orders_plot(mock_show):
    """Test plot method."""
    wav_loader = LoadWav(pytest.data_path_Acceleration_with_Tacho_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()
    sig = fc[0]
    rpm = fc[1]
    ords = [2.0, 4.0, 16.0]

    pr_orders = ProminenceRatioForOrdersOverTime(signal=sig, profile=rpm, order_list=ords)
    pr_orders.process()

    pr_orders.plot()


@patch("matplotlib.pyplot.show")
def test_prominence_ratio_for_orders_plot_with_rpm_axis(mock_show):
    """Test plot method."""
    wav_loader = LoadWav(pytest.data_path_Acceleration_with_Tacho_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()
    sig = fc[0]
    rpm = fc[1]
    ords = [2.0, 4.0, 16.0]

    pr_orders = ProminenceRatioForOrdersOverTime(signal=sig, profile=rpm, order_list=ords)
    pr_orders.process()

    pr_orders.plot(use_rpm_scale=True)


def test_prominence_ratio_for_orders_plot_exception():
    """Test plot method's exception."""
    wav_loader = LoadWav(pytest.data_path_Acceleration_with_Tacho_nonUnitaryCalib)
    wav_loader.process()
    fc = wav_loader.get_output()
    sig = fc[0]
    rpm = fc[1]
    ords = [2.0, 4.0, 16.0]
    pr_orders = ProminenceRatioForOrdersOverTime(signal=sig, profile=rpm, order_list=ords)

    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "Output is not processed yet. "
            "Use the ``ProminenceRatioForOrdersOverTime.process\\(\\)`` method."
        ),
    ):
        pr_orders.plot()
