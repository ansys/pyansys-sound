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

from ansys.dpf.core import (
    Field,
    FieldsContainer,
    GenericDataContainer,
    Operator,
    TimeFreqSupport,
    fields_container_factory,
    fields_factory,
    locations,
)
import numpy as np
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ansys.sound.core.sound_composer import SourceControlTime, SourceHarmonicsTwoParameters
from ansys.sound.core.spectral_processing import PowerSpectralDensity

REF_ACOUSTIC_POWER = 4e-10

EXP_LEVEL_OCTAVE_BAND_500 = 44.2
EXP_LEVEL_OCTAVE_BAND_1000 = 46.7
EXP_LEVEL_OCTAVE_BAND_2000 = 50.7
EXP_LEVEL_OCTAVE_BAND_500_INVCON = 51.2
EXP_LEVEL_OCTAVE_BAND_1000_INVCON = 50.3
EXP_LEVEL_OCTAVE_BAND_2000_INVCON = 35.5
EXP_ORDER_LEVEL62 = 3.9810717055349695e-05
EXP_ORDER_LEVEL33_INVERTED = 0.00039810717055349735
EXP_ORDER_LEVEL22_FROM_ACCEL = 0.0016218100973589282
EXP_STR_NOT_SET = (
    "Harmonics source with two parameters: Not set\n"
    "Source control:\n"
    "\tControl 1: Not set\n"
    "\tControl 2: Not set"
)
EXP_STR_ALL_SET = (
    "Harmonics source with two parameters: ''\n"
    "\tNumber of orders: 4\n"
    "\t\t[12. 24. 36. 48.]\n"
    "\tControl parameter 1: RPM, "
    "500.0 - 3000.0 rpm\n"
    "\tControl parameter 2: charge, "
    "0.0 - 10.0 %\n"
    "Source control:\n"
    "\tControl 1: \n"
    "\t\tMin: 0.0\n"
    "\t\tMax: 3.0\n"
    "\t\tDuration: 3.0 s\n"
    "\tControl 2: \n"
    "\t\tMin: 0.0\n"
    "\t\tMax: 3.0\n"
    "\t\tDuration: 3.0 s"
)
EXP_STR_ALL_SET_MANY_VALUES = (
    "Harmonics source with two parameters: ''\n"
    "\tNumber of orders: 15\n"
    "\t\t[1. 2. 3. 4. 5. ... 11. 12. 13. 14. 15.]\n"
    "\tControl parameter 1: RPM, "
    "500.0 - 1900.0 rpm\n"
    "\tControl parameter 2: charge, "
    "0.0 - 50.0 %\n"
    "Source control:\n"
    "\tControl 1: \n"
    "\t\tMin: 0.0\n"
    "\t\tMax: 3.0\n"
    "\t\tDuration: 3.0 s\n"
    "\tControl 2: \n"
    "\t\tMin: 0.0\n"
    "\t\tMax: 3.0\n"
    "\t\tDuration: 3.0 s"
)


def test_source_harmonics_two_parameters_instantiation_no_arg():
    """Test SourceHarmonicsTwoParameters instantiation without arguments."""
    source_obj = SourceHarmonicsTwoParameters()
    assert isinstance(source_obj, SourceHarmonicsTwoParameters)
    assert source_obj.source_harmonics_two_parameters is None


def test_source_harmonics_two_parameters_instantiation_file_arg():
    """Test SourceHarmonicsTwoParameters instantiation with file argument."""
    source_obj = SourceHarmonicsTwoParameters(
        file=pytest.data_path_sound_composer_harmonics_source_2p_in_container
    )
    assert isinstance(source_obj, SourceHarmonicsTwoParameters)
    assert source_obj.source_harmonics_two_parameters is not None


def test_source_harmonics_two_parameters___str___not_set():
    """Test SourceHarmonicsTwoParameters __str__ method when nothing is set."""
    source_obj = SourceHarmonicsTwoParameters()
    assert str(source_obj) == EXP_STR_NOT_SET


