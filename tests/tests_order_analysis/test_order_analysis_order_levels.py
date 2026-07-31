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

from ansys.dpf.core import Field
import numpy as np
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ansys.sound.core.order_analysis import OrderLevels
from ansys.sound.core.signal_utilities import LoadWav

EXP_STR_DEFAULTS = (
    "OrderLevels object\n"
    "Data\n"
    "\tSignal name: Not set\n"
    "\tRPM profile name: Not set\n"
    "\tNot set\n"
    "\tOrder analysis resolution: 2.0 %\n"
    "\tOrder analysis width: 10.0 %"
)

EXP_NUM_ORDERS = 2
EXP_NUM_RPM_POINTS = 848  # order_max=160, matching C++ reference

EXP_RPM_0 = 974.4971313476562
EXP_RPM_LAST = 4821.28173828125

# Raw squared output — order_max=160, values identical to C++ reference
EXP_SQ_ORDER2_IDX0 = 0.0053486785509092695
EXP_SQ_ORDER2_IDX10 = 0.008893666678337932
EXP_SQ_ORDER2_IDX100 = 0.00047953474928854608
EXP_SQ_ORDER2_IDX500 = 0.00090051242185874196
EXP_SQ_ORDER4_IDX0 = 5.554353083763535e-05
EXP_SQ_ORDER4_IDX10 = 0.00011636148361238936
EXP_SQ_ORDER4_IDX100 = 0.00018775817776853440
EXP_SQ_ORDER4_IDX500 = 0.00063774500269680350

# Order 10 (order_max=160 = C++ reference)
EXP_SQ_ORDER10_IDX0 = 4.6480690136126773e-07
EXP_SQ_ORDER10_IDX10 = 2.8781593669622625e-06

# sqrt(squared) — linear amplitude
EXP_LIN_ORDER2_IDX0 = 0.07313466039375086
EXP_LIN_ORDER4_IDX0 = 0.007452753238745755

# 10*log10(squared / 1.0²)
EXP_DB_ORDER2_IDX0 = -22.7175350189209
EXP_DB_ORDER4_IDX0 = -42.55366516113281

# RPM intermediate spot checks (C++ reference values)
EXP_RPM_IDX100 = 2030.80322265625
EXP_RPM_IDX500 = 4209.921875

# Raw squared output (width=100%, order_max=160 = C++ reference)
EXP_SQ_ORDER2_IDX0_W100 = 0.007259188930523296
EXP_SQ_ORDER2_IDX10_W100 = 0.009584942415342615
EXP_SQ_ORDER4_IDX0_W100 = 8.988746071167709e-05
EXP_SQ_ORDER4_IDX10_W100 = 0.00014242398895127672


def _load_signal_and_rpm():
    """Return (signal, rpm_profile) from the shared accel_with_rpm test file."""
    wav = LoadWav(pytest.data_path_accel_with_rpm)
    wav.process()
    fc = wav.get_output()
    signal = fc[0]
    rpm_profile = fc[1]
    rpm_profile.time_freq_support = signal.time_freq_support
    return signal, rpm_profile


# --- Instantiation & __str__ ---


def test_order_levels_instantiation():
    """Test instantiation with default values."""
    ol = OrderLevels()
    assert ol is not None
    assert ol.signal is None
    assert ol.rpm_profile is None
    assert ol.orders is None
    assert ol.resolution == 2.0
    assert ol.width == 10.0
    assert ol.order_max == 100


def test_order_levels_str_defaults():
    """Test __str__ with all parameters at default (not set)."""
    ol = OrderLevels()
    assert str(ol) == EXP_STR_DEFAULTS


def test_order_levels_str_with_data():
    """Test __str__ after loading signal, RPM profile and orders=[2, 4]."""
    signal, rpm_profile = _load_signal_and_rpm()
    ol = OrderLevels(signal=signal, rpm_profile=rpm_profile, orders=[2.0, 4.0])
    s = str(ol)
    assert "Signal name:" in s
    assert "Not set" not in s
    assert "2 orders: [2, 4]" in s


# --- Property: signal ---


def test_order_levels_set_get_signal():
    """Test the signal property setter and getter."""
    ol = OrderLevels()
    f = Field()
    f.data = 42.0 * np.ones(3)
    ol.signal = f
    assert ol.signal.data[0, 2] == 42.0


