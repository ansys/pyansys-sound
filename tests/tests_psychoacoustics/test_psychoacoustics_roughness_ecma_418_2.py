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
from ansys.sound.core.psychoacoustics import RoughnessECMA418_2
from ansys.sound.core.signal_utilities import LoadWav

# Skip entire test module if Sound version < 2027.1.0
if not pytest.SOUND_VERSION_GREATER_THAN_OR_EQUAL_TO_2027R1:
    pytest.skip("Requires Sound version >= 2027.1.0", allow_module_level=True)

EXP_ROUGHNESS_FREE = 0.7290801262493071
EXP_ROUGHNESS_DIFFUSE = 0.7537649028785819
EXP_BARK_COUNT = 53
EXP_SPECIFIC_ROUGHNESS_FREE_0 = 0.0
EXP_SPECIFIC_ROUGHNESS_FREE_9 = 0.011541895568370819
EXP_SPECIFIC_ROUGHNESS_FREE_40 = 0.02757706306874752
EXP_SPECIFIC_ROUGHNESS_DIFFUSE_0 = 0.0
EXP_SPECIFIC_ROUGHNESS_DIFFUSE_9 = 0.011207301169633865
EXP_SPECIFIC_ROUGHNESS_DIFFUSE_40 = 0.02750357612967491
EXP_TIME_COUNT = 151
EXP_ROUGHNESS_OVER_TIME_FREE_5 = 0.18291568756103516
EXP_ROUGHNESS_OVER_TIME_FREE_12 = 0.5290920734405518
EXP_ROUGHNESS_OVER_TIME_FREE_20 = 0.6301994919776917
EXP_ROUGHNESS_OVER_TIME_DIFFUSE_5 = 0.18654069304466248
EXP_ROUGHNESS_OVER_TIME_DIFFUSE_12 = 0.5457488298416138
EXP_ROUGHNESS_OVER_TIME_DIFFUSE_20 = 0.6524152159690857
EXP_BARK_0 = 0.5
EXP_BARK_9 = 5.0
EXP_BARK_40 = 20.5
EXP_FREQ_0 = 41.00914871505695
EXP_FREQ_9 = 455.8138290833099
EXP_FREQ_40 = 6972.177534225708
EXP_TIME_5 = 0.1
EXP_TIME_12 = 0.24
EXP_TIME_20 = 0.4
EXP_STR_DEFAULT = (
    "RoughnessECMA418_2 object\nData:\n\tSignal name: Signal not set\n\tField type: Free\n"
    "Overall roughness: Not processed"
)
EXP_STR = (
    'RoughnessECMA418_2 object\nData:\n\tSignal name: ""\n\tField type: Diffuse\n'
    "Overall roughness: 0.75 asper"
)


def test_roughness_ecma_418_2_instantiation():
    """Test the instantiation of the RoughnessECMA418_2 class."""
    roughness = RoughnessECMA418_2()
    assert roughness.signal == None
    assert roughness.field_type == "Free"
    assert roughness._output == None


def test_roughness_ecma_418_2_properties():
    """Test the properties of the RoughnessECMA418_2 class."""
    roughness = RoughnessECMA418_2()

    # Signal
    roughness.signal = Field()
    assert type(roughness.signal) == Field

    # Field type
    roughness.field_type = "Diffuse"
    assert roughness.field_type == "Diffuse"

    # Field type (case-insensitive)
    roughness.field_type = "diffuse"
    assert roughness.field_type == "diffuse"


def test_roughness_ecma_418_2_properties_exceptions():
    """Test the exceptions of the RoughnessECMA418_2 class."""
    roughness = RoughnessECMA418_2()

    with pytest.raises(PyAnsysSoundException, match="Signal must be specified as a DPF field."):
        roughness.signal = "NotAField"

    with pytest.raises(
        PyAnsysSoundException,
        match='Invalid field type "InvalidType". Available options are "Free" and "Diffuse".',
    ):
        roughness.field_type = "InvalidType"


