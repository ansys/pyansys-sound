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

from ansys.dpf.core import (
    Field,
    GenericDataContainer,
    Operator,
    TimeFreqSupport,
    fields_factory,
    locations,
)
import numpy as np
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ansys.sound.core.signal_utilities.load_wav import LoadWav
from ansys.sound.core.sound_composer import SourceControlSpectrum, SourceSpectrum
from ansys.sound.core.sound_composer import SpectrumSynthesisMethods as Methods
from ansys.sound.core.spectral_processing import PowerSpectralDensity

REF_ACOUSTIC_POWER = 4e-10

EXP_SPECTRUM_DATA3 = 9.75124494289048e-05
EXP_SPECTRUM_DATA3_DBA = 4.882796e-06
EXP_SPECTRUM_DATA3_DBAPERHZ = 3.813463e-05
EXP_LEVEL_BAND_3RD_250_Hz = 69.10828
EXP_LEVEL_BAND_3RD_500_Hz = 66.06081
EXP_LEVEL_BAND_3RD_1000_Hz = 62.85511
EXP_STR_NOT_SET = "Spectrum source: Not set\nSource control: Not set/valid"
EXP_STR_ALL_SET = (
    "Spectrum source: ''\n\tFmax: 24000 Hz\n\tDeltaF: 5.9 Hz\nSource control: IFFT, 1.0 s"
)
EXP_STR_ALL_SET_DF_NA = (
    "Spectrum source: ''\n\tFmax: 0 Hz\n\tDeltaF: N/A\nSource control: IFFT, 1.0 s"
)


def test_source_spectrum_instantiation_no_arg():
    """Test SourceSpectrum instantiation without arguments."""
    # Test instantiation.
    source_spectrum = SourceSpectrum()
    assert isinstance(source_spectrum, SourceSpectrum)
    assert source_spectrum.source_spectrum_data is None


def test_source_spectrum_instantiation_file_arg():
    """Test SourceSpectrum instantiation with file argument."""
    # Test instantiation.
    source_spectrum = SourceSpectrum(pytest.data_path_sound_composer_spectrum_source_in_container)
    assert isinstance(source_spectrum, SourceSpectrum)
    assert source_spectrum.source_spectrum_data is not None


def test_source_spectrum___str___not_set():
    """Test SourceSpectrum __str__ method when nothing is set."""
    source_spectrum = SourceSpectrum()
    assert str(source_spectrum) == EXP_STR_NOT_SET


def test_source_spectrum___str___all_set():
    """Test SourceSpectrum __str__ method when all data are set."""
    source_spectrum = SourceSpectrum(
        pytest.data_path_sound_composer_spectrum_source_in_container,
        SourceControlSpectrum(duration=1.0),
    )
    assert str(source_spectrum) == EXP_STR_ALL_SET


def test_source_spectrum___str___all_set_deltaf_not_applicable():
    """Test SourceSpectrum __str__ method when all data are set."""
    source_spectrum = SourceSpectrum(
        pytest.data_path_sound_composer_spectrum_source_in_container,
        SourceControlSpectrum(duration=1.0),
    )

    # Artificially reduce the psd support to a single point to trigger the "N/A" DeltaF.
    source_spectrum.source_spectrum_data.time_freq_support.time_frequencies.data = [0.0]
    assert str(source_spectrum) == EXP_STR_ALL_SET_DF_NA


def test_source_spectrum_properties():
    """Test SourceSpectrum properties."""
    source_spectrum = SourceSpectrum()

    # Test source_control property.
    source_spectrum.source_control = SourceControlSpectrum()
    assert isinstance(source_spectrum.source_control, SourceControlSpectrum)

    # Compute a signal's power spectral density to check source_spectrum_data property.
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    psd = PowerSpectralDensity(
        input_signal=wav_loader.get_output()[0],
        fft_size=8192,
        window_type="HANN",
        window_length=8192,
        overlap=0.75,
    )
    psd.process()

    # Test source_spectrum_data property.
    source_spectrum.source_spectrum_data = psd.get_output()
    assert isinstance(source_spectrum.source_spectrum_data, Field)