def test_order_levels_set_signal_exception():
    """Test that assigning a non-Field to signal raises PyAnsysSoundException."""
    ol = OrderLevels()
    with pytest.raises(PyAnsysSoundException, match="Signal must be specified as a DPF field."):
        ol.signal = "wrong"
    assert ol.signal is None


# --- Property: rpm_profile ---


def test_order_levels_set_get_rpm_profile():
    """Test the rpm_profile property setter and getter."""
    ol = OrderLevels()
    f = Field()
    f.append([1000.0, 2000.0, 3000.0], 1)
    ol.rpm_profile = f
    assert ol.rpm_profile.data[0, 2] == 3000.0


def test_order_levels_set_rpm_profile_exception():
    """Test that assigning a non-Field to rpm_profile raises PyAnsysSoundException."""
    ol = OrderLevels()
    with pytest.raises(
        PyAnsysSoundException, match="RPM profile must be specified as a DPF field."
    ):
        ol.rpm_profile = 12345
    assert ol.rpm_profile is None


# --- Property: orders ---


def test_order_levels_set_get_orders():
    """Test the orders property setter and getter."""
    ol = OrderLevels()
    ol.orders = [1.0, 2.0, 3.5]
    assert ol.orders == [1.0, 2.0, 3.5]


# --- Property: resolution ---


def test_order_levels_set_get_resolution():
    """Test the resolution property setter and getter."""
    ol = OrderLevels()
    ol.resolution = 0.5
    assert ol.resolution == 0.5


def test_order_levels_set_resolution_exception_zero():
    """Test that setting resolution to 0.0 raises PyAnsysSoundException."""
    ol = OrderLevels()
    with pytest.raises(PyAnsysSoundException, match="Order resolution must be greater than 0.0."):
        ol.resolution = 0.0


def test_order_levels_set_resolution_exception_negative():
    """Test that setting resolution to a negative value raises PyAnsysSoundException."""
    ol = OrderLevels()
    with pytest.raises(PyAnsysSoundException, match="Order resolution must be greater than 0.0."):
        ol.resolution = -1.0


def test_order_levels_set_resolution_exception_hundred():
    """Test that setting resolution to 100.0 raises PyAnsysSoundException."""
    ol = OrderLevels()
    with pytest.raises(PyAnsysSoundException, match="Order resolution must be less than 100.0."):
        ol.resolution = 100.0


def test_order_levels_set_resolution_exception_above_hundred():
    """Test that setting resolution above 100 raises PyAnsysSoundException."""
    ol = OrderLevels()
    with pytest.raises(PyAnsysSoundException, match="Order resolution must be less than 100.0."):
        ol.resolution = 150.0


# --- Property: width ---


def test_order_levels_set_get_width():
    """Test the width property setter and getter."""
    ol = OrderLevels()
    ol.width = 5.0
    assert ol.width == 5.0


def test_order_levels_set_width_exception_zero():
    """Test that setting width to 0.0 raises PyAnsysSoundException."""
    ol = OrderLevels()
    with pytest.raises(PyAnsysSoundException, match="Width must be greater than 0.0."):
        ol.width = 0.0


def test_order_levels_set_width_exception_negative():
    """Test that setting width to a negative value raises PyAnsysSoundException."""
    ol = OrderLevels()
    with pytest.raises(PyAnsysSoundException, match="Width must be greater than 0.0."):
        ol.width = -5.0


def test_order_levels_set_width_exception_above_100():
    """Test that setting width above 100 raises PyAnsysSoundException."""
    ol = OrderLevels()
    with pytest.raises(PyAnsysSoundException, match="Width must be less than or equal to 100.0."):
        ol.width = 101.0


# --- Property: order_max ---


def test_order_levels_set_get_order_max():
    """Test the order_max property setter and getter."""
    ol = OrderLevels()
    ol.order_max = 50
    assert ol.order_max == 50


def test_order_levels_set_order_max_exception_zero():
    """Test that setting order_max to 0 raises PyAnsysSoundException."""
    ol = OrderLevels()
    with pytest.raises(PyAnsysSoundException, match="Maximum order must be greater than 0."):
        ol.order_max = 0


def test_order_levels_set_order_max_exception_negative():
    """Test that setting order_max to a negative value raises PyAnsysSoundException."""
    ol = OrderLevels()
    with pytest.raises(PyAnsysSoundException, match="Maximum order must be greater than 0."):
        ol.order_max = -10


