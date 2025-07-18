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
    GenericDataContainer,
    Operator,
    TimeFreqSupport,
    fields_factory,
    locations,
)
import numpy as np
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ansys.sound.core.signal_processing.filter import Filter
from ansys.sound.core.sound_composer import (
    SourceAudio,
    SourceBroadbandNoise,
    SourceControlSpectrum,
    SourceControlTime,
    SourceSpectrum,
)
from ansys.sound.core.sound_composer import (
    Track,
)
from ansys.sound.core.sound_composer import SpectrumSynthesisMethods as Methods
from ansys.sound.core.spectral_processing.power_spectral_density import PowerSpectralDensity

REF_ACOUSTIC_POWER = 4e-10

EXP_STR_NOT_SET = "Unnamed track\nSource not set\nGain: +0.0 dB\nFilter: Not set"
EXP_STR_ALL_SET = "MyTrack\nAudio source: Not set\nGain: +0.0 dB\nFilter: Set"
EXP_LEVEL_BAND_3RD_250_Hz = 76.05368
EXP_LEVEL_BAND_3RD_500_Hz = 73.08566
EXP_LEVEL_BAND_3RD_1000_Hz = 69.42302


def test_track_instantiation_no_arg():
    """Test Track instantiation without arguments."""
    # Test instantiation.
    track = Track()
    assert isinstance(track, Track)
    assert track.name == ""
    assert track.gain == 0.0
    assert track.source is None
    assert track.filter is None


def test_track_instantiation_all_args():
    """Test Track instantiation with all arguments."""
    # Test instantiation.
    track = Track(name="track", gain=3.0, source=SourceAudio(), filter=Filter())
    assert isinstance(track, Track)
    assert track.name == "track"
    assert track.gain == 3.0
    assert isinstance(track.source, SourceAudio)
    assert isinstance(track.filter, Filter)


def test_track___str___not_set():
    """Test Track __str__ method when nothing is set."""
    track = Track()
    assert str(track) == EXP_STR_NOT_SET


def test_track___str___all_set():
    """Test Track __str__ method when all data are set."""
    track = Track(name="MyTrack", source=SourceAudio(), filter=Filter())
    assert str(track) == EXP_STR_ALL_SET


def test_track_properties():
    """Test Track properties."""
    track = Track()

    # Test name property.
    track.name = "track"
    assert track.name == "track"

    # Test gain property.
    track.gain = 3.0
    assert track.gain == 3.0

    # Test source property.
    track.source = SourceAudio()
    assert isinstance(track.source, SourceAudio)

    # Test filter property.
    track.filter = Filter()
    assert isinstance(track.filter, Filter)


def test_track_properties_exceptions():
    """Test Track properties' exceptions."""
    track = Track()

    # Test source setter exception (str instead a valid source type).
    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "Specified source must have a valid type \\(SourceSpectrum, SourceBroadbandNoise, "
            "SourceBroadbandNoiseTwoParameters, SourceHarmonics, SourceHarmoncisTwoParameters, or "
            "SourceAudio\\)."
        ),
    ):
        track.source = "InvalidType"

    # Test filter setter exception (str instead Filter).
    with pytest.raises(PyAnsysSoundException, match="Specified filter must be of type Filter."):
        track.filter = "InvalidType"