def test_roughness_ecma_418_2___str__():
    """Test the __str__ method of the RoughnessECMA418_2 class."""
    roughness = RoughnessECMA418_2()
    assert str(roughness) == EXP_STR_DEFAULT

    # Get a signal
    wav_loader = LoadWav(pytest.data_path_rough_noise)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    roughness.signal = fc[0]

    # Set field type
    roughness.field_type = "Diffuse"

    # Compute
    roughness.process()

    assert str(roughness) == EXP_STR


def test_roughness_ecma_418_2_process():
    """Test the process method of the RoughnessECMA418_2 class."""
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_rough_noise)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Instantiate with inputs
    roughness = RoughnessECMA418_2(signal=fc[0], field_type="Diffuse")

    # Process without error
    roughness.process()
    assert roughness._output is not None


def test_roughness_ecma_418_2_process_exceptions():
    """Test the exceptions of the process method of the RoughnessECMA418_2 class."""
    roughness = RoughnessECMA418_2()

    # No signal -> error
    with pytest.raises(
        PyAnsysSoundException,
        match="No input signal set. Use `RoughnessECMA418_2.signal`.",
    ):
        roughness.process()


@pytest.mark.parametrize(
    "field_type, exp_roughness, exp_specific_roughness, exp_roughness_over_time",
    [
        (
            "Free",
            EXP_ROUGHNESS_FREE,
            (
                EXP_SPECIFIC_ROUGHNESS_FREE_0,
                EXP_SPECIFIC_ROUGHNESS_FREE_9,
                EXP_SPECIFIC_ROUGHNESS_FREE_40,
            ),
            (
                EXP_ROUGHNESS_OVER_TIME_FREE_5,
                EXP_ROUGHNESS_OVER_TIME_FREE_12,
                EXP_ROUGHNESS_OVER_TIME_FREE_20,
            ),
        ),
        (
            "Diffuse",
            EXP_ROUGHNESS_DIFFUSE,
            (
                EXP_SPECIFIC_ROUGHNESS_DIFFUSE_0,
                EXP_SPECIFIC_ROUGHNESS_DIFFUSE_9,
                EXP_SPECIFIC_ROUGHNESS_DIFFUSE_40,
            ),
            (
                EXP_ROUGHNESS_OVER_TIME_DIFFUSE_5,
                EXP_ROUGHNESS_OVER_TIME_DIFFUSE_12,
                EXP_ROUGHNESS_OVER_TIME_DIFFUSE_20,
            ),
        ),
    ],
)
def test_roughness_ecma_418_2_get_output(
    field_type, exp_roughness, exp_specific_roughness, exp_roughness_over_time
):
    """Test the get_output method of the RoughnessECMA418_2 class."""
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_rough_noise)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Instantiate with inputs
    roughness = RoughnessECMA418_2(signal=fc[0], field_type=field_type)

    # Compute
    roughness.process()

    roughness_value, specific_roughness, roughness_over_time = roughness.get_output()
    assert roughness_value == pytest.approx(exp_roughness)
    assert type(specific_roughness) == Field
    assert specific_roughness.data[0] == pytest.approx(exp_specific_roughness[0])
    assert specific_roughness.data[9] == pytest.approx(exp_specific_roughness[1])
    assert specific_roughness.data[40] == pytest.approx(exp_specific_roughness[2])
    assert type(roughness_over_time) == Field
    assert roughness_over_time.data[5] == pytest.approx(exp_roughness_over_time[0])
    assert roughness_over_time.data[12] == pytest.approx(exp_roughness_over_time[1])
    assert roughness_over_time.data[20] == pytest.approx(exp_roughness_over_time[2])


def test_roughness_ecma_418_2_get_output_warning():
    """Test the warning of the get_output method of the RoughnessECMA418_2 class."""
    roughness = RoughnessECMA418_2()

    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the `RoughnessECMA418_2.process\\(\\)` method.",
    ):
        output = roughness.get_output()
    assert output is None