# --- process() ---


def test_order_levels_process():
    """Test process: sequential missing-input errors then success."""
    ol = OrderLevels()

    with pytest.raises(PyAnsysSoundException) as excinfo:
        ol.process()
    assert str(excinfo.value) == (
        "No signal found for order level computation. Use `OrderLevels.signal`."
    )

    signal, rpm_profile = _load_signal_and_rpm()
    ol.signal = signal

    with pytest.raises(PyAnsysSoundException) as excinfo:
        ol.process()
    assert str(excinfo.value) == (
        "No RPM profile found for order level computation. Use `OrderLevels.rpm_profile`."
    )

    ol.rpm_profile = rpm_profile

    with pytest.raises(PyAnsysSoundException) as excinfo:
        ol.process()
    assert str(excinfo.value) == (
        "No orders found for order level computation. Use `OrderLevels.orders`."
    )

    ol.orders = [2.0, 4.0]

    try:
        ol.process()
    except Exception:
        assert False, "process() raised an unexpected exception"


# --- Unprocessed state ---


def test_order_levels_get_rpm_order_representation_not_processed():
    """Test get_rpm_order_representation warns and returns None when not processed."""
    ol = OrderLevels()
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the `OrderLevels.process\\(\\)` method.",
    ):
        result = ol.get_rpm_order_representation()
    assert result is None


def test_order_levels_get_output_not_processed():
    """Test get_output warns and returns None when not processed."""
    ol = OrderLevels()
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the `OrderLevels.process\\(\\)` method.",
    ):
        result = ol.get_output()
    assert result is None


def test_order_levels_get_output_as_nparray_not_processed():
    """Test get_output_as_nparray returns an empty list when not processed."""
    ol = OrderLevels()
    with pytest.warns(PyAnsysSoundWarning):
        result = ol.get_output_as_nparray()
    assert result == []


def test_order_levels_get_associated_rpm_not_processed():
    """Test get_associated_rpm returns an empty array when not processed."""
    ol = OrderLevels()
    with pytest.warns(PyAnsysSoundWarning):
        result = ol.get_associated_rpm()
    assert result.size == 0


# --- Outputs after process() ---


def test_order_levels_get_output():
    """Test get_output returns a list of Fields of the expected length."""
    signal, rpm_profile = _load_signal_and_rpm()
    ol = OrderLevels(signal=signal, rpm_profile=rpm_profile, orders=[2.0, 4.0])
    ol.process()
    output = ol.get_output()
    assert output is not None
    assert len(output) == EXP_NUM_ORDERS


def test_order_levels_get_rpm_order_representation():
    """Test get_rpm_order_representation returns a non-None FieldsContainer after processing."""
    signal, rpm_profile = _load_signal_and_rpm()
    ol = OrderLevels(signal=signal, rpm_profile=rpm_profile, orders=[2.0, 4.0])
    ol.process()
    assert ol.get_rpm_order_representation() is not None


def test_order_levels_get_output_as_nparray():
    """Test get_output_as_nparray shape and spot values."""
    signal, rpm_profile = _load_signal_and_rpm()
    ol = OrderLevels(signal=signal, rpm_profile=rpm_profile, orders=[2.0, 4.0], order_max=160)
    ol.process()
    out = ol.get_output_as_nparray()
    assert len(out) == EXP_NUM_ORDERS
    assert len(out[0]) == EXP_NUM_RPM_POINTS
    assert out[0][0] == pytest.approx(EXP_SQ_ORDER2_IDX0, rel=1e-4)
    assert out[0][10] == pytest.approx(EXP_SQ_ORDER2_IDX10, rel=1e-4)
    assert out[0][100] == pytest.approx(EXP_SQ_ORDER2_IDX100, rel=1e-4)
    assert out[0][500] == pytest.approx(EXP_SQ_ORDER2_IDX500, rel=1e-4)
    assert out[1][0] == pytest.approx(EXP_SQ_ORDER4_IDX0, rel=1e-4)
    assert out[1][10] == pytest.approx(EXP_SQ_ORDER4_IDX10, rel=1e-4)
    assert out[1][100] == pytest.approx(EXP_SQ_ORDER4_IDX100, rel=1e-4)
    assert out[1][500] == pytest.approx(EXP_SQ_ORDER4_IDX500, rel=1e-4)


