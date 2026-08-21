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

import os
from unittest.mock import patch

from ansys.dpf.core import Field, FieldsContainer
import numpy as np
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ansys.sound.core.order_analysis import OrderLevels

# Skip entire test module if Sound version < 2027.1.0
if not pytest.SOUND_VERSION_GREATER_THAN_OR_EQUAL_TO_2027R1:
    pytest.skip("Requires Sound version >= 2027.1.0", allow_module_level=True)

EXP_STR_NOT_SET = (
    "OrderLevels object\n"
    "Data\n"
    "\tSignal name: Not set\n"
    "\tRPM profile name: Not set\n"
    "\tOrders: Not set\n"
    "\tOrder analysis width: 10.0 %\n"
    "\tOrder analysis resolution: 2.0 %"
)

EXP_STR_ALL_SET_2_ORDERS = (
    "OrderLevels object\n"
    "Data\n"
    '\tSignal name: "Acceleration_with_Tacho"\n'
    '\tRPM profile name: "Acceleration_with_Tacho_RPM"\n'
    "\tOrders (2): [2.0, 4.0]\n"
    "\tOrder analysis width: 30.0 %\n"
    "\tOrder analysis resolution: 1.0 %"
)

EXP_STR_ALL_SET_15_ORDERS = (
    "OrderLevels object\n"
    "Data\n"
    '\tSignal name: "Acceleration_with_Tacho"\n'
    '\tRPM profile name: "Acceleration_with_Tacho_RPM"\n'
    "\tOrders (15): [1, 2, 3, 4, 5, ... 11, 12, 13, 14, 15]\n"
    "\tOrder analysis width: 30.0 %\n"
    "\tOrder analysis resolution: 1.0 %"
)

EXP_NUM_ORDERS = 4
EXP_NUM_RPM_POINTS = 848

# Pa^2 output
EXP_PA2_ORDER2_RPM0 = 0.0053486785509092695
EXP_PA2_ORDER2_RPM10 = 0.008893666678337932
EXP_PA2_ORDER2_RPM100 = 0.00047953474928854608
EXP_PA2_ORDER2_RPM500 = 0.00090051242185874196
EXP_PA2_ORDER4_RPM0 = 5.554353083763535e-05
EXP_PA2_ORDER4_RPM10 = 0.00011636148361238936
EXP_PA2_ORDER4_RPM100 = 0.00018775817776853440
EXP_PA2_ORDER4_RPM500 = 0.00063774500269680350
EXP_PA2_ORDER10_RPM0 = 4.6480690136126773e-07
EXP_PA2_ORDER10_RPM10 = 2.8781593669622625e-06

# Pa^2 output (width=100%)
EXP_PA2_ORDER2_RPM0_WIDTH100 = 0.007259188930523296
EXP_PA2_ORDER2_RPM10_WIDTH100 = 0.009584942415342615
EXP_PA2_ORDER4_RPM0_WIDTH100 = 8.988746071167709e-05
EXP_PA2_ORDER4_RPM10_WIDTH100 = 0.00014242398895127672

# dB output (dBFS and dBSPL)
EXP_DBFS_ORDER2_RPM0 = -22.7175350189209
EXP_DBFS_ORDER4_RPM0 = -42.55366516113281
EXP_DBSPL_ORDER2_RPM0 = 71.26186506779948
EXP_DBSPL_ORDER4_RPM0 = 51.42573492558756

# RPM values
EXP_RPM_RPM0 = 974.4971313476562
EXP_RPM_RPM100 = 2030.80322265625
EXP_RPM_RPM500 = 4209.921875
EXP_RPM_LAST = 4821.28173828125


# --- Instantiation ---


def test_order_levels_instantiation_default():
    """Test instantiation with default values."""
    order_levels = OrderLevels()
    assert order_levels.signal is None
    assert order_levels.rpm_profile is None
    assert order_levels.orders is None
    assert order_levels.order_resolution == 2.0
    assert order_levels.order_width == 10.0


