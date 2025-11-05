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

import numpy as np
import pytest
from ansys.dpf.core import Field

from ansys.sound.core._pyansys_sound import (PyAnsysSoundException,
                                             PyAnsysSoundWarning)
from ansys.sound.core.sound_power import SoundPowerLevelISO3744

if pytest.SERVERS_VERSION_GREATER_THAN_OR_EQUAL_TO_11_0:
    # bug fix in DPF Sound 2026 R1 ID#1325159
    EXP_LW_OCT_5_CALIB = 137.0859
    EXP_LW_3_10_CALIB = 89.9082
else:
    EXP_LW_OCT_5_CALIB = 137.0898
    EXP_LW_3_10_CALIB = 89.9006

EXP_SHAPE = "Hemisphere"
EXP_K2 = 1.1463640629030585
EXP_C1 = -0.10519597099301761
EXP_C2 = 0.1266523291988306
EXP_AREA_H = 6.283185
EXP_AREA_HH = 3.141593
EXP_SHAPE_FROM_PROJECT = "Hemisphere"
EXP_RADIUS_FROM_PROJECT = 3.0
EXP_K1_FROM_PROJECT = 1.0
EXP_K2_FROM_PROJECT = 2.0
EXP_C1_FROM_PROJECT = 3.0
EXP_C2_FROM_PROJECT = 4.0
EXP_SIGNAL_LIST_FROM_PROJECT = [[0, "flute.wav"], [1, "flute.wav"]]
EXP_LW = 103.73870086669922
EXP_LWA = 102.26373291015625
EXP_LW_OCT_5 = 98.7566909790039
EXP_FC_OCT_6 = 2000.0
EXP_LW_3_10 = 92.17286682128906
EXP_FC_3_12 = 400.0
EXP_STR = (
    "SoundPowerLevelISO3744 object\n"
    + "Data:\n"
    + "  Measurement surface:\n"
    + f"    Shape: Hemisphere\n"
    + f"    Radius: 3.0 m\n"
    + f"    Area: 56.5 m^2\n"
    + f"    Number of microphone signals: 2\n"
    + "  Correction coefficient:\n"
    + f"    K1 (background noise): 1.0 dB\n"
    + f"    K2 (measurement environment): 2.0 dB\n"
    + f"    C1 (meteorological reference quantity): 3.0 dB\n"
    + f"    C2 (meteorological radiation impedance): 4.0 dB\n"
    + "  Sound power level (Lw):\n"
    + f"    Unweighted: 103.7 dB\n"
    + f"    A-weighted: 102.3 dBA\n"
)
EXP_LW_CALIB = 151.41583251953125
EXP_LWA_CALIB = 152.14


def test_sound_power_level_iso_3744_instantiation():
    """Test SoundPowerLevelISO3744 instantiation."""
    # Test instantiation.
    swl = SoundPowerLevelISO3744()
    assert swl.surface_shape == EXP_SHAPE
    assert swl.surface_radius == 1.0
    assert swl.K1 == 0.0
    assert swl.K2 == 0.0
    assert swl.C1 == 0.0
    assert swl.C2 == 0.0


def test_sound_power_level_iso_3744_setters():
    """Test SoundPowerLevelISO3744 setters."""
    # Test setters.
    swl = SoundPowerLevelISO3744()
    swl.surface_shape = "Half-hemisphere"
    assert swl.surface_shape == "Half-hemisphere"

    swl.surface_radius = 2.0
    assert swl.surface_radius == 2.0

    swl.K1 = 1.5
    assert swl.K1 == 1.5

    swl.K2 = 1.5
    assert swl.K2 == 1.5

    swl.C1 = 1.5
    assert swl.C1 == 1.5

    swl.C2 = 1.5
    assert swl.C2 == 1.5


def test_sound_power_level_iso_3744_setters_exceptions():
    """Test SoundPowerLevelISO3744 setters' exceptions."""
    swl = SoundPowerLevelISO3744()
    with pytest.raises(
        PyAnsysSoundException,
        match="Input surface shape is invalid. Available options are 'Hemisphere' and 'Half-"
        "hemisphere'.",
    ):
        swl.surface_shape = "Invalid"

    with pytest.raises(
        PyAnsysSoundException, match="Input surface radius must be strictly positive."
    ):
        swl.surface_radius = -2.0


