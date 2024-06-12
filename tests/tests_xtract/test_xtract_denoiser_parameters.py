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
import numpy as np
import pytest

from ansys.sound.core._pyansys_sound import PyAnsysSoundException
from ansys.sound.core.signal_utilities import LoadWav
from ansys.sound.core.xtract.xtract_denoiser_parameters import XtractDenoiserParameters


def test_xtract_denoiser_parameters_instantiation(dpf_sound_test_server):
    xtract_denoiser_parameters = XtractDenoiserParameters()
    assert xtract_denoiser_parameters != None


def test_xtract_denoiser_parameters_getter_setter_upper_threshold(dpf_sound_test_server):
    xtract_denoiser_parameters = XtractDenoiserParameters()

    # Invalid value
    with pytest.raises(PyAnsysSoundException) as excinfo:
        xtract_denoiser_parameters.noise_psd = None
    assert str(excinfo.value) == "Noise PSD must be a non-empty Field."

    xtract_denoiser_parameters.noise_psd = Field()

    assert type(xtract_denoiser_parameters.noise_psd) == Field


def test_xtract_denoiser_parameters_getter_generic_data_container(dpf_sound_test_server):
    xtract_denoiser_parameters = XtractDenoiserParameters()

    gdc = xtract_denoiser_parameters.get_parameters_as_generic_data_container()
    assert gdc is not None


def test_xtract_denoiser_parameters_generate_noise_psd_from_white_noise_level(
    dpf_sound_test_server,
):
    xtract_denoiser_parameters = XtractDenoiserParameters()

    noise_psd = xtract_denoiser_parameters.create_noise_psd_from_white_noise_level(
        white_noise_level=(40.0), sampling_frequency=44100.0, window_length=50
    )

    noise = noise_psd.data

    s = np.sum(noise)
    assert s == pytest.approx(464.853)


def test_xtract_denoiser_parameters_generate_noise_psd_from_automatic_estimation(
    dpf_sound_test_server,
):
    wav_loader = LoadWav(pytest.data_path_white_noise_in_container)
    wav_loader.process()
    fc_signal = wav_loader.get_output()
    xtract_denoiser_parameters = XtractDenoiserParameters()

    noise_psd = xtract_denoiser_parameters.create_noise_psd_from_automatic_estimation(fc_signal[0])

    noise = noise_psd.data

    s = np.sum(noise)
    assert s == pytest.approx(0.005321223133933017)


def test_xtract_denoiser_parameters_generate_noise_psd_from_noise_samples(
    dpf_sound_test_server,
):
    wav_loader = LoadWav(pytest.data_path_white_noise_in_container)
    wav_loader.process()
    fc_signal = wav_loader.get_output()
    xtract_denoiser_parameters = XtractDenoiserParameters()

    noise_psd = xtract_denoiser_parameters.create_noise_psd_from_noise_samples(
        fc_signal[0], 44100.0
    )

    noise = noise_psd.data

    s = np.sum(noise)
    assert s == pytest.approx(0.0025502318834469406)
