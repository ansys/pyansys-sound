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

from ansys.dpf.core import Field, FieldsContainer
import numpy as np
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ansys.sound.core.signal_utilities import LoadWav
from ansys.sound.core.spectrogram_processing import IsolateOrders


def test_isolate_orders_instantiation(dpf_sound_test_server):
    isolate_orders = IsolateOrders()
    assert isolate_orders != None


def test_isolate_orders_process(dpf_sound_test_server):
    isolate_orders = IsolateOrders()
    wav_loader = LoadWav(pytest.data_path_accel_with_rpm_in_container)
    wav_loader.process()

    fc = wav_loader.get_output()
    signal = fc[0]
    rpm_profile = fc[1]
    rpm_profile.time_freq_support = signal.time_freq_support

    # Error 1
    with pytest.raises(PyAnsysSoundException) as excinfo:
        isolate_orders.process()
    assert str(excinfo.value) == "No signal found for order isolation. Use 'IsolateOrder.signal'."

    isolate_orders.signal = signal

    # Error 2
    with pytest.raises(PyAnsysSoundException) as excinfo:
        isolate_orders.process()
    assert (
        str(excinfo.value)
        == "No RPM profile found for order isolation. Use 'IsolateOrder.rpm_profile'."
    )

    # Testing input fields container (no error expected)
    isolate_orders.rpm_profile = rpm_profile

    # Error 3
    with pytest.raises(PyAnsysSoundException) as excinfo:
        isolate_orders.process()
    assert str(excinfo.value) == "No orders found for order isolation. Use 'IsolateOrder.orders'."

    isolate_orders.orders = [2, 4]

    try:
        isolate_orders.process()
    except:
        # Should not fail
        assert False


def test_isolate_orders_get_output(dpf_sound_test_server):
    wav_loader = LoadWav(pytest.data_path_accel_with_rpm_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()
    signal = fc[0]
    rpm_profile = fc[1]
    rpm_profile.time_freq_support = signal.time_freq_support
    isolate_orders = IsolateOrders(signal=signal, rpm_profile=rpm_profile, orders=[2, 4])

    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. \
            Use the 'IsolateOrders.process()' method.",
    ):
        fc_out = isolate_orders.get_output()

    isolate_orders.process()
    fc_out = isolate_orders.get_output()

    assert len(fc_out) == 909956

    fc_bis = FieldsContainer()
    fc_bis.add_label("channel_number")
    fc_bis.add_field({"channel_number": 0}, signal)
    isolate_orders.signal = fc_bis

    isolate_orders.process()
    fc_out = isolate_orders.get_output()

    assert len(fc_out) == 1
    assert len(fc_out[0].data) == 909956


def test_isolate_orders_get_output_as_np_array(dpf_sound_test_server):
    wav_loader = LoadWav(pytest.data_path_accel_with_rpm_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()
    signal = fc[0]
    rpm_profile = fc[1]
    rpm_profile.time_freq_support = signal.time_freq_support
    isolate_orders = IsolateOrders(signal=signal, rpm_profile=rpm_profile, orders=[2, 4])

    isolate_orders.process()
    arr = isolate_orders.get_output_as_nparray()

    assert arr[100] == -0.11279940605163574
    assert arr[1000] == -0.016805129125714302
    assert arr[10000] == -0.04283715412020683

    fc_bis = FieldsContainer()
    fc_bis.add_label("channel_number")
    fc_bis.add_field({"channel_number": 0}, signal)
    isolate_orders.signal = fc_bis

    isolate_orders.process()
    arr = isolate_orders.get_output_as_nparray()

    assert arr[100] == -0.11279940605163574
    assert arr[1000] == -0.016805129125714302
    assert arr[10000] == -0.04283715412020683


def test_isolate_orders_set_get_signal(dpf_sound_test_server):
    isolate_orders = IsolateOrders()
    fc = FieldsContainer()
    fc.labels = ["channel"]
    f = Field()
    f.data = 42 * np.ones(3)
    fc.add_field({"channel": 0}, f)
    fc.name = "testField"
    isolate_orders.signal = fc
    f = isolate_orders.signal

    assert len(f[0]) == 3
    assert f[0].data[0, 2] == 42


def test_isolate_orders_set_get_fft_size(dpf_sound_test_server):
    isolate_orders = IsolateOrders()

    # Error
    with pytest.raises(PyAnsysSoundException) as excinfo:
        isolate_orders.fft_size = -12.0
    assert str(excinfo.value) == "FFT size must be greater than 0.0."

    isolate_orders.fft_size = 1234.0
    assert isolate_orders.fft_size == 1234.0


def test_isolate_orders_set_get_window_overlap(dpf_sound_test_server):
    isolate_orders = IsolateOrders()

    # Error
    with pytest.raises(PyAnsysSoundException) as excinfo:
        isolate_orders.window_overlap = -12.0
    assert str(excinfo.value) == "Window overlap must be between 0.0 and 1.0."

    isolate_orders.window_overlap = 0.5
    assert isolate_orders.window_overlap == 0.5


def test_isolate_orders_set_get_window_type(dpf_sound_test_server):
    isolate_orders = IsolateOrders()

    # Error
    with pytest.raises(PyAnsysSoundException) as excinfo:
        isolate_orders.window_type = "InvalidWindow"
    assert (
        str(excinfo.value)
        == "Invalid window type, accepted values are 'HANNING', 'BLACKMANHARRIS', 'HANN',"
        " 'BLACKMAN','HAMMING', 'KAISER', 'BARTLETT', 'RECTANGULAR'."
    )

    isolate_orders.window_type = "KAISER"
    assert isolate_orders.window_type == "KAISER"


def test_isolate_orders_set_get_rpm_profile(dpf_sound_test_server):
    isolate_orders = IsolateOrders()

    rpm = Field()
    rpm.append([1, 23, 45], 1)

    isolate_orders.rpm_profile = rpm
    assert isolate_orders.rpm_profile.data[0, 2] == 45


def test_isolate_orders_set_get_orders(dpf_sound_test_server):
    isolate_orders = IsolateOrders()
    orders = Field()
    orders.append([1, 2, 45], 1)

    isolate_orders.orders = orders
    assert isolate_orders.orders.data[0, 2] == 45

    isolate_orders.orders = [1, 2, 45]
    assert isolate_orders.orders.data[0, 2] == 45


def test_isolate_orders_set_get_width_selection(dpf_sound_test_server):
    isolate_orders = IsolateOrders()

    # Error
    with pytest.raises(PyAnsysSoundException) as excinfo:
        isolate_orders.width_selection = -12.0
    assert str(excinfo.value) == "Width selection must be greater than 0.0."

    isolate_orders.window_overlap = 0.5
    assert isolate_orders.window_overlap == 0.5


@patch("matplotlib.pyplot.show")
def test_isolate_orders_plot(mock_show, dpf_sound_test_server):
    wav_loader = LoadWav(pytest.data_path_accel_with_rpm_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()
    signal = fc[0]
    rpm_profile = fc[1]
    rpm_profile.time_freq_support = signal.time_freq_support
    isolate_orders = IsolateOrders(signal=signal, rpm_profile=rpm_profile, orders=[2, 4])
    isolate_orders.process()
    isolate_orders.plot()

    fc_bis = FieldsContainer()
    fc_bis.add_label("channel_number")
    fc_bis.add_field({"channel_number": 0}, signal)
    isolate_orders.signal = fc_bis
    isolate_orders.process()
    isolate_orders.plot()
