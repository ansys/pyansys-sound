# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.

"""
.. _calculate_psychoacoustic_indicators:

Calculate psychoacoustic indicators
-----------------------------------

This example shows how to calculate psychoacoustic indicators.
The following indicators are included:
- Loudness of stationary sounds according to ISO 532-1;
- Loudness of time-varying sounds according to ISO 532-1;
- Sharpness according to Zwicker and Fastl, "Psychoacoustics: Facts and models", 1990;
- Roughness according to Daniel and Weber, "Psychoacoustical Roughness: Implementation of an
  Optimized Model, 1997;
- Fluctuation strength according to Sontacchi, "Entwicklung eines Modulkonzeptes für die
  psychoakustische Geräuschanalyse under MatLab Diplomarbeit", 1998.

The example shows how to:
- import necessary packages,
- calculate indicators on loaded wav files,
- get calculation outputs,
- and plot some corresponding curves.

"""
# %%
# Set up analysis
# ~~~~~~~~~~~~~~~
# Setting up the analysis consists of loading Ansys libraries, connecting to the
# DPF server, and retrieving the example files.
#
# Load Ansys libraries.

import os

from ansys.dpf.sound.examples_helpers import (
    get_absolute_path_for_accel_with_rpm_wav,
    get_absolute_path_for_flute2_wav,
    get_absolute_path_for_flute_wav,
)
from ansys.dpf.sound.psychoacoustics import (
    FluctuationStrength,
    LoudnessISO532_1_Stationary,
    LoudnessISO532_1_TimeVarying,
    Roughness,
    Sharpness,
)
from ansys.dpf.sound.server_helpers import connect_to_or_start_server
from ansys.dpf.sound.signal_utilities import LoadWav

# Connect to remote or start a local server.
server = connect_to_or_start_server()

# %%
# Calculate ISO 532-1 loudness for a stationary sound
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Load a wav signal using LoadWav class, it will be returned as a
# `DPF Field Container <https://dpf.docs.pyansys.com/version/stable/api/ansys.dpf.core.operators.utility.fields_container.html>`_ # noqa: E501
path_flute_wav = get_absolute_path_for_flute_wav()
wav_loader = LoadWav(path_flute_wav)
wav_loader.process()
fc_signal = wav_loader.get_output()

# Create a LoudnessISO532_1_Stationary object, set its signal, and compute loudness.
loudness_stationary = LoudnessISO532_1_Stationary(signal=fc_signal)
loudness_stationary.process()

# %%
# Get value in sone or in phon.
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
# Load another wav file.
path_flute2_wav = get_absolute_path_for_flute2_wav()
wav_loader = LoadWav(path_flute2_wav)
wav_loader.process()

# Store the second signal with the first one.
fc_two_signals = fc_signal
fc_two_signals.add_field({"channel_number": 1}, wav_loader.get_output()[0])


# %%
# Calculate loudness for both signals at once.
loudness_stationary = LoudnessISO532_1_Stationary(signal=fc_two_signals)
loudness_stationary.process()

# %%
# Get values in sone or in phon.
loudness_sone2 = loudness_stationary.get_loudness_sone(1)
loudness_level_phon2 = loudness_stationary.get_loudness_level_phon(1)
file_name2 = os.path.basename(path_flute2_wav)
print(
    f"In comparison, the loudness of sound file {file_name2} "
    f"is{loudness_sone2: .1f} sones "
    f"or{loudness_level_phon2: .1f} phons."
)

# %%
# Plot specific loudness for both signals into a single figure. Note how the first sound has a
# higher specific loudness than the second.
loudness_stationary.plot()

# %%
# Calculate ISO 532-1 loudness for a non-stationary sound
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Load a new wav signal (non-stationary)
path_accel_wav = get_absolute_path_for_accel_with_rpm_wav()
wav_loader = LoadWav(path_accel_wav)
wav_loader.process()
f_signal = wav_loader.get_output()[0]  # Field 0 only, because we the RPM profile is useless here.

# Create a LoudnessISO532_1_TimeVarying object, set its signal, and compute loudness.
loudness_time_varying = LoudnessISO532_1_TimeVarying(signal=f_signal)
loudness_time_varying.process()

# Get percentile loudness values.
N5 = loudness_time_varying.get_N5_sone()
N10 = loudness_time_varying.get_N10_sone()
L5 = loudness_time_varying.get_L5_phon()
L10 = loudness_time_varying.get_L10_phon()

file_name3 = os.path.basename(path_accel_wav)
print(
    f"\nThe sound file {file_name3} has the following percentile loudness values: \n"
    f"- N5  ={N5: .1f} sones.\n"
    f"- N10 ={N10: .1f} sones.\n"
    f"- L5  ={L5: .1f} phons.\n"
    f"- L10 ={L10: .1f} phons."
)

# %%
# Plot loudness as a function of time.
loudness_time_varying.plot()

# %%
# Calculate sharpness, roughness, and fluctuation strength
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Now let's calculate sharpness, roughness, and fluctuation strength for these two sounds.

# %%
# Calculate sharpness.
sharpness = Sharpness(signal=fc_two_signals)
sharpness.process()
sharpness_values = (sharpness.get_sharpness(0), sharpness.get_sharpness(1))

# %%
# Calculate roughness.
roughness = Roughness(signal=fc_two_signals)
roughness.process()
roughness_values = (roughness.get_roughness(0), roughness.get_roughness(1))

# %%
# Calculate fluctuation strength.
fluctuation_strength = FluctuationStrength(signal=fc_two_signals)
fluctuation_strength.process()
fluctuation_strength_values = (
    fluctuation_strength.get_fluctuation_strength(0),
    fluctuation_strength.get_fluctuation_strength(1),
)

# Print out the results.
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

# %%
# End of script.
print("End of script reached")