def test_source_spectrum_properties_exceptions():
    """Test SourceSpectrum properties' exceptions."""
    source_spectrum = SourceSpectrum()

    # Test source_control setter exception (str instead of SourceControlSpectrum).
    with pytest.raises(
        PyAnsysSoundException,
        match="Specified source control object must be of type ``SourceControlSpectrum``.",
    ):
        source_spectrum.source_control = "InvalidType"

    # Test source_spectrum_data setter exception 1 (str instead a Field).
    with pytest.raises(
        PyAnsysSoundException, match="Specified spectrum source must be provided as a DPF field."
    ):
        source_spectrum.source_spectrum_data = "InvalidType"

    # Compute a signal's power spectral density to check source_spectrum_data property exception 2.
    wav_loader = LoadWav(pytest.data_path_flute_in_container)
    wav_loader.process()
    psd = PowerSpectralDensity(
        input_signal=wav_loader.get_output()[0],
        fft_size=8192,
        window_type="HANN",
        window_length=8192,
        overlap=0.75,
    )
    psd.process()
    field = psd.get_output()

    # Remove all frequencies from the field to trigger the exception.
    field.time_freq_support.time_frequencies.data = []

    # Test source_spectrum_data setter exception 2 (not enough elements).
    with pytest.raises(
        PyAnsysSoundException, match="Specified spectrum source must contain at least one element."
    ):
        source_spectrum.source_spectrum_data = field


def test_source_spectrum_is_source_control_valid():
    """Test SourceSpectrum is_source_control_valid method."""
    source_spectrum = SourceSpectrum()

    # Test is_source_control_valid method (not set case).
    assert source_spectrum.is_source_control_valid() is False

    # Test is_source_control_valid method (set, but duration=0 case).
    source_spectrum.source_control = SourceControlSpectrum()
    assert source_spectrum.is_source_control_valid() is False

    # Test is_source_control_valid method (set, duration>0).
    source_spectrum.source_control.duration = 1.0
    assert source_spectrum.is_source_control_valid() is True


def test_source_spectrum_load_source():
    """Test SourceSpectrum load_source method."""
    source_spectrum = SourceSpectrum()
    source_spectrum.load_source_spectrum(
        pytest.data_path_sound_composer_spectrum_source_in_container
    )
    assert isinstance(source_spectrum.source_spectrum_data, Field)
    assert source_spectrum.source_spectrum_data.data[3] == pytest.approx(EXP_SPECTRUM_DATA3)


@pytest.mark.skipif(
    not pytest.SOUND_VERSION_GREATER_THAN_OR_EQUAL_TO_2026R1,
    reason="AnsysSound_Spectrum v4 files require at least server version 11.0",
)
def test_source_spectrum_load_source_with_v4():
    """Test SourceSpectrum load_source method with v4 AnsysSound_Spectrum files."""
    source_spectrum = SourceSpectrum()
    source_spectrum.load_source_spectrum(
        pytest.data_path_sound_composer_spectrum_v4_dBA_source_in_container
    )
    assert isinstance(source_spectrum.source_spectrum_data, Field)
    assert source_spectrum.source_spectrum_data.data[3] == pytest.approx(EXP_SPECTRUM_DATA3_DBA)
    source_spectrum.load_source_spectrum(
        pytest.data_path_sound_composer_spectrum_v4_dBAPerHz_source_in_container
    )
    assert isinstance(source_spectrum.source_spectrum_data, Field)
    assert source_spectrum.source_spectrum_data.data[3] == pytest.approx(
        EXP_SPECTRUM_DATA3_DBAPERHZ
    )


def test_source_spectrum_set_from_generic_data_containers():
    """Test SourceSpectrum set_from_generic_data_containers method."""
    op = Operator("sound_composer_load_source_spectrum")
    op.connect(0, pytest.data_path_sound_composer_spectrum_source_in_container)
    op.run()
    f_data: Field = op.get_output(0, "field")

    source_data = GenericDataContainer()
    source_data.set_property("sound_composer_source", f_data)

    source_control_data = GenericDataContainer()
    source_control_data.set_property("sound_composer_source_control_spectrum_duration", 1.0)
    source_control_data.set_property("sound_composer_source_control_spectrum_method", "Hybrid")

    source_spectrum = SourceSpectrum()
    source_spectrum.set_from_generic_data_containers(source_data, source_control_data)
    assert isinstance(source_spectrum.source_spectrum_data, Field)
    assert len(source_spectrum.source_spectrum_data.data) == len(f_data.data)
    assert source_spectrum.source_control.duration == 1.0
    assert source_spectrum.source_control.method == Methods.Hybrid