def test_order_levels_instantiation_all_set(load_accel_and_rpm):
    """Test instantiation with default values."""
    signal, rpm_profile = load_accel_and_rpm
    order_levels = OrderLevels(
        signal=signal,
        rpm_profile=rpm_profile,
        orders=[2.0, 4.0],
        order_resolution=1.0,
        order_width=30.0,
    )
    assert order_levels.signal is signal
    assert order_levels.rpm_profile is rpm_profile
    assert order_levels.orders == [2.0, 4.0]
    assert order_levels.order_resolution == 1.0
    assert order_levels.order_width == 30.0


# -- __str__ ---


def test_order_levels___str___not_set():
    """Test __str__ with default parameters."""
    order_levels = OrderLevels()
    assert str(order_levels) == EXP_STR_NOT_SET


def test_order_levels___str___all_set(load_accel_and_rpm):
    """Test __str__ after setting signal, RPM profile and orders."""
    signal, rpm_profile = load_accel_and_rpm
    order_levels = OrderLevels(
        signal=signal,
        rpm_profile=rpm_profile,
        orders=[2.0, 4.0],
        order_resolution=1.0,
        order_width=30.0,
    )
    assert str(order_levels) == EXP_STR_ALL_SET_2_ORDERS

    order_levels.orders = list(range(1, 16))
    assert str(order_levels) == EXP_STR_ALL_SET_15_ORDERS


# --- Properties ---


def test_order_levels_signal_property():
    """Test the signal property setter and getter."""
    order_levels = OrderLevels()
    f = Field()
    f.data = 42.0 * np.ones(3)
    order_levels.signal = f
    assert order_levels.signal.data[0, 2] == 42.0


def test_order_levels_signal_property_exception():
    """Test that assigning a non-Field to signal raises PyAnsysSoundException."""
    order_levels = OrderLevels()
    with pytest.raises(PyAnsysSoundException, match="Signal must be specified as a DPF field."):
        order_levels.signal = "wrong"


def test_order_levels_rpm_profile_property():
    """Test the rpm_profile property setter and getter."""
    order_levels = OrderLevels()
    f = Field()
    f.append([1000.0, 2000.0, 3000.0], 1)
    order_levels.rpm_profile = f
    assert order_levels.rpm_profile.data[0, 2] == 3000.0


def test_order_levels_rpm_profile_property_exception():
    """Test that assigning a non-Field to rpm_profile raises PyAnsysSoundException."""
    order_levels = OrderLevels()
    with pytest.raises(
        PyAnsysSoundException, match="RPM profile must be specified as a DPF field."
    ):
        order_levels.rpm_profile = 12345


def test_order_levels_orders_property():
    """Test the orders property setter and getter."""
    order_levels = OrderLevels()
    order_levels.orders = [1.0, 2.0, 3.5]
    assert order_levels.orders == [1.0, 2.0, 3.5]


def test_order_levels_orders_property_exceptions():
    """Test the orders property setter's exceptions."""
    order_levels = OrderLevels()

    with pytest.raises(
        PyAnsysSoundException, match="Orders must be specified as a list of positive floats."
    ):
        order_levels.orders = "wrong"

    with pytest.raises(
        PyAnsysSoundException, match="Orders must be specified as a list of positive floats."
    ):
        order_levels.orders = [1.0, "wrong", 3.0]

    with pytest.raises(
        PyAnsysSoundException, match="Orders must be specified as a list of positive floats."
    ):
        order_levels.orders = [1.0, -2.0, 3.0]


def test_order_levels_order_resolution_property():
    """Test the order_resolution property setter and getter."""
    order_levels = OrderLevels()
    order_levels.order_resolution = 0.5
    assert order_levels.order_resolution == 0.5


def test_order_levels_order_resolution_property_exceptions():
    """Test the order_resolution setter's exceptions."""
    order_levels = OrderLevels()
    with pytest.raises(PyAnsysSoundException, match="Order resolution must be greater than 0.0 %."):
        order_levels.order_resolution = 0.0

    with pytest.raises(PyAnsysSoundException, match="Order resolution must be greater than 0.0 %."):
        order_levels.order_resolution = -1.0


