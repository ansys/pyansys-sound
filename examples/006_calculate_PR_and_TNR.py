"""
.. _calculate_PR_and_TNR:

Calculate tone-to-noise ratio and prominence ratio
--------------------------------------------------

This example shows how to calculate tone-to-noise ratio (TNR) and prominence ratio (PR), following
standards ECMA 418-1 and ISO 7779, and extract the desired TNR/PR info.
"""
# %%
# Set up analysis
# ~~~~~~~~~~~~~~~
# Setting up the analysis consists of loading Ansys libraries, connecting to the
# DPF server, and retrieving the example files.

# Load Ansys libraries.

from ansys.dpf.core import TimeFreqSupport, fields_factory, locations
import numpy as np

from ansys.dpf.sound.examples_helpers import get_absolute_path_for_flute_psd_txt
from ansys.dpf.sound.psychoacoustics import ProminenceRatio, ToneToNoiseRatio
from ansys.dpf.sound.server_helpers import connect_to_or_start_server

# Connect to remote or start a local server.
server = connect_to_or_start_server()

# %%
# Calculate TNR from a power spectral density (PSD)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Load a PSD stored in a text file, and use it to create a field that will serve as an input for
# the TNR calculation.

# Load the PSD contained in an ASCII file (2 columns: Frequency (Hz); PSD amplitude (dB SPL/Hz)).
path_flute_psd = get_absolute_path_for_flute_psd_txt()
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

# The TNR/PR operators require the frequency array to be strictly regularly spaced.
# So the original frequencies are interpolated to regularly spaced points.
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
# Create a ToneToNoiseRatio object, set the created PSD field as input, and compute TNR.
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
# Plot TNR over frequency.
tone_to_noise_ratio.plot()

# %%
# Recalculate tone-to-noise ratio for specific frequencies.
frequencies_i = [261, 525, 786, 1836]
tone_to_noise_ratio = ToneToNoiseRatio(psd=f_psd, frequency_list=frequencies_i)
tone_to_noise_ratio.process()

# %%
# Print info for a specific detected peak.
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
# Calculate PR from a power spectral density (PSD)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create a ProminenceRatio object, set the same created PSD field as input, and compute PR.
prominence_ratio = ProminenceRatio(psd=f_psd)
prominence_ratio.process()

# %%
# Print results.
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
# Plot PR over frequency.
prominence_ratio.plot()

# %%
# Recalculate tone-to-noise ratio for specific frequencies.
frequencies_i = [261, 525, 786, 1836]
prominence_ratio = ProminenceRatio(psd=f_psd, frequency_list=frequencies_i)
prominence_ratio.process()

# %%
# Print info for a specific detected peak.
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
