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
from ansys.dpf.core import (Field, FieldsContainer, GenericDataContainer,
                            Operator, TimeFreqSupport,
                            fields_container_factory, fields_factory,
                            locations)

from ansys.sound.core._pyansys_sound import (PyAnsysSoundException,
                                             PyAnsysSoundWarning)
from ansys.sound.core.sound_composer import SourceControlTime, SourceHarmonics
from ansys.sound.core.spectral_processing import PowerSpectralDensity

REF_ACOUSTIC_POWER = 4e-10

EXP_LEVEL_OCTAVE_BAND = [58.2, 74.5280270133186, 60.3]
EXP_ORDERS = [12.0, 36.0, 60.0]
EXP_RPMS = [
    500.0,
    570.0,
    600.0,
]

if pytest.SERVERS_VERSION_GREATER_THAN_OR_EQUAL_TO_11_0:
    # Third-party update (IPP) in DPF Sound 2026 R1
    EXP_ORDER_LEVEL03_REF = 1.5208672266453505e-05
    EXP_ORDER_LEVEL03_PA = 1.5208672266453505e-05
else:  # DPF Sound <= 2025 R2
    EXP_ORDER_LEVEL03_REF = 3.041734453290701e-05
    EXP_ORDER_LEVEL03_PA = 3.041734453290701e-05

EXP_ORDER_LEVEL03_XML = 5.632353957971172e-19
EXP_STR_NOT_SET = "Harmonics source: Not set\nSource control: Not set/valid"
EXP_STR_ALL_SET = (
    "Harmonics source: ''\n"
    "\tNumber of orders: 5\n"
    "\t\t[12. 24. 36. 48. 60.]\n"
    "\tControl parameter: RPM, 500.0 - 3500.0 rpm\n"
    "\t\t[500. 510. 520. 530. 540. ... 3460. 3470. 3480. 3490. 3500.]"
    "\nSource control: \n"
    "\tMin: 750.0 RPM\n"
    "\tMax: 3500.0 RPM\n"
    "\tDuration: 3.0 s"
)
EXP_STR_ALL_SET_10_40_VALUES = (
    "Harmonics source: ''\n"
    "\tNumber of orders: 40\n"
    "\t\t[1. 2. 3. 4. 5. ... 36. 37. 38. 39. 40.]\n"
    "\tControl parameter: RPM, 500.0 - 590.0 rpm\n"
    "\t\t[500. 510. 520. 530. 540. 550. 560. 570. 580. 590.]"
    "\nSource control: \n"
    "\tMin: 750.0 RPM\n"
    "\tMax: 3500.0 RPM\n"
    "\tDuration: 3.0 s"
)


def test_source_harmonics_instantiation_no_arg():
    """Test SourceHarmonics instantiation without arguments."""
    source_harmonics_obj = SourceHarmonics()
    assert isinstance(source_harmonics_obj, SourceHarmonics)
    assert source_harmonics_obj.source_harmonics is None


def test_source_harmonics_instantiation_file_arg():
    """Test SourceHarmonics instantiation with file argument."""
    source_harmonics_obj = SourceHarmonics(
        file=pytest.data_path_sound_composer_harmonics_source_in_container
    )
    assert isinstance(source_harmonics_obj, SourceHarmonics)
    assert source_harmonics_obj.source_harmonics is not None


def test_source_harmonics___str___not_set():
    """Test SourceHarmonics __str__ method when nothing is set."""
    source_harmonics_obj = SourceHarmonics()
    assert str(source_harmonics_obj) == EXP_STR_NOT_SET


