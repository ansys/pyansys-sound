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
.. _save_level_vs_rpm_of_several_orders_example:

Save the level vs RPM of several orders for the Sound Composer
----------------------------------------------------------------

Orders are harmonic and partial components in the sound related to the speed of a rotating
machine. This example shows how to compute the level over RPM of several orders of a signal
associated with an RPM profile, and how to save the result to a text file whose format (with the
``AnsysSound_Orders`` header) is compatible with the Sound Composer.

The resulting file can then be used to define a harmonics source in the Sound Composer, either with
the :class:`.SourceHarmonics` class of PyAnsys Sound, or with the Sound Composer module of Ansys
Sound SAS, in order to generate a sound corresponding to the identified orders.

This example also shows how to reload the saved file into a :class:`.SourceHarmonics` object,
and use it in a minimal :class:`.SoundComposer` project to synthesize a new sound driven by
an independent RPM profile. This illustrates a typical product simulation use case: orders
identified on an existing system can be reused to synthesize the acoustic behavior of that system
under different operating conditions, or of a product variant.

.. seealso::
    :ref:`sound_composer_create_project`
        Example demonstrating how to create a Sound Composer project, including a harmonics source.
"""

# Maximum frequency for STFT plots, change according to your need
MAX_FREQUENCY_PLOT_STFT = 2000.0

# %%
# Set up analysis
# ~~~~~~~~~~~~~~~
# Setting up the analysis consists of loading the required libraries, connecting to the DPF server,
# and retrieving the example file.

# Load standard libraries.
import matplotlib.pyplot as plt
import numpy as np

# Load Ansys libraries.
from ansys.sound.core import REFERENCE_ACOUSTIC_PRESSURE_IN_AIR
from ansys.sound.core.examples_helpers import download_accel_with_rpm_wav
from ansys.sound.core.order_analysis import OrderLevels
from ansys.sound.core.server_helpers import connect_to_or_start_server
from ansys.sound.core.signal_utilities import LoadWav, WriteWav
from ansys.sound.core.sound_composer import (
    SoundComposer,
    SourceControlTime,
    SourceHarmonics,
    Track,
)
from ansys.sound.core.spectrogram_processing import Stft

# Connect to a remote DPF server or start a local DPF server.
my_server, my_license_context = connect_to_or_start_server(use_license_context=True)


# %%
# Define custom STFT plot function
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Define a custom function for STFT plots. It differs from the ``Stft.plot()`` method in that it
# does not display the phase and allows setting custom title, maximum SPL, and maximum frequency.
def plot_stft(
    stft: Stft,
    fs: float,
    SPLmax: float,
    title: str = "STFT",
    maximum_frequency: float = MAX_FREQUENCY_PLOT_STFT,
) -> None:
    """Plot a short-term Fourier transform (STFT) into a figure window.

    Parameters
    ----------
    stft: Stft
        Object containing the STFT.
    fs: float
        Sampling frequency of the signal in Hz.
    SPLmax: float
        Maximum value (here in dB SPL) for the colormap.
    title: str, default: "STFT"
        Title of the figure.
    maximum_frequency: float, default: MAX_FREQUENCY_PLOT_STFT
        Maximum frequency in Hz to display.
    """
    magnitude = stft.get_stft_magnitude_as_nparray()
    magnitude_unit = stft.get_output()[0].unit
    if isinstance(magnitude_unit, tuple):
        magnitude_unit = magnitude_unit[1]
    frequency_unit = stft.get_output()[0].time_freq_support.time_frequencies.unit
    time_unit = stft.get_output().time_freq_support.time_frequencies.unit

    # Only extract the first half of the STFT, as it is symmetrical
    half_nfft = int(magnitude.shape[0] / 2) + 1

    # Voluntarily ignore a numpy warning
    np.seterr(divide="ignore")
    magnitude = 20 * np.log10(magnitude[0:half_nfft, :])
    np.seterr(divide="warn")

    # Obtain sampling frequency, time steps, and number of time samples
    time_data_spectrogram = stft.get_output().time_freq_support.time_frequencies.data

    # Define boundaries of the plot
    extent = [time_data_spectrogram[0], time_data_spectrogram[-1], 0.0, fs / 2.0]

    # Plot
    plt.figure()
    plt.imshow(
        magnitude,
        origin="lower",
        aspect="auto",
        cmap="jet",
        extent=extent,
        vmax=SPLmax,
        vmin=SPLmax - 70.0,
    )
    plt.colorbar(label=f"Magnitude ({magnitude_unit})")
    plt.ylabel(f"Frequency ({frequency_unit})")
    plt.xlabel(f"Time ({time_unit})")
    plt.ylim([0.0, maximum_frequency])  # Change the value of MAX_FREQUENCY_PLOT_STFT if needed.
    plt.title(title)
    plt.show()


# %%
# Load a signal with an RPM profile
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Load a signal that has been generated with Ansys Sound Analysis and Specification (SAS) from a
# WAV file, using the ``LoadWav`` class. This signal contains two channels: the actual signal (an
# acceleration recording), and the associated RPM profile.

# Return the input data of the example file.
path_accel_wav = download_accel_with_rpm_wav(server=my_server)

# Load the WAV file.
wav_loader = LoadWav(path_accel_wav)
wav_loader.process()

# Extract the audio signal and the RPM profile.
signal, rpm_profile = wav_loader.get_output()

# The AnsysSound_Orders file format only supports acoustic pressure data.
signal.unit = "Pa"

# Plot the signal and its associated RPM profile.
time = signal.time_freq_support.time_frequencies
fig, ax = plt.subplots(nrows=2, sharex=True)
ax[0].plot(time.data, signal.data)
ax[0].set_title("Audio signal")
ax[0].set_ylabel(f"Amplitude ({signal.unit})")
ax[0].grid(True)
ax[1].plot(time.data, rpm_profile.data, color="red")
ax[1].set_title("RPM profile")
ax[1].set_ylabel("RPM")
ax[1].grid(True)
plt.xlabel(f"Time ({time.unit})")
plt.show()

# %%
# Compute the level vs RPM of several orders
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Compute the level over RPM of orders 1 to 20, in steps of 0.5, with the ``OrderLevels`` class.

orders = list(np.arange(1.0, 20.5, 0.5))

order_levels = OrderLevels(signal=signal, rpm_profile=rpm_profile, orders=orders)
order_levels.process()

# %%
# Display the resulting order levels, in dB SPL, over RPM.
order_levels.plot(display_in_dB=True, reference_value=REFERENCE_ACOUSTIC_PRESSURE_IN_AIR)

# %%
# Save the order levels to a Sound Composer-compatible file
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Save the computed order levels to a text file with the ``AnsysSound_Orders`` header, using the
# ``OrderLevels.save_as_AnsysSound_Orders()`` method.

output_path = path_accel_wav[:-4] + "_order_levels.txt"
order_levels.save_as_AnsysSound_Orders(output_path)

print(f"Order levels saved to {output_path}")

# %%
# Reload the order levels into a harmonics source
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Reload the file that was just saved into a ``SourceHarmonics`` object, to be used as a source in
# a Sound Composer project. This is the object that carries the orders identified on the original
# recording, independently of any particular RPM profile.

source_harmonics = SourceHarmonics(file=output_path)

# %%
# Build an independent RPM profile to drive the synthesis
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Rather than reusing the original RPM profile, build a new, independent one to drive the
# synthesis. This mimics a product simulation scenario, where the orders extracted from an
# existing system are used to predict the sound of that same system running under different
# operating conditions. For the sake of simplicity, this new profile is obtained here by simply
# reversing the original RPM profile along the time axis.
rpm_profile_synthesis = rpm_profile.deep_copy()
rpm_profile_synthesis.data = np.flip(rpm_profile.data)

source_control = SourceControlTime()
source_control.control = rpm_profile_synthesis
source_harmonics.source_control = source_control

# %%
# Create a Sound Composer project with a single track, made of the harmonics source only (no
# filter, no additional source), to keep the synthesis focused on the identified orders.
track = Track(name="Order-based synthesis", source=source_harmonics)

sound_composer_project = SoundComposer()
sound_composer_project.name = "Order levels synthesis"
sound_composer_project.add_track(track)

# %%
# Generate the synthesized signal, using the same sampling frequency as the original signal.
sampling_frequency = 1.0 / (time.data[1] - time.data[0])
sound_composer_project.process(sampling_frequency=sampling_frequency)
sound_composer_project.plot()

synthesized_signal = sound_composer_project.get_output()

# %%
# Display the synthesized signal and the RPM profile used to drive its synthesis
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Plot the synthesized signal together with the RPM profile that was used to generate it. Because
# the synthesis is driven by the reversed RPM profile, the resulting sound reproduces the orders
# identified on the original recording, but played back as if the machine had followed this new,
# different speed variation.

time_synthesis = synthesized_signal.time_freq_support.time_frequencies
time_rpm_synthesis = rpm_profile_synthesis.time_freq_support.time_frequencies
fig, ax = plt.subplots(nrows=2, sharex=True)
ax[0].plot(time_synthesis.data, synthesized_signal.data)
ax[0].set_title("Synthesized signal")
ax[0].set_ylabel(f"Amplitude ({synthesized_signal.unit})")
ax[0].grid(True)
ax[1].plot(time_rpm_synthesis.data, rpm_profile_synthesis.data, color="red")
ax[1].set_title("RPM profile used for synthesis")
ax[1].set_ylabel("RPM")
ax[1].grid(True)
plt.xlabel(f"Time ({time_synthesis.unit})")
plt.show()

# %%
# Display the spectrogram of the synthesized signal
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Compute and display the spectrogram of the synthesized signal, using the ``Stft`` class, to
# visualize the orders that were used to drive the synthesis.
synthesized_signal.unit = "Pa"
stft = Stft(signal=synthesized_signal, fft_size=8192, window_overlap=0.9)
stft.process()
max_stft = 20 * np.log10(np.max(stft.get_stft_magnitude_as_nparray()))
plot_stft(stft, sampling_frequency, max_stft)

# %%
# Save the synthesized signal to a WAV file
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Save the synthesized signal to a WAV file, so that it can be listened to.

output_path_wav = path_accel_wav[:-4] + "_synthesized_from_orders.wav"
WriteWav(signal=synthesized_signal, path_to_write=output_path_wav).process()

print(f"Synthesized signal saved to {output_path_wav}")

# %%
# Conclusion
# ~~~~~~~~~~
# This example computed the level over RPM of a set of orders from a recorded signal and its RPM
# profile, and saved the result to an ``AnsysSound_Orders`` file. That file was then reloaded to
# drive a harmonics source in a minimal Sound Composer project, and used to synthesize a new sound
# from an independent RPM profile, unrelated to the one of the original recording.
#
# This shows that, once orders have been identified and stored, they become reusable building
# blocks: they can be combined with any RPM profile to generate new sounds, without needing a new
# recording. In a product simulation context, this makes it possible, for instance, to identify
# orders on an existing system and then synthesize the sound of a variant of that product, whose
# operating conditions, or whose harmonic content itself, may differ from the original.
#
# In a real Sound Composer project, a harmonics source like this one is typically combined with
# other sources (for example broadband noise), each capturing a different physical contribution to
# the overall sound, as shown in the :ref:`sound_composer_create_project` example.
