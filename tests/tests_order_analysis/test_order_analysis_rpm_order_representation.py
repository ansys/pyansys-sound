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

from ansys.dpf.core import Field, FieldsContainer
import numpy as np
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ansys.sound.core.order_analysis import RpmOrderRepresentation

# Skip entire test module if Sound version < 2027.1.0
if not pytest.SOUND_VERSION_GREATER_THAN_OR_EQUAL_TO_2027R1:
    pytest.skip("Requires Sound version >= 2027.1.0", allow_module_level=True)

EXP_STR_DEFAULT = (
    "RpmOrderRepresentation object\n"
    "Data:\n"
    "\tSignal name: Not set\n"
    "\tRPM profile name: Not set\n"
    "\tMaximum order: 160\n"
    "\tOrder resolution: 2.0 %"
)

EXP_STR_ALL_SET = (
    "RpmOrderRepresentation object\n"
    "Data:\n"
    '\tSignal name: "Acceleration_with_Tacho"\n'
    '\tRPM profile name: "Acceleration_with_Tacho_RPM"\n'
    "\tMaximum order: 100\n"
    "\tOrder resolution: 1.0 %"
)

EXP_RPM_COUNT_MAX160 = 858
EXP_RPM_COUNT_MAX10 = 74
EXP_ORDER_COUNT = 8192

# Expected numerical values for order_max=160, order_resolution=2.0
# (using Acceleration_with_Tacho.wav == accel_with_rpm.wav)
EXP_RPM0_ORDER0_MAX160 = -0.120336
EXP_RPM0_ORDER500_MAX160 = -0.00803356
EXP_RPM12_ORDER836_MAX160 = -0.250228
EXP_RPM24_ORDER51_MAX160 = 272.303345  # order 2
EXP_RPM814_ORDER102_MAX160 = 118.96640  # order 4

# Expected numerical values for order_max=10, order_resolution=0.125
EXP_RPM0_ORDER0_MAX10 = -0.0132574
EXP_RPM0_ORDER500_MAX10 = 0.00075042
EXP_RPM12_ORDER836_MAX10 = 1.93926
EXP_RPM31_ORDER780_MAX10 = 140.056763  # order 2
EXP_RPM41_ORDER1560_MAX10 = 37.6345825  # order 4

EXP_RPM0 = 974.50
EXP_RPM12 = 977.29
EXP_RPM31 = 1135.03
EXP_RPM41 = 1214.33

EXP_TIME0 = 0.000
EXP_TIME12 = 0.157
EXP_TIME31 = 1.538
EXP_TIME41 = 2.185

EXP_ORDER0 = 0.000
EXP_ORDER51 = 2.000
EXP_ORDER102 = 4.000
EXP_ORDER500 = 19.592
EXP_ORDER836 = 32.758


def test_rpm_order_representation_instantiation_default():
    """Test the instantiation of RpmOrderRepresentation with default values."""
    obj = RpmOrderRepresentation()
    assert obj.signal is None
    assert obj.rpm_profile is None
    assert obj.max_order == 160
    assert obj.order_resolution == 2.0


def test_rpm_order_representation_instantiation_all_set(load_accel_and_rpm):
    """Test the instantiation of RpmOrderRepresentation with explicit parameters."""
    signal, rpm_profile = load_accel_and_rpm
    obj = RpmOrderRepresentation(
        signal=signal, rpm_profile=rpm_profile, max_order=100, order_resolution=1.0
    )
    assert obj.signal == signal
    assert obj.rpm_profile == rpm_profile
    assert obj.max_order == 100
    assert obj.order_resolution == 1.0


def test_rpm_order_representation___str__(load_accel_and_rpm):
    """Test the __str__ method of RpmOrderRepresentation."""
    obj = RpmOrderRepresentation()
    assert str(obj) == EXP_STR_DEFAULT

    signal, rpm_profile = load_accel_and_rpm
    obj = RpmOrderRepresentation(
        signal=signal, rpm_profile=rpm_profile, max_order=100, order_resolution=1.0
    )
    assert str(obj) == EXP_STR_ALL_SET


def test_rpm_order_representation_signal_property():
    """Test the signal property setter and getter."""
    obj = RpmOrderRepresentation()
    signal = Field()
    signal.data = 42.0 * np.ones(3)
    obj.signal = signal
    retrieved = obj.signal
    assert len(retrieved) == 3
    assert retrieved.data[0, 2] == 42.0