def test_source_harmonics___str___all_set():
    """Test SourceHarmonics __str__ method when all data are set."""
    # Create a field to use in a SourceControlTime object.
    f_source_control = fields_factory.create_scalar_field(
        num_entities=1, location=locations.time_freq
    )
    f_source_control.append([750, 1250, 3000, 3500], 1)
    f_source_control.unit = "RPM"
    support = TimeFreqSupport()
    f_time = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
    f_time.append([0, 1, 2, 3], 1)
    f_time.unit = "s"
    support.time_frequencies = f_time
    f_source_control.time_freq_support = support

    # Create a SourceControlTime object.
    source_control = SourceControlTime()
    source_control.control = f_source_control

    # Create a SourceHarmonics object.
    source_harmonics_obj = SourceHarmonics(
        pytest.data_path_sound_composer_harmonics_source_in_container,
        source_control,
    )
    assert str(source_harmonics_obj) == EXP_STR_ALL_SET

    # Replace the source file with another that has 10 rpm values and 40 orders.
    source_harmonics_obj.load_source_harmonics(
        pytest.data_path_sound_composer_harmonics_source_10rpm_40orders_in_container
    )
    assert str(source_harmonics_obj) == EXP_STR_ALL_SET_10_40_VALUES


def test_source_harmonics_properties():
    """Test SourceHarmonics properties."""
    source_harmonics_obj = SourceHarmonics()

    # Test source_control property.
    source_harmonics_obj.source_control = SourceControlTime()
    assert isinstance(source_harmonics_obj.source_control, SourceControlTime)

    # Test source_harmonics property.
    # Create a second object and then reuse its source_harmonics property.
    source_harmonics_obj_tmp = SourceHarmonics()
    source_harmonics_obj_tmp.load_source_harmonics(
        pytest.data_path_sound_composer_harmonics_source_in_container
    )
    harmonics_fieldscontainer = source_harmonics_obj_tmp.source_harmonics
    source_harmonics_obj.source_harmonics = harmonics_fieldscontainer
    assert isinstance(source_harmonics_obj.source_harmonics, FieldsContainer)


def test_source_harmonics_properties_exceptions():
    """Test SourceHarmonics properties' exceptions."""
    source_harmonics_obj = SourceHarmonics()

    # Test source_control setter exception (str instead of SourceControlTime).
    with pytest.raises(
        PyAnsysSoundException,
        match="Specified source control object must be of type SourceControlTime.",
    ):
        source_harmonics_obj.source_control = "InvalidType"

    # Test source_harmonics setter exception 1 (str instead of FieldsContainer).
    with pytest.raises(
        PyAnsysSoundException,
        match="Specified harmonics source must be provided as a DPF fields container.",
    ):
        source_harmonics_obj.source_harmonics = "InvalidType"

    # Test source_harmonics setter exception 2 (less than 1 order level).
    fc_source_harmonics = FieldsContainer()
    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "Specified harmonics source must contain at least one order level \\(the provided DPF "
            "fields container must contain at least one field with at least one data point\\)."
        ),
    ):
        source_harmonics_obj.source_harmonics = fc_source_harmonics

    # Test source_harmonics setter exception 3 (within-field order level number mismatch).
    field = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
    field.append([1.0, 2.0, 3.0, 4.0, 5.0], 1)
    support = TimeFreqSupport()
    f_time = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
    f_time.append([1.0, 2.0], 1)
    support.time_frequencies = f_time
    field.time_freq_support = support
    fc_source_harmonics = fields_container_factory.over_time_freq_fields_container([field])
    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "Each set of order levels in the specified harmonics source must contain as many "
            "level values as the number of orders \\(in the provided DPF fields container, each "
            "field must contain the same number of data points and support values\\)."
        ),
    ):
        source_harmonics_obj.source_harmonics = fc_source_harmonics

    # Test source_harmonics setter exception 4 (between-field order level number mismatch).
    field2 = field.deep_copy()
    field.data = [1.0, 2.0]
    field2.data = [1.0, 2.0, 3.0, 4.0, 5.0]
    field2.time_freq_support.time_frequencies.data = [1.0, 2.0, 3.0, 4.0, 5.0]
    fc_source_harmonics = fields_container_factory.over_time_freq_fields_container([field, field2])
    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "Each set of order levels in the specified harmonics source must contain the same "
            "number of level values \\(in the provided DPF fields container, each field must "
            "contain the same number of data points\\)."
        ),
    ):
        source_harmonics_obj.source_harmonics = fc_source_harmonics

    # Test source_harmonics setter exception 5 (empty harmonics source's control data).
    # For this, we use a valid dataset, and then remove the control data.
    source_harmonics_obj = SourceHarmonics()
    source_harmonics_obj.load_source_harmonics(
        pytest.data_path_sound_composer_harmonics_source_in_container
    )
    support_data = source_harmonics_obj.source_harmonics.get_support("control_parameter_1")
    support_properties = support_data.available_field_supported_properties()
    support_values = support_data.field_support_by_property(support_properties[0])
    support_values.data = []
    fc_source_harmonics = source_harmonics_obj.source_harmonics
    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "The specified harmonics source must contain as many sets of order levels as the "
            "number of values in the associated control parameter \\(in the provided DPF fields "
            "container, the number of fields should be the same as the number of values in the "
            "fields container support\\)."
        ),
    ):
        source_harmonics_obj.source_harmonics = fc_source_harmonics


