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
from ansys.sound.core.spectral_processing import PowerSpectralDensity

REF_ACOUSTIC_POWER = 4e-10

EXP_LEVEL_OCTAVE_BAND = 41.0
EXP_SPECTRUM_DATA03 = 5.0357002692180686e-06
EXP_STR_NOT_SET = "Broadband noise source: Not set\nSource control: Not set"
EXP_STR_ALL_SET = (
    "Broadband noise source: ''\n"
    "\tSpectrum type: Not available\n"
    "\tSpectrum count: 5\n"
    "\tControl parameter: Speed of wind, m/s\n"
    "\t\t[ 1.   2.   5.3 10.5 27.8]"
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
    "\t\t[1. 2. 3. 4. 5. ... 36. 37. 38. 39. 40.]"
    "\nSource control: \n"
    "\tMin: 1.0\n"
    "\tMax: 10.0\n"
    "\tDuration: 3.0 s"
)


def test_source_broadband_noise_instantiation_no_arg():
    """Test SourceBroadbandNoise instantiation without arguments."""
    source_bbn_obj = SourceBroadbandNoise()
    assert isinstance(source_bbn_obj, SourceBroadbandNoise)
    assert source_bbn_obj.source_bbn is None


def test_source_broadband_noise_instantiation_file_arg():
    """Test SourceBroadbandNoise instantiation with file argument."""
    source_bbn_obj = SourceBroadbandNoise(
        file=pytest.data_path_sound_composer_bbn_source_in_container
    )
    assert isinstance(source_bbn_obj, SourceBroadbandNoise)
    assert source_bbn_obj.source_bbn is not None


def test_source_broadband_noise___str___not_set():
    """Test SourceBroadbandNoise __str__ method when nothing is set."""
    source_bbn_obj = SourceBroadbandNoise()
    assert str(source_bbn_obj) == EXP_STR_NOT_SET


def test_source_broadband_noise___str___all_set():
    """Test SourceBroadbandNoise __str__ method when all data are set."""
    # Create a field to use in a SourceControlTime object.
    f_source_control = fields_factory.create_scalar_field(
        num_entities=1, location=locations.time_freq
    )
    f_source_control.append([1, 3, 6, 10], 1)
    support = TimeFreqSupport()
    f_time = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
    f_time.append([0, 1, 2, 3], 1)
    support.time_frequencies = f_time
    f_source_control.time_freq_support = support

    # Create a SourceControlTime object.
    source_control = SourceControlTime()
    source_control.control = f_source_control

    # Create a SourceBroadbandNoise object using source file with less than 30 values and created
    # source control.
    source_bbn_obj = SourceBroadbandNoise(
        pytest.data_path_sound_composer_bbn_source_in_container,
        source_control,
    )
    assert str(source_bbn_obj) == EXP_STR_ALL_SET

    # Replace source file with one with more than 10 values.
    source_bbn_obj.load_source_bbn(
        pytest.data_path_sound_composer_bbn_source_40_values_in_container
    )
    assert str(source_bbn_obj) == EXP_STR_ALL_SET_40_VALUES


def test_source_broadband_noise_properties():
    """Test SourceBroadbandNoise properties."""
    source_bbn_obj = SourceBroadbandNoise()

    # Test source_control property.
    source_bbn_obj.source_control = SourceControlTime()
    assert isinstance(source_bbn_obj.source_control, SourceControlTime)

    # Test source_bbn property.
    # Create a second object and then reuse its source_bbn property.
    source_bbn_obj_tmp = SourceBroadbandNoise()
    source_bbn_obj_tmp.load_source_bbn(pytest.data_path_sound_composer_bbn_source_in_container)
    bbn_fieldscontainer = source_bbn_obj_tmp.source_bbn
    source_bbn_obj.source_bbn = bbn_fieldscontainer
    assert isinstance(source_bbn_obj.source_bbn, FieldsContainer)