def test_order_levels_order_width_property():
    """Test the order_width property setter and getter."""
    order_levels = OrderLevels()
    order_levels.order_width = 5.0
    assert order_levels.order_width == 5.0


def test_order_levels_order_width_property_exceptions():
    """Test the order_width property setter's exceptions."""
    order_levels = OrderLevels()
    with pytest.raises(PyAnsysSoundException, match="Width must be greater than 0.0 %."):
        order_levels.order_width = 0.0

    with pytest.raises(PyAnsysSoundException, match="Width must be greater than 0.0 %."):
        order_levels.order_width = -5.0


def test_order_levels_rpm_order_representation_property(load_accel_and_rpm):
    """Test the rpm_order_representation property getter."""
    order_levels = OrderLevels()
    assert order_levels.rpm_order_representation is None

    signal, rpm_profile = load_accel_and_rpm
    order_levels = OrderLevels(signal=signal, rpm_profile=rpm_profile, orders=[2.0, 4.0])
    order_levels.process()
    assert isinstance(order_levels.rpm_order_representation, FieldsContainer)


# --- process ---


def test_order_levels_process(load_accel_and_rpm):
    """Test the process method."""
    signal, rpm_profile = load_accel_and_rpm
    order_levels = OrderLevels(signal, rpm_profile, orders=[2.0, 4.0])

    order_levels.process()
    assert order_levels._output is not None

    # Orders specified as a numpy array or list of ints are also accepted, although not advertised
    # in the documentation.
    order_levels.orders = (2.0, 4.0, 6.0)
    order_levels.process()
    assert order_levels._output is not None

    order_levels.orders = np.array([2.0, 4.0, 6.0])
    order_levels.process()
    assert order_levels._output is not None

    order_levels.orders = [2, 4, 6]
    order_levels.process()
    assert order_levels._output is not None

    # Other parameters provided as integers (while floats are expected)
    order_levels.order_width = 10
    order_levels.order_resolution = 1
    order_levels.process()
    assert order_levels._output is not None


def test_order_levels_process_exceptions(load_accel_and_rpm):
    """Test the process method's exceptions."""
    signal, rpm_profile = load_accel_and_rpm

    order_levels = OrderLevels(rpm_profile=rpm_profile, orders=[2.0, 4.0])
    with pytest.raises(
        PyAnsysSoundException, match="No input signal is set. Use `OrderLevels.signal`."
    ):
        order_levels.process()

    order_levels = OrderLevels(signal=signal, orders=[2.0, 4.0])
    with pytest.raises(
        PyAnsysSoundException, match="No input RPM profile is set. Use `OrderLevels.rpm_profile`."
    ):
        order_levels.process()

    order_levels = OrderLevels(signal=signal, rpm_profile=rpm_profile)
    with pytest.raises(
        PyAnsysSoundException, match="No input order list is set. Use `OrderLevels.orders`."
    ):
        order_levels.process()


def test_order_levels_process_warnings(load_accel_and_rpm):
    """Test the process method's warnings."""
    signal, rpm_profile = load_accel_and_rpm

    order_levels = OrderLevels(
        signal, rpm_profile, orders=[2.0, 4.0], order_width=1.0, order_resolution=2.0
    )
    with pytest.warns(
        PyAnsysSoundWarning,
        match=(
            "Order width \(1.0 %\) is smaller than the order resolution \(2.0 %\). Results may be "
            "inaccurate. Consider increasing the order width or decreasing the order resolution."
        ),
    ):
        order_levels.process()
    assert order_levels._output is not None


# --- Outputs ---


def test_order_levels_get_output(load_accel_and_rpm):
    """Test the get_output method."""
    signal, rpm_profile = load_accel_and_rpm
    order_levels = OrderLevels(
        signal=signal, rpm_profile=rpm_profile, orders=[2.0, 4.0, 10.0, 158.0]
    )
    order_levels.process()
    output = order_levels.get_output()
    assert isinstance(output, FieldsContainer)
    assert len(output) == EXP_NUM_ORDERS


