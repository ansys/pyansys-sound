# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.

"""
.. _load_write_wav_files_example:

Load / Write Wav Files
----------------------

This example shows how to load and write wav files.
It also shows how to access the corresponding data and display it using numpy.

"""
# %%
# Set up analysis
# ~~~~~~~~~~~~~~~
# Setting up the analysis consists of loading Ansys libraries, connecting to the
# DPF server, and retrieving the example files.
#
# Load Ansys libraries.

import ansys.dpf.core as dpf

from ansys.dpf.sound.examples_helpers import get_absolute_path_for_flute_wav
from ansys.dpf.sound.server_helpers import connect_to_or_start_server
from ansys.dpf.sound.signal_utilities import LoadWav, WriteWav

# Connect to remote or start a local server
connect_to_or_start_server(ansys_path=r'C:\Program Files\ANSYS Inc\v242\ansys_dpf_server_win_v2024.2.pre1\ansys\dpf\server_2024_2_pre1')

# %%
# Load a wav signal using LoadWav class, it will be returned as a
# `DPF Field Container <https://dpf.docs.pyansys.com/version/stable/api/ansys.dpf.core.operators.utility.fields_container.html>`_ # noqa: E501

# Returning the input data of the example file
path_flute_wav = get_absolute_path_for_flute_wav()

# Load the wav file.
wav_loader = LoadWav(path_flute_wav)
wav_loader.process()
fc_signal = wav_loader.get_output()

print("TEST")

# %%
# Plot the loaded signal.
wav_loader.plot()

# %%
# Create a modified version of the signal.
#
# Write the modified signal in memory using WriteWav class.
#
# Write the output signal in the same folder as the input, with a "_modified" suffix.
fc_signal_modified = dpf.FieldsContainer.deep_copy(fc_signal)
fc_signal_modified[0].data = fc_signal[0].data * 0.2
output_path = path_flute_wav[:-4] + "_modified.wav"

wav_writer = WriteWav(path_to_write=output_path, signal=fc_signal_modified, bit_depth="int16")
wav_writer.process()
print("End of script reached")
