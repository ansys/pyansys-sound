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
.. _synthesize_harmonics_source_from_order_analysis:

Synthesize harmonics source from order analysis
-----------------------------------------------

Orders are harmonic components in the sound related to the speed of a rotating machine. This example
shows how to compute the level over RPM of several orders of a signal associated with an RPM profile,
and how to save the result to a text file with the `AnsysSound_Orders` format.

This file can then be used to define a harmonics source in the Sound Composer, either with
the :class:`.SourceHarmonics` class of PyAnsys Sound, or with the Sound Composer module of Ansys
Sound SAS, in order to generate a sound corresponding to the specified orders.

This example shows how to load the saved file into a :class:`.SourceHarmonics` object,
and use it in a :class:`.SoundComposer` project to synthesize a new sound driven by
a new RPM profile. This illustrates a typical product simulation use case: orders
identified on an existing system can be reused to synthesize the acoustic behavior of that system
under different operating conditions.

.. seealso::
    :ref:`sound_composer_create_project`
        Example demonstrating how to create a Sound Composer project, including a harmonics source.
"""

# %%
# Set up analysis
# ~~~~~~~~~~~~~~~
# Setting up the analysis consists of loading the required libraries, connecting to the DPF server,
# and retrieving the example file.

# Load Ansys libraries.
from ansys.dpf.core import upload_file_in_tmp_folder

# Load standard libraries.
import matplotlib.pyplot as plt
import numpy as np

from ansys.sound.core.examples_helpers import download_accel_with_rpm_wav
from ansys.sound.core.examples_helpers.download import download_rpm_acceleration_deceleration
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

# Maximum frequency for STFT plots, change according to your need.
MAX_FREQUENCY_PLOT_STFT = 2000.0


def plot_stft(
    stft: Stft,
    fs: float,
    SPLmax: float,
    title: str = "STFT",
    maximum_frequency: float = MAX_FREQUENCY_PLOT_STFT,
    ax=None,
) -> None:
    """Plot a short-term Fourier transform (STFT) into a Matplotlib axis or a new figure.

    Parameters
    ----------
    stft: Stft
        Object containing the STFT.
    fs: float
        Sampling frequency of the signal in Hz.
    SPLmax: float
        Maximum value (here in dB SPL) for the colormap.
    title: str, default: "STFT"
        Title of the figure or axis.
    maximum_frequency: float, default: MAX_FREQUENCY_PLOT_STFT
        Maximum frequency in Hz to display.
    ax: matplotlib.axes.Axes, optional
        Axis to draw the spectrogram into. If ``None``, a new figure is created.
    """
    magnitude = stft.get_stft_magnitude_as_nparray()
    magnitude_unit = stft.get_output()[0].unit
    if isinstance(magnitude_unit, tuple):
        magnitude_unit = magnitude_unit[1]
    frequency_unit = stft.get_output()[0].time_freq_support.time_frequencies.unit
    time_unit = stft.get_output().time_freq_support.time_frequencies.unit

    # Only extract the first half of the STFT, as it is symmetrical.
    half_nfft = int(magnitude.shape[0] / 2) + 1

    # Voluntarily ignore a numpy warning.
    np.seterr(divide="ignore")
    magnitude = 20 * np.log10(magnitude[0:half_nfft, :])
    np.seterr(divide="warn")

    # Obtain sampling frequency, time steps, and number of time samples.
    time_data_spectrogram = stft.get_output().time_freq_support.time_frequencies.data

    # Define boundaries of the plot.
    extent = [time_data_spectrogram[0], time_data_spectrogram[-1], 0.0, fs / 2.0]

    # Plot into provided axis or create a new figure.
    target_ax = ax if ax is not None else None
    if target_ax is None:
        plt.figure()
        target_ax = plt.gca()

    im = target_ax.imshow(
        magnitude,
        origin="lower",
        aspect="auto",
        cmap="jet",
        extent=extent,
        vmax=SPLmax,
        vmin=SPLmax - 70.0,
    )

    # Attach colorbar to the figure containing the target axis.
    plt.colorbar(im, ax=target_ax, label=f"Magnitude ({magnitude_unit})")
    target_ax.set_ylabel(f"Frequency ({frequency_unit})")
    target_ax.set_xlabel(f"Time ({time_unit})")
    target_ax.set_ylim(
        [0.0, maximum_frequency]
    )  # Change the value of MAX_FREQUENCY_PLOT_STFT if needed.
    target_ax.set_title(title)
    if ax is None:
        plt.show()


# %%
# Load a signal with an RPM profile
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Load a signal from a WAV file, using the :class:`.LoadWav` class. This signal contains two
# channels: the actual signal (an acceleration recording), and the associated RPM profile.

# Return the input data of the example file.
path_accel_wav = download_accel_with_rpm_wav(server=my_server)

# Load the WAV file.
wav_loader = LoadWav(path_accel_wav)
wav_loader.process()

# Extract the audio signal and the RPM profile.
signal, rpm_profile = wav_loader.get_output()
sampling_frequency = wav_loader.get_sampling_frequency()

# %%
# Compute the spectrogram.
stft = Stft(signal=signal, fft_size=8192, window_overlap=0.9)
stft.process()
max_stft = 20 * np.log10(np.max(stft.get_stft_magnitude_as_nparray()))

# %%
# Plot the RPM profile and the spectrogram side-by-side.
time = signal.time_freq_support.time_frequencies
fig, axs = plt.subplots(nrows=1, ncols=2, sharex=True, figsize=(12, 5))

# Left: RPM profile.
axs[0].plot(time.data, rpm_profile.data, color="red")
axs[0].set_title("RPM profile")
axs[0].set_ylabel("RPM")
axs[0].grid(True)
axs[0].set_xlabel(f"Time ({time.unit})")

# Right: spectrogram with the custom ``plot_stft`` function.
plot_stft(
    stft,
    sampling_frequency,
    max_stft,
    title="STFT",
    maximum_frequency=MAX_FREQUENCY_PLOT_STFT,
    ax=axs[1],
)

plt.tight_layout()
plt.show()

# %%
# Compute and save order levels over RPM
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Compute the level over RPM of every half-order between 1 to 20.5 with the :class:`.OrderLevels`
# class.

orders = list(np.arange(1.0, 20.5, 0.5))

order_levels = OrderLevels(signal=signal, rpm_profile=rpm_profile, orders=orders)
order_levels.process()

# %%
# Save the computed order levels to a text file with the `AnsysSound_Orders` header, using the
# :class:`.OrderLevels` class and its
# :meth:`save_as_AnsysSound_Orders() <.OrderLevels.save_as_AnsysSound_Orders>` method.

orders_file_path = path_accel_wav[:-4] + "_order_levels.txt"
order_levels.save_as_AnsysSound_Orders(orders_file_path)

print(f"Order levels saved to {orders_file_path}")

# %%
# Synthesize harmonics source from the saved order levels
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Load the saved file into a :class:`.SourceHarmonics` object, to be used as a source in a Sound
# Composer project.
path = orders_file_path
if my_server.has_client():
    # In remote DPF Server case, the file must be uploaded to the server's temporary folder.
    path = upload_file_in_tmp_folder(orders_file_path, my_server)

source_harmonics = SourceHarmonics(file=path)

# %%
# Load a new RPM profile for the synthesis, with acceleration and deceleration phases.
new_rpm_path = download_rpm_acceleration_deceleration()
source_control = SourceControlTime(new_rpm_path, expected_unit="RPM")
source_harmonics.source_control = source_control

# %%
# Create a Sound Composer project with a single track, made of the harmonics source only.
track = Track(name="Order-based synthesis", source=source_harmonics)

sound_composer_project = SoundComposer()
sound_composer_project.name = "Order levels synthesis"
sound_composer_project.add_track(track)

# %%
# Synthesize the signal.
sound_composer_project.process(sampling_frequency=sampling_frequency)
sound_composer_project.plot()

synthesized_signal = sound_composer_project.get_output()

# %%
# Plot the synthesized signal together with the RPM profile that was used to generate it. The
# resulting sound reproduces the orders identified in the original recording, but with a different
# temporal evolution, as if the machine speed had followed the new RPM profile.

fig, axs = plt.subplots(nrows=1, ncols=2, sharex=True, figsize=(12, 5))

# Left: RPM profile used for synthesis.
time_rpm = source_control.control.time_freq_support.time_frequencies
axs[0].plot(time_rpm.data, source_control.control.data, color="red")
axs[0].set_title("RPM profile used for synthesis")
axs[0].set_ylabel("RPM")
axs[0].grid(True)
axs[0].set_xlabel(f"Time ({time_rpm.unit})")

# Right: spectrogram of the synthesized signal.
stft_synth = Stft(signal=synthesized_signal, fft_size=8192, window_overlap=0.9)
stft_synth.process()
max_stft_synth = 20 * np.log10(np.max(stft_synth.get_stft_magnitude_as_nparray()))
plot_stft(
    stft_synth,
    sampling_frequency,
    max_stft_synth,
    title="STFT (synthesized)",
    maximum_frequency=MAX_FREQUENCY_PLOT_STFT,
    ax=axs[1],
)

plt.tight_layout()
plt.show()

# %%
# Save the synthesized signal to a WAV file.
wav_output_path = new_rpm_path[:-4] + "_synthesized_from_orders.wav"
WriteWav(signal=synthesized_signal, path_to_write=wav_output_path).process()

print(f"Synthesized signal saved to {wav_output_path}")

# %%
# Conclusion
# ~~~~~~~~~~
# This example demonstrates how to compute the level over RPM of a set of orders from a recorded
# signal and its RPM profile, and save the result to an `AnsysSound_Orders` file. It then
# demonstrates how that file can be used to synthesize a harmonics source in a Sound Composer
# project, following an RPM profile that is different from that of the original recording.
#
# This shows that, once orders have been identified and stored, they become a reusable material:
# they can be combined with any RPM profile to generate a new sound, without needing a new
# recording. In a product simulation context, this makes it possible, for instance, to identify
# orders on an existing system and then synthesize the sound that this system would have produced in
# operating conditions that differ from the original.
#
# In a realistic sound simulation context, however, such harmonics sources are typically combined
# with other sources (for example broadband noise), each capturing a different physical contribution
# to the overall sound, as shown in the :ref:`sound_composer_create_project` example.
