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

from ansys.dpf.core import Field, TimeFreqSupport, fields_factory, locations
import numpy as np
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ansys.sound.core.signal_utilities import LoadWav
from ansys.sound.core.spectral_processing import PowerSpectralDensity
from ansys.sound.core.standard_levels import OverallLevelFromPSD

# Skip entire test module if server < 2026R1
if not pytest.SOUND_VERSION_GREATER_THAN_OR_EQUAL_TO_2027R1:
    pytest.skip("Requires Sound version >= 2027.1.0", allow_module_level=True)

EXP_STR_NOT_SET = (
    "OverallLevelFromPSD object.\nData\n\tPSD: Not set\n\tScale type: dB\n"
    "\tReference value: 1.0\n\tFrequency weighting: None\n"
    "Output level value: Not processed"
)
EXP_STR_ALL_SET = (
    'OverallLevelFromPSD object.\nData\n\tPSD: "Name of the PSD"\n\tScale type: RMS\n'
    "\tFrequency weighting: Not applicable\n"
    "Output level value: Not processed"
)
EXP_STR_ALL_PROCESSED = (
    'OverallLevelFromPSD object.\nData\n\tPSD: "Name of the PSD"\n\tScale type: dB\n'
    "\tReference value: 2e-05\n\tFrequency weighting: A\n"
    "Output level value: 81.2 dBA (re 2e-05)"
)

# Expected values for flute_nonUnitaryCalib PSD
EXP_LEVEL_DEFAULT = -5.63976  # dB with reference_value=1.0, no weighting
EXP_LEVEL_RMS = 0.52254
EXP_LEVEL_DBSPL = 88.345
EXP_LEVEL_DBA = 86.868
EXP_LEVEL_DBB = 88.135
EXP_LEVEL_DBC = 88.344
EXP_LEVEL_RMS_REGULAR = 1.600078
EXP_LEVEL_DBSPL_REGULAR = 98.06222
EXP_LEVEL_RMS_NONREGULAR = 2.879844
EXP_LEVEL_DBSPL_NONREGULAR = 103.1668
EXP_LEVEL_DBA_REGULAR = 97.61288869784109
EXP_LEVEL_DBB_REGULAR = 96.29682955410959
EXP_LEVEL_DBC_REGULAR = 96.30580391645842
EXP_LEVEL_DBA_NONREGULAR = 103.8890850917627
EXP_LEVEL_DBB_NONREGULAR = 102.35895548586012
EXP_LEVEL_DBC_NONREGULAR = 102.28886603807935


@pytest.fixture
def create_psd_from_txt_data():
    """Create a PSD DPF field from the flute_psd.txt test data file."""
    path_flute_psd = pytest.data_path_flute_psd_locally

    # Open a txt file for reading
    fid = open(path_flute_psd)

    # skip first line
    fid.readline()

    # read all other lines
    all_lines = fid.readlines()
    # close file
    fid.close()

    amplitudes = []

    for line in all_lines:
        splitted_line = line.split()
        amplitudes.append(float(splitted_line[1]))

    amplitudes = np.array(amplitudes)

    # convert dBSPL / Hz -> Pa^2/Hz
    amplitudes = np.power(10, amplitudes / 10)
    amplitudes = amplitudes * 2.0e-5
    amplitudes = amplitudes * 2.0e-5

    # for now, due to a sharp constraint on regularity of frequencies (1.0e-5) in the operator,
    # we cannot use those written in the file. Let's recreate them
    frequencies = np.linspace(0, 22050, len(amplitudes))

    psd = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
    psd.append(amplitudes, 1)
    support = TimeFreqSupport()
    frequencies_field = fields_factory.create_scalar_field(
        num_entities=1, location=locations.time_freq
    )
    frequencies_field.append(frequencies, 1)
    support.time_frequencies = frequencies_field

    psd.time_freq_support = support

    yield psd


@pytest.fixture
def create_psd_from_flute_nonUnitaryCalib():
    """Create a PSD DPF field by computing PSD from flute_nonUnitaryCalib.wav."""
    loader = LoadWav(pytest.data_path_flute_nonUnitaryCalib)
    loader.process()
    signal = loader.get_output()[0]

    psd_obj = PowerSpectralDensity(
        input_signal=signal,
        fft_size=8192,
        window_type="HANN",
        window_length=8192,
        overlap=0.5,
    )
    psd_obj.process()

    yield psd_obj.get_output()


