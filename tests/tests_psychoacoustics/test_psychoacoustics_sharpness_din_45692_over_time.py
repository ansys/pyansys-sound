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
import numpy as np
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ansys.sound.core.psychoacoustics import SharpnessDIN45692OverTime
from ansys.sound.core.signal_utilities import LoadWav

EXP_MAX_SHARPNESS_FREE = 1.379897
EXP_MAX_SHARPNESS_DIFFUSE = 1.446925
EXP_SHARPNESS_OVER_TIME_COUNT = 13034
EXP_SHARPNESS_OVER_TIME_FREE_0 = 0.0
EXP_SHARPNESS_OVER_TIME_FREE_20 = 0.6866303
EXP_SHARPNESS_OVER_TIME_FREE_100 = 1.295199
EXP_SHARPNESS_OVER_TIME_DIFFUSE_0 = 0.0
EXP_SHARPNESS_OVER_TIME_DIFFUSE_20 = 0.7252110
EXP_SHARPNESS_OVER_TIME_DIFFUSE_100 = 1.375550
EXP_TIME_0 = 0.0
EXP_TIME_20 = 0.040
EXP_TIME_100 = 0.200
EXP_STR_DEFAULT = (
    "SharpnessDIN45692OverTime object\nData:\n\tSignal name: Not set\nMax sharpness: Not processed"
)
EXP_STR = (
    'SharpnessDIN45692OverTime object\nData:\n\tSignal name: "Aircraft-App2"\n'
    "Max sharpness: 1.38 acums"
)


def test_sharpness_din_45692_over_time_instantiation():
    """Test the instantiation of the SharpnessDIN45692OverTime class."""
    sharpness_obj = SharpnessDIN45692OverTime()
    assert sharpness_obj.signal is None
    assert sharpness_obj.field_type == "Free"


