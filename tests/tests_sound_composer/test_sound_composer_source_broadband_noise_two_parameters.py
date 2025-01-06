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
    TimeFreqSupport,
    fields_container_factory,
    fields_factory,
    locations,
)
import numpy as np
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ansys.sound.core.sound_composer import SourceBroadbandNoiseTwoParameters, SourceControlTime
from ansys.sound.core.spectral_processing import PowerSpectralDensity

REF_ACOUSTIC_POWER = 4e-10

EXP_LEVEL_OCTAVE_BAND_250 = 123.0
EXP_LEVEL_OCTAVE_BAND_1000 = 132.0
EXP_LEVEL_OCTAVE_BAND_4000 = 140.0
EXP_SPECTRUM_DATA03 = 3.000000238418579
EXP_STR_NOT_SET = (
    "Broadband noise source with two parameters: Not set\n"
    "Source control:\n"
    "\tControl 1: Not set\n"
    "\tControl 2: Not set"
)
EXP_STR_ALL_SET = (
    "Broadband noise source with two parameters: ''\n"
    "\tSpectrum type: Not available\n"
    "\tSpectrum count: 8\n"
    "\tControl parameter 1: temperature, 2.5-40.0 celsius\n"
    "\tControl parameter 2: charge, 0.0-10.0 %\n"
    "Source control:\n"
    "\tControl 1: \n"
    "\t\tMin: 3.0\n"
    "\t\tMax: 38.0\n"
    "\t\tDuration: 3.0 s\n"
    "\tControl 2: \n"
    "\t\tMin: 3.0\n"
    "\t\tMax: 38.0\n"
    "\t\tDuration: 3.0 s"
)


def test_source_broadband_noise_two_parameters_instantiation_no_arg():
    """Test SourceBroadbandNoiseTwoParameters instantiation without arguments."""
    source_bbn_two_parameters_obj = SourceBroadbandNoiseTwoParameters()
    assert isinstance(source_bbn_two_parameters_obj, SourceBroadbandNoiseTwoParameters)
    assert source_bbn_two_parameters_obj.source_bbn_two_parameters is None


def test_source_broadband_noise_two_parameters_instantiation_file_arg():
    """Test SourceBroadbandNoiseTwoParameters instantiation with file argument."""
    source_bbn_two_parameters_obj = SourceBroadbandNoiseTwoParameters(
        file=pytest.data_path_sound_composer_bbn_source_2p_in_container
    )
    assert isinstance(source_bbn_two_parameters_obj, SourceBroadbandNoiseTwoParameters)
    assert source_bbn_two_parameters_obj.source_bbn_two_parameters is not None


def test_source_broadband_noise_two_parameters___str___not_set():
    """Test SourceBroadbandNoiseTwoParameters __str__ method when nothing is set."""
    source_bbn_two_parameters_obj = SourceBroadbandNoiseTwoParameters()
    assert str(source_bbn_two_parameters_obj) == EXP_STR_NOT_SET


def test_source_broadband_noise_two_parameters___str___all_set():
    """Test SourceBroadbandNoiseTwoParameters __str__ method when all data are set."""
    # Create a field to use in a SourceControlTime object.
    f_source_control = fields_factory.create_scalar_field(
        num_entities=1, location=locations.time_freq
    )
    f_source_control.append([3, 4, 35, 38], 1)
    support = TimeFreqSupport()
    f_time = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
    f_time.append([0, 1, 2, 3], 1)
    support.time_frequencies = f_time
    f_source_control.time_freq_support = support

    # Create a first SourceControlTime object.
    source_control1 = SourceControlTime()
    source_control1.control = f_source_control

    # Create a second SourceControlTime object.
    source_control2 = SourceControlTime()
    source_control2.control = f_source_control

    # Create a SourceBroadbandNoiseTwoParameters object test source file with less and created
    # source controls.
    source_bbn_two_parameters_obj = SourceBroadbandNoiseTwoParameters(
        file=pytest.data_path_sound_composer_bbn_source_2p_in_container,
        source_control1=source_control1,
        source_control2=source_control2,
    )

    assert str(source_bbn_two_parameters_obj) == EXP_STR_ALL_SET


