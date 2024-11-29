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

from ansys.dpf.core import (
    Field,
    FieldsContainer,
    TimeFreqSupport,
    fields_container_factory,
    fields_factory,
    locations,
)
import numpy as np
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ansys.sound.core.sound_composer import SourceBroadbandNoise, SourceControlTime

REF_ACOUSTIC_POWER = 4e-10

EXP_SPECTRUM_DATA03 = 1.9452798369457014e-05
EXP_STR_NOT_SET = "Broadband noise source: Not set\nSource control: Not set"
EXP_STR_ALL_SET = (
    "Broadband noise source: ''\n"
    "\tSpectrum type: Not available\n"
    "\tSpectrum count: 5\n"
    "\tControl parameter: Speed of wind, m/s\n"
    "\t\t[1.0, 2.0, 5.300000190734863, 10.5, 27.777999877929688]"
    "\nSource control: \n"
    "\tMin: 1.0\n"
    "\tMax: 10.0\n"
    "\tDuration: 3.0 s"
)
EXP_STR_ALL_SET_40_VALUES = (
    "Broadband noise source: ''\n"
    "\tSpectrum type: Not available\n"
    "\tSpectrum count: 40\n"
    "\tControl parameter: Speed of wind, m/s\n"
    "\t\t[1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, ... "
    "26.0, 27.0, 28.0, 29.0, 30.0, 31.0, 32.0, 33.0, 34.0, 35.0, 36.0, 37.0, 38.0, 39.0, 40.0]"
    "\nSource control: \n"
    "\tMin: 1.0\n"
    "\tMax: 10.0\n"
    "\tDuration: 3.0 s"
)


def test_source_broadband_noise_instantiation_no_arg(dpf_sound_test_server):
    """Test SourceBroadbandNoise instantiation without arguments."""
    # Test instantiation.
    source_bbn = SourceBroadbandNoise()
    assert isinstance(source_bbn, SourceBroadbandNoise)
    assert source_bbn.source_bbn is None


def test_source_broadband_noise_instantiation_file_arg(dpf_sound_test_server):
    """Test SourceBroadbandNoise instantiation with file argument."""
    # Test instantiation.
    source_bbn = SourceBroadbandNoise(file=pytest.data_path_sound_composer_bbn_source_in_container)
    assert isinstance(source_bbn, SourceBroadbandNoise)
    assert source_bbn.source_bbn is not None


def test_source_broadband_noise___str___not_set(dpf_sound_test_server):
    """Test SourceBroadbandNoise __str__ method when nothing is set."""
    source_bbn = SourceBroadbandNoise()
    assert str(source_bbn) == EXP_STR_NOT_SET


def test_source_broadband_noise___str___all_set(dpf_sound_test_server):
    """Test SourceBroadbandNoise __str__ method when all data are set."""
    # Create a field to use in a SourceControlTime object.
    source_control_field = fields_factory.create_scalar_field(
        num_entities=1, location=locations.time_freq
    )
    source_control_field.append([1, 3, 6, 10], 1)
    support = TimeFreqSupport()
    time_field = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
    time_field.append([0, 1, 2, 3], 1)
    support.time_frequencies = time_field
    source_control_field.time_freq_support = support

    # Create a SourceControlTime object.
    source_control = SourceControlTime()
    source_control.control = source_control_field

    # Create a SourceBroadbandNoise object using source file with less than 30 values and created
    # source control.
    source_bbn = SourceBroadbandNoise(
        pytest.data_path_sound_composer_bbn_source_in_container,
        source_control,
    )
    assert str(source_bbn) == EXP_STR_ALL_SET

    # Replace source file with one with more than 30 values.
    source_bbn.load_source_bbn(pytest.data_path_sound_composer_bbn_source_40_values_in_container)
    assert str(source_bbn) == EXP_STR_ALL_SET_40_VALUES


def test_source_broadband_noise_properties(dpf_sound_test_server):
    """Test SourceBroadbandNoise properties."""
    source_bbn = SourceBroadbandNoise()

    # Test source_control property.
    source_bbn.source_control = SourceControlTime()
    assert isinstance(source_bbn.source_control, SourceControlTime)

    # Test source_bbn property.
    source_bbn_tmp = SourceBroadbandNoise()
    source_bbn_tmp.load_source_bbn(pytest.data_path_sound_composer_bbn_source_in_container)
    bbn_fieldscontainer = source_bbn_tmp.source_bbn
    source_bbn.source_bbn = bbn_fieldscontainer
    assert isinstance(source_bbn.source_bbn, FieldsContainer)