def test_sound_power_level_iso_3744_add_microphone_signal():
    """Test add_microphone_signal method."""
    swl = SoundPowerLevelISO3744()

    swl.add_microphone_signal(Field())


def test_sound_power_level_iso_3744_add_microphone_signal_exception_signal_type():
    """Test add_microphone_signal method's exception for invalid signal type."""
    swl = SoundPowerLevelISO3744()

    with pytest.raises(
        PyAnsysSoundException, match="Added signal must be provided as a DPF field."
    ):
        swl.add_microphone_signal([1, 2, 3])


def test_sound_power_level_iso_3744_get_all_signal_names():
    """Test get_all_signal_names method."""
    swl = SoundPowerLevelISO3744()
    swl.add_microphone_signal(Field())
    swl.add_microphone_signal(Field())

    names = swl.get_all_signal_names()
    assert names == [[0, ""], [1, ""]]


def test_sound_power_level_iso_3744_get_microphone_signal():
    """Test get_microphone_signal method."""
    swl = SoundPowerLevelISO3744()
    swl.add_microphone_signal(Field())

    signal = swl.get_microphone_signal(0)
    assert type(signal) is Field


def test_sound_power_level_iso_3744_get_microphone_signal_exception():
    """Test get_microphone_signal method's exception."""
    swl = SoundPowerLevelISO3744()
    swl.add_microphone_signal(Field())

    with pytest.raises(
        PyAnsysSoundException, match="No microphone signal associated with this index."
    ):
        swl.get_microphone_signal(1)


def test_sound_power_level_iso_3744_delete_microphone_signal():
    """Test delete_microphone_signal method."""
    swl = SoundPowerLevelISO3744()
    swl.add_microphone_signal(Field())
    swl.add_microphone_signal(Field())

    swl.delete_microphone_signal(0)
    assert swl.get_all_signal_names() == [[0, ""]]


def test_sound_power_level_iso_3744_delete_microphone_signal_warning():
    """Test delete_microphone_signal method's exception."""
    swl = SoundPowerLevelISO3744()
    swl.add_microphone_signal(Field())

    with pytest.warns(
        PyAnsysSoundWarning, match="No microphone signal associated with this index."
    ):
        swl.delete_microphone_signal(1)


def test_sound_power_level_iso_3744_set_C1_C2_from_meteo_parameters():
    """Test set_C1_C2_from_meteo_parameters method."""
    swl = SoundPowerLevelISO3744()
    swl.set_C1_C2_from_meteo_parameters(temperature=30, pressure=102.0)

    assert swl.C1 == pytest.approx(EXP_C1)
    assert swl.C2 == pytest.approx(EXP_C2)


def test_sound_power_level_iso_3744_set_K2_from_room_properties():
    """Test set_K2_from_room_properties method."""
    swl = SoundPowerLevelISO3744()
    swl.set_K2_from_room_properties(length=8, width=6, height=4, alpha=0.4)

    assert swl.K2 == pytest.approx(EXP_K2)


def test_sound_power_level_iso_3744_set_K2_from_room_properties_exception_negative_dimension():
    """Test set_K2_from_room_properties method's exception related to room dimensions."""
    swl = SoundPowerLevelISO3744()

    with pytest.raises(
        PyAnsysSoundException,
        match="Specified room length, width and height must be all strictly greater than 0 m.",
    ):
        swl.set_K2_from_room_properties(length=-8, width=6, height=4, alpha=0.4)

    with pytest.raises(
        PyAnsysSoundException,
        match="Specified room length, width and height must be all strictly greater than 0 m.",
    ):
        swl.set_K2_from_room_properties(width=-8, length=8, height=4, alpha=0.4)

    with pytest.raises(
        PyAnsysSoundException,
        match="Specified room length, width and height must be all strictly greater than 0 m.",
    ):
        swl.set_K2_from_room_properties(height=-8, length=8, width=6, alpha=0.4)


