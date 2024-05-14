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

from ansys.dpf.sound.examples_helpers import get_absolute_path_for_flute_wav
from ansys.dpf.sound.psychoacoustics.loudness import Loudness
from ansys.dpf.sound.server_helpers import connect_to_or_start_server
from ansys.dpf.sound.signal_utilities import LoadWav

# Connect to remote or start a local server
server = connect_to_or_start_server()

# %%
# Load a wav signal using LoadWav class, it will be returned as a
# `DPF Field Container <https://dpf.docs.pyansys.com/version/stable/api/ansys.dpf.core.operators.utility.fields_container.html>`_ # noqa: E501

# Returning the input data of the example file
path_flute_wav = get_absolute_path_for_flute_wav()

# Loading the wav file
wav_loader = LoadWav(path_flute_wav)
wav_loader.process()
fc_signal = wav_loader.get_output()

# %%
# Calculating loudness
loudness = Loudness(signal=fc_signal)
loudness.process()

# %%
# Getting value in sone or in phon
loudness_sone_value = loudness.get_loudness_sone_as_float()
loudness_phon_value = loudness.get_loudness_phon_as_float()
file_name = os.path.basename(path_flute_wav)
print(
    f"\nThe loudness of sound file {file_name} "
    f"is{loudness_sone_value: .1f} sones "
    f"or{loudness_phon_value: .1f} phons.\n"
)

# %%
# Plotting the specific loudness
loudness.plot()

print("End of script reached")
