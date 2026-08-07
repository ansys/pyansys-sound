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

from ansys.dpf.core import Field, FieldsContainer, Operator
import numpy as np
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ansys.sound.core.order_analysis import OrderLevels
from ansys.sound.core.order_analysis.rpm_order_representation import RpmOrderRepresentation

# Skip entire test module if Sound version < 2027.1.0
if not pytest.SOUND_VERSION_GREATER_THAN_OR_EQUAL_TO_2027R1:
    pytest.skip("Requires Sound version >= 2027.1.0", allow_module_level=True)

def test_repr_operator_100_1_1(load_accel_and_rpm):
    signal, rpm_profile = load_accel_and_rpm
    op = Operator("compute_rpm_order_representation")
    op.connect(0, signal)
    op.connect(1, rpm_profile)
    op.connect(2, 100)
    op.connect(3, 1.0)
    op.run()


def test_repr_operator_100_1_2(load_accel_and_rpm):
    signal, rpm_profile = load_accel_and_rpm
    op = Operator("compute_rpm_order_representation")
    op.connect(0, signal)
    op.connect(1, rpm_profile)
    op.connect(2, 100)
    op.connect(3, 1.0)
    op.run()


def test_repr_operator_100_1_3(load_accel_and_rpm):
    signal, rpm_profile = load_accel_and_rpm
    op = Operator("compute_rpm_order_representation")
    op.connect(0, signal)
    op.connect(1, rpm_profile)
    op.connect(2, 100)
    op.connect(3, 1.0)
    op.run()


def test_repr_operator_100_1_4(load_accel_and_rpm):
    signal, rpm_profile = load_accel_and_rpm
    op = Operator("compute_rpm_order_representation")
    op.connect(0, signal)
    op.connect(1, rpm_profile)
    op.connect(2, 100)
    op.connect(3, 1.0)
    op.run()


def test_repr_operator_100_1_5(load_accel_and_rpm):
    signal, rpm_profile = load_accel_and_rpm
    op = Operator("compute_rpm_order_representation")
    op.connect(0, signal)
    op.connect(1, rpm_profile)
    op.connect(2, 100)
    op.connect(3, 1.0)
    op.run()


def test_repr_operator_100_1_6(load_accel_and_rpm):
    signal, rpm_profile = load_accel_and_rpm
    op = Operator("compute_rpm_order_representation")
    op.connect(0, signal)
    op.connect(1, rpm_profile)
    op.connect(2, 100)
    op.connect(3, 1.0)
    op.run()


def test_repr_operator_100_1_7(load_accel_and_rpm):
    signal, rpm_profile = load_accel_and_rpm
    op = Operator("compute_rpm_order_representation")
    op.connect(0, signal)
    op.connect(1, rpm_profile)
    op.connect(2, 100)
    op.connect(3, 1.0)
    op.run()


def test_repr_operator_100_1_8(load_accel_and_rpm):
    signal, rpm_profile = load_accel_and_rpm
    op = Operator("compute_rpm_order_representation")
    op.connect(0, signal)
    op.connect(1, rpm_profile)
    op.connect(2, 100)
    op.connect(3, 1.0)
    op.run()


def test_repr_operator_100_1_9(load_accel_and_rpm):
    signal, rpm_profile = load_accel_and_rpm
    op = Operator("compute_rpm_order_representation")
    op.connect(0, signal)
    op.connect(1, rpm_profile)
    op.connect(2, 100)
    op.connect(3, 1.0)
    op.run()


def test_repr_operator_100_1_10(load_accel_and_rpm):
    signal, rpm_profile = load_accel_and_rpm
    op = Operator("compute_rpm_order_representation")
    op.connect(0, signal)
    op.connect(1, rpm_profile)
    op.connect(2, 100)
    op.connect(3, 1.0)
    op.run()