def test_source_harmonics_two_parameters___str___all_set():
    """Test SourceHarmonicsTwoParameters __str__ method when all data are set."""
    # Create a field to use in a SourceControlTime object.
    f_source_control = fields_factory.create_scalar_field(
        num_entities=1, location=locations.time_freq
    )
    f_source_control.append([0, 1, 2, 3], 1)
    support = TimeFreqSupport()
    f_time = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
    f_time.append([0, 1, 2, 3], 1)
    support.time_frequencies = f_time
    f_source_control.time_freq_support = support

    # Create a first SourceControlTime object.
    source_control_rpm = SourceControlTime()
    source_control_rpm.control = f_source_control

    # Create a second SourceControlTime object.
    source_control2 = SourceControlTime()
    source_control2.control = f_source_control

    # Create a SourceHarmonicsTwoParameters object test source file with less and created
    # source controls.
    source_obj = SourceHarmonicsTwoParameters(
        file=pytest.data_path_sound_composer_harmonics_source_2p_in_container,
        source_control_rpm=source_control_rpm,
        source_control2=source_control2,
    )

    assert str(source_obj) == EXP_STR_ALL_SET

    # Replace source file with one with more than 10 values for each parameter.
    source_obj.load_source_harmonics_two_parameters(
        pytest.data_path_sound_composer_harmonics_source_2p_many_values_in_container
    )
    assert str(source_obj) == EXP_STR_ALL_SET_MANY_VALUES


def test_source_harmonics_two_parameters_properties():
    """Test SourceHarmonicsTwoParameters properties."""
    source_obj = SourceHarmonicsTwoParameters()

    # Test control_rpm property.
    source_obj.source_control_rpm = SourceControlTime()
    assert isinstance(source_obj.source_control_rpm, SourceControlTime)

    # Test control2 property.
    source_obj.source_control2 = SourceControlTime()
    assert isinstance(source_obj.source_control2, SourceControlTime)

    # Test source_harmonics_two_parameters property.
    # Create a second object and then reuse its source_harmonics_two_parameters property.
    source_obj_tmp = SourceHarmonicsTwoParameters()
    source_obj_tmp.load_source_harmonics_two_parameters(
        pytest.data_path_sound_composer_harmonics_source_2p_in_container
    )
    fc_source = source_obj_tmp.source_harmonics_two_parameters
    source_obj.source_harmonics_two_parameters = fc_source
    assert isinstance(source_obj.source_harmonics_two_parameters, FieldsContainer)


def test_source_harmonics_two_parameters_properties_exceptions():
    """Test SourceHarmonicsTwoParameters properties' exceptions."""
    source_obj = SourceHarmonicsTwoParameters()

    # Test source_control_rpm setter exception (str instead of SourceControlTime).
    with pytest.raises(
        PyAnsysSoundException,
        match="Specified RPM source control object must be of type SourceControlTime.",
    ):
        source_obj.source_control_rpm = "InvalidType"

    # Test source_control2 setter exception (str instead of SourceControlTime).
    with pytest.raises(
        PyAnsysSoundException,
        match="Specified second source control object must be of type SourceControlTime.",
    ):
        source_obj.source_control2 = "InvalidType"

    # Test source_harmonics_two_parameters setter exception 1 (str instead of FieldsContainer).
    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "Specified harmonics source with two parameters must be provided as a DPF fields "
            "container."
        ),
    ):
        source_obj.source_harmonics_two_parameters = "InvalidType"

    # Test source_harmonics_two_parameters setter exception 2 (less than 1 order).
    fc_source = FieldsContainer()
    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "Specified harmonics source with two parameters must contain at least one order level "
            "\\(the provided DPF fields container must contain at least one field with at least "
            "one data point\\)."
        ),
    ):
        source_obj.source_harmonics_two_parameters = fc_source

    # Test source_harmonics_two_parameters setter exception 3 (within-field order number mismatch).
    field = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
    field.append([1.0, 2.0, 3.0, 4.0, 5.0], 1)
    support = TimeFreqSupport()
    f_time = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
    f_time.append([1.0, 2.0], 1)
    support.time_frequencies = f_time
    field.time_freq_support = support
    fc_source = fields_container_factory.over_time_freq_fields_container([field])
    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "Each set of order levels in the specified harmonics source with two parameters must "
            "contain as many level values as the number of orders \\(in the provided DPF fields "
            "container, each field must contain the same number of data points and support "
            "values\\)."
        ),
    ):
        source_obj.source_harmonics_two_parameters = fc_source

    # Test source_harmonics_two_parameters setter exception 4(between-field order number mismatch).
    field2 = field.deep_copy()
    field.data = [1.0, 2.0]
    field2.data = [1.0, 2.0, 3.0, 4.0, 5.0]
    field2.time_freq_support.time_frequencies.data = [1.0, 2.0, 3.0, 4.0, 5.0]
    fc_source = fields_container_factory.over_time_freq_fields_container([field, field2])
    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "Each set of order levels in the specified harmonics source with two parameters must "
            "contain the same number of level values \\(in the provided DPF fields container, "
            "each field must contain the same number of data points\\)."
        ),
    ):
        source_obj.source_harmonics_two_parameters = fc_source

    # Test source_harmonics_two_parameters setter exception 5 (empty harmonics source's first
    # control data). For this, we use a valid dataset, and then remove the control data.
    source_obj = SourceHarmonicsTwoParameters()
    source_obj.load_source_harmonics_two_parameters(
        pytest.data_path_sound_composer_harmonics_source_2p_in_container
    )
    support_data = source_obj.source_harmonics_two_parameters.get_support("control_parameter_1")
    support_properties = support_data.available_field_supported_properties()
    support_values = support_data.field_support_by_property(support_properties[0])
    support_values.data = []
    fc_source = source_obj.source_harmonics_two_parameters
    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "Specified harmonics source with two parameters must contain as many sets of order "
            "levels as the number of values in both associated control parameters \\(in the "
            "provided DPF fields container, the number of fields should be the same as the number "
            "of values in both fields container supports\\)."
        ),
    ):
        source_obj.source_harmonics_two_parameters = fc_source


