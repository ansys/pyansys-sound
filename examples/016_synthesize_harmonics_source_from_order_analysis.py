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
shows how to compute the level over RPM of several orders from a recorded acoustic signal,
associated with its RPM profile, and how to save the result to a text file with the
`AnsysSound_Orders` format.

This file can then be used to define a harmonics source in the Sound Composer, either with
the :class:`.SourceHarmonics` class of PyAnsys Sound, or with the Sound Composer module of Ansys
Sound SAS, in order to generate a sound from these orders.

This example shows how to load the saved file into a :class:`.SourceHarmonics` object,
and use it in a :class:`.SoundComposer` project to synthesize a new sound, driven by
an RPM profile different from the original one used at the analysis step. This illustrates a typical
product simulation use case: orders identified on an existing system can be reused to synthesize the
acoustic behavior of that system under different operating conditions.

.. seealso::
    :ref:`sound_composer_create_project`
        Example demonstrating how to create a Sound Composer project, including a harmonics source.
"""

# %%
# Set up analysis
# ~~~~~~~~~~~~~~~
# Setting up the analysis consists of loading the required libraries, connecting to the DPF server,
# and retrieving the example file.

import os
from pathlib import Path

from ansys.dpf.core import upload_file_in_tmp_folder

# Load standard libraries.
import matplotlib.pyplot as plt
import numpy as np

# Load Ansys libraries.
from ansys.sound.core import REFERENCE_ACOUSTIC_PRESSURE_IN_AIR
from ansys.sound.core.examples_helpers import (
    download_accel_with_rpm_wav,
    download_rpm_acceleration_deceleration,
)
from ansys.sound.core.examples_helpers.download import EXAMPLES_PATH
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

# sphinx_gallery_start_ignore
# sphinx_gallery_thumbnail_number = 5
# sphinx_gallery_end_ignore

# Connect to a remote DPF server or start a local DPF server.
my_server, my_license_context = connect_to_or_start_server(use_license_context=True)


# %%
# Load a signal with an RPM profile
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Load a signal from a WAV file, using the :class:`.LoadWav` class. This signal contains two
# channels: the actual acoustic signal (an acceleration recording in a car cabin), and the
# associated RPM profile (engine speed recording).

# Return the input data of the example file.
path_accel_wav = download_accel_with_rpm_wav(server=my_server)

# Load the WAV file.
wav_loader = LoadWav(path_accel_wav)
wav_loader.process()

# Extract the audio signal and the RPM profile.
signal, rpm_profile = wav_loader.get_output()
sampling_frequency = wav_loader.get_sampling_frequency()

# Fix RPM profile unit
rpm_profile.unit = "RPM"

# %%
# Compute the spectrogram.
stft = Stft(signal=signal, fft_size=8192, window_overlap=0.9)
stft.process()

# %%
# Plot the RPM profile and the spectrogram.
time = signal.time_freq_support.time_frequencies

# RPM profile.
plt.figure()
plt.plot(time.data, rpm_profile.data, color="red")
plt.title("RPM profile")
plt.ylabel("RPM")
plt.xlabel(f"Time ({time.unit})")
plt.grid(True)
plt.show()

# Spectrogram.
max_frequency = 2000.0
stft.plot_custom(
    display_phase=False,
    max_frequency=max_frequency,
    reference_value=REFERENCE_ACOUSTIC_PRESSURE_IN_AIR,
    title="STFT",
)

# %%
# Compute and save order levels over RPM
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Compute the level over RPM of every half-order between 1 to 20 with the :class:`.OrderLevels`
# class.

orders = list(np.arange(1.0, 20.0 + 0.5, 0.5))
order_levels = OrderLevels(signal=signal, rpm_profile=rpm_profile, orders=orders)
order_levels.process()

# %%
# Save the computed order levels to a text file with the `AnsysSound_Orders` header, using the
# :class:`.OrderLevels` class and its
# :meth:`save_as_AnsysSound_Orders() <.OrderLevels.save_as_AnsysSound_Orders>` method.

filename = Path(path_accel_wav).name
orders_file_path = os.path.join(EXAMPLES_PATH, "pyansys-sound", f"{filename[:-4]}_order_levels.txt")
order_levels.save_as_AnsysSound_Orders(orders_file_path)

# %%
# Synthesize harmonics source from the saved order levels
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Here we are going to synthesize a sound from the previously computed order levels, but following 
# another operating condition (new RPM profile).
# 
# To do this, we use the saved file as input of a :class:`.SourceHarmonics` object, which is made to
# generate a sound from an harmonics source, according to a given input RPM profile (called source
# control). This object is then used as a source in a Sound Composer project,
# using:class:`.SoundComposer`.
# 
# Note: this Sound Composer project can be further extended with additional tracks and sources if
# needed, for example to add the sources of rolling noise, aerodynamic noise, HVAC noise, etc.

path = orders_file_path
if my_server.has_client():
    # In remote DPF Server case, the file must be uploaded to the server's temporary folder to be
    # accessible by the server.
    path = upload_file_in_tmp_folder(file_path=orders_file_path, server=my_server)

# Create the SourceHarmonics object from the saved order levels file.
source_harmonics = SourceHarmonics(file=path)

# %%
# Load the RPM profile to be used for the sound synthesis. This profile includes acceleration and
# deceleration phases (you can find the profile displayed in a figure below).
new_rpm_path = download_rpm_acceleration_deceleration()
source_control = SourceControlTime(new_rpm_path, expected_unit="RPM")
source_harmonics.source_control = source_control

# %%
# Create a Sound Composer project with a single track, made of the harmonics source previously
# created.
track = Track(name="Order-based synthesis", source=source_harmonics)

sound_composer_project = SoundComposer()
sound_composer_project.name = "Order levels synthesis"
sound_composer_project.add_track(track)

# %%
# Synthesize the signal using :meth:`process() <.SoundComposer.process>` and plot it.
sound_composer_project.process(sampling_frequency=sampling_frequency)
sound_composer_project.plot()

# %%
# Spectrogram of the synthesized signal
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Here we plot the spectrogram of the synthesized signal together with the RPM profile used to
# generate it. Observe that the resulting sound reproduces the orders analyzed in the original
# recording, but with a different temporal evolution, as if the machine speed had followed the new
# RPM profile given as input.

# Display the RPM profile used for synthesis.
time_rpm = source_control.control.time_freq_support.time_frequencies
plt.plot(time_rpm.data, source_control.control.data, color="red")
plt.title("RPM profile used for synthesis")
plt.ylabel("RPM")
plt.xlabel(f"Time ({time_rpm.unit})")
plt.grid(True)
plt.show()

# Get the synthesized signal.
synthesized_signal = sound_composer_project.get_output()

# Calculate and display the spectrogram of the synthesized signal.
stft_synth = Stft(signal=synthesized_signal, fft_size=8192, window_overlap=0.9)
stft_synth.process()
stft_synth.plot_custom(
    display_phase=False,
    max_frequency=max_frequency,
    reference_value=REFERENCE_ACOUSTIC_PRESSURE_IN_AIR,
    title="STFT (synthesized)",
)

# %%
# Save the synthesized signal to a WAV file. You can listen to this sound by opening the generated
# WAV file in Ansys Sound SAS, or any audio player.
wav_output_path = new_rpm_path[:-4] + "_synthesized_from_orders.wav"
WriteWav(signal=synthesized_signal, path_to_write=wav_output_path).process()

print(f"Synthesized signal saved to {wav_output_path}")

# %%
# Conclusion
# ~~~~~~~~~~
# This example demonstrated how to compute the level over RPM of a set of orders from a recorded
# signal and its RPM profile, then saved the result to an `AnsysSound_Orders` file. It then
# demonstrated how that file can be used to synthesize a harmonics source in a Sound Composer
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