def test_repr_operator_100_1_11(load_accel_and_rpm):
    signal, rpm_profile = load_accel_and_rpm
    op = Operator("compute_rpm_order_representation")
    op.connect(0, signal)
    op.connect(1, rpm_profile)
    op.connect(2, 100)
    op.connect(3, 1.0)
    op.run()


def test_repr_operator_100_1_12(load_accel_and_rpm):
    signal, rpm_profile = load_accel_and_rpm
    op = Operator("compute_rpm_order_representation")
    op.connect(0, signal)
    op.connect(1, rpm_profile)
    op.connect(2, 100)
    op.connect(3, 1.0)
    op.run()


def test_repr_operator_100_1_13(load_accel_and_rpm):
    signal, rpm_profile = load_accel_and_rpm
    op = Operator("compute_rpm_order_representation")
    op.connect(0, signal)
    op.connect(1, rpm_profile)
    op.connect(2, 100)
    op.connect(3, 1.0)
    op.run()


def test_repr_operator_100_1_14(load_accel_and_rpm):
    signal, rpm_profile = load_accel_and_rpm
    op = Operator("compute_rpm_order_representation")
    op.connect(0, signal)
    op.connect(1, rpm_profile)
    op.connect(2, 100)
    op.connect(3, 1.0)
    op.run()


def test_repr_operator_100_1_15(load_accel_and_rpm):
    signal, rpm_profile = load_accel_and_rpm
    op = Operator("compute_rpm_order_representation")
    op.connect(0, signal)
    op.connect(1, rpm_profile)
    op.connect(2, 100)
    op.connect(3, 1.0)
    op.run()


def test_repr_operator_100_1_16(load_accel_and_rpm):
    signal, rpm_profile = load_accel_and_rpm
    op = Operator("compute_rpm_order_representation")
    op.connect(0, signal)
    op.connect(1, rpm_profile)
    op.connect(2, 100)
    op.connect(3, 1.0)
    op.run()


def test_repr_operator_100_1_17(load_accel_and_rpm):
    signal, rpm_profile = load_accel_and_rpm
    op = Operator("compute_rpm_order_representation")
    op.connect(0, signal)
    op.connect(1, rpm_profile)
    op.connect(2, 100)
    op.connect(3, 1.0)
    op.run()


def test_repr_operator_100_1_18(load_accel_and_rpm):
    signal, rpm_profile = load_accel_and_rpm
    op = Operator("compute_rpm_order_representation")
    op.connect(0, signal)
    op.connect(1, rpm_profile)
    op.connect(2, 100)
    op.connect(3, 1.0)
    op.run()


def test_repr_operator_100_1_19(load_accel_and_rpm):
    signal, rpm_profile = load_accel_and_rpm
    op = Operator("compute_rpm_order_representation")
    op.connect(0, signal)
    op.connect(1, rpm_profile)
    op.connect(2, 100)
    op.connect(3, 1.0)
    op.run()


def test_repr_operator_100_1_20(load_accel_and_rpm):
    signal, rpm_profile = load_accel_and_rpm
    op = Operator("compute_rpm_order_representation")
    op.connect(0, signal)
    op.connect(1, rpm_profile)
    op.connect(2, 100)
    op.connect(3, 1.0)
    op.run()


def test_repr_operator_def1(load_accel_and_rpm):
    signal, rpm_profile = load_accel_and_rpm
    op = Operator("compute_rpm_order_representation")
    op.connect(0, signal)
    op.connect(1, rpm_profile)
    op.connect(2, 160)
    op.connect(3, 2.0)
    op.run()


def test_repr_operator_def2(load_accel_and_rpm):
    signal, rpm_profile = load_accel_and_rpm
    op = Operator("compute_rpm_order_representation")
    op.connect(0, signal)
    op.connect(1, rpm_profile)
    op.connect(2, 160)
    op.connect(3, 2.0)
    op.run()


def test_repr_operator_def3(load_accel_and_rpm):
    signal, rpm_profile = load_accel_and_rpm
    op = Operator("compute_rpm_order_representation")
    op.connect(0, signal)
    op.connect(1, rpm_profile)
    op.connect(2, 160)
    op.connect(3, 2.0)
    op.run()


