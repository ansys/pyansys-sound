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

from ansys.sound.core.examples_helpers import (
    download_accel_with_rpm_wav,
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
# Load a signal from a WAV file using the :class:`LoadWav` class. It is returned as a DPF
# field container :class:`FieldsContainer <ansys.dpf.core.fields_container.FieldsContainer>`.

# Load example data from WAV file
path_flute_wav = download_flute_wav(server=my_server)
wav_loader = LoadWav(path_flute_wav)
wav_loader.process()
signal_field_1 = wav_loader.get_output()[0]

# %%
# Create a :class:`LoudnessISO532_1_Stationary` object, set its signal, and compute the loudness.
loudness_stationary = LoudnessISO532_1_Stationary(signal=signal_field_1)
loudness_stationary.process()

# %%
# Get the loudness (in sone) and loudness level (in phon).
loudness_sone = loudness_stationary.get_loudness_sone()
loudness_level_phon = loudness_stationary.get_loudness_level_phon()
file_name_1 = os.path.basename(path_flute_wav)
print(
    f"\nThe loudness of sound file {file_name_1} is {loudness_sone:.1f} sones and its loudness "
    f"level is {loudness_level_phon:.1f} phons."
)

# %%
# Plot the specific loudness, that is, the loundess at each Bark band index.
loudness_stationary.plot()

# %%
# Calculate ISO 532-1 loudness for a non-stationary sound
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Load a new (non-stationary) signal from a WAV file.
path_accel_wav = download_accel_with_rpm_wav(server=my_server)
wav_loader = LoadWav(path_accel_wav)
wav_loader.process()
signal_field_2 = wav_loader.get_output()[
    0
]  # Field 0 only, because the RPM profile is useless here.

# %%
# Create a :class:`LoudnessISO532_1_TimeVarying` object, set its signal, and compute the loudness.
loudness_time_varying = LoudnessISO532_1_TimeVarying(signal=signal_field_2)
loudness_time_varying.process()

# %%
# Get percentile loudness and loudness level values.
N5 = loudness_time_varying.get_N5_sone()
N10 = loudness_time_varying.get_N10_sone()
L5 = loudness_time_varying.get_L5_phon()
L10 = loudness_time_varying.get_L10_phon()

file_name_2 = os.path.basename(path_accel_wav)
print(
    f"\nThe sound file {file_name_2} has the following percentile loudness and loudness level "
    "values: \n"
    f"- N5  = {N5:.1f} sones.\n"
    f"- N10 = {N10:.1f} sones.\n"
    f"- L5  = {L5:.1f} phons.\n"
    f"- L10 = {L10:.1f} phons."
)

# %%
# Plot loudness as a function of time.
loudness_time_varying.plot()

# %%
# Calculate sharpness, roughness, and fluctuation strength
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# %%
# Calculate the sharpness.
sharpness = Sharpness(signal=signal_field_1, field_type="Free")
sharpness.process()
sharpness_value = sharpness.get_sharpness()

# %%
# Calculate the roughness.
roughness = Roughness(signal=signal_field_1)
roughness.process()
roughness_value = roughness.get_roughness()

# %%
# Calculate the fluctuation strength.
fluctuation_strength = FluctuationStrength(signal=signal_field_1)
fluctuation_strength.process()
fluctuation_strength_values = fluctuation_strength.get_fluctuation_strength()

# %%
# Print the results.
print(
    f"\nThe sharpness of sound file {file_name_1} "
    f"is {sharpness_value:.2f} acum, "
    f"its roughness is {roughness_value:.2f} asper, "
    f"and its fluctuation strength is {fluctuation_strength_values:.2f} vacil.\n"
)