def test_source_broadband_noise_properties_exceptions(dpf_sound_test_server):
    """Test SourceBroadbandNoise properties' exceptions."""
    source_bbn = SourceBroadbandNoise()

    # Test source_control setter exception (str instead of SourceControlTime).
    with pytest.raises(
        PyAnsysSoundException,
        match="Specified source control object must be of type ``SourceControlTime``.",
    ):
        source_bbn.source_control = "InvalidType"

    # Test source_bbn setter exception 1 (str instead a Field).
    with pytest.raises(
        PyAnsysSoundException,
        match="Specified spectrum source must be provided as a DPF fields container.",
    ):
        source_bbn.source_bbn = "InvalidType"

    # Test source_bbn setter exception 2 (less than 1 spectrum).
    bbn_fieldscontainer = FieldsContainer()
    with pytest.raises(
        PyAnsysSoundException,
        match="Specified broadband noise source must contain at least one spectrum.",
    ):
        source_bbn.source_bbn = bbn_fieldscontainer

    # Test source_bbn setter exception 3 (empty spectrum).
    bbn_fieldscontainer = fields_container_factory.over_time_freq_fields_container([Field()])
    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "Each spectrum in the specified broadband noise source must contain at least one "
            "element."
        ),
    ):
        source_bbn.source_bbn = bbn_fieldscontainer

    # Test source_bbn setter exception 4 (empty bbn source's control data).
    # For this, we use a valid dataset, and then remove the control data.
    source_bbn = SourceBroadbandNoise()
    source_bbn.load_source_bbn(pytest.data_path_sound_composer_bbn_source_in_container)
    support_data = source_bbn.source_bbn.get_support("control_parameter_1")
    support_properties = support_data.available_field_supported_properties()
    support_values = support_data.field_support_by_property(support_properties[0])
    support_values.data = []
    fc_source_bbn = source_bbn.source_bbn
    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "Control data in the specified broadband noise source must contain at least one "
            "element."
        ),
    ):
        source_bbn.source_bbn = fc_source_bbn


def test_source_broadband_noise_is_source_control_valid(dpf_sound_test_server):
    """Test SourceBroadbandNoise is_source_control_valid method."""
    source_bbn = SourceBroadbandNoise()

    # Test is_source_control_valid method (attribute not set).
    assert source_bbn.is_source_control_valid() is False

    # Test is_source_control_valid method (attribute set, but attribute's field not set).
    control = SourceControlTime()
    source_bbn.source_control = control
    assert source_bbn.is_source_control_valid() is False

    # Test is_source_control_valid method (all set).
    # source_bbn.load_source_bbn(pytest.data_path_sound_composer_bbn_source_in_container)
    field = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
    field.append([1.0, 2.0, 3.0, 4.0, 5.0], 1)
    source_bbn.source_control.control = field
    assert source_bbn.is_source_control_valid() is True


def test_source_specrum_load_source_bbn(dpf_sound_test_server):
    """Test SourceBroadbandNoise load_source_bbn method."""
    source_bbn = SourceBroadbandNoise()
    source_bbn.load_source_bbn(pytest.data_path_sound_composer_bbn_source_in_container)
    assert isinstance(source_bbn.source_bbn, FieldsContainer)
    assert source_bbn.source_bbn[0].data[3] == pytest.approx(EXP_SPECTRUM_DATA03)


def test_source_broadband_noise_process(dpf_sound_test_server):
    """Test SourceBroadbandNoise process method."""
    # Create a field to use in a SourceControlTime object.
    source_control_field = fields_factory.create_scalar_field(
        num_entities=1, location=locations.time_freq
    )
    source_control_field.append([1, 3, 6, 10], 1)
    support = TimeFreqSupport()
    time_field = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
    time_field.append([0, 1, 2, 3], 1)
    support.time_frequencies = time_field
    source_control_field.time_freq_support = support

    # Create a SourceControlTime object.
    source_control = SourceControlTime()
    source_control.control = source_control_field

    source_bbn = SourceBroadbandNoise(
        pytest.data_path_sound_composer_bbn_source_in_container,
        source_control,
    )
    source_bbn.process()
    assert source_bbn._output is not None


def test_source_broadband_noise_process_exceptions(dpf_sound_test_server):
    """Test SourceBroadbandNoise process method exceptions."""
    # Test process method exception1 (missing control).
    source_bbn = SourceBroadbandNoise(pytest.data_path_sound_composer_bbn_source_in_container)
    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "Broadband noise source control is not set. "
            "Use ``SourceBroadbandNoise.source_control``."
        ),
    ):
        source_bbn.process()

    # Test process method exception2 (missing bbn source data).
    source_bbn.source_bbn = None
    field = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
    field.append([1.0, 2.0, 3.0, 4.0, 5.0], 1)
    source_control = SourceControlTime()
    source_control.control = field
    source_bbn.source_control = source_control
    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "Broadband noise source data is not set. Use ``SourceBroadbandNoise.source_bbn`` "
            "or method ``SourceBroadbandNoise.load_source_bbn\\(\\)``."
        ),
    ):
        source_bbn.process()

    # Test process method exception3 (invalid sampling frequency value).
    source_bbn.load_source_bbn(pytest.data_path_sound_composer_bbn_source_in_container)
    with pytest.raises(
        PyAnsysSoundException, match="Sampling frequency must be strictly positive."
    ):
        source_bbn.process(sampling_frequency=0.0)