def test_order_levels_get_output_warnings():
    """Test the get_output method's warnings."""
    order_levels = OrderLevels()
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the `OrderLevels.process\(\)` method.",
    ):
        output = order_levels.get_output()
    assert output is None


def test_order_levels_get_output_as_nparray(load_accel_and_rpm):
    """Test the get_output_as_nparray method."""
    order_levels = OrderLevels()
    with pytest.warns(PyAnsysSoundWarning):
        levels, orders, rpm = order_levels.get_output_as_nparray()
    assert len(levels) == 0
    assert len(orders) == 0
    assert len(rpm) == 0

    signal, rpm_profile = load_accel_and_rpm
    order_levels = OrderLevels(
        signal=signal, rpm_profile=rpm_profile, orders=[2.0, 4.0, 10.0, 158.0]
    )
    order_levels.process()
    levels, orders, rpm = order_levels.get_output_as_nparray()
    assert len(levels) == EXP_NUM_ORDERS
    assert len(levels[0]) == EXP_NUM_RPM_POINTS
    assert levels[0][0] == pytest.approx(EXP_PA2_ORDER2_RPM0, rel=1e-4)
    assert levels[0][10] == pytest.approx(EXP_PA2_ORDER2_RPM10, rel=1e-4)
    assert levels[0][100] == pytest.approx(EXP_PA2_ORDER2_RPM100, rel=1e-4)
    assert levels[0][500] == pytest.approx(EXP_PA2_ORDER2_RPM500, rel=1e-4)
    assert levels[1][0] == pytest.approx(EXP_PA2_ORDER4_RPM0, rel=1e-4)
    assert levels[1][10] == pytest.approx(EXP_PA2_ORDER4_RPM10, rel=1e-4)
    assert levels[1][100] == pytest.approx(EXP_PA2_ORDER4_RPM100, rel=1e-4)
    assert levels[1][500] == pytest.approx(EXP_PA2_ORDER4_RPM500, rel=1e-4)
    assert levels[2][0] == pytest.approx(EXP_PA2_ORDER10_RPM0, rel=1e-4)
    assert levels[2][10] == pytest.approx(EXP_PA2_ORDER10_RPM10, rel=1e-4)
    assert len(orders) == EXP_NUM_ORDERS
    assert orders[0] == 2.0
    assert orders[1] == 4.0
    assert orders[2] == 10.0
    assert len(rpm) == EXP_NUM_RPM_POINTS


def test_order_levels_get_output_as_nparray_width_100(load_accel_and_rpm):
    """Test get_output_as_nparray with width=100%."""
    signal, rpm_profile = load_accel_and_rpm
    order_levels = OrderLevels(
        signal=signal, rpm_profile=rpm_profile, orders=[2.0, 4.0, 10.0, 158.0], order_width=100.0
    )
    order_levels.process()
    levels, _, _ = order_levels.get_output_as_nparray()
    assert len(levels) == EXP_NUM_ORDERS
    assert len(levels[0]) == EXP_NUM_RPM_POINTS
    assert levels[0][0] == pytest.approx(EXP_PA2_ORDER2_RPM0_WIDTH100, rel=1e-4)
    assert levels[0][10] == pytest.approx(EXP_PA2_ORDER2_RPM10_WIDTH100, rel=1e-4)
    assert levels[1][0] == pytest.approx(EXP_PA2_ORDER4_RPM0_WIDTH100, rel=1e-4)
    assert levels[1][10] == pytest.approx(EXP_PA2_ORDER4_RPM10_WIDTH100, rel=1e-4)