def test_rpm_order_representation_signal_property_exceptions():
    """Test the signal property exceptions."""
    obj = RpmOrderRepresentation()
    with pytest.raises(PyAnsysSoundException, match="Signal must be specified as a DPF field."):
        obj.signal = "WrongType"


def test_rpm_order_representation_rpm_profile_property():
    """Test the rpm_profile property setter and getter."""
    obj = RpmOrderRepresentation()
    rpm = Field()
    rpm.append([1000.0, 2000.0, 3000.0], 1)
    obj.rpm_profile = rpm
    assert obj.rpm_profile.data[0, 2] == 3000.0


def test_rpm_order_representation_rpm_profile_property_exceptions():
    """Test the rpm_profile property exceptions."""
    obj = RpmOrderRepresentation()
    with pytest.raises(
        PyAnsysSoundException, match="RPM profile must be specified as a DPF field."
    ):
        obj.rpm_profile = 12345


def test_rpm_order_representation_max_order_property():
    """Test the max_order property setter and getter."""
    obj = RpmOrderRepresentation()
    obj.max_order = 50
    assert obj.max_order == 50


def test_rpm_order_representation_max_order_property_exceptions():
    """Test that setting max_order to 0 raises PyAnsysSoundException."""
    obj = RpmOrderRepresentation()

    with pytest.raises(PyAnsysSoundException, match="Maximum order must be greater than 0."):
        obj.max_order = 0

    with pytest.raises(PyAnsysSoundException, match="Maximum order must be greater than 0."):
        obj.max_order = -5


def test_rpm_order_representation_order_resolution_property():
    """Test the order_resolution property setter and getter."""
    obj = RpmOrderRepresentation()
    obj.order_resolution = 0.5
    assert obj.order_resolution == 0.5


def test_rpm_order_representation_order_resolution_property_exceptions():
    """Test the order_resolution property exceptions."""
    obj = RpmOrderRepresentation()
    with pytest.raises(PyAnsysSoundException, match="Order resolution must be greater than 0.0."):
        obj.order_resolution = 0.0


def test_rpm_order_representation_process(load_accel_and_rpm):
    """Test the process method."""
    signal, rpm_profile = load_accel_and_rpm
    obj = RpmOrderRepresentation(signal=signal, rpm_profile=rpm_profile)
    obj.process()
    assert obj._output is not None


def test_rpm_order_representation_process_exceptions(load_accel_and_rpm):
    """Test the process method's exceptions."""
    signal, rpm_profile = load_accel_and_rpm
    obj = RpmOrderRepresentation(rpm_profile=rpm_profile)
    with pytest.raises(
        PyAnsysSoundException, match="No input signal is set. Use `RpmOrderRepresentation.signal`."
    ):
        obj.process()

    obj = RpmOrderRepresentation(signal=signal)
    with pytest.raises(
        PyAnsysSoundException,
        match="No RPM profile is set. Use `RpmOrderRepresentation.rpm_profile`.",
    ):
        obj.process()

    obj = RpmOrderRepresentation(
        signal=signal, rpm_profile=rpm_profile, max_order=10, order_resolution=10
    )
    with pytest.raises(
        PyAnsysSoundException, match="Order resolution must be less than the maximum order."
    ):
        obj.process()


def test_rpm_order_representation_get_output(load_accel_and_rpm):
    """Test the get_output method."""
    signal, rpm_profile = load_accel_and_rpm
    obj = RpmOrderRepresentation(signal=signal, rpm_profile=rpm_profile, max_order=160)

    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the `RpmOrderRepresentation.process\(\)` method.",
    ):
        rpm_order_representation = obj.get_output()
    assert rpm_order_representation is None

    obj.process()
    rpm_order_representation = obj.get_output()
    assert isinstance(rpm_order_representation, FieldsContainer)
    assert len(rpm_order_representation) == EXP_RPM_COUNT_MAX160 * 2  # *2: Real and imaginary parts
    assert len(rpm_order_representation[0].data) == EXP_ORDER_COUNT
    assert rpm_order_representation[0].data[0] == pytest.approx(EXP_RPM0_ORDER0_MAX160, abs=1e-4)
    assert rpm_order_representation[0].data[500] == pytest.approx(
        EXP_RPM0_ORDER500_MAX160, abs=1e-4
    )
    assert rpm_order_representation[24].data[836] == pytest.approx(
        EXP_RPM12_ORDER836_MAX160, abs=1e-4
    )
    assert rpm_order_representation[48].data[51] == pytest.approx(
        EXP_RPM24_ORDER51_MAX160, abs=1e-4
    )
    assert rpm_order_representation[1628].data[102] == pytest.approx(
        EXP_RPM814_ORDER102_MAX160, abs=1e-1
    )
    assert rpm_order_representation.get_support("RPM") is not None
    assert rpm_order_representation.get_support("time") is not None