def test_sharpness_din_45692_over_time___str__():
    """Test the __str__ method of the SharpnessDIN45692OverTime class."""
    sharpness_obj = SharpnessDIN45692OverTime()
    assert str(sharpness_obj) == EXP_STR_DEFAULT

    wav_loader = LoadWav(pytest.data_path_aircraft_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    sharpness_obj.signal = fc[0]
    sharpness_obj.process()
    assert str(sharpness_obj) == EXP_STR


def test_sharpness_din_45692_over_time_properties():
    """Test the properties of the SharpnessDIN45692OverTime class."""
    sharpness_obj = SharpnessDIN45692OverTime()

    wav_loader = LoadWav(pytest.data_path_aircraft_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    sharpness_obj.signal = fc[0]
    assert isinstance(sharpness_obj.signal, Field)

    sharpness_obj.field_type = "Diffuse"
    assert sharpness_obj.field_type == "Diffuse"


def test_sharpness_din_45692_over_time_properties_exceptions():
    """Test the properties of the SharpnessDIN45692OverTime class."""
    sharpness_obj = SharpnessDIN45692OverTime()

    with pytest.raises(PyAnsysSoundException, match="Signal must be specified as a DPF field."):
        sharpness_obj.signal = "WrongType"
    assert sharpness_obj.signal is None

    with pytest.raises(
        PyAnsysSoundException,
        match=(
            'Invalid field type "InvalidFieldType". Available options are "Free" and "Diffuse".'
        ),
    ):
        sharpness_obj.field_type = "InvalidFieldType"
    assert sharpness_obj.field_type == "Free"


def test_sharpness_din_45692_over_time_process():
    """Test the process method of the SharpnessDIN45692OverTime class."""
    sharpness_obj = SharpnessDIN45692OverTime()

    wav_loader = LoadWav(pytest.data_path_aircraft_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    sharpness_obj.signal = fc[0]
    sharpness_obj.process()
    assert sharpness_obj._output is not None


def test_sharpness_din_45692_over_time_process_exception():
    """Test the process method of the SharpnessDIN45692OverTime class."""
    sharpness_obj = SharpnessDIN45692OverTime()

    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "No signal found for sharpness over time computation. Use "
            "`SharpnessDIN45692OverTime.signal`."
        ),
    ):
        sharpness_obj.process()
    assert sharpness_obj._output is None


def test_sharpness_din_45692_over_time_get_output():
    """Test the get_output method of the SharpnessDIN45692OverTime class."""
    sharpness_obj = SharpnessDIN45692OverTime()

    wav_loader = LoadWav(pytest.data_path_aircraft_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    sharpness_obj.signal = fc[0]

    sharpness_obj.field_type = "Free"
    sharpness_obj.process()

    sharpness_max, sharpness_over_time = sharpness_obj.get_output()
    assert sharpness_max == pytest.approx(EXP_MAX_SHARPNESS_FREE)
    assert len(sharpness_over_time.data) == EXP_SHARPNESS_OVER_TIME_COUNT
    assert sharpness_over_time.data[0] == pytest.approx(EXP_SHARPNESS_OVER_TIME_FREE_0)
    assert sharpness_over_time.data[20] == pytest.approx(EXP_SHARPNESS_OVER_TIME_FREE_20)
    assert sharpness_over_time.data[100] == pytest.approx(EXP_SHARPNESS_OVER_TIME_FREE_100)

    sharpness_obj.field_type = "Diffuse"
    sharpness_obj.process()

    sharpness_max, sharpness_over_time = sharpness_obj.get_output()
    assert sharpness_max == pytest.approx(EXP_MAX_SHARPNESS_DIFFUSE)
    assert len(sharpness_over_time.data) == EXP_SHARPNESS_OVER_TIME_COUNT
    assert sharpness_over_time.data[0] == pytest.approx(EXP_SHARPNESS_OVER_TIME_DIFFUSE_0)
    assert sharpness_over_time.data[20] == pytest.approx(EXP_SHARPNESS_OVER_TIME_DIFFUSE_20)
    assert sharpness_over_time.data[100] == pytest.approx(EXP_SHARPNESS_OVER_TIME_DIFFUSE_100)


def test_sharpness_din_45692_over_time_get_output_warning():
    """Test the get_output method of the SharpnessDIN45692OverTime class."""
    sharpness_obj = SharpnessDIN45692OverTime()

    with pytest.warns(
        PyAnsysSoundWarning,
        match=(
            "Output is not processed yet. Use the `SharpnessDIN45692OverTime.process\\(\\)` method."
        ),
    ):
        output = sharpness_obj.get_output()
    assert output is None


def test_sharpness_din_45692_over_time_get_output_as_nparray():
    """Test the get_output_as_nparray method of the SharpnessDIN45692OverTime class."""
    sharpness_obj = SharpnessDIN45692OverTime()

    with pytest.warns(
        PyAnsysSoundWarning,
        match=(
            "Output is not processed yet. Use the `SharpnessDIN45692OverTime.process\\(\\)` method."
        ),
    ):
        max_sharpness, sharpness_over_time, time_scale = sharpness_obj.get_output_as_nparray()
    assert np.isnan(max_sharpness)
    assert len(sharpness_over_time) == 0
    assert len(time_scale) == 0

    wav_loader = LoadWav(pytest.data_path_aircraft_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    sharpness_obj.signal = fc[0]

    sharpness_obj.field_type = "Free"
    sharpness_obj.process()

    max_sharpness, sharpness_over_time, time_scale = sharpness_obj.get_output_as_nparray()
    assert max_sharpness == pytest.approx(EXP_MAX_SHARPNESS_FREE)
    assert len(sharpness_over_time) == EXP_SHARPNESS_OVER_TIME_COUNT
    assert len(time_scale) == EXP_SHARPNESS_OVER_TIME_COUNT
    assert sharpness_over_time[0] == pytest.approx(EXP_SHARPNESS_OVER_TIME_FREE_0)
    assert sharpness_over_time[20] == pytest.approx(EXP_SHARPNESS_OVER_TIME_FREE_20)
    assert sharpness_over_time[100] == pytest.approx(EXP_SHARPNESS_OVER_TIME_FREE_100)

    sharpness_obj.field_type = "Diffuse"
    sharpness_obj.process()

    sharpness_max, sharpness_over_time, _ = sharpness_obj.get_output_as_nparray()
    assert sharpness_max == pytest.approx(EXP_MAX_SHARPNESS_DIFFUSE)
    assert len(sharpness_over_time) == EXP_SHARPNESS_OVER_TIME_COUNT
    assert sharpness_over_time[0] == pytest.approx(EXP_SHARPNESS_OVER_TIME_DIFFUSE_0)
    assert sharpness_over_time[20] == pytest.approx(EXP_SHARPNESS_OVER_TIME_DIFFUSE_20)
    assert sharpness_over_time[100] == pytest.approx(EXP_SHARPNESS_OVER_TIME_DIFFUSE_100)


def test_sharpness_din_45692_over_time_get_max_sharpness():
    """Test the get_max_sharpness method of the SharpnessDIN45692OverTime class."""
    sharpness_obj = SharpnessDIN45692OverTime()

    wav_loader = LoadWav(pytest.data_path_aircraft_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    sharpness_obj.signal = fc[0]

    sharpness_obj.field_type = "Free"
    sharpness_obj.process()

    max_sharpness = sharpness_obj.get_max_sharpness()
    assert max_sharpness == pytest.approx(EXP_MAX_SHARPNESS_FREE)

    sharpness_obj.field_type = "Diffuse"
    sharpness_obj.process()

    max_sharpness = sharpness_obj.get_max_sharpness()
    assert max_sharpness == pytest.approx(EXP_MAX_SHARPNESS_DIFFUSE)


def test_sharpness_din_45692_over_time_get_sharpness_over_time():
    """Test the get_sharpness_over_time method of the SharpnessDIN45692OverTime class."""
    sharpness_obj = SharpnessDIN45692OverTime()

    wav_loader = LoadWav(pytest.data_path_aircraft_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    sharpness_obj.signal = fc[0]

    sharpness_obj.field_type = "Free"
    sharpness_obj.process()

    sharpness_over_time = sharpness_obj.get_sharpness_over_time()
    assert len(sharpness_over_time.data) == EXP_SHARPNESS_OVER_TIME_COUNT
    assert sharpness_over_time[0] == pytest.approx(EXP_SHARPNESS_OVER_TIME_FREE_0)
    assert sharpness_over_time[20] == pytest.approx(EXP_SHARPNESS_OVER_TIME_FREE_20)
    assert sharpness_over_time[100] == pytest.approx(EXP_SHARPNESS_OVER_TIME_FREE_100)

    sharpness_obj.field_type = "Diffuse"
    sharpness_obj.process()

    sharpness_over_time = sharpness_obj.get_sharpness_over_time()
    assert len(sharpness_over_time.data) == EXP_SHARPNESS_OVER_TIME_COUNT
    assert sharpness_over_time[0] == pytest.approx(EXP_SHARPNESS_OVER_TIME_DIFFUSE_0)
    assert sharpness_over_time[20] == pytest.approx(EXP_SHARPNESS_OVER_TIME_DIFFUSE_20)
    assert sharpness_over_time[100] == pytest.approx(EXP_SHARPNESS_OVER_TIME_DIFFUSE_100)


def test_sharpness_din_45692_over_time_get_time_scale():
    """Test the get_time_scale method of the SharpnessDIN45692OverTime class."""
    sharpness_obj = SharpnessDIN45692OverTime()

    wav_loader = LoadWav(pytest.data_path_aircraft_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    sharpness_obj.signal = fc[0]
    sharpness_obj.process()

    time_scale = sharpness_obj.get_time_scale()
    assert len(time_scale) == EXP_SHARPNESS_OVER_TIME_COUNT
    assert time_scale[0] == pytest.approx(EXP_TIME_0)
    assert time_scale[20] == pytest.approx(EXP_TIME_20)
    assert time_scale[100] == pytest.approx(EXP_TIME_100)


@patch("matplotlib.pyplot.show")
def test_sharpness_din_45692_over_time_plot(mock_show):
    """Test the plot method of the SharpnessDIN45692OverTime class."""
    sharpness_obj = SharpnessDIN45692OverTime()

    wav_loader = LoadWav(pytest.data_path_aircraft_nonUnitaryCalib_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    sharpness_obj.signal = fc[0]
    sharpness_obj.process()
    sharpness_obj.plot()


def test_sharpness_din_45692_over_time_plot_exception():
    """Test the plot method of the SharpnessDIN45692OverTime class."""
    sharpness_obj = SharpnessDIN45692OverTime()

    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "Output is not processed yet. Use the `SharpnessDIN45692OverTime.process\\(\\)` method."
        ),
    ):
        sharpness_obj.plot()
