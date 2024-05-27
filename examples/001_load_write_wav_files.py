# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.

"""
.. _load_resample_amplify_write_wav_files_example:

Load / Write Wav Files, resample and apply gains
----------------------

This example shows how to load a Wav file, modify its samply frequency, amplify it and write the resulting Wav file in memory.
It also shows how to access the corresponding data and display it using numpy.

"""
# %% 
# Set up analysis 
# ~~~~~~~~~~~~~~~
# Setting up the analysis consists of loading Ansys libraries, connecting to the 
# DPF server, and retrieving the example files.
#
# Load Ansys & other libraries.

import ansys.dpf.core as dpf

from ansys.dpf.sound.examples_helpers import get_absolute_path_for_flute_wav
from ansys.dpf.sound.server_helpers import connect_to_or_start_server
from ansys.dpf.sound.signal_utilities import LoadWav, Resample, ApplyGain, WriteWav

import matplotlib.pyplot as plt

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
fc_signal_original = wav_loader.get_output()

# %%
# Change the sampling frequency of the loaded signal.
resampler = Resample(fc_signal_original, new_sampling_frequency = 20000)
resampler.process()
fc_signal_resampled = resampler.get_output()

t1 = fc_signal_original[0].time_freq_support.time_frequencies.data 
sf1=(1.0/(t1[1] - t1[0]))
print (f"The sampling frequency of the original signal is {sf1:.1f} Hz" ) #":.1f" is to only get 1 decimal

# %%
# Change the gain of the resampled signal.
g = 10
gain_applier= ApplyGain(fc_signal_resampled, gain = g, gain_in_db = True)
gain_applier.process()
fc_signal_modified = gain_applier.get_output()

t2 = fc_signal_modified[0].time_freq_support.time_frequencies.data 
sf2=(1.0/(t2[1] - t2[0]))
print (f"The new sampling frequency of the signal is {sf2:.1f} Hz" ) #":.1f" is to only get 1 decimal

# %%
# Plot the original and the modified signals.
data_original = wav_loader.get_output_as_nparray()
data_modified = gain_applier.get_output_as_nparray()

fig, axs = plt.subplots(2)
fig.suptitle('Signals')

axs[0].plot(t1 , data_original , color='g', label=f'original signal, sf={sf1:.1f} Hz')
axs[0].set_ylabel('Pa')
axs[0].legend(loc="upper right")
axs[0].set_ylim([-3, 3])

axs[1].plot(t2 , data_modified , color='r', label=f'modified signal, sf={sf2:.1f} Hz, gain={g} dBSPL')
axs[1].set_xlabel('s')
axs[1].set_ylabel('Pa')
axs[1].legend(loc="upper right")
axs[1].set_ylim([-3, 3])

plt.show()

# %% Write the modified signal in memory using WriteWav class
output_path = path_flute_wav[:-4] + "_modified.wav" #"[-4]" is to remove the ".wav"
wav_writer = WriteWav(path_to_write=output_path, signal=fc_signal_modified, bit_depth="int16")
wav_writer.process()
print("End of script reached")