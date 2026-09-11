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

.. seealso::
    :ref:`sound_composer_create_project`
        Example demonstrating how to create a Sound Composer project, including a harmonics source.
"""

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
from ansys.sound.core.signal_utilities import LoadWav

# Connect to a remote DPF server or start a local DPF server.
my_server, my_license_context = connect_to_or_start_server(use_license_context=True)

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