def test_track_set_from_generic_data_containers():
    """Test Track set_from_generic_data_containers method."""
    # Create generic data containers for the source and source control.
    source_control = SourceControlSpectrum(duration=3.0, method=Methods.Hybrid)
    source = SourceSpectrum(
        file_source=pytest.data_path_sound_composer_spectrum_source_in_container,
        source_control=source_control,
    )
    source_data, source_control_data = source.get_as_generic_data_containers()

    # Create a generic data container for the track.
    track_data = GenericDataContainer()
    track_data.set_property("track_name", "My track")
    track_data.set_property("track_gain", 15.6)
    track_data.set_property("track_type", 5)
    track_data.set_property("track_source", source_data)
    track_data.set_property("track_source_control", source_control_data)
    track_data.set_property("track_is_filter", 0)

    # Create a track and test method set_from_generic_data_container.
    track = Track()
    track.set_from_generic_data_containers(track_data)
    assert track.name == "My track"
    assert track.gain == 15.6
    assert isinstance(track.source, SourceSpectrum)
    assert len(track.source.source_spectrum_data.data) == len(source.source_spectrum_data.data)
    assert isinstance(track.source.source_control, SourceControlSpectrum)
    assert track.source.source_control.duration == 3.0
    assert track.source.source_control.method == Methods.Hybrid
    assert track.filter is None

    # Add a filter to the generic data container.
    op_frf = Operator("load_FRF_from_txt")
    op_frf.connect(0, pytest.data_path_filter_frf)
    op_frf.run()
    f_filter_frf: Field = op_frf.get_output(0, "field")

    track_data.set_property("track_is_filter", 1)
    track_data.set_property("track_filter", f_filter_frf)

    track.set_from_generic_data_containers(track_data)
    assert track.name == "My track"
    assert track.gain == 15.6
    assert isinstance(track.source, SourceSpectrum)
    assert len(track.source.source_spectrum_data.data) == len(source.source_spectrum_data.data)
    assert isinstance(track.source.source_control, SourceControlSpectrum)
    assert track.source.source_control.duration == 3.0
    assert track.source.source_control.method == Methods.Hybrid
    assert isinstance(track.filter, Filter)


def test_track_get_as_generic_data_containers():
    """Test Track get_as_generic_data_containers method."""
    # Create a source and a source control.
    source_control = SourceControlSpectrum(duration=3.0, method=Methods.Hybrid)
    source = SourceSpectrum(
        file_source=pytest.data_path_sound_composer_spectrum_source_in_container,
        source_control=source_control,
    )

    # Create a track (no filter).
    track = Track(
        name="My track",
        gain=15.6,
        source=source,
    )

    # Test method get_as_generic_data_containers.
    track_data = track.get_as_generic_data_containers()
    assert set(track_data.get_property_description()) == {
        "track_name",
        "track_gain",
        "track_type",
        "track_source",
        "track_source_control",
        "track_is_filter",
    }
    assert track_data.get_property("track_name") == "My track"
    assert track_data.get_property("track_gain") == 15.6
    assert track_data.get_property("track_type") == 5
    assert isinstance(track_data.get_property("track_source"), GenericDataContainer)
    assert isinstance(track_data.get_property("track_source_control"), GenericDataContainer)
    assert track_data.get_property("track_is_filter") == 0

    # Add a filter to the track.
    track.filter = Filter(a_coefficients=[1.0], b_coefficients=[1.0, 0.5])

    # Test method get_as_generic_data_containers again.
    track_data = track.get_as_generic_data_containers()
    assert set(track_data.get_property_description()) == {
        "track_name",
        "track_gain",
        "track_type",
        "track_source",
        "track_source_control",
        "track_is_filter",
        "track_filter",
    }
    assert track_data.get_property("track_name") == "My track"
    assert track_data.get_property("track_gain") == 15.6
    assert track_data.get_property("track_type") == 5
    assert isinstance(track_data.get_property("track_source"), GenericDataContainer)
    assert isinstance(track_data.get_property("track_source_control"), GenericDataContainer)
    assert track_data.get_property("track_is_filter") == 1
    assert isinstance(track_data.get_property("track_filter"), Field)


def test_track_get_as_generic_data_containers_warning():
    """Test Track get_as_generic_data_containers method's warning."""
    # Create a track.
    track = Track()

    # Test method get_as_generic_data_containers.
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Cannot create track generic data container because there is no source.",
    ):
        track_data = track.get_as_generic_data_containers()
    assert track_data is None