@pytest.fixture
def create_psd_from_data():
    """Create a PSD DPF field from a two-column (frequency, amplitude) text data file.

    This fixture uses the *factory* pattern: it yields a callable ``_create(path)``
    instead of a ready-made object. This allows a single fixture to serve multiple
    tests that need PSD fields built from different files (e.g. regular vs. non-regular
    frequency grids), without duplicating the fixture body.

    Usage in a test::

        def test_something(create_psd_from_data):
            psd = create_psd_from_data(pytest.data_path_psd_regular)
            ...

    Supported file format:
        - One header line (skipped).
        - One data row per frequency bin: ``<frequency_Hz>  <amplitude_Pa2_per_Hz>``.
        - Amplitudes are assumed to be already in Pa²/Hz (no unit conversion applied).
    """

    def _create(path):
        # --- Read the text file ---
        fid = open(path)
        fid.readline()  # skip header line
        all_lines = fid.readlines()
        fid.close()

        frequencies = []
        amplitudes = []

        for line in all_lines:
            splitted_line = line.split()
            frequencies.append(float(splitted_line[0]))
            amplitudes.append(float(splitted_line[1]))

        frequencies = np.array(frequencies)
        amplitudes = np.array(amplitudes)

        # It is supposed that data is already in Pa²/Hz — no conversion is done.

        # --- Build the DPF field ---
        # The PSD values are stored as a scalar field in the time_freq location,
        # which is the standard DPF container for spectral data.
        psd = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
        psd.append(amplitudes, 1)

        # Attach the frequency axis via a TimeFreqSupport so that the DPF operator
        # can retrieve the bin spacing (regular or non-regular).
        support = TimeFreqSupport()
        frequencies_field = fields_factory.create_scalar_field(
            num_entities=1, location=locations.time_freq
        )
        frequencies_field.append(frequencies, 1)
        support.time_frequencies = frequencies_field

        psd.time_freq_support = support

        return psd

    # Yield the factory so pytest manages the fixture lifetime while letting each
    # test call _create() as many times as needed with different paths.
    yield _create


def test_overall_level_from_psd_instantiation():
    """Test OverallLevelFromPSD instantiation."""
    level_obj = OverallLevelFromPSD()
    assert level_obj.psd is None
    assert level_obj.scale == "dB"
    assert level_obj.reference_value == 1.0
    assert level_obj.frequency_weighting == ""


def test_overall_level_from_psd_properties():
    """Test OverallLevelFromPSD properties."""
    level_obj = OverallLevelFromPSD()
    level_obj.psd = Field()
    assert type(level_obj.psd) == Field

    level_obj.scale = "RMS"
    assert level_obj.scale == "RMS"

    level_obj.reference_value = 2e-5
    assert level_obj.reference_value == 2e-5

    level_obj.frequency_weighting = "A"
    assert level_obj.frequency_weighting == "A"


def test_overall_level_from_psd_properties_exceptions():
    """Test OverallLevelFromPSD properties exceptions."""
    level_obj = OverallLevelFromPSD()
    with pytest.raises(
        PyAnsysSoundException,
        match="The input PSD must be provided as a DPF field.",
    ):
        level_obj.psd = "InvalidType"

    with pytest.raises(PyAnsysSoundException, match="The scale type must be either 'dB' or 'RMS'."):
        level_obj.scale = "Invalid"

    with pytest.raises(
        PyAnsysSoundException, match="The reference value must be strictly positive."
    ):
        level_obj.reference_value = -1

    with pytest.raises(
        PyAnsysSoundException,
        match="The frequency weighting must be one of \\['', 'A', 'B', 'C'\\].",
    ):
        level_obj.frequency_weighting = "Invalid"


def test_overall_level_from_psd___str__(create_psd_from_txt_data):
    """Test OverallLevelFromPSD __str__ method."""
    level_obj = OverallLevelFromPSD()
    assert str(level_obj) == EXP_STR_NOT_SET

    psd = create_psd_from_txt_data
    psd.name = "Name of the PSD"

    level_obj.psd = psd
    level_obj.scale = "RMS"
    level_obj.frequency_weighting = "A"
    assert str(level_obj) == EXP_STR_ALL_SET

    level_obj.process()
    assert str(level_obj) == (
        'OverallLevelFromPSD object.\nData\n\tPSD: "Name of the PSD"\n\tScale type: RMS\n'
        "\tFrequency weighting: Not applicable\n"
        f"Output level value: {level_obj.get_output():.1f} (RMS)"
    )

    level_obj.scale = "dB"
    level_obj.reference_value = 2e-5
    level_obj.process()
    assert str(level_obj) == EXP_STR_ALL_PROCESSED


def test_overall_level_from_psd_process(create_psd_from_txt_data):
    """Test OverallLevelFromPSD process method."""
    level_obj = OverallLevelFromPSD(psd=create_psd_from_txt_data)
    level_obj.process()
    assert level_obj.get_output() is not None


def test_overall_level_from_psd_process_exceptions():
    """Test OverallLevelFromPSD process method exceptions."""
    level_obj = OverallLevelFromPSD()
    with pytest.raises(
        PyAnsysSoundException,
        match="No input PSD is set. Use OverallLevelFromPSD.psd.",
    ):
        level_obj.process()


