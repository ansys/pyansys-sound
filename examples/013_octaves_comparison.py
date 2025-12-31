# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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

This example shows how to compute 1/3-octave and octave levels, shows and explains the differences.

"""
# %%
# Octave and one-third-octave levels
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# In this example, we show how to compute octave and one-third-octave levels using PyAnsys Sound.
# The different methods available are illustrated, along with their differences.
# Some theoretical explanations are also provided to help the user understand the different
# computation methods.
#
#
# What are octave and one-third-octave levels?
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# An octave or one-third-octave spectrum is a way of analyzing the energy content of a signal
# within specific frequency bands (see Octave and Third Octave Bands), related to human perception.
#
# Octave bands are frequency bands that have a width of one octave. This means that an octave
# band is always twice as wide as the previous octave band and half as wide as the successive
# octave band.
#
# One-third-ctave bands are frequency bands built from the subdivision of octave bands into three
# sections.
#
# ANSI S1.11-1986 and IEC 61260:1995 standards define the band limits and the corresponding
# filter sets to apply in order to compute the level within these 29 bands from the temporal
# signal.
#
# Why are there several computation methods, and when to use them?
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# There are several methods to compute octave and one-third-octave levels in PyAnsys Sound, which
# differ by the type of input data used and by the computation method.
# More details about the computation can be found in the :ref:`Theory` section below.
#
# :class:`OctaveLevelsFromSignal`
#     This class can be used only if a time-domain signal is available as input.
#     It will produce a result following the ANSI S1.11-1986 and IEC 61260:1995 standards, and can
#     therefore be used when a standard result is needed.
#
# :class:`OneThirdOctaveLevelsFromSignal`
#     This class can be used with a Power Spectral Density (PSD).
#     This PSD may be computed from a temporal signal or provided directly as the result of a
#     simulation.
# * It should be used with parameter ``use_ansi_s1_11_1986=False`` (default), when there is no need
#   to compare with results computed on a time-domain signal.
#
# * It should be used with parameter ``use_ansi_s1_11_1986=True``, when the user wants to compare
#   with results computed on a time-domain signal, or with standard results.


# %%
# Octave computation
# ~~~~~~~~~~~~~~~~~~
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

# Connect to a DPF Sound server (remote or local).
my_server = connect_to_or_start_server(
    ansys_path=r"C:\ANSYSDev\Tests\DPF Servers\20251215\ansys\dpf\server_2026_1_pre1",
    use_license_context=True,
)

# Download the necessary files for this example.
flute_wav_files_path = download_flute_wav()
wav_loader = LoadWav(flute_wav_files_path)
wav_loader.process()
signal_flute = wav_loader.get_output()[0]

# %%
# Compute octave levels

octave_levels_signal = OctaveLevelsFromSignal(signal_flute)
octave_levels_signal.process()
levels_from_signal, frequencies_octaves = octave_levels_signal.get_output_as_nparray()

# %%
# For comparison, compute PSD (Power Spectral Density) from the temporal signal
psd = PowerSpectralDensity(signal_flute)
psd.process()
psd_levels = psd.get_output()

# %%
# Plot octave levels and PSD

psd_levels_as_nparray_dB = psd.get_PSD_dB_as_nparray()
frequencies_narroband = psd.get_frequencies()

frequencies_octave_for_plot = (
    [frequencies_octaves[0] / pow(2, 1 / 6)]
    + [x * pow(2, 1 / 6) for x in frequencies_octaves[0:-1] for _ in range(2)]
    + [frequencies_octaves[-1] * pow(2, 1 / 6)]
)
levels_from_signal_for_plot = [x for x in levels_from_signal for _ in range(2)]

plt.figure()
plt.plot(frequencies_narroband, psd_levels_as_nparray_dB, label="PSD", color="gray", linestyle=":")
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
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Here we illustrate the differences between the computation from a temporal signal and from
# a PSD, with or without ANSI weighting. The example is done on 1/3-octave levels using the classes
# :class:`OneThirdOctaveLevelsFromSignal` and :class:`OneThirdOctaveLevelsFromPSD`.

# %%
# Compute 1/3-octave levels from signal
one_third_octave_levels_signal = OneThirdOctaveLevelsFromSignal(signal_flute)
one_third_octave_levels_signal.process()
levels_from_signal, frequencies_third_octaves = (
    one_third_octave_levels_signal.get_output_as_nparray()
)

# %%
# Compute 1/3-octave levels from PSD. Here, for comparison sake, we use the PSD computed from the
# same signal. However, the PSD may also be provided directly as input, for example as the result
# of a simulation.

one_third_octave_levels_psd = OneThirdOctaveLevelsFromPSD(psd_levels)
one_third_octave_levels_psd.process()
levels_from_psd = one_third_octave_levels_psd.get_output_as_nparray()[0]

one_third_octave_levels_psd_ansi = OneThirdOctaveLevelsFromPSD(psd_levels, use_ansi_s1_11_1986=True)
one_third_octave_levels_psd_ansi.process()
levels_from_psd_ansi = one_third_octave_levels_psd_ansi.get_output_as_nparray()[0]

# %%
# Plot 1/3-octave levels and PSD

psd_levels_as_nparray_dB = psd.get_PSD_dB_as_nparray()
frequencies_narroband = psd.get_frequencies()

frequencies_third_octave_for_plot = (
    [frequencies_third_octaves[0] / pow(2, 1 / 6)]
    + [x * pow(2, 1 / 6) for x in frequencies_third_octaves[0:-1] for _ in range(2)]
    + [frequencies_third_octaves[-1] * pow(2, 1 / 6)]
)
levels_from_signal_for_plot = [x for x in levels_from_signal for _ in range(2)]
levels_from_psd_for_plot = [x for x in levels_from_psd for _ in range(2)]
levels_from_psd_ansi_for_plot = [x for x in levels_from_psd_ansi for _ in range(2)]

plt.figure()
plt.plot(frequencies_narroband, psd_levels_as_nparray_dB, label="PSD", color="gray", linestyle=":")
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
# Influence of the frequency resolution for PSD-based computation
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Here we show that the frequency resolution used for PSD computation will influence the results
# obtained when using computation from PSD.

# %%
# Compute PSD 1024 points. Frequency resolution is 44100Hz / 1024 = 43Hz
psd.fft_size = 1024
psd.window_length = 1024
psd.process()
psd_as_field_1024 = psd.get_output()
psd_levels_1024 = psd.get_PSD_dB_as_nparray()
frequencies_narroband_1024 = psd.get_frequencies()
# Compute 1/3-octave levels from PSD with 1024 points
one_third_octave_levels_psd.psd = psd_as_field_1024
one_third_octave_levels_psd.process()
levels_from_psd_1024 = one_third_octave_levels_psd.get_output_as_nparray()[0]
# Compute 1/3-octave levels from PSD with 1024 points with ANSI weighting
one_third_octave_levels_psd_ansi.psd = psd_as_field_1024
one_third_octave_levels_psd_ansi.process()
levels_from_psd_ansi_1024 = one_third_octave_levels_psd_ansi.get_output_as_nparray()[0]

# %%
# Compute PSD 8192 points. Frequency resolution is 44100Hz / 8192 = 5.38Hz
psd.fft_size = 8192
psd.window_length = 8192
psd.process()
psd_as_field_8192 = psd.get_output()
psd_levels_8192 = psd.get_PSD_dB_as_nparray()
frequencies_narroband_8192 = psd.get_frequencies()
# Compute 1/3-octave levels from PSD with 8192 points
one_third_octave_levels_psd.psd = psd_as_field_8192
one_third_octave_levels_psd.process()
levels_from_psd_8192 = one_third_octave_levels_psd.get_output_as_nparray()[0]
# Compute 1/3-octave levels from PSD with 8192 points with ANSI weighting
one_third_octave_levels_psd_ansi.psd = psd_as_field_8192
one_third_octave_levels_psd_ansi.process()
levels_from_psd_ansi_8192 = one_third_octave_levels_psd_ansi.get_output_as_nparray()[0]

# %%
# Plot 1/3-octave levels with different PSD resolutions
levels_from_psd_1024_for_plot = [x for x in levels_from_psd_1024 for _ in range(2)]
levels_from_psd_8192_for_plot = [x for x in levels_from_psd_8192 for _ in range(2)]

levels_from_psd_ansi_1024_for_plot = [x for x in levels_from_psd_ansi_1024 for _ in range(2)]
levels_from_psd_ansi_8192_for_plot = [x for x in levels_from_psd_ansi_8192 for _ in range(2)]

plt.figure()
plt.plot(
    frequencies_narroband_1024, psd_levels_1024, label="PSD 1024 pts", color="gray", linestyle=":"
)
plt.plot(
    frequencies_third_octave_for_plot,
    levels_from_psd_1024_for_plot,
    label="1/3-octave from PSD 1024 pts",
    color="blue",
    linestyle="--",
)
plt.plot(
    frequencies_narroband_8192, psd_levels_8192, label="PSD 8192 pts", color="black", linestyle=":"
)
plt.plot(
    frequencies_third_octave_for_plot,
    levels_from_psd_8192_for_plot,
    label="1/3-octave from PSD 8192 pts",
    color="orange",
    linestyle="-.",
)

plt.title("1/3-octave-band levels \n influence of frequency resolution")
plt.xlabel("Frequency (Hz)")
plt.xscale("log")
plt.ylabel("1/3-octave levels")
plt.xticks(rotation=90)
plt.grid()
plt.legend()
plt.show()

plt.figure()
plt.plot(
    frequencies_narroband_1024, psd_levels_1024, label="PSD 1024 pts", color="gray", linestyle=":"
)
plt.plot(
    frequencies_third_octave_for_plot,
    levels_from_psd_ansi_1024_for_plot,
    label="1/3-octave from PSD with ANSI weighting 1024 pts",
    color="blue",
    linestyle="--",
)
plt.plot(
    frequencies_narroband_8192, psd_levels_8192, label="PSD 8192 pts", color="black", linestyle=":"
)
plt.plot(
    frequencies_third_octave_for_plot,
    levels_from_psd_ansi_8192_for_plot,
    label="1/3-octave from PSD with ANSI weighting 8192 pts",
    color="orange",
    linestyle="-.",
)

plt.title("1/3-octave-band levels with ANSI weighting \n influence of frequency resolution")
plt.xlabel("Frequency (Hz)")
plt.xscale("log")
plt.ylabel("1/3-octave levels")
plt.xticks(rotation=90)
plt.grid()
plt.legend()
plt.show()

# %%
# Results computed with ANSI weighting are far less sensitive to the frequency resolution of the
# PSD, especially when it contains peaks.

# %%
# .. _Theory:
# Theory
# ~~~~~~
#
# Levels from signal
# ^^^^^^^^^^^^^^^^^^
# The computation using :class:`OneThirdOctaveLevelsFromSignal` or :class:`OctaveLevelsFromSignal`
# follows the ANSI S1.11-1986 and IEC 61260:1995 standards.
#
# When computing levels from a temporal signal, the signal is first filtered using band-pass
# filters. Each band-pass filter corresponds to one octave or one 1/3-octave band defined in the
# standards. Then, the level is computed in each band from the filtered signal.
#
# .. image:: ../../_static/_image/example013_method1.png
#
# Levels from PSD
# ^^^^^^^^^^^^^^^
#
# The computation using :class:`OneThirdOctaveLevelsFromPSD` or :class:`OctaveLevelsFromPSD` with
# parameter ``use_ansi_s1_11_1986=True`` (default value) is done using the Power Spectral Density
# (PSD) as input. This PSD may be computed from a temporal signal or # provided directly as the
# result of a simulation.
#
# When computing levels from a PSD, the level in each band is computed by integrating the PSD over
# the frequency range corresponding to a given band.
#
# .. image:: ../../_static/_image/example013_method2.png
#
# Levels from PSD with ANSI weighting
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# The computation using :class:`OneThirdOctaveLevelsFromPSD` or :class:`OctaveLevelsFromPSD` with
# the parameter ``use_ansi_s1_11_1986=True`` applies frequency weighting defined in the ANSI
# S1.11-1986, in order to approximate the results obtained from a temporal signal.
#
# This may for example allow comparing simulation results with measurements.
#
# When computing levels from a PSD with ANSI weighting, the PSD is first weighted using the
# frequency weighting defined in the ANSI S1.11-1986. Then, the level in each band is computed by
# integrating the weighted PSD over the whole frequency range.
#
# .. image:: ../../_static/_image/example013_method3.png
