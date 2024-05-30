# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.

"""
.. _calculate_psychoacoustic_indicators:

Calculate psychoacoustic indicators
-----------------------------------

This example shows how to calculate psychoacoustic indicators.
It also shows how to plot specific loudness.

"""
# %%
# Set up analysis
# ~~~~~~~~~~~~~~~
# Setting up the analysis consists of loading Ansys libraries, connecting to the
# DPF server, and retrieving the example files.
#
# Load Ansys libraries.

import os

from ansys.sound.core.examples_helpers import (
    get_absolute_path_for_flute2_wav,
    get_absolute_path_for_flute_wav,
)
from ansys.sound.core.psychoacoustics.fluctuation_strength import FluctuationStrength
from ansys.sound.core.psychoacoustics.loudness_iso_532_1_stationary import (
    LoudnessISO532_1_Stationary,
)
from ansys.sound.core.psychoacoustics.roughness import Roughness
from ansys.sound.core.psychoacoustics.sharpness import Sharpness
from ansys.sound.core.server_helpers import connect_to_or_start_server
from ansys.sound.core.signal_utilities import LoadWav

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

# Create a Loudness object, set its signal, and compute loudness.
loudness = LoudnessISO532_1_Stationary(signal=fc_signal)
loudness.process()

# %%
# Get value in sone or in phon.
loudness_sone = loudness.get_loudness_sone()
loudness_level_phon = loudness.get_loudness_level_phon()
file_name = os.path.basename(path_flute_wav)
print(
    f"\nThe loudness of sound file {file_name} "
    f"is{loudness_sone: .1f} sones "
    f"or{loudness_level_phon: .1f} phons.\n"
)

# %%
# Plot the specific loudness.
loudness.plot()

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
loudness = LoudnessISO532_1_Stationary(signal=fc_two_signals)
loudness.process()

# %%
# Get values in sone or in phon.
loudness_sone2 = loudness.get_loudness_sone(1)
loudness_level_phon2 = loudness.get_loudness_level_phon(1)
file_name2 = os.path.basename(path_flute2_wav)
print(
    f"The loudness of sound file {file_name} "
    f"is{loudness_sone: .1f} sones "
    f"or{loudness_level_phon: .1f} phons,\n"  # noqa: E231
    f"whereas the loudness of sound file {file_name2} "
    f"is{loudness_sone2: .1f} sones "
    f"or{loudness_level_phon2: .1f} phons.\n"
)

# %%
# Plot specific loudness for both signals into a single figure. Note how the first sound has a
# higher specific loudness than the second.
loudness.plot()

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
    f"The sharpness of sound file {file_name} "
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