def test_source_harmonics_two_parameters_is_source_control_valid():
    """Test SourceHarmonicsTwoParameters is_source_control_valid method."""
    source_obj = SourceHarmonicsTwoParameters()

    # Test is_source_control_valid method (attribute not set).
    assert source_obj.is_source_control_valid() is False

    # Test is_source_control_valid method (first attribute set, but not the second).
    source_control_obj = SourceControlTime()
    source_obj.source_control_rpm = source_control_obj
    assert source_obj.is_source_control_valid() is False

    # Test is_source_control_valid method (both attributes set, but attributes' fields not set).
    source_control_obj = SourceControlTime()
    source_obj.source_control2 = source_control_obj
    assert source_obj.is_source_control_valid() is False

    # Test is_source_control_valid method (only one attribute's field set).
    f_source_control = fields_factory.create_scalar_field(
        num_entities=1, location=locations.time_freq
    )
    f_source_control.append([1.0, 2.0, 3.0, 4.0, 5.0], 1)
    source_obj.source_control_rpm.control = f_source_control
    assert source_obj.is_source_control_valid() is False

    # Test is_source_control_valid method (all set).
    source_obj.source_control2.control = f_source_control
    assert source_obj.is_source_control_valid() is True


def test_source_specrum_load_source_harmonics_two_parameters():
    """Test SourceHarmonicsTwoParameters load_source_harmonics method."""
    source_obj = SourceHarmonicsTwoParameters()
    source_obj.load_source_harmonics_two_parameters(
        pytest.data_path_sound_composer_harmonics_source_2p_in_container
    )
    assert isinstance(source_obj.source_harmonics_two_parameters, FieldsContainer)
    assert source_obj.source_harmonics_two_parameters[6].data[2] == pytest.approx(EXP_ORDER_LEVEL62)

    source_obj.load_source_harmonics_two_parameters(
        pytest.data_path_sound_composer_harmonics_source_2p_inverted_controls_in_container
    )
    assert isinstance(source_obj.source_harmonics_two_parameters, FieldsContainer)
    assert source_obj.source_harmonics_two_parameters[3].data[3] == pytest.approx(
        EXP_ORDER_LEVEL33_INVERTED
    )

    source_obj.load_source_harmonics_two_parameters(
        pytest.data_path_sound_composer_harmonics_source_2p_from_accel_in_container
    )
    assert isinstance(source_obj.source_harmonics_two_parameters, FieldsContainer)
    assert source_obj.source_harmonics_two_parameters[2].data[2] == pytest.approx(
        EXP_ORDER_LEVEL22_FROM_ACCEL
    )


