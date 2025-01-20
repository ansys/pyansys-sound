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
.. _calculate_psychoacoustic_indicators:

Calculate psychoacoustic indicators
-----------------------------------

This example shows how to calculate psychoacoustic indicators.
The following indicators are included:

- Loudness of stationary sounds according to ISO 532-1.
- Loudness of time-varying sounds according to ISO 532-1.
- Sharpness according to Zwicker and Fastl, "Psychoacoustics: Facts and models", 1990.
- Roughness according to Daniel and Weber, "Psychoacoustical Roughness: Implementation of an
  Optimized Model, 1997.
- Fluctuation strength according to Sontacchi, "Entwicklung eines Modulkonzeptes für die
  psychoakustische Geräuschanalyse under MatLab Diplomarbeit", 1998.

The example shows how to perform these operations:

- Set up the analysis.
- Calculate indicators on loaded WAV files.
- Get calculation outputs.
- Plot some corresponding curves.

"""

# %%
# Set up analysis
# ~~~~~~~~~~~~~~~
# Setting up the analysis consists of loading Ansys libraries, connecting to the
# DPF server, and retrieving the example files.

# Load Ansys libraries.
import os

import numpy as np

from ansys.sound.core.examples_helpers import (
    download_accel_with_rpm_wav,
    download_flute_2_wav,
    download_flute_wav,
)
from ansys.sound.core.psychoacoustics import (
    FluctuationStrength,
    LoudnessISO532_1_Stationary,
    LoudnessISO532_1_TimeVarying,
    Roughness,
    Sharpness,
)
from ansys.sound.core.psychoacoustics.roughness import Roughness
from ansys.sound.core.psychoacoustics.sharpness import Sharpness
from ansys.sound.core.server_helpers import connect_to_or_start_server
from ansys.sound.core.signal_utilities import LoadWav

# Connect to a remote server or start a local server.
my_server = connect_to_or_start_server(use_license_context=True)


# %%
# Calculate ISO 532-1 loudness for a stationary sound
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Load a signal from a WAV file using the ``LoadWav`` class. It is returned as a DPF
# field container. For more information, see `fields_container
# <https://dpf.docs.pyansys.com/version/stable/api/ansys.dpf.core.operators.utility.fields_container.html>`_
# in the DPF-Core API documentation.

# Load example data from WAV file
path_flute_wav = download_flute_wav(server=my_server)
wav_loader = LoadWav(path_flute_wav)
wav_loader.process()
fc_signal = wav_loader.get_output()

# %%
# Create a ``LoudnessISO532_1_Stationary`` object, set its signal, and compute the loudness.
loudness_stationary = LoudnessISO532_1_Stationary(signal=fc_signal)
loudness_stationary.process()

# %%
# Get the value in sone or in phon.
loudness_sone = loudness_stationary.get_loudness_sone()
loudness_level_phon = loudness_stationary.get_loudness_level_phon()
file_name = os.path.basename(path_flute_wav)
print(
    f"\nThe loudness of sound file {file_name} "
    f"is{loudness_sone: .1f} sones "
    f"or{loudness_level_phon: .1f} phons."
)

# %%
# Plot the specific loudness.
loudness_stationary.plot()

# %%
# Calculate ISO 532-1 loudness for several signals at once
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Load another WAV file and store it along with the first one.

path_flute2_wav = download_flute_2_wav(server=my_server)
wav_loader = LoadWav(path_flute2_wav)
wav_loader.process()

# Store the second signal as a second field in the DPF fields container.
fc_two_signals = fc_signal
fc_two_signals.add_field({"channel_number": 1}, wav_loader.get_output()[0])


# %%
# Calculate the loudness for both signals at once.
loudness_stationary = LoudnessISO532_1_Stationary(signal=fc_two_signals)
loudness_stationary.process()

# %%
# Get the values in sone or in phon.
loudness_sone2 = loudness_stationary.get_loudness_sone(1)
loudness_level_phon2 = loudness_stationary.get_loudness_level_phon(1)
file_name2 = os.path.basename(path_flute2_wav)
print(
    f"In comparison, the loudness of sound file {file_name2} "
    f"is{loudness_sone2: .1f} sones "
    f"or{loudness_level_phon2: .1f} phons."
)

# %%
# Plot specific loudness for both signals in a single figure. Note how the first sound has a
# higher specific loudness than the second.
loudness_stationary.plot()

# %%
# Calculate ISO 532-1 loudness for a non-stationary sound
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Load a new signal (non-stationary) from a WAV file.
path_accel_wav = download_accel_with_rpm_wav(server=my_server)
wav_loader = LoadWav(path_accel_wav)
wav_loader.process()
f_signal = wav_loader.get_output()[0]  # Field 0 only, because the RPM profile is useless here.

# %%
# Create a ``LoudnessISO532_1_TimeVarying`` object, set its signal, and compute the loudness.
loudness_time_varying = LoudnessISO532_1_TimeVarying(signal=f_signal)
loudness_time_varying.process()

# %%
# Get percentile loudness values.
N5 = loudness_time_varying.get_N5_sone()
N10 = loudness_time_varying.get_N10_sone()
L5 = loudness_time_varying.get_L5_phon()
L10 = loudness_time_varying.get_L10_phon()

file_name3 = os.path.basename(path_accel_wav)
print(
    f"\nThe sound file {file_name3} has the following percentile loudness values: \n"
    f"- N5  = {np.round(N5, 1)} sones.\n"
    f"- N10 = {np.round(N10, 1)} sones.\n"
    f"- L5  = {np.round(L5, 1)} phons.\n"
    f"- L10 = {np.round(L10, 1)} phons."
)

# %%
# Plot loudness as a function of time.
loudness_time_varying.plot()

# %%
# Calculate sharpness, roughness, and fluctuation strength
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Calculate sharpness, roughness, and fluctuation strength for the two sounds.

# %%
# Calculate the sharpness.
sharpness = Sharpness(signal=fc_two_signals)
sharpness.process()
sharpness_values = (sharpness.get_sharpness(0), sharpness.get_sharpness(1))

# %%
# Calculate the roughness.
roughness = Roughness(signal=fc_two_signals)
roughness.process()
roughness_values = (roughness.get_roughness(0), roughness.get_roughness(1))

# %%
# Calculate the fluctuation strength.
fluctuation_strength = FluctuationStrength(signal=fc_two_signals)
fluctuation_strength.process()
fluctuation_strength_values = (
    fluctuation_strength.get_fluctuation_strength(0),
    fluctuation_strength.get_fluctuation_strength(1),
)

# %%
# Print the results.
print(
    f"\nThe sharpness of sound file {file_name} "
    f"is{sharpness_values[0]: .2f} acum, "
    f"its roughness is{roughness_values[0]: .2f} asper, "
    f"and its fluctuation strength is{fluctuation_strength_values[0]: .2f} vacil.\n"
    f"For sound file {file_name2}, these indicators' values are, respectively, "
    f"{sharpness_values[1]: .2f} acum, "
    f"{roughness_values[1]: .2f} asper, "
    f"and{fluctuation_strength_values[1]: .2f} vacil.\n"
)