def test_source_broadband_noise_properties_exceptions():
    """Test SourceBroadbandNoise properties' exceptions."""
    source_bbn_obj = SourceBroadbandNoise()

    # Test source_control setter exception (str instead of SourceControlTime).
    with pytest.raises(
        PyAnsysSoundException,
        match="Specified source control object must be of type ``SourceControlTime``.",
    ):
        source_bbn_obj.source_control = "InvalidType"

    # Test source_bbn setter exception 1 (str instead a Field).
    with pytest.raises(
        PyAnsysSoundException,
        match="Specified broadband noise source must be provided as a DPF fields container.",
    ):
        source_bbn_obj.source_bbn = "InvalidType"

    # Test source_bbn setter exception 2 (less than 1 spectrum).
    fc_source_bbn = FieldsContainer()
    with pytest.raises(
        PyAnsysSoundException,
        match="Specified broadband noise source must contain at least one spectrum.",
    ):
        source_bbn_obj.source_bbn = fc_source_bbn

    # Test source_bbn setter exception 3 (empty spectrum).
    fc_source_bbn = fields_container_factory.over_time_freq_fields_container([Field()])
    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "Each spectrum in the specified broadband noise source must contain at least one "
            "element."
        ),
    ):
        source_bbn_obj.source_bbn = fc_source_bbn

    # Test source_bbn setter exception 4 (empty bbn source's control data).
    # For this, we use a valid dataset, and then remove the control data.
    source_bbn_obj = SourceBroadbandNoise()
    source_bbn_obj.load_source_bbn(pytest.data_path_sound_composer_bbn_source_in_container)
    support_data = source_bbn_obj.source_bbn.get_support("control_parameter_1")
    support_properties = support_data.available_field_supported_properties()
    support_values = support_data.field_support_by_property(support_properties[0])
    support_values.data = []
    fc_source_bbn = source_bbn_obj.source_bbn
    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "Broadband noise source must contain as many spectra as the number of values in the "
            "associated control parameter \\(in the provided DPF fields container, the number of "
            "fields should be the same as the number of values in the fields container support\\)."
        ),
    ):
        source_bbn_obj.source_bbn = fc_source_bbn


def test_source_broadband_noise_is_source_control_valid():
    """Test SourceBroadbandNoise is_source_control_valid method."""
    source_bbn_obj = SourceBroadbandNoise()

    # Test is_source_control_valid method (attribute not set).
    assert source_bbn_obj.is_source_control_valid() is False

    # Test is_source_control_valid method (attribute set, but attribute's field not set).
    source_control_obj = SourceControlTime()
    source_bbn_obj.source_control = source_control_obj
    assert source_bbn_obj.is_source_control_valid() is False

    # Test is_source_control_valid method (all set).
    f_source_control = fields_factory.create_scalar_field(
        num_entities=1, location=locations.time_freq
    )
    f_source_control.append([1.0, 2.0, 3.0, 4.0, 5.0], 1)
    source_bbn_obj.source_control.control = f_source_control
    assert source_bbn_obj.is_source_control_valid() is True


def test_source_specrum_load_source_bbn():
    """Test SourceBroadbandNoise load_source_bbn method."""
    source_bbn_obj = SourceBroadbandNoise()
    source_bbn_obj.load_source_bbn(pytest.data_path_sound_composer_bbn_source_in_container)
    assert isinstance(source_bbn_obj.source_bbn, FieldsContainer)
    assert source_bbn_obj.source_bbn[0].data[3] == pytest.approx(EXP_SPECTRUM_DATA03)


def test_source_broadband_noise_process():
    """Test SourceBroadbandNoise process method."""
    # Create a field to use in a SourceControlTime object.
    f_source_control = fields_factory.create_scalar_field(
        num_entities=1, location=locations.time_freq
    )
    f_source_control.append([1, 3, 6, 10], 1)
    support = TimeFreqSupport()
    f_time = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
    f_time.append([0, 1, 2, 3], 1)
    support.time_frequencies = f_time
    f_source_control.time_freq_support = support

    # Create a SourceControlTime object.
    source_control_obj = SourceControlTime()
    source_control_obj.control = f_source_control

    source_bbn_obj = SourceBroadbandNoise(
        pytest.data_path_sound_composer_bbn_source_in_container,
        source_control_obj,
    )
    source_bbn_obj.process()
    assert source_bbn_obj._output is not None