def test_source_harmonics_two_parameters_set_from_generic_data_containers():
    """Test SourceHarmonicsTwoParameters set_from_generic_data_containers method."""
    op = Operator("sound_composer_load_source_harmonics_two_parameters")
    op.connect(0, pytest.data_path_sound_composer_harmonics_source_2p_in_container)
    op.run()
    fc_data: FieldsContainer = op.get_output(0, "fields_container")

    source_data = GenericDataContainer()
    source_data.set_property("sound_composer_source", fc_data)

    f_source_control = fields_factory.create_scalar_field(
        num_entities=1, location=locations.time_freq
    )
    f_source_control.append([1.0, 2.0, 3.0, 4.0, 5.0], 1)
    source_control_data = GenericDataContainer()
    source_control_data.set_property("sound_composer_source_control_parameter_1", f_source_control)
    source_control_data.set_property("sound_composer_source_control_parameter_2", f_source_control)
    source_control_data.set_property(
        "sound_composer_source_control_two_parameter_displayed_string1", "test1"
    )
    source_control_data.set_property(
        "sound_composer_source_control_two_parameter_displayed_string2", "test2"
    )

    source_harmo_2p_obj = SourceHarmonicsTwoParameters()
    source_harmo_2p_obj.set_from_generic_data_containers(source_data, source_control_data)
    assert isinstance(source_harmo_2p_obj.source_harmonics_two_parameters, FieldsContainer)
    assert len(source_harmo_2p_obj.source_harmonics_two_parameters) == len(fc_data)
    assert isinstance(source_harmo_2p_obj.source_control_rpm, SourceControlTime)
    assert len(source_harmo_2p_obj.source_control_rpm.control.data) == 5
    assert isinstance(source_harmo_2p_obj.source_control2, SourceControlTime)
    assert len(source_harmo_2p_obj.source_control2.control.data) == 5
    assert source_harmo_2p_obj.source_control_rpm.description == "test1"
    assert source_harmo_2p_obj.source_control2.description == "test2"


def test_source_harmonics_two_parameters_get_as_generic_data_containers():
    """Test SourceHarmonicsTwoParameters get_as_generic_data_containers method."""
    # Source controls undefined => warning.
    source_harmo_2p_obj = SourceHarmonicsTwoParameters(
        file=pytest.data_path_sound_composer_harmonics_source_2p_in_container
    )
    with pytest.warns(
        PyAnsysSoundWarning,
        match=(
            "Cannot create source control generic data container because at least one source "
            "control data is missing."
        ),
    ):
        _, source_control_data = source_harmo_2p_obj.get_as_generic_data_containers()
    assert source_control_data is None

    # Source data undefined => warning.
    source_harmo_2p_obj.source_harmonics_two_parameters = None
    f_source_control = fields_factory.create_scalar_field(
        num_entities=1, location=locations.time_freq
    )
    f_source_control.append([1.0, 2.0, 3.0, 4.0, 5.0], 1)
    source_control_obj = SourceControlTime()
    source_control_obj.control = f_source_control
    source_harmo_2p_obj.source_control_rpm = source_control_obj
    source_harmo_2p_obj.source_control_rpm.description = "test1"
    source_harmo_2p_obj.source_control2 = source_control_obj
    source_harmo_2p_obj.source_control2.description = "test2"
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Cannot create source generic data container because there is no source data.",
    ):
        source_data, _ = source_harmo_2p_obj.get_as_generic_data_containers()
    assert source_data is None

    # Both source and source control are defined.
    source_harmo_2p_obj.load_source_harmonics_two_parameters(
        pytest.data_path_sound_composer_harmonics_source_2p_in_container,
    )
    source_data, source_control_data = source_harmo_2p_obj.get_as_generic_data_containers()

    assert isinstance(source_data, GenericDataContainer)
    assert isinstance(source_data.get_property("sound_composer_source"), FieldsContainer)
    assert isinstance(source_control_data, GenericDataContainer)
    assert isinstance(
        source_control_data.get_property("sound_composer_source_control_parameter_1"), Field
    )
    assert isinstance(
        source_control_data.get_property("sound_composer_source_control_parameter_2"), Field
    )
    assert (
        source_control_data.get_property(
            "sound_composer_source_control_two_parameter_displayed_string1"
        )
        == "test1"
    )
    assert (
        source_control_data.get_property(
            "sound_composer_source_control_two_parameter_displayed_string2"
        )
        == "test2"
    )


