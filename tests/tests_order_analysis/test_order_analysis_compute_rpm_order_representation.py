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

from ansys.dpf.core import Field
import numpy as np
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ansys.sound.core.order_analysis import ComputeRPMOrderRepresentation
from ansys.sound.core.signal_utilities import LoadWav

# Skip entire test module if Sound version < 2027.1.0
if not pytest.SOUND_VERSION_GREATER_THAN_OR_EQUAL_TO_2027R1:
    pytest.skip("Requires Sound version >= 2027.1.0", allow_module_level=True)

# Time frame counts per complex part (real or imaginary); the output FieldsContainer holds
# both real (complex=0) and imaginary (complex=1) fields, so total field count is * 2.
EXP_NUM_FRAMES_160 = 858
EXP_NUM_FRAMES_10 = 74

# Expected numerical values for order_max=160, order_resolution=2.0
# (from C++ TestSuiteOrderAnalysis using Acceleration_with_Tacho.wav == accel_with_rpm.wav)
EXP_160_FRAME0_IDX0 = -0.120336
EXP_160_FRAME0_IDX500 = -0.00803356
EXP_160_FRAME12_IDX836 = -0.250228
EXP_160_FRAME24_IDX51 = 272.302979  # order 2
EXP_160_FRAME814_IDX102 = 118.987877  # order 4

# Expected numerical values for order_max=10, order_resolution=0.125
EXP_10_FRAME0_IDX0 = -0.0132574
EXP_10_FRAME0_IDX500 = 0.00075042
EXP_10_FRAME12_IDX836 = 1.93926
EXP_10_FRAME31_IDX780 = 140.056763  # order 2
EXP_10_FRAME41_IDX1560 = 37.6345825  # order 4


def test_compute_rpm_order_representation_instantiation():
    """Test the instantiation of ComputeRPMOrderRepresentation with default values."""
    obj = ComputeRPMOrderRepresentation()
    assert obj is not None
    assert obj.signal is None
    assert obj.rpm_profile is None
    assert obj.order_max == 100
    assert obj.order_resolution == 2.0


def test_compute_rpm_order_representation_str():
    """Test the __str__ method of ComputeRPMOrderRepresentation."""
    obj = ComputeRPMOrderRepresentation()
    expected = (
        "ComputeRPMOrderRepresentation object\n"
        "Data:\n"
        "\tSignal name: Not set\n"
        "\tRPM profile name: Not set\n"
        "\tMaximum order: 100\n"
        "\tOrder resolution: 2.0 %"
    )
    assert str(obj) == expected

    wav_loader = LoadWav(pytest.data_path_accel_with_rpm)
    wav_loader.process()
    fc = wav_loader.get_output()
    obj.signal = fc[0]
    obj.rpm_profile = fc[1]
    s = str(obj)
    assert "Signal name:" in s
    assert "RPM profile name:" in s
    assert "Not set" not in s


def test_compute_rpm_order_representation_set_get_signal():
    """Test the signal property setter and getter."""
    obj = ComputeRPMOrderRepresentation()
    signal = Field()
    signal.data = 42.0 * np.ones(3)
    obj.signal = signal
    retrieved = obj.signal
    assert len(retrieved) == 3
    assert retrieved.data[0, 2] == 42.0


def test_compute_rpm_order_representation_set_signal_exception():
    """Test that assigning a non-Field to signal raises PyAnsysSoundException."""
    obj = ComputeRPMOrderRepresentation()
    with pytest.raises(PyAnsysSoundException, match="Signal must be specified as a DPF field."):
        obj.signal = "WrongType"
    assert obj.signal is None


def test_compute_rpm_order_representation_set_get_rpm_profile():
    """Test the rpm_profile property setter and getter."""
    obj = ComputeRPMOrderRepresentation()
    rpm = Field()
    rpm.append([1000.0, 2000.0, 3000.0], 1)
    obj.rpm_profile = rpm
    assert obj.rpm_profile.data[0, 2] == 3000.0


def test_compute_rpm_order_representation_set_rpm_profile_exception():
    """Test that assigning a non-Field to rpm_profile raises PyAnsysSoundException."""
    obj = ComputeRPMOrderRepresentation()
    with pytest.raises(
        PyAnsysSoundException, match="RPM profile must be specified as a DPF field."
    ):
        obj.rpm_profile = 12345
    assert obj.rpm_profile is None


def test_compute_rpm_order_representation_set_get_order_max():
    """Test the order_max property setter and getter."""
    obj = ComputeRPMOrderRepresentation()
    obj.order_max = 50
    assert obj.order_max == 50


def test_compute_rpm_order_representation_set_order_max_exception_zero():
    """Test that setting order_max to 0 raises PyAnsysSoundException."""
    obj = ComputeRPMOrderRepresentation()
    with pytest.raises(PyAnsysSoundException, match="Maximum order must be greater than 0."):
        obj.order_max = 0


def test_compute_rpm_order_representation_set_order_max_exception_negative():
    """Test that setting order_max to a negative value raises PyAnsysSoundException."""
    obj = ComputeRPMOrderRepresentation()
    with pytest.raises(PyAnsysSoundException, match="Maximum order must be greater than 0."):
        obj.order_max = -5


def test_compute_rpm_order_representation_set_get_order_resolution():
    """Test the order_resolution property setter and getter."""
    obj = ComputeRPMOrderRepresentation()
    obj.order_resolution = 0.5
    assert obj.order_resolution == 0.5


def test_compute_rpm_order_representation_set_order_resolution_exception_zero():
    """Test that setting order_resolution to 0.0 raises PyAnsysSoundException."""
    obj = ComputeRPMOrderRepresentation()
    with pytest.raises(PyAnsysSoundException, match="Order resolution must be greater than 0.0."):
        obj.order_resolution = 0.0


