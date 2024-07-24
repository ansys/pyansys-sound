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

from ansys.dpf.core import Field
import numpy as np
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ansys.sound.core.sound_power import SoundPowerLevelISO3744

EXP_K2 = 9.320628889992298
EXP_C1 = -0.10519597099301761
EXP_C2 = 0.1266523291988306
EXP_AREA1 = 6.2832
EXP_AREA2 = 3.1416
EXP_SHAPE_FROM_PROJECT = "Hemisphere"  # To set when feature is available in SAS
EXP_RADIUS_FROM_PROJECT = 1.0  # To set when feature is available in SAS
EXP_K1_FROM_PROJECT = 0.0  # To set when feature is available in SAS
EXP_K2_FROM_PROJECT = 0.0  # To set when feature is available in SAS
EXP_C1_FROM_PROJECT = 0.0  # To set when feature is available in SAS
EXP_C2_FROM_PROJECT = 0.0  # To set when feature is available in SAS
EXP_LW = 80.0  # To set when feature is available in SAS
EXP_LWA = 80.0  # To set when feature is available in SAS
EXP_LW_OCT_5 = 60.0  # To set when feature is available in SAS
EXP_FC_OCT_6 = 1000.0  # To set when feature is available in SAS
EXP_LW_3_10 = 60.0  # To set when feature is available in SAS
EXP_FC_3_12 = 500.0  # To set when feature is available in SAS
EXP_STR = (
    "SoundPowerLevelISO3744 object\n"
    + "Data:\n"
    + "  Measurement surface:\n"
    + f"    Shape: Hemisphere\n"
    + f"    Radius: 2 m\n"
    + f"    Area: 25.13 m^2\n"
    + f"    Number of microphone signals: 10\n"
    + "  Correction coefficient:\n"
    + f"    K1 (background noise): 20 dB\n"
    + f"    K2 (measurement environment): 30 dB\n"
    + f"    C1 (meteorological reference quantity): 0.1 dB\n"
    + f"    C2 (meteorological radiation impedance): 0.2 dB\n"
    + "  Sound power level (Lw):\n"
    + f"    Unweighted: 80 dB\n"
    + f"    A-weighted: 90 dBA\n"
)  # To set when feature is available in SAS


def test_sound_power_level_iso_3744_instantiation(dpf_sound_test_server):
    """Test SoundPowerLevelISO3744 instantiation."""
    # Test instantiation.
    swl = SoundPowerLevelISO3744()
    assert swl.surface_shape == "Hemisphere"
    assert swl.surface_radius == 1.0
    assert swl.K1 == 0.0
    assert swl.K2 == 0.0
    assert swl.C1 == 0.0
    assert swl.C2 == 0.0


def test_sound_power_level_iso_3744_setters(dpf_sound_test_server):
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


def test_sound_power_level_iso_3744_setters_exceptions(dpf_sound_test_server):
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


def test_sound_power_level_iso_3744_add_microphone_signal(dpf_sound_test_server):
    """Test add_microphone_signal method."""
    swl = SoundPowerLevelISO3744()

    swl.add_microphone_signal(Field(), name="MySignal1")


def test_sound_power_level_iso_3744_add_microphone_signal_exception(dpf_sound_test_server):
    """Test add_microphone_signal method's exception."""
    swl = SoundPowerLevelISO3744()

    with pytest.raises(
        PyAnsysSoundException, match="Added signal must be provided as a DPF field."
    ):
        swl.add_microphone_signal([1, 2, 3], name="MySignal1")


def test_sound_power_level_iso_3744_get_all_signal_names(dpf_sound_test_server):
    """Test get_all_signal_names method."""
    swl = SoundPowerLevelISO3744()
    swl.add_microphone_signal(Field(), name="MySignal1")
    swl.add_microphone_signal(Field(), name="MySignal2")

    names = swl.get_all_signal_names()
    assert names == ("MySignal1", "MySignal2")


def test_sound_power_level_iso_3744_get_microphone_signal(dpf_sound_test_server):
    """Test get_microphone_signal method."""
    swl = SoundPowerLevelISO3744()
    swl.add_microphone_signal(Field(), name="MySignal1")

    signal = swl.get_microphone_signal("MySignal1")
    assert type(signal) is Field


def test_sound_power_level_iso_3744_get_microphone_signal_exception(dpf_sound_test_server):
    """Test get_microphone_signal method's exception."""
    swl = SoundPowerLevelISO3744()
    swl.add_microphone_signal(Field(), name="ValidKey")

    with pytest.raises(
        PyAnsysSoundException, match="No microphone signal associated with this name."
    ):
        swl.get_microphone_signal("InvalidKey")


