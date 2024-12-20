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

"""
.. _calculate_PR_and_TNR:

Calculate TNR and PR
--------------------

This example shows how to calculate tone-to-noise ratio (TNR) and prominence
ratio (PR) following the ECMA 418-1 and ISO 7779 standards. It also extracts
the desired TNR and PR information.
"""

# %%
# Set up analysis
# ~~~~~~~~~~~~~~~
# Setting up the analysis consists of loading Ansys libraries, connecting to the
# DPF server, and retrieving the example files.

# Load Ansys libraries.
from ansys.dpf.core import TimeFreqSupport, fields_factory, locations
import numpy as np

from ansys.sound.core.examples_helpers import download_flute_psd, download_flute_wav
from ansys.sound.core.psychoacoustics import ProminenceRatio, ToneToNoiseRatio
from ansys.sound.core.server_helpers import connect_to_or_start_server
from ansys.sound.core.signal_utilities import LoadWav
from ansys.sound.core.spectral_processing import PowerSpectralDensity

# Connect to a remote server or start a local server.
my_server = connect_to_or_start_server(use_license_context=True)

# %%
# Calculate TNR from a PSD
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Load a power spectral density (PSD) stored as a text file and then use it to create
# a field that serves as an input for the TNR calculation.

# Load the PSD contained in an ASCII file. This file has two columns: 'Frequency (Hz)'
# and 'PSD amplitude (dB SPL/Hz)'. The data is located in
# "C:\Users\username\AppData\Local\Ansys\ansys_sound_core\examples\".
path_flute_psd = download_flute_psd()
fid = open(path_flute_psd)
fid.readline()  # Skip the first line (header)
all_lines = fid.readlines()
fid.close()

# Create the array of PSD amplitude values.
psd_dBSPL_per_Hz = []
frequencies_original = []
for line in all_lines:
    splitted_line = line.split()
    psd_dBSPL_per_Hz.append(float(splitted_line[1]))
    frequencies_original.append(float(splitted_line[0]))

# Convert amplitudes in dBSPL/Hz into power in Pa^2/Hz.
psd_dBSPL_per_Hz = np.array(psd_dBSPL_per_Hz)
psd_Pa2_per_Hz = np.power(10, psd_dBSPL_per_Hz / 10) * 4e-10

# The TNR/PR operators require the frequency array to be regularly spaced.
# Thus, the original frequencies are interpolated to regularly spaced points.
frequencies_interp = np.linspace(0, 22050, len(frequencies_original))
psd_Pa2_per_Hz_interp = np.interp(frequencies_interp, frequencies_original, psd_Pa2_per_Hz)

# Create the input PSD field for computation of TNR and PR.
f_psd = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
f_psd.append(psd_Pa2_per_Hz_interp, 1)

# Create and include a field containing the array of frequencies.
support = TimeFreqSupport()
f_frequencies = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
f_frequencies.append(frequencies_interp, 1)
support.time_frequencies = f_frequencies
f_psd.time_freq_support = support

# %%
# Create a ``ToneToNoiseRatio`` object, set the created PSD field as input, and compute the TNR.
tone_to_noise_ratio = ToneToNoiseRatio(psd=f_psd)
tone_to_noise_ratio.process()

# %%
# Print results.
number_tones = tone_to_noise_ratio.get_nb_tones()
TNR = tone_to_noise_ratio.get_max_TNR_value()
TNR_frequencies = tone_to_noise_ratio.get_peaks_frequencies()
TNR_values = tone_to_noise_ratio.get_TNR_values()
TNR_levels = tone_to_noise_ratio.get_peaks_levels()

print(
    f"\n"
    f"Number of tones found: {number_tones}\n"
    f"Maximum TNR value: {np.round(TNR, 1)} dB\n"
    f"All detected peaks' frequencies (Hz): "
    f"{np.round(TNR_frequencies)}\n"
    f"All peaks' TNR values (dB): {np.round(TNR_values, 1)}\n"
    f"All peaks' absolute levels (dB SPL): {np.round(TNR_levels, 1)}\n"
)

# %%
# Plot the TNR over frequency.
tone_to_noise_ratio.plot()

# %%
# Recalculate the TNR for specific frequencies.
frequencies_i = [261, 525, 786, 1836]
tone_to_noise_ratio = ToneToNoiseRatio(psd=f_psd, frequency_list=frequencies_i)
tone_to_noise_ratio.process()

# %%
# Print information for a specific detected peak.
tone_to_noise_ratio_525 = tone_to_noise_ratio.get_single_tone_info(tone_index=1)
TNR_frequency = tone_to_noise_ratio_525[0]
TNR_width = tone_to_noise_ratio_525[4] - tone_to_noise_ratio_525[3]
TNR = tone_to_noise_ratio_525[1]
print(
    f"\n"
    f"TNR info for peak at ~525 Hz: \n"
    f"Exact tone frequency: {round(TNR_frequency, 2)} Hz\n"
    f"Tone width: {round(TNR_width, 2)} Hz\n"
    f"TNR value: {round(TNR, 2)} dB\n\n"
)

# %%
# Calculate PR from a PSD
# ~~~~~~~~~~~~~~~~~~~~~~~
# Use the PowerSpectralDensity class to calculate a PSD, and compute Prominence Ratio (PR).

# Load example data from WAV file.
path_flute_wav = download_flute_wav(server=my_server)
wav_loader = LoadWav(path_flute_wav)
wav_loader.process()
flute_signal = wav_loader.get_output()[0]

# %%
# Create a PowerSpectralDensity object, set its input signal and parameters, and compute the PSD.
psd_object = PowerSpectralDensity(
    flute_signal, fft_size=8192, window_type="HANN", window_length=8192, overlap=0.8
)
psd_object.process()

# %%
# Get the computed PSD as a Field.
f_psd = psd_object.get_output()

# %%
# Create a ProminenceRatio object, set the computed PSD as input, and compute the PR.
prominence_ratio = ProminenceRatio(psd=f_psd)
prominence_ratio.process()

# %%
# Print the results.
number_tones = prominence_ratio.get_nb_tones()
PR = prominence_ratio.get_max_PR_value()
PR_frequencies = prominence_ratio.get_peaks_frequencies()
PR_values = prominence_ratio.get_PR_values()
PR_levels = prominence_ratio.get_peaks_levels()
print(
    f"\n"
    f"Number of tones found: {number_tones}\n"
    f"Maximum PR value: {np.round(PR, 1)} dB\n"
    f"All detected peaks' frequencies (Hz): {np.round(PR_frequencies)}\n"
    f"All peaks' PR values (dB): {np.round(PR_values, 1)}\n"
    f"All peaks' absolute levels (dB SPL): {np.round(PR_levels, 1)}\n"
)

# %%
# Plot the PR as a function of frequency.
prominence_ratio.plot()

# %%
# Recalculate the PR for specific frequencies.
frequencies_i = [261, 525, 786, 1836]
prominence_ratio = ProminenceRatio(psd=f_psd, frequency_list=frequencies_i)
prominence_ratio.process()

# %%
# Print information for a specific detected peak.
prominence_ratio_786 = prominence_ratio.get_single_tone_info(tone_index=2)
PR_frequency = prominence_ratio_786[0]
PR_width = prominence_ratio_786[4] - prominence_ratio_786[3]
PR = prominence_ratio_786[1]
print(
    f"\n"
    f"PR info for peak at ~786 Hz: \n"
    f"Exact tone frequency: {round(PR_frequency, 2)} Hz\n"
    f"Tone width: {round(PR_width, 2)} Hz\n"
    f"PR value: {round(PR, 2)} dB\n"
)