def test_sound_power_level_iso_3744_set_K2_from_room_properties_exception_alpha_range():
    """Test set_K2_from_room_properties method's exception related to alpha."""
    swl = SoundPowerLevelISO3744()

    with pytest.raises(
        PyAnsysSoundException,
        match="Specified mean absorption coefficient alpha must be strictly greater than 0, and "
        "smaller than 1.",
    ):
        swl.set_K2_from_room_properties(alpha=0, length=8, width=6, height=4)

    with pytest.raises(
        PyAnsysSoundException,
        match="Specified mean absorption coefficient alpha must be strictly greater than 0, and "
        "smaller than 1.",
    ):
        swl.set_K2_from_room_properties(alpha=1.1, length=8, width=6, height=4)


def test_sound_power_level_iso_3744_load_project():
    """Test load_project method."""
    swl = SoundPowerLevelISO3744()
    swl.load_project(pytest.data_path_swl_project_file_in_container)

    assert swl.surface_shape == EXP_SHAPE_FROM_PROJECT
    assert swl.surface_radius == pytest.approx(EXP_RADIUS_FROM_PROJECT)
    assert swl.K1 == pytest.approx(EXP_K1_FROM_PROJECT)
    assert swl.K2 == pytest.approx(EXP_K2_FROM_PROJECT)
    assert swl.C1 == pytest.approx(EXP_C1_FROM_PROJECT)
    assert swl.C2 == pytest.approx(EXP_C2_FROM_PROJECT)

    all_signals = swl.get_all_signal_names()
    assert all_signals == EXP_SIGNAL_LIST_FROM_PROJECT
    assert type(swl.get_microphone_signal(0)) == Field


def test_sound_power_level_iso_3744_process():
    """Test process method."""
    swl = SoundPowerLevelISO3744()
    swl.load_project(pytest.data_path_swl_project_file_in_container)
    swl.process()


def test_sound_power_level_iso_3744_process_exception():
    """Test process method's exception."""
    swl = SoundPowerLevelISO3744()

    with pytest.raises(
        PyAnsysSoundException,
        match="No microphone signal was defined. "
        "Use SoundPowerLevelISO3744.add_microphone_signal().",
    ):
        swl.process()


def test_sound_power_level_iso_3744_get_output():
    """Test get_output method."""
    swl = SoundPowerLevelISO3744()
    swl.load_project(pytest.data_path_swl_project_file_in_container)
    swl.process()

    output = swl.get_output()
    assert output is not None


def test_sound_power_level_iso_3744_get_output_unprocessed():
    """Test get_output method's warning."""
    swl = SoundPowerLevelISO3744()

    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. "
        "Use the 'SoundPowerLevelISO3744.process\\(\\)' method.",
    ):
        output = swl.get_output()
    assert output is None


def test_sound_power_level_iso_3744_get_output_as_nparray():
    """Test get_output_as_nparray method."""
    swl = SoundPowerLevelISO3744()
    swl.load_project(pytest.data_path_swl_project_file_in_container)
    swl.process()

    Lw, LwA, Lw_oct, fc_oct, Lw_3, fc_3 = swl.get_output_as_nparray()
    assert Lw == pytest.approx(EXP_LW)
    assert LwA == pytest.approx(EXP_LWA)
    assert Lw_oct[5] == pytest.approx(EXP_LW_OCT_5)
    assert fc_oct[6] == pytest.approx(EXP_FC_OCT_6)
    assert Lw_3[10] == pytest.approx(EXP_LW_3_10)
    assert fc_3[12] == pytest.approx(EXP_FC_3_12)


def test_sound_power_level_iso_3744_get_output_as_nparray_unprocessed():
    """Test get_output_as_nparray method's warning."""
    swl = SoundPowerLevelISO3744()

    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. "
        "Use the 'SoundPowerLevelISO3744.process\\(\\)' method.",
    ):
        Lw, LwA, Lw_oct, fc_oct, Lw_3, fc_3 = swl.get_output_as_nparray()
    assert np.isnan(Lw) == True
    assert np.isnan(LwA) == True
    assert len(Lw_oct) == 0
    assert len(fc_oct) == 0
    assert len(Lw_3) == 0
    assert len(fc_3) == 0


def test_sound_power_level_iso_3744_get_Lw():
    """Test get_Lw method."""
    swl = SoundPowerLevelISO3744()
    swl.load_project(pytest.data_path_swl_project_file_in_container)
    swl.process()

    Lw = swl.get_Lw()
    assert Lw == pytest.approx(EXP_LW)


