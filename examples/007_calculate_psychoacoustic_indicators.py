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
- Loudness over time, according to ISO 532-1.
- Loudness (monaural ad binaural) of stationary sounds according to ISO 532-2.
- Sharpness according to Zwicker and Fastl, "Psychoacoustics: Facts and models", 1990.
- Sharpness over time, according to Zwicker and Fastl.
- Sharpness according to DIN45692.
- Sharpness over time, according to DIN45692.
- Roughness according to Daniel and Weber, "Psychoacoustical Roughness: Implementation of an
  Optimized Model, 1997.
- Roughness over time, according to Daniel and Weber.
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
    LoudnessISO532_2,
    Roughness,
    Sharpness,
    SharpnessDIN45692,
    SharpnessDIN45692OverTime,
    SharpnessOverTime,
)
from ansys.sound.core.psychoacoustics.roughness import Roughness
from ansys.sound.core.psychoacoustics.sharpness import Sharpness
from ansys.sound.core.server_helpers import connect_to_or_start_server
from ansys.sound.core.signal_utilities import LoadWav

# Connect to a remote DPF server or start a local DPF server.
my_server = connect_to_or_start_server(use_license_context=True)


# %%
# Load the WAV files used in this example
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Load the signals from WAV files using the :class:`.LoadWav` class. It is returned as a
# :class:`FieldsContainer <ansys.dpf.core.fields_container.FieldsContainer>` object.

# Load example data from WAV file: recording of a flute
path_flute_wav = download_flute_wav(server=my_server)
wav_loader = LoadWav(path_flute_wav)
wav_loader.process()
signal_flute = wav_loader.get_output()[0]

# Load another signal from a WAV file: recording of an acceleration inside a car cabin
path_accel_wav = download_accel_with_rpm_wav(server=my_server)
wav_loader = LoadWav(path_accel_wav)
wav_loader.process()
signal_car_acceleration = wav_loader.get_output()[0]
# The second field of this signal (RPM profile) is useless in this example.

# get file names, to use later on
file_name_flute = os.path.basename(path_flute_wav)
file_name_car_acceleration = os.path.basename(path_accel_wav)


# %%
# Calculate ISO 532-1 loudness for a stationary sound
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# %%
# Create a :class:`.LoudnessISO532_1_Stationary` object, set its signal, and compute the loudness
# according to standard ISO532-1.
loudness_ISO532_1_stationary = LoudnessISO532_1_Stationary(signal=signal_flute)
loudness_ISO532_1_stationary.process()

# %%
# Get the ISO532-1 loudness (in sone) and loudness level (in phon).
loudness_ISO532_1_sone = loudness_ISO532_1_stationary.get_loudness_sone()
loudness_ISO532_1_level_phon = loudness_ISO532_1_stationary.get_loudness_level_phon()

print(
    f"\nThe ISO 532-1 loudness of sound file {file_name_flute} is "
    f"{loudness_ISO532_1_sone:.1f} sones "
    f"and its loudness level is {loudness_ISO532_1_level_phon:.1f} phons."
)

# %%
# Plot the ISO532-1 specific loudness, that is, the loudness at each Bark band index.
loudness_ISO532_1_stationary.plot()

# %%
# Calculate ISO 532-1 loudness for a non-stationary sound
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# %%
# Create a :class:`.LoudnessISO532_1_TimeVarying` object, set its signal, and compute the loudness.
loudness_ISO532_1_time_varying = LoudnessISO532_1_TimeVarying(signal=signal_car_acceleration)
loudness_ISO532_1_time_varying.process()

# %%
# Get percentile loudness and loudness level values.
N5 = loudness_ISO532_1_time_varying.get_N5_sone()
N10 = loudness_ISO532_1_time_varying.get_N10_sone()
L5 = loudness_ISO532_1_time_varying.get_L5_phon()
L10 = loudness_ISO532_1_time_varying.get_L10_phon()

print(
    f"\nThe sound file {file_name_car_acceleration} has the following percentile "
    f"loudness and loudness level values:\n"
    f"- N5  = {N5:.1f} sones.\n"
    f"- N10 = {N10:.1f} sones.\n"
    f"- L5  = {L5:.1f} phons.\n"
    f"- L10 = {L10:.1f} phons."
)