def test_source_harmonics_two_parameters_process():
    """Test SourceHarmonicsTwoParameters process method."""
    # Create a field to use in a SourceControlTime object.
    f_source_control = fields_factory.create_scalar_field(
        num_entities=1, location=locations.time_freq
    )
    f_source_control.append([500, 1250, 2000, 3000], 1)
    support = TimeFreqSupport()
    f_time = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
    f_time.append([0, 1, 2, 3], 1)
    support.time_frequencies = f_time
    f_source_control.time_freq_support = support

    # Create a first SourceControlTime object.
    source_control_rpm = SourceControlTime()
    source_control_rpm.control = f_source_control

    # Create another field to use in a SourceControlTime object.
    f_source_control = fields_factory.create_scalar_field(
        num_entities=1, location=locations.time_freq
    )
    f_source_control.append([9.5, 9, 1, 0.5], 1)
    support = TimeFreqSupport()
    f_time = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
    f_time.append([0, 1, 2, 3], 1)
    support.time_frequencies = f_time
    f_source_control.time_freq_support = support

    # Create a second SourceControlTime object.
    source_control2 = SourceControlTime()
    source_control2.control = f_source_control

    # Create a SourceHarmonicsTwoParameters object test source file with less and created
    # source controls.
    source_obj = SourceHarmonicsTwoParameters(
        file=pytest.data_path_sound_composer_harmonics_source_2p_in_container,
        source_control_rpm=source_control_rpm,
        source_control2=source_control2,
    )

    source_obj.process()
    assert source_obj._output is not None


def test_source_harmonics_two_parameters_process_exceptions():
    """Test SourceHarmonicsTwoParameters process method exceptions."""
    # Test process method exception1 (missing controls).
    source_obj = SourceHarmonicsTwoParameters(
        pytest.data_path_sound_composer_harmonics_source_2p_in_container
    )
    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "At least one source control for harmonics source with two parameters is not set. Use "
            "``SourceHarmonicsTwoParameters.source_control_rpm`` and/or "
            "``SourceHarmonicsTwoParameters.source_control2``."
        ),
    ):
        source_obj.process()

    # Test process method exception2 (missing harmonics source data).
    source_obj.source_harmonics_two_parameters = None
    f_source_control = fields_factory.create_scalar_field(
        num_entities=1, location=locations.time_freq
    )
    f_source_control.append([1.0, 2.0, 3.0, 4.0, 5.0], 1)
    source_control_obj = SourceControlTime()
    source_control_obj.control = f_source_control
    source_obj.source_control_rpm = source_control_obj
    source_obj.source_control2 = source_control_obj
    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "Harmonics source with two parameters data is not set. Use "
            "``SourceHarmonicsTwoParameters.source_harmonics_two_parameters`` or method "
            "``SourceHarmonicsTwoParameters.load_source_harmonics_two_parameters\\(\\)``."
        ),
    ):
        source_obj.process()

    # Test process method exception3 (invalid sampling frequency value).
    source_obj.load_source_harmonics_two_parameters(
        pytest.data_path_sound_composer_harmonics_source_2p_in_container
    )
    with pytest.raises(
        PyAnsysSoundException, match="Sampling frequency must be strictly positive."
    ):
        source_obj.process(sampling_frequency=0.0)