def test_track_process():
    """Test Track process method (no resample needed)."""
    track = Track(
        gain=3.0,
        source=SourceSpectrum(
            file_source=pytest.data_path_sound_composer_spectrum_source_in_container,
            source_control=SourceControlSpectrum(duration=3.0, method=Methods.Hybrid),
        ),
        filter=Filter(a_coefficients=[1.0], b_coefficients=[1.0, 0.5]),
    )
    track.process()
    assert track._output is not None


def test_track_process_exceptions():
    """Test Track process method exceptions."""
    # Test process method exception1 (source not set).
    track = Track()
    with pytest.raises(
        PyAnsysSoundException,
        match="Source is not set. Use Track.source.",
    ):
        track.process()

    # Test process method exception2 (invalid sampling frequency value).
    track = Track()
    with pytest.raises(
        PyAnsysSoundException, match="Sampling frequency must be strictly positive."
    ):
        track.process(sampling_frequency=0.0)

    # Test process method exception3 (sampling frequency value mismatch).
    track = Track()
    track.filter = Filter(sampling_frequency=48000.0)
    with pytest.raises(
        PyAnsysSoundException,
        match=(
            "Specified sampling frequency must be equal to that which is stored in the track's "
            "filter."
        ),
    ):
        track.process(sampling_frequency=44100.0)


def test_track_get_output():
    """Test Track get_output method."""
    track = Track(
        gain=3.0,
        source=SourceSpectrum(
            file_source=pytest.data_path_sound_composer_spectrum_source_in_container,
            source_control=SourceControlSpectrum(duration=3.0, method=Methods.Hybrid),
        ),
        filter=Filter(a_coefficients=[1.0], b_coefficients=[1.0, 0.5]),
    )
    track.process(sampling_frequency=44100.0)

    output_signal = track.get_output()
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


def test_track_get_output_unprocessed():
    """Test Track get_output method's exception."""
    track = Track()
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the Track.process\\(\\) method.",
    ):
        output_signal = track.get_output()
    assert output_signal is None


def test_track_get_output_as_nparray():
    """Test Track get_output_as_nparray method."""
    track = Track(
        gain=3.0,
        source=SourceSpectrum(
            file_source=pytest.data_path_sound_composer_spectrum_source_in_container,
            source_control=SourceControlSpectrum(duration=3.0, method=Methods.Hybrid),
        ),
        filter=Filter(a_coefficients=[1.0], b_coefficients=[1.0, 0.5]),
    )
    track.process(sampling_frequency=44100.0)

    output_signal = track.get_output_as_nparray()
    assert isinstance(output_signal, np.ndarray)
    assert len(output_signal) == pytest.approx(44100.0 * 3.0)


def test_track_get_output_as_nparray_unprocessed():
    """Test Track get_output_as_nparray method's exception."""
    track = Track()
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the Track.process\\(\\) method.",
    ):
        output_signal = track.get_output_as_nparray()
    assert isinstance(output_signal, np.ndarray)
    assert len(output_signal) == 0


@patch("matplotlib.pyplot.show")
def test_track_plot(mock_show):
    """Test Track plot method."""
    # We need create a suitable source control first.
    f_control = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
    f_control.append([1, 3, 6, 10], 1)
    support = TimeFreqSupport()
    f_time = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
    f_time.append([0, 1, 2, 3], 1)
    support.time_frequencies = f_time
    f_control.time_freq_support = support

    # Create a SourceControlTime object.
    source_control = SourceControlTime()
    source_control.control = f_control

    track = Track(
        gain=3.0,
        source=SourceBroadbandNoise(
            file=pytest.data_path_sound_composer_bbn_source_in_container,
            source_control=source_control,
        ),
        filter=Filter(a_coefficients=[1.0], b_coefficients=[1.0, 0.5]),
    )
    track.process(sampling_frequency=44100.0)
    track.plot()


def test_track_plot_exceptions():
    """Test Track plot method's exception."""
    track = Track()
    with pytest.raises(
        PyAnsysSoundException,
        match="Output is not processed yet. Use the Track.process\\(\\) method.",
    ):
        track.plot()