def test_source_broadband_noise_two_parameters_properties():
    """Test SourceBroadbandNoiseTwoParameters properties."""
    source_bbn_two_parameters_obj = SourceBroadbandNoiseTwoParameters()

    # Test source_control1 property.
    source_bbn_two_parameters_obj.source_control1 = SourceControlTime()
    assert isinstance(source_bbn_two_parameters_obj.source_control1, SourceControlTime)

    # Test source_control2 property.
    source_bbn_two_parameters_obj.source_control2 = SourceControlTime()
    assert isinstance(source_bbn_two_parameters_obj.source_control2, SourceControlTime)

    # Test source_bbn_two_parameters property.
    # Create a second object and then reuse its source_bbn_two_parameters property.
    source_bbn_two_parameters_obj_tmp = SourceBroadbandNoiseTwoParameters()
    source_bbn_two_parameters_obj_tmp.load_source_bbn_two_parameters(
        pytest.data_path_sound_composer_bbn_source_2p_in_container
    )
    fc_source = source_bbn_two_parameters_obj_tmp.source_bbn_two_parameters
    source_bbn_two_parameters_obj.source_bbn_two_parameters = fc_source
    assert isinstance(source_bbn_two_parameters_obj.source_bbn_two_parameters, FieldsContainer)


def test_source_broadband_noise_two_parameters_properties_exceptions():
    """Test SourceBroadbandNoiseTwoParameters properties' exceptions."""
    source_bbn_two_parameters_obj = SourceBroadbandNoiseTwoParameters()

    # Test source_control1 setter exception (str instead of SourceControlTime).
    with pytest.raises(
        PyAnsysSoundException,
        match="Specified first source control object must be of type ``SourceControlTime``.",
    ):
        source_bbn_two_parameters_obj.source_control1 = "InvalidType"

    # Test source_control1 setter exception (str instead of SourceControlTime).
    with pytest.raises(
        PyAnsysSoundException,
        match="Specified second source control object must be of type ``SourceControlTime``.",
    ):
        source_bbn_two_parameters_obj.source_control2 = "InvalidType"

    # Test source_bbn_two_parameters setter exception 1 (str instead a Field).
    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "Specified broadband noise source with two parameters must be provided as a DPF "
            "fields container."
        ),
    ):
        source_bbn_two_parameters_obj.source_bbn_two_parameters = "InvalidType"

    # Test source_bbn_two_parameters setter exception 2 (less than 1 spectrum).
    fc_source_bbn = FieldsContainer()
    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "Specified broadband noise source with two parameters must contain at least one "
            "spectrum."
        ),
    ):
        source_bbn_two_parameters_obj.source_bbn_two_parameters = fc_source_bbn

    # Test source_bbn_two_parameters setter exception 3 (empty spectrum).
    fc_source_bbn = fields_container_factory.over_time_freq_fields_container([Field()])
    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "Each spectrum in the specified broadband noise source with two parameters must "
            "contain at least one element."
        ),
    ):
        source_bbn_two_parameters_obj.source_bbn_two_parameters = fc_source_bbn

    # Test source_bbn_two_parameters setter exception 4 (empty bbn source's first control data).
    # For this, we use a valid dataset, and then remove the control data.
    source_bbn_two_parameters_obj = SourceBroadbandNoiseTwoParameters()
    source_bbn_two_parameters_obj.load_source_bbn_two_parameters(
        pytest.data_path_sound_composer_bbn_source_2p_in_container
    )
    support_data = source_bbn_two_parameters_obj.source_bbn_two_parameters.get_support(
        "control_parameter_1"
    )
    support_properties = support_data.available_field_supported_properties()
    support_values = support_data.field_support_by_property(support_properties[0])
    support_values.data = []
    fc_source_bbn = source_bbn_two_parameters_obj.source_bbn_two_parameters
    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "Broadband noise source with two parameters must contain as many spectra as the "
            "number of values in both associated control parameters \\(in the provided DPF fields "
            "container, the number of fields should be the same as the number of values in both "
            "fields container supports\\)."
        ),
    ):
        source_bbn_two_parameters_obj.source_bbn_two_parameters = fc_source_bbn


def test_source_broadband_noise_two_parameters_is_source_control_valid():
    """Test SourceBroadbandNoiseTwoParameters is_source_control_valid method."""
    source_bbn_two_parameters_obj = SourceBroadbandNoiseTwoParameters()

    # Test is_source_control_valid method (attribute not set).
    assert source_bbn_two_parameters_obj.is_source_control_valid() is False

    # Test is_source_control_valid method (first attribute set, but not the second).
    source_control_obj = SourceControlTime()
    source_bbn_two_parameters_obj.source_control1 = source_control_obj
    assert source_bbn_two_parameters_obj.is_source_control_valid() is False

    # Test is_source_control_valid method (both attributes set, but attributes' fields not set).
    source_control_obj = SourceControlTime()
    source_bbn_two_parameters_obj.source_control2 = source_control_obj
    assert source_bbn_two_parameters_obj.is_source_control_valid() is False

    # Test is_source_control_valid method (only one attribute's field set).
    f_source_control = fields_factory.create_scalar_field(
        num_entities=1, location=locations.time_freq
    )
    f_source_control.append([1.0, 2.0, 3.0, 4.0, 5.0], 1)
    source_bbn_two_parameters_obj.source_control1.control = f_source_control
    assert source_bbn_two_parameters_obj.is_source_control_valid() is False

    # Test is_source_control_valid method (all set).
    source_bbn_two_parameters_obj.source_control2.control = f_source_control
    assert source_bbn_two_parameters_obj.is_source_control_valid() is True