def test_source_harmonics_two_parameters_get_output():
    """Test SourceHarmonicsTwoParameters get_output method."""
    # Create a field to use in a SourceControlTime object.
    f_source_control = fields_factory.create_scalar_field(
        num_entities=1, location=locations.time_freq
    )
    f_source_control.append([500, 1250, 2000, 3000], 1)
    support = TimeFreqSupport()
    f_time = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
    f_time.append([0, 1, 2, 3], 1)
    support.time_frequencies = f_time
    f_source_control.time_freq_support = support

    # Create a first SourceControlTime object.
    source_control_rpm = SourceControlTime()
    source_control_rpm.control = f_source_control

    # Create another field to use in a SourceControlTime object.
    f_source_control = fields_factory.create_scalar_field(
        num_entities=1, location=locations.time_freq
    )
    f_source_control.append([9.5, 9, 1, 0.5], 1)
    support = TimeFreqSupport()
    f_time = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
    f_time.append([0, 1, 2, 3], 1)
    support.time_frequencies = f_time
    f_source_control.time_freq_support = support

    # Create a second SourceControlTime object.
    source_control2 = SourceControlTime()
    source_control2.control = f_source_control

    # Create a SourceHarmonicsTwoParameters object test source file and created source
    # controls.
    source_obj = SourceHarmonicsTwoParameters(
        file=pytest.data_path_sound_composer_harmonics_source_2p_in_container,
        source_control_rpm=source_control_rpm,
        source_control2=source_control2,
    )

    source_obj.process(sampling_frequency=44100.0)
    f_output = source_obj.get_output()
    assert isinstance(f_output, Field)
    assert len(f_output.data) / 44100.0 == pytest.approx(3.0)

    # Compute the power spectral density over the output signal.
    psd = PowerSpectralDensity(
        input_signal=f_output,
        fft_size=8192,
        window_type="HANN",
        window_length=8192,
        overlap=0.75,
    )
    psd.process()
    psd_squared, psd_freq = psd.get_PSD_squared_linear_as_nparray()
    delat_f = psd_freq[1] - psd_freq[0]

    # Check the sound power level in the octave bands centered at 500, 1000 and 2000 Hz.
    # Due to the non-deterministic nature of the produced signal, tolerance is set to 1 dB.
    psd_squared_band = psd_squared[
        (psd_freq >= 500 * 2 ** (-1 / 2)) & (psd_freq < 500 * 2 ** (1 / 2))
    ]
    level = 10 * np.log10(psd_squared_band.sum() * delat_f / REF_ACOUSTIC_POWER)
    assert level == pytest.approx(EXP_LEVEL_OCTAVE_BAND_500, abs=1.0)

    psd_squared_band = psd_squared[
        (psd_freq >= 1000 * 2 ** (-1 / 2)) & (psd_freq < 1000 * 2 ** (1 / 2))
    ]
    level = 10 * np.log10(psd_squared_band.sum() * delat_f / REF_ACOUSTIC_POWER)
    assert level == pytest.approx(EXP_LEVEL_OCTAVE_BAND_1000, abs=1.0)

    psd_squared_band = psd_squared[
        (psd_freq >= 2000 * 2 ** (-1 / 2)) & (psd_freq < 2000 * 2 ** (1 / 2))
    ]
    level = 10 * np.log10(psd_squared_band.sum() * delat_f / REF_ACOUSTIC_POWER)
    assert level == pytest.approx(EXP_LEVEL_OCTAVE_BAND_2000, abs=1.0)

    # Test output with another source file with inverted controls.
    source_obj.load_source_harmonics_two_parameters(
        pytest.data_path_sound_composer_harmonics_source_2p_inverted_controls_in_container,
    )

    source_obj.process(sampling_frequency=44100.0)
    f_output = source_obj.get_output()
    assert isinstance(f_output, Field)
    assert len(f_output.data) / 44100.0 == pytest.approx(3.0)

    # Compute the power spectral density over the output signal.
    psd = PowerSpectralDensity(
        input_signal=f_output,
        fft_size=8192,
        window_type="HANN",
        window_length=8192,
        overlap=0.75,
    )
    psd.process()
    psd_squared, psd_freq = psd.get_PSD_squared_linear_as_nparray()
    delat_f = psd_freq[1] - psd_freq[0]

    # Check the sound power level in the octave bands centered at 500, 1000 and 2000 Hz.
    # Due to the non-deterministic nature of the produced signal, tolerance is set to 1 dB.
    psd_squared_band = psd_squared[
        (psd_freq >= 500 * 2 ** (-1 / 2)) & (psd_freq < 500 * 2 ** (1 / 2))
    ]
    level = 10 * np.log10(psd_squared_band.sum() * delat_f / REF_ACOUSTIC_POWER)
    assert level == pytest.approx(EXP_LEVEL_OCTAVE_BAND_500_INVCON, abs=1.0)

    psd_squared_band = psd_squared[
        (psd_freq >= 1000 * 2 ** (-1 / 2)) & (psd_freq < 1000 * 2 ** (1 / 2))
    ]
    level = 10 * np.log10(psd_squared_band.sum() * delat_f / REF_ACOUSTIC_POWER)
    assert level == pytest.approx(EXP_LEVEL_OCTAVE_BAND_1000_INVCON, abs=1.0)

    psd_squared_band = psd_squared[
        (psd_freq >= 2000 * 2 ** (-1 / 2)) & (psd_freq < 2000 * 2 ** (1 / 2))
    ]
    level = 10 * np.log10(psd_squared_band.sum() * delat_f / REF_ACOUSTIC_POWER)
    assert level == pytest.approx(EXP_LEVEL_OCTAVE_BAND_2000_INVCON, abs=1.0)