def test_rpm_order_representation_get_output_as_nparray_order_max_160(load_accel_and_rpm):
    """Test get_output_as_nparray with order_max=160 and order_resolution=2.0."""
    obj = RpmOrderRepresentation()
    with pytest.warns(PyAnsysSoundWarning):
        representation, orders, rpm, time = obj.get_output_as_nparray()
    assert len(representation) == 0
    assert len(orders) == 0
    assert len(rpm) == 0
    assert len(time) == 0

    signal, rpm_profile = load_accel_and_rpm
    obj = RpmOrderRepresentation(
        signal=signal, rpm_profile=rpm_profile, max_order=160, order_resolution=2.0
    )
    obj.process()
    representation, orders, rpm, time = obj.get_output_as_nparray()

    assert isinstance(representation, np.ndarray)
    assert isinstance(orders, np.ndarray)
    assert isinstance(rpm, np.ndarray)
    assert isinstance(time, np.ndarray)
    assert representation.shape == (EXP_RPM_COUNT_MAX160, EXP_ORDER_COUNT)
    assert representation[0][0].real == pytest.approx(EXP_RPM0_ORDER0_MAX160, abs=1e-4)
    assert representation[0][500].real == pytest.approx(EXP_RPM0_ORDER500_MAX160, abs=1e-4)
    assert representation[12][836].real == pytest.approx(EXP_RPM12_ORDER836_MAX160, abs=1e-4)
    assert representation[24][51].real == pytest.approx(EXP_RPM24_ORDER51_MAX160, abs=1e-2)
    assert representation[814][102].real == pytest.approx(EXP_RPM814_ORDER102_MAX160, abs=1e-1)
    assert len(orders) == EXP_ORDER_COUNT
    assert orders[0] == pytest.approx(EXP_ORDER0, abs=1e-2)
    assert orders[51] == pytest.approx(EXP_ORDER51, abs=1e-2)
    assert orders[102] == pytest.approx(EXP_ORDER102, abs=1e-2)
    assert orders[500] == pytest.approx(EXP_ORDER500, abs=1e-2)
    assert orders[836] == pytest.approx(EXP_ORDER836, abs=1e-2)
    assert len(rpm) == EXP_RPM_COUNT_MAX160
    assert rpm[0] == pytest.approx(EXP_RPM0, abs=1e-1)
    assert rpm[12] == pytest.approx(EXP_RPM12, abs=1e-1)
    assert rpm[31] == pytest.approx(EXP_RPM31, abs=1e-1)
    assert rpm[41] == pytest.approx(EXP_RPM41, abs=1e-1)
    assert len(time) == EXP_RPM_COUNT_MAX160
    assert time[0] == pytest.approx(EXP_TIME0, abs=1e-2)
    assert time[12] == pytest.approx(EXP_TIME12, abs=1e-2)
    assert time[31] == pytest.approx(EXP_TIME31, abs=1e-2)
    assert time[41] == pytest.approx(EXP_TIME41, abs=1e-2)


def test_rpm_order_representation_get_output_as_nparray_order_max_10(load_accel_and_rpm):
    """Test get_output_as_nparray with order_max=10 and order_resolution=0.125."""
    signal, rpm_profile = load_accel_and_rpm
    obj = RpmOrderRepresentation(
        signal=signal, rpm_profile=rpm_profile, max_order=10, order_resolution=0.125
    )
    obj.process()
    representation, _, _, _ = obj.get_output_as_nparray()

    assert representation.shape == (EXP_RPM_COUNT_MAX10, EXP_ORDER_COUNT)
    assert representation[0][0].real == pytest.approx(EXP_RPM0_ORDER0_MAX10, abs=1e-4)
    assert representation[0][500].real == pytest.approx(EXP_RPM0_ORDER500_MAX10, abs=1e-4)
    assert representation[12][836].real == pytest.approx(EXP_RPM12_ORDER836_MAX10, abs=1e-4)
    assert representation[31][780].real == pytest.approx(EXP_RPM31_ORDER780_MAX10, abs=1e-2)
    assert representation[41][1560].real == pytest.approx(EXP_RPM41_ORDER1560_MAX10, abs=1e-2)