def test_order_levels_get_order_levels_in_squared_linear_unit():
    """Test get_order_levels_in_squared_linear_unit is identical to get_output_as_nparray."""
    signal, rpm_profile = _load_signal_and_rpm()
    ol = OrderLevels(signal=signal, rpm_profile=rpm_profile, orders=[2.0, 4.0])
    ol.process()
    sq = ol.get_order_levels_in_squared_linear_unit()
    raw = ol.get_output_as_nparray()
    assert len(sq) == EXP_NUM_ORDERS
    np.testing.assert_array_equal(sq[0], raw[0])
    np.testing.assert_array_equal(sq[1], raw[1])


def test_order_levels_get_order_levels_in_linear_unit():
    """Test get_order_levels_in_linear_unit returns the sqrt of squared values."""
    signal, rpm_profile = _load_signal_and_rpm()
    ol = OrderLevels(signal=signal, rpm_profile=rpm_profile, orders=[2.0, 4.0], order_max=160)
    ol.process()
    lin = ol.get_order_levels_in_linear_unit()
    assert len(lin) == EXP_NUM_ORDERS
    assert lin[0][0] == pytest.approx(EXP_LIN_ORDER2_IDX0, rel=1e-4)
    assert lin[1][0] == pytest.approx(EXP_LIN_ORDER4_IDX0, rel=1e-4)


def test_order_levels_get_order_levels_in_dB():
    """Test get_order_levels_in_dB spot values with reference_value=1.0."""
    signal, rpm_profile = _load_signal_and_rpm()
    ol = OrderLevels(signal=signal, rpm_profile=rpm_profile, orders=[2.0, 4.0], order_max=160)
    ol.process()
    db = ol.get_order_levels_in_dB(reference_value=1.0)
    assert len(db) == EXP_NUM_ORDERS
    assert db[0][0] == pytest.approx(EXP_DB_ORDER2_IDX0, rel=1e-4)
    assert db[1][0] == pytest.approx(EXP_DB_ORDER4_IDX0, rel=1e-4)


def test_order_levels_get_order_levels_in_dB_exception_zero():
    """Test get_order_levels_in_dB raises when reference_value is 0."""
    signal, rpm_profile = _load_signal_and_rpm()
    ol = OrderLevels(signal=signal, rpm_profile=rpm_profile, orders=[2.0, 4.0])
    ol.process()
    with pytest.raises(PyAnsysSoundException, match="Reference value must be greater than 0."):
        ol.get_order_levels_in_dB(reference_value=0)


def test_order_levels_get_order_levels_in_dB_exception_negative():
    """Test get_order_levels_in_dB raises when reference_value is negative."""
    signal, rpm_profile = _load_signal_and_rpm()
    ol = OrderLevels(signal=signal, rpm_profile=rpm_profile, orders=[2.0, 4.0])
    ol.process()
    with pytest.raises(PyAnsysSoundException, match="Reference value must be greater than 0."):
        ol.get_order_levels_in_dB(reference_value=-1.0)


def test_order_levels_get_order_level():
    """Test get_order_level returns the correct array for a given order."""
    signal, rpm_profile = _load_signal_and_rpm()
    ol = OrderLevels(signal=signal, rpm_profile=rpm_profile, orders=[2.0, 4.0], order_max=160)
    ol.process()
    lvl = ol.get_order_level(2.0)
    assert isinstance(lvl, np.ndarray)
    assert len(lvl) == EXP_NUM_RPM_POINTS
    assert lvl[0] == pytest.approx(EXP_SQ_ORDER2_IDX0, rel=1e-4)


def test_order_levels_get_order_level_exception():
    """Test get_order_level raises when the requested order is absent from the list."""
    signal, rpm_profile = _load_signal_and_rpm()
    ol = OrderLevels(signal=signal, rpm_profile=rpm_profile, orders=[2.0, 4.0])
    ol.process()
    with pytest.raises(
        PyAnsysSoundException,
        match="Order 99.0 is not in the list of orders.",
    ):
        ol.get_order_level(99.0)