def test_source_broadband_noise_two_parameters_load_source_bbn_two_parameters():
    """Test SourceBroadbandNoiseTwoParameters load_source_bbn method."""
    source_bbn_two_parameters_obj = SourceBroadbandNoiseTwoParameters()
    source_bbn_two_parameters_obj.load_source_bbn_two_parameters(
        pytest.data_path_sound_composer_bbn_source_2p_in_container
    )
    assert isinstance(source_bbn_two_parameters_obj.source_bbn_two_parameters, FieldsContainer)
    assert source_bbn_two_parameters_obj.source_bbn_two_parameters[0].data[3] == pytest.approx(
        EXP_SPECTRUM_DATA03
    )


def test_source_broadband_noise_two_parameters_process():
    """Test SourceBroadbandNoiseTwoParameters process method."""
    # Create a field to use in a SourceControlTime object.
    f_source_control = fields_factory.create_scalar_field(
        num_entities=1, location=locations.time_freq
    )
    f_source_control.append([3, 4, 35, 38], 1)
    support = TimeFreqSupport()
    f_time = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
    f_time.append([0, 1, 2, 3], 1)
    support.time_frequencies = f_time
    f_source_control.time_freq_support = support

    # Create a first SourceControlTime object.
    source_control1 = SourceControlTime()
    source_control1.control = f_source_control

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

    # Create a SourceBroadbandNoiseTwoParameters object test source file with less and created
    # source controls.
    source_bbn_two_parameters_obj = SourceBroadbandNoiseTwoParameters(
        file=pytest.data_path_sound_composer_bbn_source_2p_in_container,
        source_control1=source_control1,
        source_control2=source_control2,
    )

    source_bbn_two_parameters_obj.process()
    assert source_bbn_two_parameters_obj._output is not None


def test_source_broadband_noise_two_parameters_process_exceptions():
    """Test SourceBroadbandNoiseTwoParameters process method exceptions."""
    # Test process method exception1 (missing controls).
    source_bbn_two_parameters_obj = SourceBroadbandNoiseTwoParameters(
        pytest.data_path_sound_composer_bbn_source_2p_in_container
    )
    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "At least one source control for broadband noise source with two parameters is not "
            "set. Use ``SourceBroadbandNoiseTwoParameters.source_control1`` and/or "
            "``SourceBroadbandNoiseTwoParameters.source_control2``."
        ),
    ):
        source_bbn_two_parameters_obj.process()

    # Test process method exception2 (missing bbn source data).
    source_bbn_two_parameters_obj.source_bbn_two_parameters = None
    f_source_control = fields_factory.create_scalar_field(
        num_entities=1, location=locations.time_freq
    )
    f_source_control.append([1.0, 2.0, 3.0, 4.0, 5.0], 1)
    source_control_obj = SourceControlTime()
    source_control_obj.control = f_source_control
    source_bbn_two_parameters_obj.source_control1 = source_control_obj
    source_bbn_two_parameters_obj.source_control2 = source_control_obj
    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "Broadband noise source with two parameters data is not set. Use "
            "``SourceBroadbandNoiseTwoParameters.source_bbn_two_parameters`` or method "
            "``SourceBroadbandNoiseTwoParameters.load_source_bbn_two_parameters\\(\\)``."
        ),
    ):
        source_bbn_two_parameters_obj.process()

    # Test process method exception3 (invalid sampling frequency value).
    source_bbn_two_parameters_obj.load_source_bbn_two_parameters(
        pytest.data_path_sound_composer_bbn_source_2p_in_container
    )
    with pytest.raises(
        PyAnsysSoundException, match="Sampling frequency must be strictly positive."
    ):
        source_bbn_two_parameters_obj.process(sampling_frequency=0.0)


