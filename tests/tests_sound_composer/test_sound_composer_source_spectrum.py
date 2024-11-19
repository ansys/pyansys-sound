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

from ansys.dpf.core import Field
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ansys.sound.core.sound_composer import SourceControlSpectrum, SourceSpectrum

EXP_SPECTRUM_DATA3 = 3.4100000858306885
EXP_OUTPUT_DATA5 = 0.0
EXP_STR_NOT_SET = "Spectrum source: Not set\nSource control: Not set/valid"
EXP_STR_ALL_SET = (
    "Spectrum source: 'toto'\n"
    "\tFmax: 22050 Hz\n"
    "\tDeltaF: 1 Hz\n"
    "Source control: (IFFT, 1.0 s)"
)


def test_source_spectrum_instantiation_no_arg(dpf_sound_test_server):
    """Test SourceSpectrum instantiation without arguments."""
    # Test instantiation.
    source_spectrum = SourceSpectrum()
    assert isinstance(source_spectrum, SourceSpectrum)
    assert source_spectrum.source_spectrum_data is None


def test_source_spectrum_instantiation_file_arg(dpf_sound_test_server):
    """Test SourceSpectrum instantiation with file argument."""
    # Test instantiation.
    source_spectrum = SourceSpectrum(pytest.data_path_sound_composer_spectrum_source_in_container)
    assert isinstance(source_spectrum, SourceSpectrum)
    assert source_spectrum.source_spectrum_data is not None


def test_source_spectrum___str___not_set(dpf_sound_test_server):
    """Test SourceSpectrum __str__ method when nothing is set."""
    source_spectrum = SourceSpectrum()
    assert str(source_spectrum) == EXP_STR_NOT_SET


def test_source_spectrum___str___all_set(dpf_sound_test_server):
    """Test SourceSpectrum __str__ method when all data are set."""
    source_spectrum = SourceSpectrum(
        pytest.data_path_sound_composer_spectrum_source_in_container,
        SourceControlSpectrum(duration=1.0),
    )
    assert str(source_spectrum) == EXP_STR_ALL_SET


def test_source_spectrum_properties(dpf_sound_test_server):
    """Test SourceSpectrum properties."""
    source_spectrum = SourceSpectrum()

    # Test source_control property.
    source_spectrum.source_control = SourceControlSpectrum()
    assert isinstance(source_spectrum.source_control, SourceControlSpectrum)

    # Test source_spectrum_data property.
    source_spectrum.source_spectrum_data = Field()
    assert isinstance(source_spectrum.source_spectrum_data, Field)


def test_source_spectrum_propertiess_exceptions(dpf_sound_test_server):
    """Test SourceSpectrum properties' exceptions."""
    source_spectrum = SourceSpectrum()

    # Test source_control setter exception (str instead of SourceControlSpectrum).
    with pytest.raises(
        PyAnsysSoundException,
        match="Specified source control object must be of type ``SourceControlSpectrum``.",
    ):
        source_spectrum.source_control = "InvalidType"

    # Test source_spectrum_data setter exception (str instead a Field).
    with pytest.raises(
        PyAnsysSoundException, match="Specified spectrum source must be provided as a DPF field."
    ):
        source_spectrum.source_spectrum_data = "InvalidType"


def test_source_spectrum_is_source_control_valid(dpf_sound_test_server):
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


def test_source_specrum_load_source(dpf_sound_test_server):
    """Test SourceSpectrum load_source method."""
    source_spectrum = SourceSpectrum()
    source_spectrum.load_source_spectrum(
        pytest.data_path_sound_composer_spectrum_source_in_container
    )
    assert isinstance(source_spectrum.source_spectrum_data, Field)
    assert source_spectrum.source_spectrum_data.data[3] == pytest.approx(EXP_SPECTRUM_DATA3)


def test_source_spectrum_load_source_exceptions(dpf_sound_test_server):
    """Test SourceSpectrum load_source method exceptions."""
    source_spectrum = SourceSpectrum()

    # Test load_source method exception.
    with pytest.raises(
        PyAnsysSoundException, match="Specified spectrum source file 'InvalidPath' does not exist."
    ):
        source_spectrum.load_source_spectrum("InvalidPath")
    assert source_spectrum.source_spectrum_data is None


def test_source_spectrum_process(dpf_sound_test_server):
    """Test SourceSpectrum process method."""
    source_spectrum = SourceSpectrum(
        pytest.data_path_sound_composer_spectrum_source_in_container,
        SourceControlSpectrum(duration=1.0),
    )
    source_spectrum.process()
    assert source_spectrum._output is not None


def test_source_spectrum_process_exceptions(dpf_sound_test_server):
    """Test SourceSpectrum process method exceptions."""
    source_spectrum = SourceSpectrum(pytest.data_path_sound_composer_spectrum_source_in_container)

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


def test_source_spectrum_get_output(dpf_sound_test_server):
    """Test SourceSpectrum get_output method."""
    source_spectrum = SourceSpectrum(
        pytest.data_path_sound_composer_spectrum_source_in_container,
        SourceControlSpectrum(duration=1.0),
    )
    source_spectrum.process()
    assert isinstance(source_spectrum.get_output(), Field)
    assert source_spectrum.get_output().data[5] == pytest.approx(EXP_OUTPUT_DATA5)


def test_source_spectrum_get_output_unprocessed(dpf_sound_test_server):
    """Test SourceSpectrum get_output method's exception."""
    source_spectrum = SourceSpectrum()
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the ``SourceSpectrum.process\\(\\)`` method.",
    ):
        output = source_spectrum.get_output()
    assert output is None


def test_source_spectrum_get_output_as_nparray(dpf_sound_test_server):
    """Test SourceSpectrum get_output_as_nparray method."""
    source_spectrum = SourceSpectrum(
        pytest.data_path_sound_composer_spectrum_source_in_container,
        SourceControlSpectrum(duration=1.0),
    )
    source_spectrum.process()
    assert source_spectrum.get_output_as_nparray()[5] == pytest.approx(EXP_OUTPUT_DATA5)


def test_source_spectrum_get_output_as_nparray_unprocessed(dpf_sound_test_server):
    """Test SourceSpectrum get_output_as_nparray method's exception."""
    source_spectrum = SourceSpectrum()
    with pytest.warns(
        PyAnsysSoundWarning,
        match="Output is not processed yet. Use the ``SourceSpectrum.process\\(\\)`` method.",
    ):
        output = source_spectrum.get_output_as_nparray()
    assert len(output) == 0


def test_source_spectrum_plot(dpf_sound_test_server):
    """Test SourceSpectrum plot method."""
    source_spectrum = SourceSpectrum(
        pytest.data_path_sound_composer_spectrum_source_in_container,
        SourceControlSpectrum(duration=1.0),
    )
    source_spectrum.process()
    source_spectrum.plot()


def test_source_spectrum_plot_exceptions(dpf_sound_test_server):
    """Test SourceSpectrum plot method's exception."""
    source_spectrum = SourceSpectrum()
    with pytest.raises(
        PyAnsysSoundException,
        match="Output is not processed yet. Use the 'SourceSpectrum.process\\(\\)' method.",
    ):
        source_spectrum.plot()
