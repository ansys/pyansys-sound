# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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
.. _isolate_orders_example:

Isolate orders
--------------

Orders are harmonic and partial components in the sound related to the speed of a
rotating machine. This example shows how to isolate orders in a signal containing an RPM profile.
It also uses additional classes from PyAnsys Sound to compute spectrograms
and the loudness of the isolated signals.
"""

# %%
# Set up analysis
# ~~~~~~~~~~~~~~~
# Setting up the analysis consists of loading the required libraries, connecting to the
# DPF server, and retrieving the example files.
#

# Load standard libraries.
import matplotlib.pyplot as plt
import numpy as np

# Load Ansys libraries.
from ansys.sound.core import REFERENCE_ACOUSTIC_PRESSURE_IN_AIR
from ansys.sound.core.examples_helpers import (
    download_accel_with_rpm_2_wav,
    download_accel_with_rpm_3_wav,
    download_accel_with_rpm_wav,
)
from ansys.sound.core.order_analysis import IsolateOrders
from ansys.sound.core.psychoacoustics import LoudnessISO532_1_Stationary
from ansys.sound.core.server_helpers import connect_to_or_start_server
from ansys.sound.core.signal_utilities import LoadWav, WriteWav
from ansys.sound.core.spectrogram_processing import Stft

# sphinx_gallery_start_ignore
# sphinx_gallery_thumbnail_path = '_static/_image/example004_thumbnail.png'
# sphinx_gallery_end_ignore

# Connect to a remote DPF server or start a local DPF server.
my_server, my_license_context = connect_to_or_start_server(use_license_context=True)


# %%
# Load a signal with an RPM profile
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Load a signal from a WAV file using the :class:`.LoadWav` class.
# This class contains two channels:
#
# - The actual signal (an acceleration recording)
# - The associated RPM profile

# Return the input data of the example file.
path_accel_wav = download_accel_with_rpm_wav(server=my_server)

# Load the WAV file.
wav_loader = LoadWav(path_accel_wav)
wav_loader.process()

# Extract the audio signal and the RPM profile.
signal, rpm_profile = wav_loader.get_output()
fs = wav_loader.get_sampling_frequency()

# Extract time support associated with the signal.
time = signal.time_freq_support.time_frequencies

# Plot the signal and its associated RPM profile.
fig, ax = plt.subplots(nrows=2, sharex=True)
ax[0].plot(time.data, signal.data)
ax[0].set_title("Audio Signal")
ax[0].set_ylabel(f"Amplitude ({signal.unit})")
ax[0].grid(True)
ax[1].plot(time.data, rpm_profile.data, color="red")
ax[1].set_title("RPM profile")
ax[1].set_ylabel(f"RPM")
ax[1].grid(True)
plt.xlabel(f"Time ({time.unit})")
plt.show()

# %%
# Plot spectrogram of the original signal
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Plot the spectrogram of the original signal.

stft = Stft(signal=signal, window_overlap=0.9, fft_size=8192)
stft.process()
max_stft_dBSPL = 20 * np.log10(np.max(stft.get_magnitude()) / REFERENCE_ACOUSTIC_PRESSURE_IN_AIR)
max_frequency_Hz = 2000.0
stft.plot_magnitude_dB(
    reference_value=REFERENCE_ACOUSTIC_PRESSURE_IN_AIR,
    max_dB=max_stft_dBSPL,
    max_frequency=max_frequency_Hz,
)

# %%
# Isolate orders
# ~~~~~~~~~~~~~~
# Isolate orders 2, 4, and 6 with the :class:`.IsolateOrders` class.

rpm_profile = wav_loader.get_output()[1]

# Define parameters for order isolation
order_to_isolate = [2, 4, 6]  # Orders indexes to isolate as a list
fft_size = 8192  # FFT Size (in samples)
window_type = "HANN"  # Window type
window_overlap = 0.9  # Window overlap
width_selection = 3  # Width of the order selection in Hz

# Instantiate the :class:`.IsolateOrders` class with the parameters.
isolate_orders = IsolateOrders(
    signal=signal,
    rpm_profile=rpm_profile,
    orders=order_to_isolate,
    fft_size=fft_size,
    window_type=window_type,
    window_overlap=window_overlap,
    width_selection=width_selection,
)

# Isolate orders.
isolate_orders.process()

# Plot the spectrogram of the isolated orders.
stft.signal = isolate_orders.get_output()
stft.process()
stft.plot_magnitude_dB(
    reference_value=REFERENCE_ACOUSTIC_PRESSURE_IN_AIR,
    max_dB=max_stft_dBSPL,
    max_frequency=max_frequency_Hz,
)

# %%
# Isolate different orders
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Change FFT size, order indexes, and window type. Then re-isolate the orders.

# Change some parameters directly using the setters of the class.
isolate_orders.orders = [2, 6]
isolate_orders.window_type = "BLACKMAN"

# Reprocess (Must be called explicitly. Otherwise, the output won't be updated).
isolate_orders.process()

# Plot the spectrogram of the isolated orders.
stft.signal = isolate_orders.get_output()
stft.process()
stft.plot_magnitude_dB(
    reference_value=REFERENCE_ACOUSTIC_PRESSURE_IN_AIR,
    max_dB=max_stft_dBSPL,
    max_frequency=max_frequency_Hz,
)

# %%
# Work with the isolated signal
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Plot the signal containing the isolated orders and compute its loudness.

# Plot the signal directly using the method from the :class:`.IsolateOrders` class.
isolate_orders.plot()

# Use the :class:`.LoudnessISO532_1_Stationary` class to compute the loudness of the order-isolated
# signal.
signal_isolated = isolate_orders.get_output()
signal_isolated.unit = "Pa"
loudness = LoudnessISO532_1_Stationary(signal=signal_isolated)
loudness.process()

loudness_level_isolated_signal = loudness.get_loudness_level_phon()

# Compute the loudness for the original signal.
loudness.signal = signal
loudness.process()

loudness_level_original_signal = loudness.get_loudness_level_phon()

print(f"The loudness level of the original signal is {loudness_level_original_signal:.1f} phons.")
print(f"The loudness level of the isolated signal is {loudness_level_isolated_signal:.1f} phons.")

# %%
# Isolate orders of several signals in a loop
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Loop over a list of given signals and write them as a WAV file.

path_accel_wav_2 = download_accel_with_rpm_2_wav(server=my_server)
path_accel_wav_3 = download_accel_with_rpm_3_wav(server=my_server)
paths = (path_accel_wav, path_accel_wav_2, path_accel_wav_3)

fft_sizes = [256, 2048, 4096]

wav_writer = WriteWav()

# Isolate orders for all the files containing RPM profiles in this folder.
for file, fft_sz in zip(paths, fft_sizes):
    # Load the file.
    wav_loader.path_to_wav = file
    wav_loader.process()

    # Set parameters for order isolation.
    isolate_orders.signal = wav_loader.get_output()[0]
    isolate_orders.rpm_profile = wav_loader.get_output()[1]
    isolate_orders.fft_size = fft_sz
    isolate_orders.process()

    # Write as a WAV file.
    path_to_write = file[:-4] + "_isolated_fft_size_" + str(fft_sz) + ".wav"
    wav_writer.path_to_write = str(path_to_write)
    wav_writer.signal = isolate_orders.get_output()
    wav_writer.process()