def test_source_broadband_noise_two_parameters_get_output():
    """Test SourceBroadbandNoiseTwoParameters get_output method."""
    # Create a field to use in a SourceControlTime object.
    f_source_control = fields_factory.create_scalar_field(
        num_entities=1, location=locations.time_freq
    )
    f_source_control.append([3, 4, 35, 38], 1)
    support = TimeFreqSupport()
    f_time = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
    f_time.append([0, 1, 2, 3], 1)
    support.time_frequencies = f_time
    f_source_control.time_freq_support = support

    # Create a first SourceControlTime object.
    source_control1 = SourceControlTime()
    source_control1.control = f_source_control

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

    # Create a SourceBroadbandNoiseTwoParameters object test source file and created source
    # controls.
    source_bbn_two_parameters_obj = SourceBroadbandNoiseTwoParameters(
        file=pytest.data_path_sound_composer_bbn_source_2p_in_container,
        source_control1=source_control1,
        source_control2=source_control2,
    )

    source_bbn_two_parameters_obj.process(sampling_frequency=44100.0)
    f_output = source_bbn_two_parameters_obj.get_output()
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

    # Check the sound power level in the octave bands centered at 250, 1000 and 4000 Hz.
    # Due to the non-deterministic nature of the produced signal, tolerance is set to 3 dB.
    psd_squared_band = psd_squared[
        (psd_freq >= 250 * 2 ** (-1 / 2)) & (psd_freq < 250 * 2 ** (1 / 2))
    ]
    level = 10 * np.log10(psd_squared_band.sum() * delat_f / REF_ACOUSTIC_POWER)
    assert level == pytest.approx(EXP_LEVEL_OCTAVE_BAND_250, abs=3.0)

    psd_squared_band = psd_squared[
        (psd_freq >= 1000 * 2 ** (-1 / 2)) & (psd_freq < 1000 * 2 ** (1 / 2))
    ]
    level = 10 * np.log10(psd_squared_band.sum() * delat_f / REF_ACOUSTIC_POWER)
    assert level == pytest.approx(EXP_LEVEL_OCTAVE_BAND_1000, abs=3.0)

    psd_squared_band = psd_squared[
        (psd_freq >= 4000 * 2 ** (-1 / 2)) & (psd_freq < 4000 * 2 ** (1 / 2))
    ]
    level = 10 * np.log10(psd_squared_band.sum() * delat_f / REF_ACOUSTIC_POWER)
    assert level == pytest.approx(EXP_LEVEL_OCTAVE_BAND_4000, abs=3.0)


def test_source_broadband_noise_two_parameters_get_output_unprocessed():
    """Test SourceBroadbandNoiseTwoParameters get_output method's exception."""
    source_bbn_two_parameters_obj = SourceBroadbandNoiseTwoParameters()
    with pytest.warns(
        PyAnsysSoundWarning,
        match=(
            "Output is not processed yet. Use the "
            "``SourceBroadbandNoiseTwoParameters.process\\(\\)`` method."
        ),
    ):
        f_output = source_bbn_two_parameters_obj.get_output()
    assert f_output is None


def test_source_broadband_noise_two_parameters_get_output_as_nparray():
    """Test SourceBroadbandNoiseTwoParameters get_output_as_nparray method."""
    # Create a field to use in a SourceControlTime object.
    f_source_control = fields_factory.create_scalar_field(
        num_entities=1, location=locations.time_freq
    )
    f_source_control.append([3, 4, 35, 38], 1)
    support = TimeFreqSupport()
    f_time = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
    f_time.append([0, 1, 2, 3], 1)
    support.time_frequencies = f_time
    f_source_control.time_freq_support = support

    # Create a first SourceControlTime object.
    source_control1 = SourceControlTime()
    source_control1.control = f_source_control

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

    # Create a SourceBroadbandNoiseTwoParameters object test source file with less and created
    # source controls.
    source_bbn_two_parameters_obj = SourceBroadbandNoiseTwoParameters(
        file=pytest.data_path_sound_composer_bbn_source_2p_in_container,
        source_control1=source_control1,
        source_control2=source_control2,
    )

    source_bbn_two_parameters_obj.process(sampling_frequency=44100.0)
    output_nparray = source_bbn_two_parameters_obj.get_output_as_nparray()
    assert isinstance(output_nparray, np.ndarray)
    assert len(output_nparray) / 44100.0 == pytest.approx(3.0)


def test_source_broadband_noise_two_parameters_get_output_as_nparray_unprocessed():
    """Test SourceBroadbandNoiseTwoParameters get_output_as_nparray method's exception."""
    source_bbn_two_parameters_obj = SourceBroadbandNoiseTwoParameters()
    with pytest.warns(
        PyAnsysSoundWarning,
        match=(
            "Output is not processed yet. Use the "
            "``SourceBroadbandNoiseTwoParameters.process\\(\\)`` method."
        ),
    ):
        output_nparray = source_bbn_two_parameters_obj.get_output_as_nparray()
    assert len(output_nparray) == 0