def test_overall_level_from_psd_get_output(create_psd_from_flute_nonUnitaryCalib):
    """Test OverallLevelFromPSD get_output method."""
    level_obj = OverallLevelFromPSD(psd=create_psd_from_flute_nonUnitaryCalib)
    level_obj.process()
    output = level_obj.get_output()
    assert type(output) == float

    # RMS
    level_obj.scale = "RMS"
    level_obj.process()
    assert level_obj.get_output() == pytest.approx(EXP_LEVEL_RMS, abs=1e-3)

    # dB SPL
    level_obj.scale = "dB"
    level_obj.reference_value = 2e-5
    level_obj.process()
    assert level_obj.get_output() == pytest.approx(EXP_LEVEL_DBSPL, abs=1e-3)

    # dBA
    level_obj.frequency_weighting = "A"
    level_obj.process()
    assert level_obj.get_output() == pytest.approx(EXP_LEVEL_DBA, abs=1e-3)

    # dBB
    level_obj.frequency_weighting = "B"
    level_obj.process()
    assert level_obj.get_output() == pytest.approx(EXP_LEVEL_DBB, abs=1e-3)

    # dBC
    level_obj.frequency_weighting = "C"
    level_obj.process()
    assert level_obj.get_output() == pytest.approx(EXP_LEVEL_DBC, abs=1e-3)


def test_overall_level_from_psd_get_output_regular(create_psd_from_data):
    """Test OverallLevelFromPSD get_output method with regular PSD data."""
    level_obj = OverallLevelFromPSD(psd=create_psd_from_data(pytest.data_path_psd_regular))

    # RMS
    level_obj.scale = "RMS"
    level_obj.process()
    assert level_obj.get_output() == pytest.approx(EXP_LEVEL_RMS_REGULAR, abs=1e-3)

    # dB SPL
    level_obj.scale = "dB"
    level_obj.reference_value = 2e-5
    level_obj.process()
    assert level_obj.get_output() == pytest.approx(EXP_LEVEL_DBSPL_REGULAR, abs=1e-3)

    # dBA
    level_obj.frequency_weighting = "A"
    level_obj.process()
    assert level_obj.get_output() == pytest.approx(EXP_LEVEL_DBA_REGULAR, abs=1e-3)

    # dBB
    level_obj.frequency_weighting = "B"
    level_obj.process()
    assert level_obj.get_output() == pytest.approx(EXP_LEVEL_DBB_REGULAR, abs=1e-3)

    # dBC
    level_obj.frequency_weighting = "C"
    level_obj.process()
    assert level_obj.get_output() == pytest.approx(EXP_LEVEL_DBC_REGULAR, abs=1e-3)


def test_overall_level_from_psd_get_output_nonregular(create_psd_from_data):
    """Test OverallLevelFromPSD get_output method with non-regular PSD data."""
    level_obj = OverallLevelFromPSD(psd=create_psd_from_data(pytest.data_path_psd_nonregular))

    # RMS
    level_obj.scale = "RMS"
    level_obj.process()
    assert level_obj.get_output() == pytest.approx(EXP_LEVEL_RMS_NONREGULAR, abs=1e-3)

    # dB SPL
    level_obj.scale = "dB"
    level_obj.reference_value = 2e-5
    level_obj.process()
    assert level_obj.get_output() == pytest.approx(EXP_LEVEL_DBSPL_NONREGULAR, abs=1e-3)

    # # dBA
    level_obj.frequency_weighting = "A"
    level_obj.process()
    assert level_obj.get_output() == pytest.approx(EXP_LEVEL_DBA_NONREGULAR, abs=1e-3)

    # # dBB
    level_obj.frequency_weighting = "B"
    level_obj.process()
    assert level_obj.get_output() == pytest.approx(EXP_LEVEL_DBB_NONREGULAR, abs=1e-3)

    # # dBC
    level_obj.frequency_weighting = "C"
    level_obj.process()
    assert level_obj.get_output() == pytest.approx(EXP_LEVEL_DBC_NONREGULAR, abs=1e-3)


def test_overall_level_from_psd_get_output_warnings():
    """Test OverallLevelFromPSD get_output method warnings."""
    level_obj = OverallLevelFromPSD()
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the OverallLevelFromPSD.process\\(\\) method.",
    ):
        output = level_obj.get_output()
    assert output is None


def test_overall_level_from_psd_get_output_as_nparray(create_psd_from_txt_data):
    """Test OverallLevelFromPSD get_output_as_nparray method."""
    level_obj = OverallLevelFromPSD(psd=create_psd_from_txt_data)
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the OverallLevelFromPSD.process\\(\\) method.",
    ):
        assert level_obj.get_output_as_nparray() is None

    level_obj.process()
    output = level_obj.get_output_as_nparray()
    assert type(output) == np.ndarray
    assert len(output) == 1


def test_overall_level_from_psd_get_level(create_psd_from_txt_data):
    """Test OverallLevelFromPSD get_level method."""
    level_obj = OverallLevelFromPSD(psd=create_psd_from_txt_data)
    level_obj.process()
    level = level_obj.get_level()
    assert type(level) == float
    assert level == level_obj.get_output()