def test_sound_power_level_iso_3744_delete_microphone_signal(dpf_sound_test_server):
    """Test delete_microphone_signal method."""
    swl = SoundPowerLevelISO3744()
    swl.add_microphone_signal(Field(), name="MySignal1")
    swl.add_microphone_signal(Field(), name="MySignal2")

    swl.delete_microphone_signal("MySignal1")
    assert swl.get_all_signal_names() == ("MySignal2",)


def test_sound_power_level_iso_3744_get_microphone_signal_warning(dpf_sound_test_server):
    """Test get_microphone_signal method's exception."""
    swl = SoundPowerLevelISO3744()
    swl.add_microphone_signal(Field(), name="ValidKey")

    with pytest.warns(PyAnsysSoundWarning, match="No microphone signal associated with this name."):
        swl.delete_microphone_signal("InvalidKey")


def test_sound_power_level_iso_3744_set_C1_C2_from_meteo_parameters(dpf_sound_test_server):
    """Test set_C1_C2_from_meteo_parameters method."""
    swl = SoundPowerLevelISO3744()
    swl.set_C1_C2_from_meteo_parameters(temperature=30, pressure=102.0)

    assert swl.C1 == pytest.approx(EXP_C1)
    assert swl.C2 == pytest.approx(EXP_C2)


def test_sound_power_level_iso_3744_set_K2_from_room_properties(dpf_sound_test_server):
    """Test set_K2_from_room_properties method."""
    swl = SoundPowerLevelISO3744()
    swl.set_K2_from_room_properties(length=8, width=6, height=4, alpha=0.4)

    assert swl.K2 == pytest.approx(EXP_K2)


def test_sound_power_level_iso_3744_set_K2_from_room_properties_exception1(dpf_sound_test_server):
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


def test_sound_power_level_iso_3744_set_K2_from_room_properties_exception2(dpf_sound_test_server):
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


def test_sound_power_level_iso_3744_load_project(dpf_sound_test_server):
    """Test load_project method."""
    swl = SoundPowerLevelISO3744()
    swl.load_project(
        "SWLprojecFile.extension"
    )  # File name (and file location) to adjust when feature is implemented in SAS

    assert swl.surface_shape == EXP_SHAPE_FROM_PROJECT
    assert swl.surface_radius == pytest.approx(EXP_RADIUS_FROM_PROJECT)
    assert swl.K1 == pytest.approx(EXP_K1_FROM_PROJECT)
    assert swl.K2 == pytest.approx(EXP_K2_FROM_PROJECT)
    assert swl.C1 == pytest.approx(EXP_C1_FROM_PROJECT)
    assert swl.C2 == pytest.approx(EXP_C2_FROM_PROJECT)
    assert swl.get_all_signal_names() == (
        "sig1",
        "sig2",
        "sig3",
    )  # To adjust when when feature is implemented in SAS
    assert (
        type(swl.get_microphone_signal("sig1")) == Field
    )  # To adjust (name) when when feature is implemented in SAS


def test_process(dpf_sound_test_server):
    """Test process method."""
    swl = SoundPowerLevelISO3744()
    swl.load_project(
        "SWLprojecFile.extension"
    )  # File name (and file location) to adjust when feature is implemented in SAS
    swl.process()


def test_process_exception(dpf_sound_test_server):
    """Test process method's exception."""
    swl = SoundPowerLevelISO3744()

    with pytest.raises(
        PyAnsysSoundException,
        match="No microphone signal was defined. "
        "Use SoundPowerLevelISO3744.add_microphone_signal().",
    ):
        swl.process()


def test_sound_power_level_iso_3744_get_output(dpf_sound_test_server):
    """Test get_output method."""
    swl = SoundPowerLevelISO3744()
    swl.load_project(
        "SWLprojecFile.extension"
    )  # File name (and file location) to adjust when feature is implemented in SAS
    swl.process()

    output = swl.get_output()
    assert output is not None


def test_sound_power_level_iso_3744_get_output_warning(dpf_sound_test_server):
    """Test get_output method's warning."""
    swl = SoundPowerLevelISO3744()

    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the 'SoundPowerLevelISO3744.process()' method.",
    ):
        swl.get_output()


def test_sound_power_level_iso_3744_get_output_as_nparray(dpf_sound_test_server):
    """Test get_output_as_nparray method."""
    swl = SoundPowerLevelISO3744()
    swl.load_project(
        "SWLprojecFile.extension"
    )  # File name (and file location) to adjust when feature is implemented in SAS
    swl.process()

    Lw, LwA, Lw_oct, fc_oct, Lw_3, fc_3 = swl.get_output_as_nparray()
    assert Lw == pytest.approx(EXP_LW)
    assert LwA == pytest.approx(EXP_LWA)
    assert Lw_oct[5] == pytest.approx(EXP_LW_OCT_5)
    assert fc_oct[6] == pytest.approx(EXP_FC_OCT_6)
    assert Lw_3[10] == pytest.approx(EXP_LW_3_10)
    assert fc_3[12] == pytest.approx(EXP_FC_3_12)