def test_order_levels_get_order_levels_squared_linear(load_accel_and_rpm):
    """Test the get_order_levels_squared_linear method."""
    signal, rpm_profile = load_accel_and_rpm
    order_levels = OrderLevels(
        signal=signal, rpm_profile=rpm_profile, orders=[2.0, 4.0, 10.0, 158.0]
    )
    order_levels.process()
    levels = order_levels.get_order_levels_squared_linear()
    assert len(levels) == EXP_NUM_ORDERS
    assert len(levels[0]) == EXP_NUM_RPM_POINTS
    assert levels[0][0] == pytest.approx(EXP_PA2_ORDER2_RPM0, rel=1e-4)
    assert levels[0][10] == pytest.approx(EXP_PA2_ORDER2_RPM10, rel=1e-4)
    assert levels[0][100] == pytest.approx(EXP_PA2_ORDER2_RPM100, rel=1e-4)
    assert levels[0][500] == pytest.approx(EXP_PA2_ORDER2_RPM500, rel=1e-4)
    assert levels[1][0] == pytest.approx(EXP_PA2_ORDER4_RPM0, rel=1e-4)
    assert levels[1][10] == pytest.approx(EXP_PA2_ORDER4_RPM10, rel=1e-4)
    assert levels[1][100] == pytest.approx(EXP_PA2_ORDER4_RPM100, rel=1e-4)
    assert levels[1][500] == pytest.approx(EXP_PA2_ORDER4_RPM500, rel=1e-4)
    assert levels[2][0] == pytest.approx(EXP_PA2_ORDER10_RPM0, rel=1e-4)
    assert levels[2][10] == pytest.approx(EXP_PA2_ORDER10_RPM10, rel=1e-4)


def test_order_levels_get_order_levels_dB(load_accel_and_rpm):
    """Test the get_order_levels_dB method."""
    signal, rpm_profile = load_accel_and_rpm
    order_levels = OrderLevels(
        signal=signal, rpm_profile=rpm_profile, orders=[2.0, 4.0, 10.0, 158.0]
    )
    order_levels.process()
    levels = order_levels.get_order_levels_dB(reference_value=1.0)
    assert len(levels) == EXP_NUM_ORDERS
    assert len(levels[0]) == EXP_NUM_RPM_POINTS
    assert levels[0][0] == pytest.approx(EXP_DBFS_ORDER2_RPM0, rel=1e-4)
    assert levels[1][0] == pytest.approx(EXP_DBFS_ORDER4_RPM0, rel=1e-4)

    levels = order_levels.get_order_levels_dB(reference_value=2e-5)
    assert len(levels) == EXP_NUM_ORDERS
    assert len(levels[0]) == EXP_NUM_RPM_POINTS
    assert levels[0][0] == pytest.approx(EXP_DBSPL_ORDER2_RPM0, rel=1e-4)
    assert levels[1][0] == pytest.approx(EXP_DBSPL_ORDER4_RPM0, rel=1e-4)


def test_order_levels_get_order_levels_dB_exceptions(load_accel_and_rpm):
    """Test the get_order_levels_dB method's exceptions."""
    signal, rpm_profile = load_accel_and_rpm
    order_levels = OrderLevels(signal=signal, rpm_profile=rpm_profile, orders=[2.0, 4.0])
    order_levels.process()

    with pytest.raises(PyAnsysSoundException, match="Reference value must be greater than 0."):
        order_levels.get_order_levels_dB(reference_value=0)

    with pytest.raises(PyAnsysSoundException, match="Reference value must be greater than 0."):
        order_levels.get_order_levels_dB(reference_value=-1.0)


def test_order_levels_get_order_level_squared_linear(load_accel_and_rpm):
    """Test the get_order_level_squared_linear method."""
    signal, rpm_profile = load_accel_and_rpm
    order_levels = OrderLevels(signal=signal, rpm_profile=rpm_profile, orders=[2.0, 4.0, 158.0])

    with pytest.warns(PyAnsysSoundWarning):
        levels = order_levels.get_order_level_squared_linear(2.0)
    assert len(levels) == 0

    order_levels.process()
    levels = order_levels.get_order_level_squared_linear(2.0)
    assert isinstance(levels, np.ndarray)
    assert len(levels) == EXP_NUM_RPM_POINTS
    assert levels[0] == pytest.approx(EXP_PA2_ORDER2_RPM0, rel=1e-4)
    assert levels[10] == pytest.approx(EXP_PA2_ORDER2_RPM10, rel=1e-4)
    assert levels[100] == pytest.approx(EXP_PA2_ORDER2_RPM100, rel=1e-4)
    assert levels[500] == pytest.approx(EXP_PA2_ORDER2_RPM500, rel=1e-4)