def test_source_harmonics_two_parameters_get_output_unprocessed():
    """Test SourceHarmonicsTwoParameters get_output method's exception."""
    source_obj = SourceHarmonicsTwoParameters()
    with pytest.warns(
        PyAnsysSoundWarning,
        match=(
            "Output is not processed yet. Use the "
            "``SourceHarmonicsTwoParameters.process\\(\\)`` method."
        ),
    ):
        f_output = source_obj.get_output()
    assert f_output is None


def test_source_harmonics_two_parameters_get_output_as_nparray():
    """Test SourceHarmonicsTwoParameters get_output_as_nparray method."""
    # Create a field to use in a SourceControlTime object.
    f_source_control = fields_factory.create_scalar_field(
        num_entities=1, location=locations.time_freq
    )
    f_source_control.append([500, 1250, 2000, 3000], 1)
    support = TimeFreqSupport()
    f_time = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
    f_time.append([0, 1, 2, 3], 1)
    support.time_frequencies = f_time
    f_source_control.time_freq_support = support

    # Create a first SourceControlTime object.
    source_control_rpm = SourceControlTime()
    source_control_rpm.control = f_source_control

    # Create another field to use in a SourceControlTime object.
    f_source_control = fields_factory.create_scalar_field(
        num_entities=1, location=locations.time_freq
    )
    f_source_control.append([9.5, 9, 1, 0.5], 1)
    support = TimeFreqSupport()
    f_time = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
    f_time.append([0, 1, 2, 3], 1)
    support.time_frequencies = f_time
    f_source_control.time_freq_support = support

    # Create a second SourceControlTime object.
    source_control2 = SourceControlTime()
    source_control2.control = f_source_control

    # Create a SourceHarmonicsTwoParameters object test source file with less and created source
    # controls.
    source_obj = SourceHarmonicsTwoParameters(
        file=pytest.data_path_sound_composer_harmonics_source_2p_in_container,
        source_control_rpm=source_control_rpm,
        source_control2=source_control2,
    )

    source_obj.process(sampling_frequency=44100.0)
    output_nparray = source_obj.get_output_as_nparray()
    assert isinstance(output_nparray, np.ndarray)
    assert len(output_nparray) / 44100.0 == pytest.approx(3.0)


def test_source_harmonics_two_parameters_get_output_as_nparray_unprocessed():
    """Test SourceHarmonicsTwoParameters get_output_as_nparray method's exception."""
    source_obj = SourceHarmonicsTwoParameters()
    with pytest.warns(
        PyAnsysSoundWarning,
        match=(
            "Output is not processed yet. Use the ``SourceHarmonicsTwoParameters.process\\(\\)`` "
            "method."
        ),
    ):
        output_nparray = source_obj.get_output_as_nparray()
    assert len(output_nparray) == 0