def test_source_harmonics_is_source_control_valid():
    """Test SourceHarmonics is_source_control_valid method."""
    source_harmonics_obj = SourceHarmonics()

    # Test is_source_control_valid method (attribute not set).
    assert source_harmonics_obj.is_source_control_valid() is False

    # Test is_source_control_valid method (attribute set, but attribute's field not set).
    source_control_obj = SourceControlTime()
    source_harmonics_obj.source_control = source_control_obj
    assert source_harmonics_obj.is_source_control_valid() is False

    # Test is_source_control_valid method (attribute and attribute's field set, but empty).
    f_source_control = fields_factory.create_scalar_field(
        num_entities=1, location=locations.time_freq
    )
    f_source_control.append([1.0, 2.0, 3.0, 4.0, 5.0], 1)
    source_harmonics_obj.source_control.control = f_source_control
    # Control data must be emptied out after assignment, otherwise it triggers an exception from
    # SourceControlTime's setter.
    source_harmonics_obj.source_control.control.data = []
    assert source_harmonics_obj.is_source_control_valid() is False

    # Test is_source_control_valid method (all set).
    f_source_control.append([1.0, 2.0, 3.0, 4.0, 5.0], 1)
    source_harmonics_obj.source_control.control = f_source_control
    assert source_harmonics_obj.is_source_control_valid() is True


def test_source_harmonics_load_source_harmonics():
    """Test SourceHarmonics load_source_harmonics method."""
    source_harmonics_obj = SourceHarmonics()

    # Load reference source file (dBSPL).
    source_harmonics_obj.load_source_harmonics(
        pytest.data_path_sound_composer_harmonics_source_in_container
    )
    assert isinstance(source_harmonics_obj.source_harmonics, FieldsContainer)
    assert source_harmonics_obj.source_harmonics[0].data[3] == pytest.approx(EXP_ORDER_LEVEL03_REF)

    # Load source file in Pa.
    source_harmonics_obj.load_source_harmonics(
        pytest.data_path_sound_composer_harmonics_source_Pa_in_container
    )
    assert isinstance(source_harmonics_obj.source_harmonics, FieldsContainer)
    assert source_harmonics_obj.source_harmonics[0].data[3] == pytest.approx(EXP_ORDER_LEVEL03_PA)

    # Load wrong-header file (DPF error).
    with pytest.raises(Exception):
        source_harmonics_obj.load_source_harmonics(
            pytest.data_path_sound_composer_harmonics_source_wrong_type_in_container
        )

    # Load xml file.
    source_harmonics_obj.load_source_harmonics(
        pytest.data_path_sound_composer_harmonics_source_xml_in_container
    )
    assert isinstance(source_harmonics_obj.source_harmonics, FieldsContainer)
    assert source_harmonics_obj.source_harmonics[0].data[3] == pytest.approx(EXP_ORDER_LEVEL03_XML)