def test_source_spectrum_get_as_generic_data_containers():
    """Test SourceSpectrum get_as_generic_data_containers method."""
    # Source control undefined => warning.
    source_spectrum = SourceSpectrum(
        file_source=pytest.data_path_sound_composer_spectrum_source_in_container
    )
    with pytest.warns(
        PyAnsysSoundWarning,
        match=(
            "Cannot create source control generic data container because there is no source "
            "control data."
        ),
    ):
        _, source_control_data = source_spectrum.get_as_generic_data_containers()
    assert source_control_data is None

    # Source data undefined => warning.
    source_spectrum.source_spectrum_data = None
    source_spectrum.source_control = SourceControlSpectrum(duration=1.0)
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Cannot create source generic data container because there is no source data.",
    ):
        source_data, _ = source_spectrum.get_as_generic_data_containers()
    assert source_data is None

    # Both source and source control are defined.
    source_spectrum.load_source_spectrum(
        pytest.data_path_sound_composer_spectrum_source_in_container,
    )
    source_spectrum.source_control = SourceControlSpectrum(duration=1.0)
    source_data, source_control_data = source_spectrum.get_as_generic_data_containers()

    assert isinstance(source_data, GenericDataContainer)
    assert isinstance(source_data.get_property("sound_composer_source"), Field)
    assert isinstance(source_control_data, GenericDataContainer)
    assert (
        source_control_data.get_property("sound_composer_source_control_spectrum_duration") == 1.0
    )
    assert (
        source_control_data.get_property("sound_composer_source_control_spectrum_method") == "IFFT"
    )


def test_source_spectrum_process():
    """Test SourceSpectrum process method."""
    source_spectrum = SourceSpectrum(
        pytest.data_path_sound_composer_spectrum_source_in_container,
        SourceControlSpectrum(duration=1.0),
    )
    source_spectrum.process()
    assert source_spectrum._output is not None


def test_source_spectrum_process_exceptions():
    """Test SourceSpectrum process method exceptions."""
    # Test process method exception1 (missing control).
    source_spectrum = SourceSpectrum(pytest.data_path_sound_composer_spectrum_source_in_container)
    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "Spectrum source control is not valid. Either it is not set "
            "\\(use ``SourceSpectrum.source_control``\\) or its duration is not strictly positive "
            "\\(use ``SourceSpectrum.source_control.duration``\\)."
        ),
    ):
        source_spectrum.process()

    # Test process method exception2 (missing spectrum).
    source_spectrum.source_spectrum_data = None
    source_spectrum.source_control = SourceControlSpectrum(duration=1.0)
    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "Source spectrum is not set. Use ``SourceSpectrum.source_spectrum_data`` "
            "or method ``SourceSpectrum.load_source_spectrum\\(\\)``."
        ),
    ):
        source_spectrum.process()

    # Test process method exception3 (invalid sampling frequency value).
    source_spectrum = SourceSpectrum()
    with pytest.raises(
        PyAnsysSoundException, match="Sampling frequency must be strictly positive."
    ):
        source_spectrum.process(sampling_frequency=0.0)


def test_source_spectrum_get_output():
    """Test SourceSpectrum get_output method."""
    source_spectrum = SourceSpectrum(
        pytest.data_path_sound_composer_spectrum_source_in_container,
        SourceControlSpectrum(duration=1.0),
    )
    source_spectrum.process(sampling_frequency=44100.0)

    # Check output type and sampling frequency.
    output_signal = source_spectrum.get_output()
    time = output_signal.time_freq_support.time_frequencies.data
    fs = 1.0 / (time[1] - time[0])
    assert isinstance(output_signal, Field)
    assert fs == pytest.approx(44100.0)

    # Compute the power spectral density over the output signal.
    psd = PowerSpectralDensity(
        input_signal=output_signal,
        fft_size=8192,
        window_type="HANN",
        window_length=8192,
        overlap=0.75,
    )
    psd.process()
    psd_squared, psd_freq = psd.get_PSD_squared_linear_as_nparray()
    delat_f = psd_freq[1] - psd_freq[0]

    # Check the sound power level in the 1/3-octave bands centered at 250, 500, and 1000 Hz.
    # Due to the non-deterministic nature of the produced signal, tolerance is set to 3 dB.
    # Differences are typically of a few tenths of dB, but can sometimes reach larger values.
    psd_squared_250 = psd_squared[
        (psd_freq >= 250 * 2 ** (-1 / 6)) & (psd_freq < 250 * 2 ** (1 / 6))
    ]
    level_250 = 10 * np.log10(psd_squared_250.sum() * delat_f / REF_ACOUSTIC_POWER)
    assert level_250 == pytest.approx(EXP_LEVEL_BAND_3RD_250_Hz, abs=3.0)

    psd_squared_500 = psd_squared[
        (psd_freq >= 500 * 2 ** (-1 / 6)) & (psd_freq < 500 * 2 ** (1 / 6))
    ]
    level_500 = 10 * np.log10(psd_squared_500.sum() * delat_f / REF_ACOUSTIC_POWER)
    assert level_500 == pytest.approx(EXP_LEVEL_BAND_3RD_500_Hz, abs=3.0)

    psd_squared_1000 = psd_squared[
        (psd_freq >= 1000 * 2 ** (-1 / 6)) & (psd_freq < 1000 * 2 ** (1 / 6))
    ]
    level_1000 = 10 * np.log10(psd_squared_1000.sum() * delat_f / REF_ACOUSTIC_POWER)
    assert level_1000 == pytest.approx(EXP_LEVEL_BAND_3RD_1000_Hz, abs=3.0)


