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

from ansys.dpf.sound.examples_helpers import (
    get_absolute_path_for_flute2_wav,
    get_absolute_path_for_flute_wav,
)
from ansys.dpf.sound.psychoacoustics.loudness_iso532_1_stationary import (
    Loudness_ISO532_1_stationary,
)
from ansys.dpf.sound.server_helpers import connect_to_or_start_server
from ansys.dpf.sound.signal_utilities import LoadWav

# Connect to remote or start a local server.
server = connect_to_or_start_server()

# %%
# Load a wav signal using LoadWav class, it will be returned as a
# `DPF Field Container <https://dpf.docs.pyansys.com/version/stable/api/ansys.dpf.core.operators.utility.fields_container.html>`_ # noqa: E501

# Return the input data of the example file.
path_flute_wav = get_absolute_path_for_flute_wav()

# Load the wav file.
wav_loader = LoadWav(path_flute_wav)
wav_loader.process()
fc_signal = wav_loader.get_output()

# %%
# Calculate ISO 532-1 loudness for a stationary sound
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create a Loudness object, set its signal, and compute loudness.
loudness = Loudness_ISO532_1_stationary(signal=fc_signal)
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
loudness = Loudness_ISO532_1_stationary(signal=fc_two_signals)
loudness.process()

# %%
# Get values in sone or in phon.
loudness_sone2 = loudness.get_loudness_sone(1)
loudness_level_phon2 = loudness.get_loudness_level_phon(1)
file_name2 = os.path.basename(path_flute2_wav)
print(
    f"\nThe loudness of sound file {file_name} "
    f"is{loudness_sone: .1f} sones "
    f"or{loudness_level_phon: .1f} phons,\n"  # noqa: E231
    f"whereas the loudness of sound file {file_name2} "
    f"is{loudness_sone2: .1f} sones "
    f"or{loudness_level_phon2: .1f} phons.\n"
)

# %%
# Plot specific loudness for both signals into a single figure.
loudness.plot()

# %%
# End of script.
print("End of script reached")
