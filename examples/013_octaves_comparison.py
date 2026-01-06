# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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
.. _octaves_comparison:

Octave and one-third-octave levels computation
----------------------------------------------

This example shows how to compute 1/3-octave and octave levels with PyAnsys Sound.
It presents the different available methods and explains their differences.

"""
# %%
# Octave and one-third-octave levels
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# What are octave and one-third-octave levels?
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# Octave (or one-third-octave) levels is a way of analyzing the energy content of a signal
# within specific frequency bands, related to human perception.
#
# Octave bands are frequency bands that have a width of one octave. This means that an octave
# band is always twice as wide as the previous octave band and half as wide as the successive
# octave band.
#
# One-third-octave bands are frequency bands built from the subdivision of octave bands into three
# sections.
#
# ANSI S1.11-1986 and IEC 61260:1995 standards define the band limits and specify band-pass
# filters to compute the levels within these 29 bands from the time-domain signal.
#
# Why are there several computation methods, and when to use them?
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# There are several methods to compute octave and one-third-octave levels in PyAnsys Sound, which
# differ by the type of input data used and by the computation method.
# More details about the computation can be found in the :ref:`Theory` section below.
#
# :class:`OctaveLevelsFromSignal`
#     Use this class to calculate octave levels from a time-domain signal.
#     It follows  the ANSI S1.11-1986 and IEC 61260:1995 standards, and can
#     therefore be used when a standard result is needed.
#
# :class:`OctaveLevelsFromPSD`
#     Use this class to calculate octave levels from a Power Spectral Density (PSD).
#     The PSD may come from the analysis of a time-domain signal or be the result of a
#     simulation.
#
# * Set parameter ``use_ansi_s1_11_1986=False`` (default), when there is no need
#   to compare with results computed on a time-domain signal.
#
# * Set parameter ``use_ansi_s1_11_1986=True``, when you want to compare
#   with results computed on a time-domain signal, or with standard results.


# %%
# Octave levels computation
# ~~~~~~~~~~~~~~~~~~~~~~~~~
# Here we show how to compute octave levels using :class:`OctaveLevelsFromSignal`.
#
# The same processing can be applied using :class:`OctaveLevelsFromPSD`,
# :class:`OneThirdOctaveLevelsFromSignal` and :class:`OneThirdOctaveLevelsFromPSD`.

# %%
# Set up analysis: load Ansys libraries, connect to the DPF server, and
# download the necessary data files.

# Load standard libraries.
import matplotlib.pyplot as plt

# Load Ansys libraries.
from ansys.sound.core.examples_helpers import (
    download_flute_wav,
)
from ansys.sound.core.server_helpers import connect_to_or_start_server
from ansys.sound.core.signal_utilities import LoadWav
from ansys.sound.core.spectral_processing import PowerSpectralDensity
from ansys.sound.core.standard_levels import (
    OctaveLevelsFromSignal,
    OneThirdOctaveLevelsFromPSD,
    OneThirdOctaveLevelsFromSignal,
)

# Connect to a remote DPF server or start a local DPF server.
my_server = connect_to_or_start_server(use_license_context=True)

# Download the necessary files for this example.
flute_wav_files_path = download_flute_wav()
wav_loader = LoadWav(flute_wav_files_path)
wav_loader.process()
signal_flute = wav_loader.get_output()[0]

# %%
# Compute octave levels.

octave_levels_signal = OctaveLevelsFromSignal(signal_flute)
octave_levels_signal.process()
levels_from_signal, frequencies_octaves = octave_levels_signal.get_output_as_nparray()

# %%
# Compute the Power Spectral Density (PSD) from the time-domain signal, to display
# it in the same graph as the PSD for illustration.
psd = PowerSpectralDensity(signal_flute)
psd.process()
psd_levels = psd.get_output()

# %%
# Plot octave levels and PSD on a single graph.

psd_levels_as_nparray_dB = psd.get_PSD_dB_as_nparray()
frequencies_narrowband = psd.get_frequencies()

frequencies_octave_for_plot = (
    [frequencies_octaves[0] / pow(2, 1 / 6)]
    + [x * pow(2, 1 / 6) for x in frequencies_octaves[0:-1] for _ in range(2)]
    + [frequencies_octaves[-1] * pow(2, 1 / 6)]
)
levels_from_signal_for_plot = [x for x in levels_from_signal for _ in range(2)]

plt.figure()
plt.plot(frequencies_narrowband, psd_levels_as_nparray_dB, label="PSD", color="gray", linestyle=":")
plt.plot(
    frequencies_octave_for_plot,
    levels_from_signal_for_plot,
    label="1/3 octave from signal",
    color="blue",
    linestyle="-",
)

plt.title("Octave levels from signal")
plt.xlabel("Frequency (Hz)")
plt.xscale("log")
plt.ylabel("Octave levels (dB)")
plt.xticks(rotation=90)
plt.grid()
plt.show()

# %%
# Methods comparison
# ~~~~~~~~~~~~~~~~~~
# Here we illustrate the differences between the computation from a temporal signal and from
# a PSD, with or without ANSI weighting. The example is done on 1/3-octave levels using the classes
# :class:`OneThirdOctaveLevelsFromSignal` and :class:`OneThirdOctaveLevelsFromPSD`.

# %%
# Compute 1/3-octave levels from signal.
one_third_octave_levels_signal = OneThirdOctaveLevelsFromSignal(signal_flute)
one_third_octave_levels_signal.process()
levels_from_signal, frequencies_third_octaves = (
    one_third_octave_levels_signal.get_output_as_nparray()
)

# %%
# Compute 1/3-octave levels from PSD. Here, for comparison, we use the PSD computed from the
# same signal. However, the PSD may also be provided directly as input, for example as the result
# of a simulation.

one_third_octave_levels_psd = OneThirdOctaveLevelsFromPSD(psd_levels)
one_third_octave_levels_psd.process()
levels_from_psd = one_third_octave_levels_psd.get_output_as_nparray()[0]

one_third_octave_levels_psd_ansi = OneThirdOctaveLevelsFromPSD(psd_levels, use_ansi_s1_11_1986=True)
one_third_octave_levels_psd_ansi.process()
levels_from_psd_ansi = one_third_octave_levels_psd_ansi.get_output_as_nparray()[0]

# %%
# Plot 1/3-octave levels and PSD.

psd_levels_as_nparray_dB = psd.get_PSD_dB_as_nparray()
frequencies_narrowband = psd.get_frequencies()

frequencies_third_octave_for_plot = (
    [frequencies_third_octaves[0] / pow(2, 1 / 6)]
    + [x * pow(2, 1 / 6) for x in frequencies_third_octaves[0:-1] for _ in range(2)]
    + [frequencies_third_octaves[-1] * pow(2, 1 / 6)]
)
levels_from_signal_for_plot = [x for x in levels_from_signal for _ in range(2)]
levels_from_psd_for_plot = [x for x in levels_from_psd for _ in range(2)]
levels_from_psd_ansi_for_plot = [x for x in levels_from_psd_ansi for _ in range(2)]

plt.figure()
plt.plot(frequencies_narrowband, psd_levels_as_nparray_dB, label="PSD", color="gray", linestyle=":")
plt.plot(
    frequencies_third_octave_for_plot,
    levels_from_signal_for_plot,
    label="1/3 octave from signal",
    color="red",
    linestyle="-",
)
plt.plot(
    frequencies_third_octave_for_plot,
    levels_from_psd_for_plot,
    label="1/3 octave from PSD",
    color="blue",
    linestyle="--",
)
plt.plot(
    frequencies_third_octave_for_plot,
    levels_from_psd_ansi_for_plot,
    label="1/3 octave from PSD with ANSI weighting",
    color="green",
    linestyle="-.",
)

plt.title("1/3-octave-band levels - methods comparison")
plt.xlabel("Frequency (Hz)")
plt.xscale("log")
plt.ylabel("1/3 octave levels")
plt.xticks(rotation=90)
plt.grid()
plt.legend()
plt.show()

# %%
# The red curve represents the levels calculated from the time-domain signal, it is the standard
# way to do when working with test data.
#
# The blue curve represents the levels calculated from the PSD of the signal. It is highly dependent
# on the frequency resolution of the PSD, as it only sums up the levels that are exactly in each
# 1/3-octave band to calculte their respective levels.
#
# The green curve represents the levels calculated from the PSD, with a correction added to
# be closer to the calculation that would be done with the first method. You can notice that the
# levels obtained with the third method are closer to the first method's ones, because of this
# correction. However some differences still appear, mainly because of the influence of the frequency
# resolution of the PSD.

# %%
# .. _Theory:
#
# Theory
# ~~~~~~
#
# In this section, some details are given about the principles behind each of the three
# calculation methods.
#
# Levels from signal
# ^^^^^^^^^^^^^^^^^^
# The computation using :class:`OneThirdOctaveLevelsFromSignal` or :class:`OctaveLevelsFromSignal`
# follows the ANSI S1.11-1986 and IEC 61260:1995 standards.
#
# 1. the signal is filtered using octave (or one-third-octave) band-pass filters, resulting in
#    as many band-filtered signals as the number of octave (or one-third-octaves).
#    Each band-pass filter has a bandwith of 1 octave (or 1 one-third-octave), and is centered at the
#    standardized center frequencies of the bands.
# 2. for each band filtered signal, the level is calculated by averaging the sum of the squares of the
#    samples. This level is the level of the band.
#
# The figure below illustrates this process.
#
# .. image:: ../../_static/_image/example013_method1.png
#
# Levels from PSD
# ^^^^^^^^^^^^^^^
#
# The computation using :class:`OneThirdOctaveLevelsFromPSD` or :class:`OctaveLevelsFromPSD` with
# parameter ``use_ansi_s1_11_1986=False`` (default value) is done using the Power Spectral Density
# (PSD) as input.
#
# The level in each octave or one-third-octave band is calculated by integrating the PSD over
# the frequency range corresponding to a each octave or one-third-octave band.
#
# The figure below illustrates this process.
#
# .. image:: ../../_static/_image/example013_method2.png
#
# Levels from PSD with ANSI weighting
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# The computation using :class:`OneThirdOctaveLevelsFromPSD` or :class:`OctaveLevelsFromPSD` with
# the parameter ``use_ansi_s1_11_1986=True`` is done using a Power Spectral Density (PSD) as input.
# For each band, it applies a frequency weighting based on the frequency response of the band-pass
# filters defined in the ANSI S1.11-1986 standard, in order to approximate the results obtained from
# a time-domain signal following ANSI S1.11-1986.
#
# This may, for example, allow comparing simulation results with measurements.
#
# 1. the PSD values are weighted using the frequency response of the filter for this band, as defined
#    in ANSI S1.11-1986.
# 2. the level in each band is calculated by integrating the weighted PSD over the whole frequency range.
#
# The figure below illustrates this process.
#
# .. image:: ../../_static/_image/example013_method3.png