def test_sound_power_level_iso_3744_get_output_as_nparray_warning(dpf_sound_test_server):
    """Test get_output_as_nparray method's warning."""
    swl = SoundPowerLevelISO3744()

    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the 'SoundPowerLevelISO3744.process()' method.",
    ):
        Lw, LwA, Lw_oct, fc_oct, Lw_3, fc_3 = swl.get_output_as_nparray()
    assert np.isnan(Lw) == True
    assert np.isnan(LwA) == True
    assert len(Lw_oct) == 0
    assert len(fc_oct) == 0
    assert len(Lw_3) == 0
    assert len(fc_3) == 0


def test_sound_power_level_iso_3744_get_Lw(dpf_sound_test_server):
    """Test get_Lw method."""
    swl = SoundPowerLevelISO3744()
    swl.load_project(
        "SWLprojecFile.extension"
    )  # File name (and file location) to adjust when feature is implemented in SAS
    swl.process()

    Lw = swl.get_Lw()
    assert Lw == pytest.approx(EXP_LW)


def test_sound_power_level_iso_3744_get_LwA(dpf_sound_test_server):
    """Test get_LwA method."""
    swl = SoundPowerLevelISO3744()
    swl.load_project(
        "SWLprojecFile.extension"
    )  # File name (and file location) to adjust when feature is implemented in SAS
    swl.process()

    LwA = swl.get_LwA()
    assert LwA == pytest.approx(EXP_LWA)


def test_sound_power_level_iso_3744_get_Lw_octave(dpf_sound_test_server):
    """Test get_Lw_octave method."""
    swl = SoundPowerLevelISO3744()
    swl.load_project(
        "SWLprojecFile.extension"
    )  # File name (and file location) to adjust when feature is implemented in SAS
    swl.process()

    Lw_oct = swl.get_Lw_octave()
    assert Lw_oct[5] == pytest.approx(EXP_LW_OCT_5)


def test_sound_power_level_iso_3744_get_octave_center_frequencies(dpf_sound_test_server):
    """Test get_octave_center_frequencies method."""
    swl = SoundPowerLevelISO3744()
    swl.load_project(
        "SWLprojecFile.extension"
    )  # File name (and file location) to adjust when feature is implemented in SAS
    swl.process()

    fc_oct = swl.get_octave_center_frequencies()
    assert fc_oct[6] == pytest.approx(EXP_FC_OCT_6)


def test_sound_power_level_iso_3744_get_Lw_thirdoctave(dpf_sound_test_server):
    """Test get_Lw_thirdoctave method."""
    swl = SoundPowerLevelISO3744()
    swl.load_project(
        "SWLprojecFile.extension"
    )  # File name (and file location) to adjust when feature is implemented in SAS
    swl.process()

    Lw_3 = swl.get_Lw_thirdoctave()
    assert Lw_3[10] == pytest.approx(EXP_LW_3_10)


def test_sound_power_level_iso_3744_get_thirdoctave_center_frequencies(dpf_sound_test_server):
    """Test get_thirdoctave_center_frequencies method."""
    swl = SoundPowerLevelISO3744()
    swl.load_project(
        "SWLprojecFile.extension"
    )  # File name (and file location) to adjust when feature is implemented in SAS
    swl.process()

    fc_3 = swl.get_thirdoctave_center_frequencies()
    assert fc_3[12] == pytest.approx(EXP_FC_3_12)


@patch("matplotlib.pyplot.show")
def test_sound_power_level_iso_3744_plot(mock_show, dpf_sound_test_server):
    """Test plot method."""
    swl = SoundPowerLevelISO3744()
    swl.load_project(
        "SWLprojecFile.extension"
    )  # File name (and file location) to adjust when feature is implemented in SAS
    swl.process()

    swl.plot()  # Plot over a linear frequency scale.
    swl.plot(logfreq=True)  # Plot over a logarithmic frequency scale.


def test_sound_power_level_iso_3744___get_surface_area(dpf_sound_test_server):
    """Test __get_surface_area method."""
    swl = SoundPowerLevelISO3744()

    area = swl.__get_surface_area()
    assert area == pytest.approx(EXP_AREA1)

    swl.surface_shape = "Half-hemisphere"
    area = swl.__get_surface_area()
    assert area == pytest.approx(EXP_AREA2)


def test_sound_power_level_iso_3744___str__(dpf_sound_test_server):
    """Test __str__ method."""
    swl = SoundPowerLevelISO3744()
    swl.load_project(
        "SWLprojecFile.extension"
    )  # File name (and file location) to adjust when feature is implemented in SAS

    assert swl.__str__() == EXP_STR