def test_source_broadband_noise_process_exceptions():
    """Test SourceBroadbandNoise process method exceptions."""
    # Test process method exception1 (missing control).
    source_bbn_obj = SourceBroadbandNoise(pytest.data_path_sound_composer_bbn_source_in_container)
    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "Broadband noise source control is not set. "
            "Use ``SourceBroadbandNoise.source_control``."
        ),
    ):
        source_bbn_obj.process()

    # Test process method exception2 (missing bbn source data).
    source_bbn_obj.source_bbn = None
    f_source_control = fields_factory.create_scalar_field(
        num_entities=1, location=locations.time_freq
    )
    f_source_control.append([1.0, 2.0, 3.0, 4.0, 5.0], 1)
    source_control_obj = SourceControlTime()
    source_control_obj.control = f_source_control
    source_bbn_obj.source_control = source_control_obj
    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "Broadband noise source data is not set. Use ``SourceBroadbandNoise.source_bbn`` "
            "or method ``SourceBroadbandNoise.load_source_bbn\\(\\)``."
        ),
    ):
        source_bbn_obj.process()

    # Test process method exception3 (invalid sampling frequency value).
    source_bbn_obj.load_source_bbn(pytest.data_path_sound_composer_bbn_source_in_container)
    with pytest.raises(
        PyAnsysSoundException, match="Sampling frequency must be strictly positive."
    ):
        source_bbn_obj.process(sampling_frequency=0.0)


def test_source_broadband_noise_get_output():
    """Test SourceBroadbandNoise get_output method."""
    # Create a field to use in a SourceControlTime object.
    f_source_control = fields_factory.create_scalar_field(
        num_entities=1, location=locations.time_freq
    )
    f_source_control.append([1, 3, 6, 10], 1)
    support = TimeFreqSupport()
    f_time = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
    f_time.append([0, 1, 2, 3], 1)
    support.time_frequencies = f_time
    f_source_control.time_freq_support = support

    # Create a SourceControlTime object.
    source_control_obj = SourceControlTime()
    source_control_obj.control = f_source_control

    source_bbn_obj = SourceBroadbandNoise(
        pytest.data_path_sound_composer_bbn_source_in_container,
        source_control_obj,
    )
    source_bbn_obj.process(sampling_frequency=44100.0)
    f_output = source_bbn_obj.get_output()
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
    # Due to the non-deterministic nature of the produced signal, tolerance is set to 1 dB.
    psd_squared_band = psd_squared[
        (psd_freq >= 250 * 2 ** (-1 / 2)) & (psd_freq < 250 * 2 ** (1 / 2))
    ]
    level = 10 * np.log10(psd_squared_band.sum() * delat_f / REF_ACOUSTIC_POWER)
    assert level == pytest.approx(EXP_LEVEL_OCTAVE_BAND, abs=1.0)

    psd_squared_band = psd_squared[
        (psd_freq >= 1000 * 2 ** (-1 / 2)) & (psd_freq < 1000 * 2 ** (1 / 2))
    ]
    level = 10 * np.log10(psd_squared_band.sum() * delat_f / REF_ACOUSTIC_POWER)
    assert level == pytest.approx(EXP_LEVEL_OCTAVE_BAND, abs=1.0)

    psd_squared_band = psd_squared[
        (psd_freq >= 4000 * 2 ** (-1 / 2)) & (psd_freq < 4000 * 2 ** (1 / 2))
    ]
    level = 10 * np.log10(psd_squared_band.sum() * delat_f / REF_ACOUSTIC_POWER)
    assert level == pytest.approx(EXP_LEVEL_OCTAVE_BAND, abs=1.0)