def test_compute_rpm_order_representation_process():
    """Test the process method of ComputeRPMOrderRepresentation."""
    obj = ComputeRPMOrderRepresentation()

    # Error: no signal set
    with pytest.raises(PyAnsysSoundException) as excinfo:
        obj.process()
    assert (
        str(excinfo.value) == "No signal found for RPM order representation computation. "
        "Use `ComputeRPMOrderRepresentation.signal`."
    )

    wav_loader = LoadWav(pytest.data_path_accel_with_rpm)
    wav_loader.process()
    fc = wav_loader.get_output()
    signal = fc[0]
    rpm_profile = fc[1]
    rpm_profile.time_freq_support = signal.time_freq_support

    obj.signal = signal

    # Error: no RPM profile set
    with pytest.raises(PyAnsysSoundException) as excinfo:
        obj.process()
    assert (
        str(excinfo.value) == "No RPM profile found for RPM order representation computation. "
        "Use `ComputeRPMOrderRepresentation.rpm_profile`."
    )

    obj.rpm_profile = rpm_profile

    try:
        obj.process()
    except Exception:
        assert False, "process() raised an unexpected exception"


def test_compute_rpm_order_representation_get_output():
    """Test the get_output method of ComputeRPMOrderRepresentation."""
    wav_loader = LoadWav(pytest.data_path_accel_with_rpm)
    wav_loader.process()
    fc = wav_loader.get_output()
    signal = fc[0]
    rpm_profile = fc[1]
    rpm_profile.time_freq_support = signal.time_freq_support

    # Use order_max=160 to match EXP_NUM_FRAMES_160 (frame count depends on order_max).
    obj = ComputeRPMOrderRepresentation(signal=signal, rpm_profile=rpm_profile, order_max=160)

    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. "
        "Use the `ComputeRPMOrderRepresentation.process\\(\\)` method.",
    ):
        output = obj.get_output()
        assert output is None

    obj.process()
    output = obj.get_output()
    assert output is not None
    # FieldsContainer contains real (complex=0) and imaginary (complex=1) fields.
    assert len(output) == EXP_NUM_FRAMES_160 * 2


def test_compute_rpm_order_representation_get_output_as_nparray_not_processed():
    """Test that get_output_as_nparray returns an empty array when not yet processed."""
    obj = ComputeRPMOrderRepresentation()
    with pytest.warns(PyAnsysSoundWarning):
        arr = obj.get_output_as_nparray()
    assert arr.size == 0


def test_compute_rpm_order_representation_get_output_as_nparray_order_max_160():
    """Test get_output_as_nparray with order_max=160 and order_resolution=2.0."""
    wav_loader = LoadWav(pytest.data_path_accel_with_rpm)
    wav_loader.process()
    fc = wav_loader.get_output()
    signal = fc[0]
    rpm_profile = fc[1]
    rpm_profile.time_freq_support = signal.time_freq_support

    obj = ComputeRPMOrderRepresentation(
        signal=signal, rpm_profile=rpm_profile, order_max=160, order_resolution=2.0
    )
    obj.process()
    arr = obj.get_output_as_nparray()

    # DPF iterates interleaved: real part of frame i is at arr[2*i], imaginary at arr[2*i+1].
    assert arr.shape[0] == EXP_NUM_FRAMES_160 * 2
    assert arr[0][0] == pytest.approx(EXP_160_FRAME0_IDX0, abs=1e-4)
    assert arr[0][500] == pytest.approx(EXP_160_FRAME0_IDX500, abs=1e-4)
    assert arr[24][836] == pytest.approx(EXP_160_FRAME12_IDX836, abs=1e-4)
    assert arr[48][51] == pytest.approx(EXP_160_FRAME24_IDX51, abs=1e-2)
    assert arr[1628][102] == pytest.approx(EXP_160_FRAME814_IDX102, abs=1e-1)


def test_compute_rpm_order_representation_get_output_as_nparray_order_max_10():
    """Test get_output_as_nparray with order_max=10 and order_resolution=0.125."""
    wav_loader = LoadWav(pytest.data_path_accel_with_rpm)
    wav_loader.process()
    fc = wav_loader.get_output()
    signal = fc[0]
    rpm_profile = fc[1]
    rpm_profile.time_freq_support = signal.time_freq_support

    obj = ComputeRPMOrderRepresentation(
        signal=signal, rpm_profile=rpm_profile, order_max=10, order_resolution=0.125
    )
    obj.process()
    arr = obj.get_output_as_nparray()

    # DPF iterates interleaved: real part of frame i is at arr[2*i], imaginary at arr[2*i+1].
    assert arr.shape[0] == EXP_NUM_FRAMES_10 * 2
    assert arr[0][0] == pytest.approx(EXP_10_FRAME0_IDX0, abs=1e-4)
    assert arr[0][500] == pytest.approx(EXP_10_FRAME0_IDX500, abs=1e-4)
    assert arr[24][836] == pytest.approx(EXP_10_FRAME12_IDX836, abs=1e-4)
    assert arr[62][780] == pytest.approx(EXP_10_FRAME31_IDX780, abs=1e-2)
    assert arr[82][1560] == pytest.approx(EXP_10_FRAME41_IDX1560, abs=1e-2)


def test_compute_rpm_order_representation_plot_exception():
    """Test that plot() raises PyAnsysSoundException (plotting is not supported)."""
    obj = ComputeRPMOrderRepresentation()
    with pytest.raises(
        PyAnsysSoundException,
        match="Plotting is not supported for class `ComputeRPMOrderRepresentation`",
    ):
        obj.plot()