# %%
# Plot loudness ISO 532-1 as a function of time.
loudness_ISO532_1_time_varying.plot()

# %%
# Calculate ISO 532-2 loudness for a stationary sound
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# %%
# Create a :class:`.LoudnessISO532_2` object, set its signal, and compute the loudness
# according to standard ISO532-2.
loudness_ISO532_2 = LoudnessISO532_2(signal=signal_flute, field_type="Free")
loudness_ISO532_2.process()

# %%
# Get the binaural and monaural ISO532-2 loudness (in sone) and loudness level (in phon).
loudness_ISO532_2_sone_monaural = loudness_ISO532_2.get_monaural_loudness_sone()[0]
loudness_ISO532_2_phon_monaural = loudness_ISO532_2.get_monaural_loudness_level_phon()[0]
loudness_ISO532_2_sone_binaural = loudness_ISO532_2.get_binaural_loudness_sone()
loudness_ISO532_2_phon_binaural = loudness_ISO532_2.get_binaural_loudness_level_phon()

print(
    f"\nThe ISO 532-2 loudness of sound file {file_name_flute} is: \n"
    f" monaural loudness: {loudness_ISO532_2_sone_monaural:.1f} sones, "
    f"{loudness_ISO532_2_phon_monaural:.1f} phons.\n"
    f" binaural loudness: {loudness_ISO532_2_sone_binaural:.1f} sones, "
    f"{loudness_ISO532_2_phon_binaural:.1f} phons."
)

# %%
# You can compare the loudness values to the ISO 532-1 loudness values,
# to see the difference between the two standards.
print(
    f"\nThe ISO 532-1 loudness of sound file {file_name_flute} is "
    f"{loudness_ISO532_1_sone:.1f} sones "
    f"and its loudness level is {loudness_ISO532_1_level_phon:.1f} phons."
)

# %%
# Plot the ISO 532-2 binaural specific loudness, that is,
# the binaural loudness at each Bark band index.
loudness_ISO532_2.plot()


# %%
# Calculate sharpness, roughness, and fluctuation strength
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# %%
# Calculate the sharpness.
sharpness = Sharpness(signal=signal_flute, field_type="Free")
sharpness.process()
sharpness_value = sharpness.get_sharpness()

# %%
# Calculate the sharpness over time and plot it.
sharpness_over_time = SharpnessOverTime(signal=signal_flute, field_type="Free")
sharpness_over_time.process()
sharpness_over_time.plot()

# %%
# Calculate the sharpness DIN45692.
sharpness_DIN45692 = SharpnessDIN45692(signal=signal_flute, field_type="Free")
sharpness_DIN45692.process()
sharpness_DIN45692_value = sharpness_DIN45692.get_sharpness()

# %%
# Calculate the sharpness DIN45692 over time and plot it.
sharpness_DIN45692_over_time = SharpnessDIN45692OverTime(signal=signal_flute, field_type="Free")
sharpness_DIN45692_over_time.process()
sharpness_DIN45692_over_time.plot()

# %%
# Calculate the roughness and roughness over time, plot the second one.
roughness = Roughness(signal=signal_flute)
roughness.process()
roughness_value = roughness.get_roughness()

# get roughness over time, and plot it.
roughness_over_time = roughness.get_roughness_over_time()
roughness.plot()

# %%
# Calculate the fluctuation strength.
fluctuation_strength = FluctuationStrength(signal=signal_flute)
fluctuation_strength.process()
fluctuation_strength_values = fluctuation_strength.get_fluctuation_strength()

# %%
# Print the results.
print(
    f"\nThe sharpness of sound file {file_name_flute} "
    f"is {sharpness_value:.2f} acum,\n"
    f"its sharpness DIN45692 is {sharpness_DIN45692_value:.2f} acum,\n"
    f"its roughness is {roughness_value:.2f} asper,\n"
    f"and its fluctuation strength is {fluctuation_strength_values:.2f} vacil."
)