def test_source_broadband_noise_get_output(dpf_sound_test_server):
    """Test SourceBroadbandNoise get_output method."""
    # Create a field to use in a SourceControlTime object.
    source_control_field = fields_factory.create_scalar_field(
        num_entities=1, location=locations.time_freq
    )
    source_control_field.append([1, 3, 6, 10], 1)
    support = TimeFreqSupport()
    time_field = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
    time_field.append([0, 1, 2, 3], 1)
    support.time_frequencies = time_field
    source_control_field.time_freq_support = support

    # Create a SourceControlTime object.
    source_control = SourceControlTime()
    source_control.control = source_control_field

    source_bbn = SourceBroadbandNoise(
        pytest.data_path_sound_composer_bbn_source_in_container,
        source_control,
    )
    source_bbn.process(sampling_frequency=44100.0)
    output = source_bbn.get_output()
    assert isinstance(output, Field)
    assert len(output.data) / 44100.0 == pytest.approx(3.0)


def test_source_broadband_noise_get_output_unprocessed(dpf_sound_test_server):
    """Test SourceBroadbandNoise get_output method's exception."""
    source_bbn = SourceBroadbandNoise()
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the ``SourceBroadbandNoise.process\\(\\)`` method.",
    ):
        output = source_bbn.get_output()
    assert output is None


def test_source_broadband_noise_get_output_as_nparray(dpf_sound_test_server):
    """Test SourceBroadbandNoise get_output_as_nparray method."""
    # Create a field to use in a SourceControlTime object.
    source_control_field = fields_factory.create_scalar_field(
        num_entities=1, location=locations.time_freq
    )
    source_control_field.append([1, 3, 6, 10], 1)
    support = TimeFreqSupport()
    time_field = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
    time_field.append([0, 1, 2, 3], 1)
    support.time_frequencies = time_field
    source_control_field.time_freq_support = support

    # Create a SourceControlTime object.
    source_control = SourceControlTime()
    source_control.control = source_control_field

    source_bbn = SourceBroadbandNoise(
        pytest.data_path_sound_composer_bbn_source_in_container,
        source_control,
    )
    source_bbn.process(sampling_frequency=44100.0)
    output = source_bbn.get_output_as_nparray()
    assert isinstance(output, np.ndarray)
    assert len(output) / 44100.0 == pytest.approx(3.0)


def test_source_broadband_noise_get_output_as_nparray_unprocessed(dpf_sound_test_server):
    """Test SourceBroadbandNoise get_output_as_nparray method's exception."""
    source_bbn = SourceBroadbandNoise()
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the ``SourceBroadbandNoise.process\\(\\)`` method.",
    ):
        output = source_bbn.get_output_as_nparray()
    assert len(output) == 0


@patch("matplotlib.pyplot.show")
def test_source_broadband_noise_plot(dpf_sound_test_server):
    """Test SourceBroadbandNoise plot method."""
    # Create a field to use in a SourceControlTime object.
    source_control_field = fields_factory.create_scalar_field(
        num_entities=1, location=locations.time_freq
    )
    source_control_field.append([1, 3, 6, 10], 1)
    support = TimeFreqSupport()
    time_field = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
    time_field.append([0, 1, 2, 3], 1)
    support.time_frequencies = time_field
    source_control_field.time_freq_support = support

    # Create a SourceControlTime object.
    source_control = SourceControlTime()
    source_control.control = source_control_field

    source_bbn = SourceBroadbandNoise(
        pytest.data_path_sound_composer_bbn_source_in_container,
        source_control,
    )
    source_bbn.process()
    source_bbn.plot()


def test_source_broadband_noise_plot_exceptions(dpf_sound_test_server):
    """Test SourceBroadbandNoise plot method's exception."""
    source_bbn = SourceBroadbandNoise()
    with pytest.raises(
        PyAnsysSoundException,
        match="Output is not processed yet. Use the 'SourceBroadbandNoise.process\\(\\)' method.",
    ):
        source_bbn.plot()


def test_source_broadband_noise___extract_bbn_info(dpf_sound_test_server):
    """Test SourceBroadbandNoise __extract_bbn_info method."""
    source_bbn = SourceBroadbandNoise()
    assert source_bbn._SourceBroadbandNoise__extract_bbn_info() == ("", 0.0, "", "", [])

    source_bbn.load_source_bbn(pytest.data_path_sound_composer_bbn_source_in_container)
    assert source_bbn._SourceBroadbandNoise__extract_bbn_info() == (
        "Not available",
        10.0,
        "Speed of wind",
        "m/s",
        [1.0, 2.0, 5.300000190734863, 10.5, 27.777999877929688],
    )

    source_bbn.source_bbn[0].time_freq_support.time_frequencies.data = []
    assert source_bbn._SourceBroadbandNoise__extract_bbn_info() == (
        "Not available",
        0.0,
        "Speed of wind",
        "m/s",
        [1.0, 2.0, 5.300000190734863, 10.5, 27.777999877929688],
    )