def test_source_harmonics_set_from_generic_data_containers():
    """Test SourceHarmonics set_from_generic_data_containers method."""
    op = Operator("sound_composer_load_source_harmonics")
    op.connect(0, pytest.data_path_sound_composer_harmonics_source_in_container)
    op.run()
    fc_data: FieldsContainer = op.get_output(0, "fields_container")

    source_data = GenericDataContainer()
    source_data.set_property("sound_composer_source", fc_data)

    f_source_control = fields_factory.create_scalar_field(
        num_entities=1, location=locations.time_freq
    )
    f_source_control.append([1.0, 2.0, 3.0, 4.0, 5.0], 1)
    source_control_data = GenericDataContainer()
    source_control_data.set_property(
        "sound_composer_source_control_one_parameter", f_source_control
    )
    source_control_data.set_property(
        "sound_composer_source_control_one_parameter_displayed_string", "test"
    )

    source_harmo_obj = SourceHarmonics()
    source_harmo_obj.set_from_generic_data_containers(source_data, source_control_data)
    assert isinstance(source_harmo_obj.source_harmonics, FieldsContainer)
    assert len(source_harmo_obj.source_harmonics) == len(fc_data)
    assert isinstance(source_harmo_obj.source_control, SourceControlTime)
    assert len(source_harmo_obj.source_control.control.data) == 5
    assert source_harmo_obj.source_control.description == "test"


def test_source_harmonics_get_as_generic_data_containers():
    """Test SourceHarmonics get_as_generic_data_containers method."""
    # Source control undefined => warning.
    source_harmo_obj = SourceHarmonics(
        file=pytest.data_path_sound_composer_harmonics_source_in_container
    )
    with pytest.warns(
        PyAnsysSoundWarning,
        match=(
            "Cannot create source control generic data container, either because there is no "
            "source control data, or because the source control data is invalid."
        ),
    ):
        _, source_control_data = source_harmo_obj.get_as_generic_data_containers()
    assert source_control_data is None

    # Source data undefined => warning.
    source_harmo_obj.source_harmonics = None
    f_source_control = fields_factory.create_scalar_field(
        num_entities=1, location=locations.time_freq
    )
    f_source_control.append([1.0, 2.0, 3.0, 4.0, 5.0], 1)
    source_control_obj = SourceControlTime()
    source_control_obj.control = f_source_control
    source_harmo_obj.source_control = source_control_obj
    source_harmo_obj.source_control.description = "test"
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Cannot create source generic data container because there is no source data.",
    ):
        source_data, _ = source_harmo_obj.get_as_generic_data_containers()
    assert source_data is None

    # Both source and source control are defined.
    source_harmo_obj.load_source_harmonics(
        pytest.data_path_sound_composer_harmonics_source_in_container,
    )
    source_data, source_control_data = source_harmo_obj.get_as_generic_data_containers()

    assert isinstance(source_data, GenericDataContainer)
    assert isinstance(source_data.get_property("sound_composer_source"), FieldsContainer)
    assert isinstance(source_control_data, GenericDataContainer)
    assert isinstance(
        source_control_data.get_property("sound_composer_source_control_one_parameter"), Field
    )
    assert (
        source_control_data.get_property(
            "sound_composer_source_control_one_parameter_displayed_string"
        )
        == "test"
    )


def test_source_harmonics_process():
    """Test SourceHarmonics process method."""
    # Create a field to use in a SourceControlTime object.
    f_source_control = fields_factory.create_scalar_field(
        num_entities=1, location=locations.time_freq
    )
    f_source_control.append([500, 2000, 3000, 3500], 1)
    support = TimeFreqSupport()
    f_time = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
    f_time.append([0, 1, 2, 3], 1)
    support.time_frequencies = f_time
    f_source_control.time_freq_support = support

    # Create a SourceControlTime object.
    source_control_obj = SourceControlTime()
    source_control_obj.control = f_source_control

    source_harmonics_obj = SourceHarmonics(
        pytest.data_path_sound_composer_harmonics_source_in_container,
        source_control_obj,
    )
    source_harmonics_obj.process()
    assert source_harmonics_obj._output is not None