def test_order_levels_get_associated_rpm():
    """Test get_associated_rpm returns the expected RPM support vector."""
    signal, rpm_profile = _load_signal_and_rpm()
    ol = OrderLevels(signal=signal, rpm_profile=rpm_profile, orders=[2.0, 4.0], order_max=160)
    ol.process()
    rpm_arr = ol.get_associated_rpm()
    assert isinstance(rpm_arr, np.ndarray)
    assert len(rpm_arr) == EXP_NUM_RPM_POINTS
    assert rpm_arr[0] == pytest.approx(EXP_RPM_0, rel=1e-4)
    assert rpm_arr[100] == pytest.approx(EXP_RPM_IDX100, rel=1e-4)
    assert rpm_arr[500] == pytest.approx(EXP_RPM_IDX500, rel=1e-4)
    assert rpm_arr[-1] == pytest.approx(EXP_RPM_LAST, rel=1e-4)


def test_order_levels_get_output_as_nparray_with_order_10():
    """Test get_output_as_nparray returns 3 arrays when orders=[2,4,10]."""
    signal, rpm_profile = _load_signal_and_rpm()
    ol = OrderLevels(signal=signal, rpm_profile=rpm_profile, orders=[2.0, 4.0, 10.0], order_max=160)
    ol.process()
    out = ol.get_output_as_nparray()
    assert len(out) == 3
    assert len(out[2]) == EXP_NUM_RPM_POINTS
    assert out[2][0] == pytest.approx(EXP_SQ_ORDER10_IDX0, rel=1e-4)
    assert out[2][10] == pytest.approx(EXP_SQ_ORDER10_IDX10, rel=1e-4)


def test_order_levels_get_output_as_nparray_width_100():
    """Test get_output_as_nparray with width=100%."""
    signal, rpm_profile = _load_signal_and_rpm()
    ol = OrderLevels(
        signal=signal, rpm_profile=rpm_profile, orders=[2.0, 4.0], width=100.0, order_max=160
    )
    ol.process()
    out = ol.get_output_as_nparray()
    assert len(out) == EXP_NUM_ORDERS
    assert len(out[0]) == EXP_NUM_RPM_POINTS
    assert out[0][0] == pytest.approx(EXP_SQ_ORDER2_IDX0_W100, rel=1e-4)
    assert out[0][10] == pytest.approx(EXP_SQ_ORDER2_IDX10_W100, rel=1e-4)
    assert out[1][0] == pytest.approx(EXP_SQ_ORDER4_IDX0_W100, rel=1e-4)
    assert out[1][10] == pytest.approx(EXP_SQ_ORDER4_IDX10_W100, rel=1e-4)


# --- plot() ---


@patch("matplotlib.pyplot.show")
def test_order_levels_plot(mock_show):
    """Test plot: raises before processing, succeeds after."""
    signal, rpm_profile = _load_signal_and_rpm()
    ol = OrderLevels(signal=signal, rpm_profile=rpm_profile, orders=[2.0, 4.0])

    with pytest.raises(
        PyAnsysSoundException,
        match="Output is not processed yet. Use the `OrderLevels.process\\(\\)` method.",
    ):
        ol.plot()

    ol.process()
    ol.plot()
    mock_show.assert_called_once()


@patch("matplotlib.pyplot.show")
def test_order_levels_plot_in_dB(mock_show):
    """Test plot with display_in_dB=True."""
    signal, rpm_profile = _load_signal_and_rpm()
    ol = OrderLevels(signal=signal, rpm_profile=rpm_profile, orders=[2.0, 4.0])
    ol.process()
    ol.plot(display_in_dB=True, reference_value=2e-5)
    mock_show.assert_called_once()


@patch("matplotlib.pyplot.show")
def test_order_levels_plot_warning_more_than_10_orders(mock_show):
    """Test that plot emits a warning and still runs when more than 10 orders are set."""
    signal, rpm_profile = _load_signal_and_rpm()
    orders_11 = [float(i) for i in range(1, 12)]
    ol = OrderLevels(signal=signal, rpm_profile=rpm_profile, orders=orders_11)
    ol.process()
    with pytest.warns(
        PyAnsysSoundWarning,
        match="More than 10 order values were listed.",
    ):
        ol.plot()
    mock_show.assert_called_once()


# --- export ---


def test_order_levels_export_not_implemented():
    """Test that export_as_AnsysSound_Orders raises NotImplementedError."""
    ol = OrderLevels()
    with pytest.raises(NotImplementedError):
        ol.export_as_AnsysSound_Orders("dummy_path.txt")