@pytest.mark.parametrize(
    "field_type, exp_roughness, exp_specific_roughness, exp_roughness_over_time",
    [
        (
            "Free",
            EXP_ROUGHNESS_FREE,
            (
                EXP_SPECIFIC_ROUGHNESS_FREE_0,
                EXP_SPECIFIC_ROUGHNESS_FREE_9,
                EXP_SPECIFIC_ROUGHNESS_FREE_40,
            ),
            (
                EXP_ROUGHNESS_OVER_TIME_FREE_5,
                EXP_ROUGHNESS_OVER_TIME_FREE_12,
                EXP_ROUGHNESS_OVER_TIME_FREE_20,
            ),
        ),
        (
            "Diffuse",
            EXP_ROUGHNESS_DIFFUSE,
            (
                EXP_SPECIFIC_ROUGHNESS_DIFFUSE_0,
                EXP_SPECIFIC_ROUGHNESS_DIFFUSE_9,
                EXP_SPECIFIC_ROUGHNESS_DIFFUSE_40,
            ),
            (
                EXP_ROUGHNESS_OVER_TIME_DIFFUSE_5,
                EXP_ROUGHNESS_OVER_TIME_DIFFUSE_12,
                EXP_ROUGHNESS_OVER_TIME_DIFFUSE_20,
            ),
        ),
    ],
)
def test_roughness_ecma_418_2_get_output_as_nparray(
    field_type, exp_roughness, exp_specific_roughness, exp_roughness_over_time
):
    """Test the get_output_as_nparray method of the RoughnessECMA418_2 class."""
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_rough_noise)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Instantiate with inputs
    roughness = RoughnessECMA418_2(signal=fc[0], field_type=field_type)

    # Check returns when not processed yet (warning)
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the `RoughnessECMA418_2.process\\(\\)` method.",
    ):
        roughness_value, specific_roughness, bark_scale, roughness_over_time, time_scale = (
            roughness.get_output_as_nparray()
        )
    assert np.isnan(roughness_value)
    assert len(specific_roughness) == 0
    assert len(bark_scale) == 0
    assert len(roughness_over_time) == 0
    assert len(time_scale) == 0

    # Compute
    roughness.process()

    roughness_value, specific_roughness, bark_scale, roughness_over_time, time_scale = (
        roughness.get_output_as_nparray()
    )
    assert roughness_value == pytest.approx(exp_roughness)
    assert isinstance(specific_roughness, np.ndarray)
    assert specific_roughness[0] == pytest.approx(exp_specific_roughness[0])
    assert specific_roughness[9] == pytest.approx(exp_specific_roughness[1])
    assert specific_roughness[40] == pytest.approx(exp_specific_roughness[2])
    assert isinstance(bark_scale, np.ndarray)
    assert bark_scale[0] == pytest.approx(EXP_BARK_0)
    assert bark_scale[9] == pytest.approx(EXP_BARK_9)
    assert bark_scale[40] == pytest.approx(EXP_BARK_40)
    assert isinstance(roughness_over_time, np.ndarray)
    assert roughness_over_time[5] == pytest.approx(exp_roughness_over_time[0])
    assert roughness_over_time[12] == pytest.approx(exp_roughness_over_time[1])
    assert roughness_over_time[20] == pytest.approx(exp_roughness_over_time[2])
    assert isinstance(time_scale, np.ndarray)
    assert time_scale[5] == pytest.approx(EXP_TIME_5)
    assert time_scale[12] == pytest.approx(EXP_TIME_12)
    assert time_scale[20] == pytest.approx(EXP_TIME_20)


@pytest.mark.parametrize(
    "field_type, exp_roughness",
    [("Free", EXP_ROUGHNESS_FREE), ("Diffuse", EXP_ROUGHNESS_DIFFUSE)],
)
def test_roughness_ecma_418_2_get_roughness(field_type, exp_roughness):
    """Test the get_roughness method of the RoughnessECMA418_2 class."""
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_rough_noise)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Instantiate with inputs
    roughness = RoughnessECMA418_2(fc[0], field_type=field_type)

    # Compute
    roughness.process()

    roughness = roughness.get_roughness()
    assert type(roughness) == float
    assert roughness == pytest.approx(exp_roughness)