def test_source_broadband_noise_get_output_unprocessed(dpf_sound_test_server):
    """Test SourceBroadbandNoise get_output method's exception."""
    source_bbn_obj = SourceBroadbandNoise()
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the ``SourceBroadbandNoise.process\\(\\)`` method.",
    ):
        f_output = source_bbn_obj.get_output()
    assert f_output is None


def test_source_broadband_noise_get_output_as_nparray():
    """Test SourceBroadbandNoise get_output_as_nparray method."""
    # Create a field to use in a SourceControlTime object.
    f_source_control = fields_factory.create_scalar_field(
        num_entities=1, location=locations.time_freq
    )
    f_source_control.append([1, 3, 6, 10], 1)
    support = TimeFreqSupport()
    f_time = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
    f_time.append([0, 1, 2, 3], 1)
    support.time_frequencies = f_time
    f_source_control.time_freq_support = support

    # Create a SourceControlTime object.
    source_control_obj = SourceControlTime()
    source_control_obj.control = f_source_control

    source_bbn_obj = SourceBroadbandNoise(
        pytest.data_path_sound_composer_bbn_source_in_container,
        source_control_obj,
    )
    source_bbn_obj.process(sampling_frequency=44100.0)
    output_nparray = source_bbn_obj.get_output_as_nparray()
    assert isinstance(output_nparray, np.ndarray)
    assert len(output_nparray) / 44100.0 == pytest.approx(3.0)


def test_source_broadband_noise_get_output_as_nparray_unprocessed():
    """Test SourceBroadbandNoise get_output_as_nparray method's exception."""
    source_bbn_obj = SourceBroadbandNoise()
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the ``SourceBroadbandNoise.process\\(\\)`` method.",
    ):
        output_nparray = source_bbn_obj.get_output_as_nparray()
    assert len(output_nparray) == 0


@patch("matplotlib.pyplot.show")
def test_source_broadband_noise_plot(mock_show):
    """Test SourceBroadbandNoise plot method."""
    # Create a field to use in a SourceControlTime object.
    f_source_control = fields_factory.create_scalar_field(
        num_entities=1, location=locations.time_freq
    )
    f_source_control.append([1, 3, 6, 10], 1)
    support = TimeFreqSupport()
    f_time = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
    f_time.append([0, 1, 2, 3], 1)
    support.time_frequencies = f_time
    f_source_control.time_freq_support = support

    # Create a SourceControlTime object.
    source_control_obj = SourceControlTime()
    source_control_obj.control = f_source_control

    source_bbn_obj = SourceBroadbandNoise(
        pytest.data_path_sound_composer_bbn_source_in_container,
        source_control_obj,
    )
    source_bbn_obj.process()
    source_bbn_obj.plot()


def test_source_broadband_noise_plot_exceptions():
    """Test SourceBroadbandNoise plot method's exception."""
    source_bbn_obj = SourceBroadbandNoise()
    with pytest.raises(
        PyAnsysSoundException,
        match="Output is not processed yet. Use the 'SourceBroadbandNoise.process\\(\\)' method.",
    ):
        source_bbn_obj.plot()


def test_source_broadband_noise___extract_bbn_info():
    """Test SourceBroadbandNoise __extract_bbn_info method."""
    source_bbn_obj = SourceBroadbandNoise()
    assert source_bbn_obj._SourceBroadbandNoise__extract_bbn_info() == ("", 0.0, "", "", [])

    source_bbn_obj.load_source_bbn(pytest.data_path_sound_composer_bbn_source_in_container)
    assert source_bbn_obj._SourceBroadbandNoise__extract_bbn_info() == (
        "Not available",
        31.0,
        "Speed of wind",
        "m/s",
        [1.0, 2.0, 5.300000190734863, 10.5, 27.777999877929688],
    )

    # Test with empty control support (delta_f not applicable).
    source_bbn_obj.source_bbn[0].time_freq_support.time_frequencies.data = []
    assert source_bbn_obj._SourceBroadbandNoise__extract_bbn_info() == (
        "Not available",
        0.0,
        "Speed of wind",
        "m/s",
        [1.0, 2.0, 5.300000190734863, 10.5, 27.777999877929688],
    )