def test_repr_operator_def4(load_accel_and_rpm):
    signal, rpm_profile = load_accel_and_rpm
    op = Operator("compute_rpm_order_representation")
    op.connect(0, signal)
    op.connect(1, rpm_profile)
    op.connect(2, 160)
    op.connect(3, 2.0)
    op.run()


def test_repr_operator_def5(load_accel_and_rpm):
    signal, rpm_profile = load_accel_and_rpm
    op = Operator("compute_rpm_order_representation")
    op.connect(0, signal)
    op.connect(1, rpm_profile)
    op.connect(2, 160)
    op.connect(3, 2.0)
    op.run()


def test_repr_operator_100_1_21(load_accel_and_rpm):
    signal, rpm_profile = load_accel_and_rpm
    op = Operator("compute_rpm_order_representation")
    op.connect(0, signal)
    op.connect(1, rpm_profile)
    op.connect(2, 100)
    op.connect(3, 1.0)
    op.run()


def test_repr_operator_100_1_22(load_accel_and_rpm):
    signal, rpm_profile = load_accel_and_rpm
    op = Operator("compute_rpm_order_representation")
    op.connect(0, signal)
    op.connect(1, rpm_profile)
    op.connect(2, 100)
    op.connect(3, 1.0)
    op.run()


def test_repr_operator_100_1_23(load_accel_and_rpm):
    signal, rpm_profile = load_accel_and_rpm
    op = Operator("compute_rpm_order_representation")
    op.connect(0, signal)
    op.connect(1, rpm_profile)
    op.connect(2, 100)
    op.connect(3, 1.0)
    op.run()


def test_repr_operator_100_1_24(load_accel_and_rpm):
    signal, rpm_profile = load_accel_and_rpm
    op = Operator("compute_rpm_order_representation")
    op.connect(0, signal)
    op.connect(1, rpm_profile)
    op.connect(2, 100)
    op.connect(3, 1.0)
    op.run()


def test_repr_operator_100_1_25(load_accel_and_rpm):
    signal, rpm_profile = load_accel_and_rpm
    op = Operator("compute_rpm_order_representation")
    op.connect(0, signal)
    op.connect(1, rpm_profile)
    op.connect(2, 100)
    op.connect(3, 1.0)
    op.run()

def test_repr_operator_10_0p1_1(load_accel_and_rpm):
    signal, rpm_profile = load_accel_and_rpm
    op = Operator("compute_rpm_order_representation")
    op.connect(0, signal)
    op.connect(1, rpm_profile)
    op.connect(2, 10)
    op.connect(3, 0.1)
    op.run()


def test_repr_operator_10_0p1_2(load_accel_and_rpm):
    signal, rpm_profile = load_accel_and_rpm
    op = Operator("compute_rpm_order_representation")
    op.connect(0, signal)
    op.connect(1, rpm_profile)
    op.connect(2, 10)
    op.connect(3, 0.1)
    op.run()


def test_repr_operator_10_0p1_3(load_accel_and_rpm):
    signal, rpm_profile = load_accel_and_rpm
    op = Operator("compute_rpm_order_representation")
    op.connect(0, signal)
    op.connect(1, rpm_profile)
    op.connect(2, 10)
    op.connect(3, 0.1)
    op.run()


def test_repr_operator_10_0p1_4(load_accel_and_rpm):
    signal, rpm_profile = load_accel_and_rpm
    op = Operator("compute_rpm_order_representation")
    op.connect(0, signal)
    op.connect(1, rpm_profile)
    op.connect(2, 10)
    op.connect(3, 0.1)
    op.run()


def test_repr_operator_10_0p1_5(load_accel_and_rpm):
    signal, rpm_profile = load_accel_and_rpm
    op = Operator("compute_rpm_order_representation")
    op.connect(0, signal)
    op.connect(1, rpm_profile)
    op.connect(2, 10)
    op.connect(3, 0.1)
    op.run()