def test_source_harmonics_process_exceptions():
    """Test SourceHarmonics process method exceptions."""
    # Test process method exception1 (missing control).
    source_harmonics_obj = SourceHarmonics(
        pytest.data_path_sound_composer_harmonics_source_in_container
    )
    with pytest.raises(
        PyAnsysSoundException,
        match="Harmonics source control is not set/valid. Use ``SourceHarmonics.source_control``.",
    ):
        source_harmonics_obj.process()

    # Test process method exception2 (missing harmonics source data).
    source_harmonics_obj.source_harmonics = None
    f_source_control = fields_factory.create_scalar_field(
        num_entities=1, location=locations.time_freq
    )
    f_source_control.append([500, 2000, 3000, 3500], 1)
    source_control_obj = SourceControlTime()
    source_control_obj.control = f_source_control
    source_harmonics_obj.source_control = source_control_obj
    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "Harmonics source data is not set. Use ``SourceHarmonics.source_harmonics`` "
            "or method ``SourceHarmonics.load_source_harmonics\\(\\)``."
        ),
    ):
        source_harmonics_obj.process()

    # Test process method exception3 (invalid sampling frequency value).
    source_harmonics_obj.load_source_harmonics(
        pytest.data_path_sound_composer_harmonics_source_in_container
    )
    with pytest.raises(
        PyAnsysSoundException, match="Sampling frequency must be strictly positive."
    ):
        source_harmonics_obj.process(sampling_frequency=0.0)


def test_source_harmonics_get_output():
    """Test SourceHarmonics get_output method."""
    # Create a field to use in a SourceControlTime object.
    f_source_control = fields_factory.create_scalar_field(
        num_entities=1, location=locations.time_freq
    )
    f_source_control.append([500, 2000, 3000, 3500], 1)
    support = TimeFreqSupport()
    f_time = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
    f_time.append([0, 1, 2, 3], 1)
    support.time_frequencies = f_time
    f_source_control.time_freq_support = support

    # Create a SourceControlTime object.
    source_control_obj = SourceControlTime()
    source_control_obj.control = f_source_control

    source_harmonics_obj = SourceHarmonics(
        pytest.data_path_sound_composer_harmonics_source_in_container,
        source_control_obj,
    )
    source_harmonics_obj.process(sampling_frequency=44100.0)
    f_output = source_harmonics_obj.get_output()
    assert isinstance(f_output, Field)
    assert len(f_output.data) / 44100.0 == pytest.approx(3.0, abs=1e-2)

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

    # Check the sound power level in the octave bands centered at 250, 1000 and 4000 Hz.
    # Due to the non-deterministic nature of the produced signal, tolerance is set to 1 dB.
    psd_squared_band = psd_squared[
        (psd_freq >= 250 * 2 ** (-1 / 2)) & (psd_freq < 250 * 2 ** (1 / 2))
    ]
    level = 10 * np.log10(psd_squared_band.sum() * delat_f / REF_ACOUSTIC_POWER)
    assert level == pytest.approx(EXP_LEVEL_OCTAVE_BAND[0], abs=1.0)

    psd_squared_band = psd_squared[
        (psd_freq >= 1000 * 2 ** (-1 / 2)) & (psd_freq < 1000 * 2 ** (1 / 2))
    ]
    level = 10 * np.log10(psd_squared_band.sum() * delat_f / REF_ACOUSTIC_POWER)
    assert level == pytest.approx(EXP_LEVEL_OCTAVE_BAND[1], abs=1.0)

    psd_squared_band = psd_squared[
        (psd_freq >= 4000 * 2 ** (-1 / 2)) & (psd_freq < 4000 * 2 ** (1 / 2))
    ]
    level = 10 * np.log10(psd_squared_band.sum() * delat_f / REF_ACOUSTIC_POWER)
    assert level == pytest.approx(EXP_LEVEL_OCTAVE_BAND[2], abs=1.0)


def test_source_harmonics_get_output_unprocessed():
    """Test SourceHarmonics get_output method's exception."""
    source_harmonics_obj = SourceHarmonics()
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the ``SourceHarmonics.process\\(\\)`` method.",
    ):
        f_output = source_harmonics_obj.get_output()
    assert f_output is None


def test_source_harmonics_get_output_as_nparray():
    """Test SourceHarmonics get_output_as_nparray method."""
    # Create a field to use in a SourceControlTime object.
    f_source_control = fields_factory.create_scalar_field(
        num_entities=1, location=locations.time_freq
    )
    f_source_control.append([500, 2000, 3000, 3500], 1)
    support = TimeFreqSupport()
    f_time = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
    f_time.append([0, 1, 2, 3], 1)
    support.time_frequencies = f_time
    f_source_control.time_freq_support = support

    # Create a SourceControlTime object.
    source_control_obj = SourceControlTime()
    source_control_obj.control = f_source_control

    source_harmonics_obj = SourceHarmonics(
        pytest.data_path_sound_composer_harmonics_source_in_container,
        source_control_obj,
    )
    source_harmonics_obj.process(sampling_frequency=44100.0)
    output_nparray = source_harmonics_obj.get_output_as_nparray()
    assert isinstance(output_nparray, np.ndarray)
    assert len(output_nparray) / 44100.0 == pytest.approx(3.0, abs=1e-2)