def test_rpm_order_representation_get_rpm_order_representation(load_accel_and_rpm):
    """Test the get_rpm_order_representation method."""
    signal, rpm_profile = load_accel_and_rpm
    obj = RpmOrderRepresentation(signal=signal, rpm_profile=rpm_profile, max_order=160)
    obj.process()
    rpm_order_representation = obj.get_rpm_order_representation()
    assert isinstance(rpm_order_representation, np.ndarray)
    assert rpm_order_representation.shape == (EXP_RPM_COUNT_MAX160, EXP_ORDER_COUNT)
    assert rpm_order_representation[0][0].real == pytest.approx(EXP_RPM0_ORDER0_MAX160, abs=1e-4)
    assert rpm_order_representation[0][500].real == pytest.approx(
        EXP_RPM0_ORDER500_MAX160, abs=1e-4
    )
    assert rpm_order_representation[12][836].real == pytest.approx(
        EXP_RPM12_ORDER836_MAX160, abs=1e-4
    )
    assert rpm_order_representation[24][51].real == pytest.approx(
        EXP_RPM24_ORDER51_MAX160, abs=1e-2
    )
    assert rpm_order_representation[814][102].real == pytest.approx(
        EXP_RPM814_ORDER102_MAX160, abs=1e-1
    )


def test_rpm_order_representation_get_orders(load_accel_and_rpm):
    """Test the get_orders method."""
    signal, rpm_profile = load_accel_and_rpm
    obj = RpmOrderRepresentation(signal=signal, rpm_profile=rpm_profile, max_order=160)
    obj.process()
    orders = obj.get_orders()
    assert isinstance(orders, np.ndarray)
    assert len(orders) == EXP_ORDER_COUNT
    assert orders[0] == pytest.approx(EXP_ORDER0, abs=1e-2)
    assert orders[51] == pytest.approx(EXP_ORDER51, abs=1e-2)
    assert orders[102] == pytest.approx(EXP_ORDER102, abs=1e-2)
    assert orders[500] == pytest.approx(EXP_ORDER500, abs=1e-2)
    assert orders[836] == pytest.approx(EXP_ORDER836, abs=1e-2)


def test_rpm_order_representation_get_rpm_scale(load_accel_and_rpm):
    """Test the get_rpm_scale method."""
    signal, rpm_profile = load_accel_and_rpm
    obj = RpmOrderRepresentation(signal=signal, rpm_profile=rpm_profile, max_order=160)
    obj.process()
    rpm = obj.get_rpm_scale()
    assert isinstance(rpm, np.ndarray)
    assert len(rpm) == EXP_RPM_COUNT_MAX160
    assert rpm[0] == pytest.approx(EXP_RPM0, abs=1e-1)
    assert rpm[12] == pytest.approx(EXP_RPM12, abs=1e-1)
    assert rpm[31] == pytest.approx(EXP_RPM31, abs=1e-1)
    assert rpm[41] == pytest.approx(EXP_RPM41, abs=1e-1)


def test_rpm_order_representation_get_time_scale(load_accel_and_rpm):
    """Test the get_time_scale method."""
    signal, rpm_profile = load_accel_and_rpm
    obj = RpmOrderRepresentation(signal=signal, rpm_profile=rpm_profile, max_order=160)
    obj.process()
    time = obj.get_time_scale()
    assert isinstance(time, np.ndarray)
    assert len(time) == EXP_RPM_COUNT_MAX160
    assert time[0] == pytest.approx(EXP_TIME0, abs=1e-2)
    assert time[12] == pytest.approx(EXP_TIME12, abs=1e-2)
    assert time[31] == pytest.approx(EXP_TIME31, abs=1e-2)
    assert time[41] == pytest.approx(EXP_TIME41, abs=1e-2)