def test_roughness_ecma_418_2_get_specific_roughness():
    """Test the get_specific_roughness method of the RoughnessECMA418_2 class."""
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_rough_noise)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Instantiate with inputs
    roughness = RoughnessECMA418_2(fc[0], field_type="Free")

    # Compute
    roughness.process()

    specific_roughness = roughness.get_specific_roughness()
    assert type(specific_roughness) == np.ndarray
    assert len(specific_roughness) == EXP_BARK_COUNT
    assert specific_roughness[0] == pytest.approx(EXP_SPECIFIC_ROUGHNESS_FREE_0)
    assert specific_roughness[9] == pytest.approx(EXP_SPECIFIC_ROUGHNESS_FREE_9)
    assert specific_roughness[40] == pytest.approx(EXP_SPECIFIC_ROUGHNESS_FREE_40)


def test_roughness_ecma_418_2_get_bark_band_indexes():
    """Test the get_bark_band_indexes method of the RoughnessECMA418_2 class."""
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_rough_noise)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Instantiate with inputs
    roughness = RoughnessECMA418_2(fc[0], field_type="Free")

    # Compute
    roughness.process()

    bark_band_indexes = roughness.get_bark_band_indexes()
    assert type(bark_band_indexes) == np.ndarray
    assert len(bark_band_indexes) == EXP_BARK_COUNT
    assert bark_band_indexes[0] == pytest.approx(EXP_BARK_0)
    assert bark_band_indexes[9] == pytest.approx(EXP_BARK_9)
    assert bark_band_indexes[40] == pytest.approx(EXP_BARK_40)


def test_roughness_ecma_418_2_get_bark_band_frequencies():
    """Test the get_bark_band_frequencies method of the RoughnessECMA418_2 class."""
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_rough_noise)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Instantiate with inputs
    roughness = RoughnessECMA418_2(fc[0], field_type="Free")

    # Compute
    roughness.process()

    bark_band_frequencies = roughness.get_bark_band_frequencies()
    assert type(bark_band_frequencies) == np.ndarray
    assert len(bark_band_frequencies) == EXP_BARK_COUNT
    assert bark_band_frequencies[0] == pytest.approx(EXP_FREQ_0)
    assert bark_band_frequencies[9] == pytest.approx(EXP_FREQ_9)
    assert bark_band_frequencies[40] == pytest.approx(EXP_FREQ_40)


def test_roughness_ecma_418_2_get_roughness_over_time():
    """Test the get_roughness_over_time method of the RoughnessECMA418_2 class."""
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_rough_noise)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Instantiate with inputs
    roughness = RoughnessECMA418_2(fc[0], field_type="Free")

    # Compute
    roughness.process()

    roughness_over_time = roughness.get_roughness_over_time()
    assert type(roughness_over_time) == np.ndarray
    assert len(roughness_over_time) == EXP_TIME_COUNT
    assert roughness_over_time[5] == pytest.approx(EXP_ROUGHNESS_OVER_TIME_FREE_5)
    assert roughness_over_time[12] == pytest.approx(EXP_ROUGHNESS_OVER_TIME_FREE_12)
    assert roughness_over_time[20] == pytest.approx(EXP_ROUGHNESS_OVER_TIME_FREE_20)


def test_roughness_ecma_418_2_get_time_scale():
    """Test the get_time_scale method of the RoughnessECMA418_2 class."""
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_rough_noise)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Instantiate with inputs
    roughness = RoughnessECMA418_2(fc[0], field_type="Free")

    # Compute
    roughness.process()

    time_scale = roughness.get_time_scale()
    assert type(time_scale) == np.ndarray
    assert len(time_scale) == EXP_TIME_COUNT
    assert time_scale[5] == pytest.approx(EXP_TIME_5)
    assert time_scale[12] == pytest.approx(EXP_TIME_12)
    assert time_scale[20] == pytest.approx(EXP_TIME_20)


@patch("matplotlib.pyplot.show")
def test_roughness_ecma_418_2_plot(mock_show):
    """Test the plot method."""
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_rough_noise)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Instantiate with inputs
    roughness = RoughnessECMA418_2(fc[0], field_type="Free")

    # RoughnessECMA418_2 not computed yet -> error
    with pytest.raises(
        PyAnsysSoundException,
        match="Output is not processed yet. Use the `RoughnessECMA418_2.process\\(\\)` method.",
    ):
        roughness.plot()

    # Compute
    roughness.process()

    # Plot
    roughness.plot()