def test_order_levels_get_order_level_squared_linear_exceptions(load_accel_and_rpm):
    """Test the get_order_level_squared_linear method's exceptions."""
    signal, rpm_profile = load_accel_and_rpm
    order_levels = OrderLevels(signal=signal, rpm_profile=rpm_profile, orders=[2.0, 4.0])
    order_levels.process()
    with pytest.raises(
        PyAnsysSoundException,
        match="Order 99.0 is not in the `orders` list.",
    ):
        order_levels.get_order_level_squared_linear(99.0)


def test_order_levels_get_order_level_dB(load_accel_and_rpm):
    """Test the get_order_level_dB method."""
    signal, rpm_profile = load_accel_and_rpm
    order_levels = OrderLevels(signal=signal, rpm_profile=rpm_profile, orders=[2.0, 4.0, 158.0])

    with pytest.warns(PyAnsysSoundWarning):
        levels = order_levels.get_order_level_dB(2.0)
    assert len(levels) == 0

    order_levels.process()
    levels = order_levels.get_order_level_dB(2.0)
    assert isinstance(levels, np.ndarray)
    assert len(levels) == EXP_NUM_RPM_POINTS
    assert levels[0] == pytest.approx(EXP_DBFS_ORDER2_RPM0, rel=1e-4)


def test_order_levels_get_rpm_scale(load_accel_and_rpm):
    """Test the get_rpm_scale method."""
    signal, rpm_profile = load_accel_and_rpm
    order_levels = OrderLevels(signal=signal, rpm_profile=rpm_profile, orders=[2.0, 4.0, 158.0])
    order_levels.process()
    rpm = order_levels.get_rpm_scale()
    assert isinstance(rpm, np.ndarray)
    assert len(rpm) == EXP_NUM_RPM_POINTS
    assert rpm[0] == pytest.approx(EXP_RPM_RPM0, rel=1e-4)
    assert rpm[100] == pytest.approx(EXP_RPM_RPM100, rel=1e-4)
    assert rpm[500] == pytest.approx(EXP_RPM_RPM500, rel=1e-4)
    assert rpm[-1] == pytest.approx(EXP_RPM_LAST, rel=1e-4)


# --- plot ---


@patch("matplotlib.pyplot.show")
def test_order_levels_plot(mock_show, load_accel_and_rpm):
    """Test the plot method."""
    signal, rpm_profile = load_accel_and_rpm
    order_levels = OrderLevels(signal=signal, rpm_profile=rpm_profile, orders=[2.0, 4.0, 10.0])
    order_levels.process()
    order_levels.plot()
    mock_show.assert_called_once()

    # Empty name and unit (affects title and Y axis label)
    signal.name = ""
    signal.unit = ""
    mock_show.reset_mock()
    order_levels.plot()
    mock_show.assert_called_once()

    # Composed unit => we cannot simply use ^2 in the Y axis label
    signal.unit = "m/s^2"
    mock_show.reset_mock()
    order_levels.plot()
    mock_show.assert_called_once()


@patch("matplotlib.pyplot.show")
def test_order_levels_plot_in_dB(mock_show, load_accel_and_rpm):
    """Test the plot method when display_in_dB is True."""
    signal, rpm_profile = load_accel_and_rpm
    order_levels = OrderLevels(signal=signal, rpm_profile=rpm_profile, orders=[2.0, 4.0])
    order_levels.process()
    order_levels.plot(display_in_dB=True, reference_value=2e-5)
    mock_show.assert_called_once()

    # Additional code paths
    signal.unit = ""
    mock_show.reset_mock()
    order_levels.plot(display_in_dB=True, reference_value=2e-5)
    mock_show.assert_called_once()


