# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.

"""
.. _load_write_wav_files_example:

Load / Write Wav Files
----------------------

This example shows how to load and write wav files.
It also show how to access the corresponding data and display it using numpy.

"""
# %%
# Set up analysis
# ~~~~~~~~~~~~~~~
# Setting up the analysis consists of loading Ansys libraries, connecting to the
# DPF server, and retrieving the example files.
#
# Load Ansys libraries.

import ansys.dpf.core as dpf
import matplotlib.pyplot as plt

from ansys.dpf.sound.examples_helpers import get_absolute_path_for_flute_wav
from ansys.dpf.sound.server_helpers import connect_to_or_start_server
from ansys.dpf.sound.sound_helpers import load_wav_signal, write_wav_signal

# Connect to remote or start a local server
connect_to_or_start_server(ansys_path=r"C:\TempDocker\ansys\dpf\server_2024_2_pre0")
path_flute_wav = get_absolute_path_for_flute_wav()

# %%
# Load a wav signal using load_wav_signal, it will be returned as a
# `DPF Field Container <https://dpf.docs.pyansys.com/version/stable/api/ansys.dpf.core.operators.utility.fields_container.html>`_ # noqa: E501

# Returning the input data of the example file
path_flute_wav = get_absolute_path_for_flute_wav()

# Loading the wav file
fc_signal = load_wav_signal(path_flute_wav)

# %%
# Create a modified version of the signal and plot the signals
fc_signal_modified = dpf.FieldsContainer.deep_copy(fc_signal)
fc_signal_modified[0].data = fc_signal[0].data * 0.2

# Obtaining the [Time Frequency support](https://dpf.docs.pyansys.com/version/stable/api/ansys.dpf.core.time_freq_support.html) # noqa: E501
# that contains the associated times of the signal
time_support = fc_signal[0].time_freq_support.time_frequencies.data

plt.plot(time_support, fc_signal[0].data, label="Original Signal")
plt.plot(time_support, fc_signal_modified[0].data, label="Modified Signal")
plt.title("My signals")
plt.legend()
plt.xlabel("s")
plt.ylabel("Pa")
plt.show()

# %%
# Write the modified signal in memory using write_wav_signal

write_wav_signal("flute_modified.wav", fc_signal_modified, "int16")

print("End of script reached")
