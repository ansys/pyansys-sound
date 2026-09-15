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
.. _order_analysis_example:

Compute order levels
--------------------

This example shows how to compute the levels over RPM of a list of orders using the
:class:`.OrderLevels` class from an acoustic or vibration measurement (also called a test), together
with the related tachometric information. Orders are harmonic components of a sound or vibration
that are related to the rotation speed of a machine.

The example also illustrates the effect of the parameters
:attr:`~.OrderLevels.order_resolution` and :attr:`~.OrderLevels.order_width` on the computed order
levels: the order levels are extracted from an intermediate RPM-order representation (see
:class:`.RpmOrderRepresentation`), whose order resolution directly drives the combined RPM and
order resolution of the result.
"""

# sphinx_gallery_start_ignore
# sphinx_gallery_thumbnail_path = '_static/_image/example015_thumbnail.png'
# sphinx_gallery_end_ignore

# %%
# Set up analysis
# ~~~~~~~~~~~~~~~
# Setting up the analysis consists of loading the required libraries, connecting to the DPF server,
# and downloading the necessary data files.

# Load standard libraries.
import matplotlib.pyplot as plt

# Load Ansys libraries.
from ansys.sound.core import REFERENCE_ACOUSTIC_PRESSURE_IN_AIR
from ansys.sound.core.examples_helpers import download_accel_with_rpm_wav
from ansys.sound.core.order_analysis import OrderLevels
from ansys.sound.core.server_helpers import connect_to_or_start_server
from ansys.sound.core.signal_utilities import LoadWav

# Connect to a remote DPF server or start a local DPF server.
my_server, my_license_context = connect_to_or_start_server(use_license_context=True)

# Download the necessary file for this example.
path_accel_wav = download_accel_with_rpm_wav(server=my_server)

# %%
# Load a signal with its RPM profile
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Load the WAV file. It contains two channels:
#
# - the actual signal (an acceleration recording of the sound pressure in a car),
# - the associated RPM profile of the engine, in rev/min.

wav_loader = LoadWav(path_accel_wav)
wav_loader.process()

signal, rpm_profile = wav_loader.get_output()

# fix RPM profile unit
rpm_profile.unit = "RPM"

# Plot the signal and its associated RPM profile.
time = signal.time_freq_support.time_frequencies

fig, ax = plt.subplots(nrows=2, sharex=True)
ax[0].plot(time.data, signal.data)
ax[0].set_title("Input signal")
ax[0].set_ylabel(f"Amplitude ({signal.unit})")
ax[0].grid(True)
ax[1].plot(time.data, rpm_profile.data, color="red")
ax[1].set_title("RPM profile")
ax[1].set_ylabel(f"Speed ({rpm_profile.unit})")
ax[1].grid(True)
plt.xlabel(f"Time ({time.unit})")
plt.tight_layout()
plt.show()

# %%
# Compute order levels with a coarse order resolution
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Compute the levels over RPM for orders 2, 4, 6, 8, and 10, which are the dominant orders in the
# signal because the engine has four cylinders. To do this, we use a coarse order resolution of 4 %.
# This means the order axis is divided into increments of 4 % of the order value. Since this method
# relies on the short-time Fourier transform, a coarser order resolution yields a finer RPM
# resolution.
#
# Note:
# The order width (50 % of the order value here) defines the order range around each requested
# order over which the energy is integrated to obtain the order levels. This is generally a
# sufficient value in most cases, but it may need to be adjusted depending on the specific signal
# characteristics, such as the presence of background noise, the proximity of neighboring orders,
# and the slope of the RPM profile curve.

orders = [2, 4, 6, 8, 10]

order_levels_coarse = OrderLevels(
    signal=signal,
    rpm_profile=rpm_profile,
    orders=orders,
    order_width=50.0,
    order_resolution=4.0,
)
order_levels_coarse.process()

# %%
# Display the RPM-order representation of the signal
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# The order levels are extracted from an intermediate RPM-order representation, which is computed
# during the call to the ``process()`` method. It is a spectrogram-like map, where the vertical
# axis is the order number instead of the frequency, and the horizontal axis is the RPM instead of
# the time. The orders appear as horizontal lines, which makes it easy to identify the dominant
# ones.
#
# This representation is useful for visualizing the distribution of energy across orders and RPM
# values. It is also convenient to adjust the value of :attr:`~.OrderLevels.order_width` to control
# the integration range around each order.
# One should set it according to the proximity between neighboring orders, the level of the
# background noise outside of the order itself on the graph, and the apparent width on the colormap.
#
# Note: this representation is directly available from the ``OrderLevels`` object, so there is no
# need to compute it again with the :class:`.RpmOrderRepresentation` class.

order_levels_coarse.plot_rpm_order_representation(
    display_in_dB=True, reference_value=REFERENCE_ACOUSTIC_PRESSURE_IN_AIR
)

# %%
# Plot the order levels
# ~~~~~~~~~~~~~~~~~~~~~
# A coarse order resolution means that fewer signal samples are needed to compute each point of
# the RPM-order representation. As a consequence, the RPM step between two successive computed
# levels is small: the resulting curves are precise in RPM, but noisier, because each level is
# estimated over a short portion of the signal.

order_levels_coarse.plot(display_in_dB=True, reference_value=REFERENCE_ACOUSTIC_PRESSURE_IN_AIR)

# %%
# Compute order levels with a fine order resolution
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Now compute the same order levels, keeping the same order width (50 %), but with a much finer
# order resolution of 0.5 %.
#
# A fine order resolution requires more signal samples for each point of the RPM-order
# representation. Each level is therefore averaged over a longer portion of the signal, and the
# RPM step between two successive computed levels is larger. The resulting curves are smoother, but
# less precise in RPM: fast level variations are smeared over a wider RPM range.
#
# In practice, the order resolution is a trade-off: decrease it to obtain smooth and well-separated
# order levels on slow run-ups, and increase it to follow rapid level variations on fast run-ups.

order_levels_fine = OrderLevels(
    signal=signal,
    rpm_profile=rpm_profile,
    orders=orders,
    order_width=50.0,
    order_resolution=0.5,
)
order_levels_fine.process()
order_levels_fine.plot(display_in_dB=True, reference_value=REFERENCE_ACOUSTIC_PRESSURE_IN_AIR)

# %%
# Compare the number of RPM values obtained in both cases.
print(f"Order resolution 4 %:   {len(order_levels_coarse.get_rpm_scale())} RPM values.")
print(f"Order resolution 0.5 %: {len(order_levels_fine.get_rpm_scale())} RPM values.")