def test_order_levels_plot_exceptions(load_accel_and_rpm):
    """Test the plot method's exceptions."""
    signal, rpm_profile = load_accel_and_rpm
    order_levels = OrderLevels(signal=signal, rpm_profile=rpm_profile, orders=[2.0, 4.0, 10.0])

    with pytest.raises(
        PyAnsysSoundException,
        match="Output is not processed yet. Use the `OrderLevels.process\(\)` method.",
    ):
        order_levels.plot()


@patch("matplotlib.pyplot.show")
def test_order_levels_plot_warnings(mock_show, load_accel_and_rpm):
    """Test the plot method's warnings."""
    signal, rpm_profile = load_accel_and_rpm
    orders = [float(i) for i in range(1, 12)]
    order_levels = OrderLevels(signal=signal, rpm_profile=rpm_profile, orders=orders)
    order_levels.process()
    with pytest.warns(
        PyAnsysSoundWarning,
        match="There are more than 10 order values. Only the first 10 are displayed.",
    ):
        order_levels.plot()
    mock_show.assert_called_once()


# --- export ---


def test_order_levels_save_as_AnsysSound_Orders(load_accel_and_rpm):
    """Test that save_as_AnsysSound_Orders method."""
    signal, rpm_profile = load_accel_and_rpm
    order_levels = OrderLevels(signal=signal, rpm_profile=rpm_profile, orders=[2.0, 4.0, 10.0])
    order_levels.process()

    path_to_save = os.path.join(pytest.output_folder, "test_order_levels_save.txt")
    order_levels.save_as_AnsysSound_Orders(path_to_save)
    assert os.path.exists(path_to_save)


def test_order_levels_save_as_AnsysSound_Orders_exceptions(load_accel_and_rpm):
    """Test the save_as_AnsysSound_Orders method's exceptions."""
    signal, rpm_profile = load_accel_and_rpm
    order_levels = OrderLevels(signal=signal, rpm_profile=rpm_profile, orders=[2.0, 4.0, 10.0])

    path_to_save = os.path.join(pytest.output_folder, "test_order_levels_save.txt")
    with pytest.raises(
        PyAnsysSoundException,
        match="Output is not processed yet. Use the `OrderLevels.process\(\)` method.",
    ):
        order_levels.save_as_AnsysSound_Orders(path_to_save)


def test_order_levels_save_as_AnsysSound_Orders_warnings(load_accel_and_rpm):
    """Test the save_as_AnsysSound_Orders method's warnings."""
    signal, rpm_profile = load_accel_and_rpm
    signal.unit = "m/s^2"
    order_levels = OrderLevels(signal=signal, rpm_profile=rpm_profile, orders=[2.0, 4.0, 10.0])
    order_levels.process()

    path_to_save = os.path.join(pytest.output_folder, "test_order_levels_save_not_Pa.txt")
    with pytest.warns(
        PyAnsysSoundWarning,
        match=(
            "The input signal is not in Pa, while the format only allows storing acoustic pressure "
            "data \(Pa, Pa\^2, dB SPL, etc.\). The data will be saved as if it were acoustic "
            "pressure data, using Pa\^2 as unit."
        ),
    ):
        order_levels.save_as_AnsysSound_Orders(path_to_save)
    assert os.path.exists(path_to_save)


# --- private methods ---


@pytest.mark.parametrize(
    "orders, resolution, expected_output",
    [
        ([8], 2, 10),
        ([12], 2, 20),
        ([15], 2, 20),
        ([8], 1, 10),
        ([12], 1, 20),
        ([8], 1.5, 15),
        ([158], 2, 160),
    ],
)
def test_order_levels__compute_max_order(orders, resolution, expected_output):
    """Test the _compute_max_order method."""
    order_levels = OrderLevels(orders=orders, order_resolution=resolution)
    assert order_levels._compute_max_order() == expected_output