@patch("matplotlib.pyplot.show")
def test_source_broadband_noise_two_parameters_plot(mock_show):
    """Test SourceBroadbandNoiseTwoParameters plot method."""
    # Create a field to use in a SourceControlTime object.
    f_source_control = fields_factory.create_scalar_field(
        num_entities=1, location=locations.time_freq
    )
    f_source_control.append([3, 4, 35, 38], 1)
    support = TimeFreqSupport()
    f_time = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
    f_time.append([0, 1, 2, 3], 1)
    support.time_frequencies = f_time
    f_source_control.time_freq_support = support

    # Create a first SourceControlTime object.
    source_control1 = SourceControlTime()
    source_control1.control = f_source_control

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

    # Create a SourceBroadbandNoiseTwoParameters object with test source file and created source
    # controls.
    source_bbn_two_parameters_obj = SourceBroadbandNoiseTwoParameters(
        file=pytest.data_path_sound_composer_bbn_source_2p_in_container,
        source_control1=source_control1,
        source_control2=source_control2,
    )

    source_bbn_two_parameters_obj.process()
    source_bbn_two_parameters_obj.plot()


def test_source_broadband_noise_two_parameters_plot_exceptions():
    """Test SourceBroadbandNoiseTwoParameters plot method's exception."""
    source_bbn_two_parameters_obj = SourceBroadbandNoiseTwoParameters()
    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "Output is not processed yet. Use the "
            "'SourceBroadbandNoiseTwoParameters.process\\(\\)' method."
        ),
    ):
        source_bbn_two_parameters_obj.plot()


@patch("matplotlib.pyplot.show")
def test_source_broadband_noise_two_parameters_plot_control(mock_show):
    """Test SourceBroadbandNoiseTwoParameters plot_control method."""
    # Create a field to use in a SourceControlTime object.
    f_source_control = fields_factory.create_scalar_field(
        num_entities=1, location=locations.time_freq
    )
    f_source_control.append([3, 4, 35, 38], 1)
    support = TimeFreqSupport()
    f_time = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
    f_time.append([0, 1, 2, 3], 1)
    support.time_frequencies = f_time
    f_source_control.time_freq_support = support

    # Create a first SourceControlTime object.
    source_control1 = SourceControlTime()
    source_control1.control = f_source_control

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

    # Create a SourceBroadbandNoiseTwoParameters object with created source controls.
    source_bbn_two_parameters_obj = SourceBroadbandNoiseTwoParameters(
        source_control1=source_control1,
        source_control2=source_control2,
    )

    source_bbn_two_parameters_obj.plot_control()


def test_source_broadband_noise_two_parameters_plot_control_exceptions():
    """Test SourceBroadbandNoiseTwoParameters plot_control method's exception."""
    source_bbn_two_parameters_obj = SourceBroadbandNoiseTwoParameters()
    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "At least one source control for broadband noise source with two parameters is not "
            "set. Use ``SourceBroadbandNoiseTwoParameters.source_control1`` and/or "
            "``SourceBroadbandNoiseTwoParameters.source_control2``."
        ),
    ):
        source_bbn_two_parameters_obj.plot_control()


def test_source_broadband_noise_two_parameters___extract_bbn_two_parameters_info():
    """Test SourceBroadbandNoiseTwoParameters __extract_bbn_two_parameters_info method."""
    source = SourceBroadbandNoiseTwoParameters()
    assert source._SourceBroadbandNoiseTwoParameters__extract_bbn_two_parameters_info() == (
        "",
        0.0,
        "",
        "",
        (),
        "",
        "",
        (),
    )

    source.load_source_bbn_two_parameters(
        pytest.data_path_sound_composer_bbn_source_2p_in_container
    )
    assert source._SourceBroadbandNoiseTwoParameters__extract_bbn_two_parameters_info() == (
        "Not available",
        1000.0,
        "temperature",
        "celsius",
        (2.5, 40.0),
        "charge",
        "%",
        (0, 10.0),
    )

    # Test with empty control support (delta_f not applicable).
    source.source_bbn_two_parameters[0].time_freq_support.time_frequencies.data = []
    assert source._SourceBroadbandNoiseTwoParameters__extract_bbn_two_parameters_info() == (
        "Not available",
        0.0,
        "temperature",
        "celsius",
        (2.5, 40.0),
        "charge",
        "%",
        (0, 10.0),
    )
