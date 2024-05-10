# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.

"""
.. _calculate_psychoacoustic_indicators:

Calculate psychoacoustic indicators
-----------------------------------

This example shows how to calculate psychoacoustic indicators.
It also show how to plot specific loudness.

"""
# %%
# Set up analysis
# ~~~~~~~~~~~~~~~
# Setting up the analysis consists of loading Ansys libraries, connecting to the
# DPF server, and retrieving the example files.
#
# Load Ansys libraries.

import os
import ansys.dpf.core as dpf

from ansys.dpf.sound.examples_helpers import get_absolute_path_for_flute_wav
from ansys.dpf.sound.server_helpers import connect_to_or_start_server
from ansys.dpf.sound.signal_utilities import LoadWav, WriteWav
from ansys.dpf.sound.psychoacoustics.loudness import Loudness

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
loudness_sone = loudness.get_loudness_sone()
loudness_sone_value = loudness_sone[0].data[0]
loudness_phon = loudness.get_loudness_phon()
loudness_phon_value = loudness_phon[0].data[0]
file_name = os.path.basename(path_flute_wav)
print("\nThe loudness of sound file %s is %.1f sones or %.1f phons.\n" % (file_name, loudness_sone_value, loudness_phon_value))


# %%
# Plotting the specific loudness
loudness.plot()

print("End of script reached")