def test_sound_power_level_iso_3744_get_Lw_A():
    """Test get_Lw_A method."""
    swl = SoundPowerLevelISO3744()
    swl.load_project(pytest.data_path_swl_project_file_in_container)
    swl.process()

    LwA = swl.get_Lw_A()
    assert LwA == pytest.approx(EXP_LWA)


def test_sound_power_level_iso_3744_get_Lw_octave():
    """Test get_Lw_octave method."""
    swl = SoundPowerLevelISO3744()
    swl.load_project(pytest.data_path_swl_project_file_in_container)
    swl.process()

    Lw_oct = swl.get_Lw_octave()
    assert Lw_oct[5] == pytest.approx(EXP_LW_OCT_5)


def test_sound_power_level_iso_3744_get_octave_center_frequencies():
    """Test get_octave_center_frequencies method."""
    swl = SoundPowerLevelISO3744()
    swl.load_project(pytest.data_path_swl_project_file_in_container)
    swl.process()

    fc_oct = swl.get_octave_center_frequencies()
    assert fc_oct[6] == pytest.approx(EXP_FC_OCT_6)


def test_sound_power_level_iso_3744_get_Lw_thirdoctave():
    """Test get_Lw_thirdoctave method."""
    swl = SoundPowerLevelISO3744()
    swl.load_project(pytest.data_path_swl_project_file_in_container)
    swl.process()

    Lw_3 = swl.get_Lw_thirdoctave()
    assert Lw_3[10] == pytest.approx(EXP_LW_3_10)


def test_sound_power_level_iso_3744_get_thirdoctave_center_frequencies():
    """Test get_thirdoctave_center_frequencies method."""
    swl = SoundPowerLevelISO3744()
    swl.load_project(pytest.data_path_swl_project_file_in_container)
    swl.process()

    fc_3 = swl.get_thirdoctave_center_frequencies()
    assert fc_3[12] == pytest.approx(EXP_FC_3_12)


def test_sound_power_level_iso_3744_load_project_with_calibrations():
    """Test loading swl project created with signals with calibrations."""
    swl = SoundPowerLevelISO3744()
    swl.load_project(pytest.data_path_swl_project_file_with_calibration_in_container)
    swl.process()

    Lw, LwA, Lw_oct, fc_oct, Lw_3, fc_3 = swl.get_output_as_nparray()
    assert Lw == pytest.approx(EXP_LW_CALIB)
    assert LwA == pytest.approx(EXP_LWA_CALIB)
    assert Lw_oct[5] == pytest.approx(EXP_LW_OCT_5_CALIB)
    assert fc_oct[6] == pytest.approx(EXP_FC_OCT_6)
    assert Lw_3[10] == pytest.approx(EXP_LW_3_10_CALIB)
    assert fc_3[12] == pytest.approx(EXP_FC_3_12)


@patch("matplotlib.pyplot.show")
def test_sound_power_level_iso_3744_plot(mock_show):
    """Test plot method."""
    swl = SoundPowerLevelISO3744()
    swl.load_project(pytest.data_path_swl_project_file_in_container)
    swl.process()

    swl.plot()


def test_sound_power_level_iso_3744_plot_exception():
    """Test plot method's exception."""
    swl = SoundPowerLevelISO3744()
    swl.load_project(pytest.data_path_swl_project_file_in_container)

    with pytest.raises(
        PyAnsysSoundException,
        match="Output is not processed yet. Use the 'SoundPowerLevelISO3744.process\\(\\)' method.",
    ):
        swl.plot()


def test_sound_power_level_iso_3744___get_surface_area():
    """Test __get_surface_area method."""
    swl = SoundPowerLevelISO3744()

    area = swl._SoundPowerLevelISO3744__get_surface_area()
    assert area == pytest.approx(EXP_AREA_H)

    swl.surface_shape = "Half-hemisphere"
    area = swl._SoundPowerLevelISO3744__get_surface_area()
    assert area == pytest.approx(EXP_AREA_HH)


def test_sound_power_level_iso_3744___str__():
    """Test __str__ method."""
    swl = SoundPowerLevelISO3744()
    swl.load_project(pytest.data_path_swl_project_file_in_container)
    swl.process()

    assert swl.__str__() == EXP_STR