def test_source_harmonics_get_output_as_nparray_unprocessed():
    """Test SourceHarmonics get_output_as_nparray method's exception."""
    source_harmonics_obj = SourceHarmonics()
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the ``SourceHarmonics.process\\(\\)`` method.",
    ):
        output_nparray = source_harmonics_obj.get_output_as_nparray()
    assert len(output_nparray) == 0


@patch("matplotlib.pyplot.show")
def test_source_harmonics_plot(mock_show):
    """Test SourceHarmonics plot method."""
    # Create a field to use in a SourceControlTime object.
    f_source_control = fields_factory.create_scalar_field(
        num_entities=1, location=locations.time_freq
    )
    f_source_control.append([500, 2000, 3000, 3500], 1)
    support = TimeFreqSupport()
    f_time = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
    f_time.append([0, 1, 2, 3], 1)
    support.time_frequencies = f_time
    f_source_control.time_freq_support = support

    # Create a SourceControlTime object.
    source_control_obj = SourceControlTime()
    source_control_obj.control = f_source_control

    source_harmonics_obj = SourceHarmonics(
        pytest.data_path_sound_composer_harmonics_source_in_container,
        source_control_obj,
    )
    source_harmonics_obj.process()
    source_harmonics_obj.plot()


def test_source_harmonics_plot_exceptions():
    """Test SourceHarmonics plot method's exception."""
    source_harmonics_obj = SourceHarmonics()
    with pytest.raises(
        PyAnsysSoundException,
        match="Output is not processed yet. Use the 'SourceHarmonics.process\\(\\)' method.",
    ):
        source_harmonics_obj.plot()


@patch("matplotlib.pyplot.show")
def test_source_harmonics_plot_control(mock_show):
    """Test SourceHarmonics plot_control method."""
    # Create a field to use in a SourceControlTime object.
    f_source_control = fields_factory.create_scalar_field(
        num_entities=1, location=locations.time_freq
    )
    f_source_control.append([500, 2000, 3000, 3500], 1)
    support = TimeFreqSupport()
    f_time = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
    f_time.append([0, 1, 2, 3], 1)
    support.time_frequencies = f_time
    f_source_control.time_freq_support = support

    # Create a SourceControlTime object.
    source_control = SourceControlTime()
    source_control.control = f_source_control

    # Create a SourceHarmonics object with the created source control.
    source_obj = SourceHarmonics(
        source_control=source_control,
    )

    source_obj.plot_control()


def test_source_harmonics_plot_control_exceptions():
    """Test SourceHarmonics plot_control method's exception."""
    source_obj = SourceHarmonics()
    with pytest.raises(
        PyAnsysSoundException,
        match="Harmonics source control is not set/valid. Use ``SourceHarmonics.source_control``.",
    ):
        source_obj.plot_control()


def test_source_harmonics___extract_harmonics_info():
    """Test SourceHarmonics __extract_harmonics_info method."""
    source_harmonics_obj = SourceHarmonics()
    assert source_harmonics_obj._SourceHarmonics__extract_harmonics_info() == ([], "", [])

    source_harmonics_obj.load_source_harmonics(
        pytest.data_path_sound_composer_harmonics_source_in_container
    )
    orders, name, rpms = source_harmonics_obj._SourceHarmonics__extract_harmonics_info()
    assert orders[0] == pytest.approx(EXP_ORDERS[0])
    assert orders[2] == pytest.approx(EXP_ORDERS[1])
    assert orders[4] == pytest.approx(EXP_ORDERS[2])
    assert name == "RPM"
    assert rpms[0] == pytest.approx(EXP_RPMS[0])
    assert rpms[7] == pytest.approx(EXP_RPMS[1])
    assert rpms[10] == pytest.approx(EXP_RPMS[2])