# def test_levels_defaults(load_accel_and_rpm):
#     signal, rpm_profile = load_accel_and_rpm
#     levels = OrderLevels(signal, rpm_profile, [1.0, 2.0, 3.0])
#     levels.process()


# def test_levels_1(load_accel_and_rpm):
#     signal, rpm_profile = load_accel_and_rpm
#     levels = OrderLevels(signal, rpm_profile, [1.0, 2.0, 3.0], order_width=5.0, max_order=100)
#     levels.process()


# # def test_levels_2(load_accel_and_rpm):
# #     signal, rpm_profile = load_accel_and_rpm
# #     levels = OrderLevels(signal, rpm_profile, [1.0, 2.0, 3.0], order_width=20.0, max_order=200)
# #     levels.process()


# def test_levels_3(load_accel_and_rpm):
#     signal, rpm_profile = load_accel_and_rpm
#     levels = OrderLevels(signal, rpm_profile, [1.0, 2.0, 3.0],  order_width=1.0, max_order=10)
#     levels.process()


# def test_levels_4(load_accel_and_rpm):
#     signal, rpm_profile = load_accel_and_rpm
#     levels = OrderLevels(signal, rpm_profile, [1.0, 2.0, 3.0], order_width=10.0, max_order=160)
#     levels.process()


# def test_levels_5(load_accel_and_rpm):
#     signal, rpm_profile = load_accel_and_rpm
#     levels = OrderLevels(signal, rpm_profile, [1.0, 2.0, 3.0],  order_width=10.0, max_order=160)
#     levels.process()


# def test_levels_6(load_accel_and_rpm):
#     signal, rpm_profile = load_accel_and_rpm
#     levels = OrderLevels(signal, rpm_profile, [1.0, 2.0, 3.0], order_width=10.0, max_order=160)
#     levels.process()


# def test_levels_7(load_accel_and_rpm):
#     signal, rpm_profile = load_accel_and_rpm
#     levels = OrderLevels(signal, rpm_profile, [1.0, 2.0, 3.0], order_width=10.0, max_order=160)
#     levels.process()


# def test_repr_default(load_accel_and_rpm):
#     signal, rpm_profile = load_accel_and_rpm
#     repr = RpmOrderRepresentation(signal, rpm_profile)
#     repr.process()


# def test_repr_1(load_accel_and_rpm):
#     signal, rpm_profile = load_accel_and_rpm
#     repr = RpmOrderRepresentation(signal, rpm_profile, max_order=100, order_resolution=1.0)
#     repr.process()


# def test_repr_2(load_accel_and_rpm):
#     signal, rpm_profile = load_accel_and_rpm
#     repr = RpmOrderRepresentation(signal, rpm_profile, max_order=200, order_resolution=5.0)
#     repr.process()


# def test_repr_3(load_accel_and_rpm):
#     signal, rpm_profile = load_accel_and_rpm
#     repr = RpmOrderRepresentation(signal, rpm_profile, max_order=10, order_resolution=0.5)
#     repr.process()


# def test_repr_4(load_accel_and_rpm):
#     signal, rpm_profile = load_accel_and_rpm
#     repr = RpmOrderRepresentation(signal, rpm_profile)
#     repr.process()


# def test_repr_5(load_accel_and_rpm):
#     signal, rpm_profile = load_accel_and_rpm
#     repr = RpmOrderRepresentation(signal, rpm_profile)
#     repr.process()


# def test_repr_6(load_accel_and_rpm):
#     signal, rpm_profile = load_accel_and_rpm
#     repr = RpmOrderRepresentation(signal, rpm_profile)
#     repr.process()


# def test_repr_7(load_accel_and_rpm):
#     signal, rpm_profile = load_accel_and_rpm
#     repr = RpmOrderRepresentation(signal, rpm_profile)
#     repr.process()