@patch("matplotlib.pyplot.show")
def test_source_harmonics_two_parameters_plot(mock_show):
    """Test SourceHarmonicsTwoParameters plot method."""
    # Create a field to use in a SourceControlTime object.
    f_source_control = fields_factory.create_scalar_field(
        num_entities=1, location=locations.time_freq
    )
    f_source_control.append([500, 1250, 2000, 3000], 1)
    support = TimeFreqSupport()
    f_time = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
    f_time.append([0, 1, 2, 3], 1)
    support.time_frequencies = f_time
    f_source_control.time_freq_support = support

    # Create a first SourceControlTime object.
    source_control_rpm = SourceControlTime()
    source_control_rpm.control = f_source_control

    # Create another field to use in a SourceControlTime object.
    f_source_control = fields_factory.create_scalar_field(
        num_entities=1, location=locations.time_freq
    )
    f_source_control.append([9.5, 9, 1, 0.5], 1)
    support = TimeFreqSupport()
    f_time = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
    f_time.append([0, 1, 2, 3], 1)
    support.time_frequencies = f_time
    f_source_control.time_freq_support = support

    # Create a second SourceControlTime object.
    source_control2 = SourceControlTime()
    source_control2.control = f_source_control

    # Create a SourceHarmonicsTwoParameters object test source file with less and created source
    # controls.
    source_obj = SourceHarmonicsTwoParameters(
        file=pytest.data_path_sound_composer_harmonics_source_2p_in_container,
        source_control_rpm=source_control_rpm,
        source_control2=source_control2,
    )

    source_obj.process()
    source_obj.plot()


def test_source_harmonics_two_parameters_plot_exceptions():
    """Test SourceHarmonicsTwoParameters plot method's exception."""
    source_obj = SourceHarmonicsTwoParameters()
    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "Output is not processed yet. Use the 'SourceHarmonicsTwoParameters.process\\(\\)' "
            "method."
        ),
    ):
        source_obj.plot()


@patch("matplotlib.pyplot.show")
def test_source_harmonics_two_parameters_plot_control(mock_show):
    """Test SourceHarmonicsTwoParameters plot_control method."""
    # Create a field to use in a SourceControlTime object.
    f_source_control = fields_factory.create_scalar_field(
        num_entities=1, location=locations.time_freq
    )
    f_source_control.append([500, 1250, 2000, 3000], 1)
    support = TimeFreqSupport()
    f_time = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
    f_time.append([0, 1, 2, 3], 1)
    support.time_frequencies = f_time
    f_source_control.time_freq_support = support

    # Create a first SourceControlTime object.
    source_control_rpm = SourceControlTime()
    source_control_rpm.control = f_source_control

    # Create another field to use in a SourceControlTime object.
    f_source_control = fields_factory.create_scalar_field(
        num_entities=1, location=locations.time_freq
    )
    f_source_control.append([9.5, 9, 1, 0.5], 1)
    support = TimeFreqSupport()
    f_time = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
    f_time.append([0, 1, 2, 3], 1)
    support.time_frequencies = f_time
    f_source_control.time_freq_support = support

    # Create a second SourceControlTime object.
    source_control2 = SourceControlTime()
    source_control2.control = f_source_control

    # Create a SourceHarmonicsTwoParameters object with created source controls.
    source_obj = SourceHarmonicsTwoParameters(
        source_control_rpm=source_control_rpm,
        source_control2=source_control2,
    )

    source_obj.plot_control()


def test_source_harmonics_two_parameters_plot_control_exceptions():
    """Test SourceHarmonicsTwoParameters plot_control method's exception."""
    source_obj = SourceHarmonicsTwoParameters()
    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "At least one source control for harmonics source with two parameters is not set. "
            "Use ``SourceHarmonicsTwoParameters.source_control_rpm`` and/or "
            "``SourceHarmonicsTwoParameters.source_control2``."
        ),
    ):
        source_obj.plot_control()


def test_source_harmonics_two_parameters___extract_harmonics_two_parameters_info():
    """Test SourceHarmonicsTwoParameters __extract_harmonics_two_parameters_info method."""
    source = SourceHarmonicsTwoParameters()
    assert source._SourceHarmonicsTwoParameters__extract_harmonics_two_parameters_info() == (
        [],
        "",
        (),
        "",
        "",
        (),
    )

    source.load_source_harmonics_two_parameters(
        pytest.data_path_sound_composer_harmonics_source_2p_in_container
    )
    assert source._SourceHarmonicsTwoParameters__extract_harmonics_two_parameters_info() == (
        [12.0, 24.0, 36.0, 48.0],
        "RPM",
        (500.0, 3000.0),
        "charge",
        "%",
        (0.0, 10.0),
    )