def test_source_spectrum_get_output_unprocessed():
    """Test SourceSpectrum get_output method's exception."""
    source_spectrum = SourceSpectrum()
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the ``SourceSpectrum.process\\(\\)`` method.",
    ):
        output = source_spectrum.get_output()
    assert output is None


def test_source_spectrum_get_output_as_nparray():
    """Test SourceSpectrum get_output_as_nparray method."""
    source_spectrum = SourceSpectrum(
        pytest.data_path_sound_composer_spectrum_source_in_container,
        SourceControlSpectrum(duration=1.0),
    )
    source_spectrum.process(sampling_frequency=44100.0)

    # Checkout output type.
    output_signal = source_spectrum.get_output_as_nparray()
    assert isinstance(output_signal, np.ndarray)

    # Reconstruct a DPF field from the output signal to compute the PSD.
    signal_field = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
    signal_field.append(output_signal, 1)
    support = TimeFreqSupport()
    time_field = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
    time_field.append(np.array(range(len(output_signal))) / 44100.0, 1)
    support.time_frequencies = time_field
    signal_field.time_freq_support = support

    # Compute the power spectral density over the output signal.
    psd = PowerSpectralDensity(
        input_signal=signal_field,
        fft_size=8192,
        window_type="HANN",
        window_length=8192,
        overlap=0.75,
    )
    psd.process()
    psd_squared, psd_freq = psd.get_PSD_squared_linear_as_nparray()
    delat_f = psd_freq[1] - psd_freq[0]

    # Check the sound power level in the 1/3-octave bands centered at 250, 500, and 1000 Hz.
    # Due to the non-deterministic nature of the produced signal, tolerance is set to 3 dB.
    # Differences are typically of a few tenths of dB, but can sometimes reach larger values.
    psd_squared_250 = psd_squared[
        (psd_freq >= 250 * 2 ** (-1 / 6)) & (psd_freq < 250 * 2 ** (1 / 6))
    ]
    level_250 = 10 * np.log10(psd_squared_250.sum() * delat_f / REF_ACOUSTIC_POWER)
    assert level_250 == pytest.approx(EXP_LEVEL_BAND_3RD_250_Hz, abs=3.0)

    psd_squared_500 = psd_squared[
        (psd_freq >= 500 * 2 ** (-1 / 6)) & (psd_freq < 500 * 2 ** (1 / 6))
    ]
    level_500 = 10 * np.log10(psd_squared_500.sum() * delat_f / REF_ACOUSTIC_POWER)
    assert level_500 == pytest.approx(EXP_LEVEL_BAND_3RD_500_Hz, abs=3.0)

    psd_squared_1000 = psd_squared[
        (psd_freq >= 1000 * 2 ** (-1 / 6)) & (psd_freq < 1000 * 2 ** (1 / 6))
    ]
    level_1000 = 10 * np.log10(psd_squared_1000.sum() * delat_f / REF_ACOUSTIC_POWER)
    assert level_1000 == pytest.approx(EXP_LEVEL_BAND_3RD_1000_Hz, abs=3.0)


def test_source_spectrum_get_output_as_nparray_unprocessed():
    """Test SourceSpectrum get_output_as_nparray method's exception."""
    source_spectrum = SourceSpectrum()
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the ``SourceSpectrum.process\\(\\)`` method.",
    ):
        output = source_spectrum.get_output_as_nparray()
    assert len(output) == 0


@patch("matplotlib.pyplot.show")
def test_source_spectrum_plot(mock_show):
    """Test SourceSpectrum plot method."""
    source_spectrum = SourceSpectrum(
        pytest.data_path_sound_composer_spectrum_source_in_container,
        SourceControlSpectrum(duration=1.0),
    )
    source_spectrum.process()
    source_spectrum.plot()


def test_source_spectrum_plot_exceptions():
    """Test SourceSpectrum plot method's exception."""
    source_spectrum = SourceSpectrum()
    with pytest.raises(
        PyAnsysSoundException,
        match="Output is not processed yet. Use the 'SourceSpectrum.process\\(\\)' method.",
    ):
        source_spectrum.plot()
