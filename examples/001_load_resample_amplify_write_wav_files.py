"""
.. _load_resample_amplify_write_wav_files_example:

Load / write wav files, resample and apply gains
------------------------------------------------

This example shows how to load a wav file, modify its sampling frequency,
amplify it and write the resulting wav file on the disk.
It also shows how to access the corresponding data and display it using matplotlib.

"""
# %%
# Set up analysis
# ~~~~~~~~~~~~~~~
# Setting up the analysis consists of loading Ansys libraries, connecting to the
# DPF server, and retrieving the example files.
#
# Load Ansys & other libraries.

import matplotlib.pyplot as plt

from ansys.sound.core.examples_helpers import get_absolute_path_for_flute_wav
from ansys.sound.core.server_helpers import connect_to_or_start_server
from ansys.sound.core.signal_utilities import ApplyGain, LoadWav, Resample, WriteWav

# Connect to remote or start a local server
server = connect_to_or_start_server()

# %%
# Load a wav Signal
# ~~~~~~~~~~~~~~~~~
# Load a wav signal using LoadWav class, it will be returned as a
# `DPF Field Container <https://dpf.docs.pyansys.com/version/stable/api/ansys.dpf.core.operators.utility.fields_container.html>`_ # noqa: E501

# Returning the input data of the example file
path_flute_wav = get_absolute_path_for_flute_wav()

# Load the wav file.
wav_loader = LoadWav(path_flute_wav)
wav_loader.process()
fc_signal_original = wav_loader.get_output()

t1 = fc_signal_original[0].time_freq_support.time_frequencies.data
sf1 = 1.0 / (t1[1] - t1[0])
print(f"The sampling frequency of the original signal is {int(sf1)} Hz")

# %%
# Resample the signal
# ~~~~~~~~~~~~~~~~~~~
# Change the sampling frequency of the loaded signal.
resampler = Resample(fc_signal_original, new_sampling_frequency=20000.0)
resampler.process()
fc_signal_resampled = resampler.get_output()

# %%
# Apply a gain to the signal
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# Change the gain of the resampled signal.
gain = 10.0
gain_applier = ApplyGain(fc_signal_resampled, gain=gain, gain_in_db=True)
gain_applier.process()
fc_signal_modified = gain_applier.get_output()

t2 = fc_signal_modified[0].time_freq_support.time_frequencies.data
sf2 = 1.0 / (t2[1] - t2[0])
print(f"The new sampling frequency of the signal is {int(sf2)} Hz")

# %%
# Plotting signals
# ~~~~~~~~~~~~~~~~
# Plot the original and the modified signals.
data_original = wav_loader.get_output_as_nparray()
data_modified = gain_applier.get_output_as_nparray()

fig, axs = plt.subplots(2)
fig.suptitle("Signals")

axs[0].plot(t1, data_original, color="g", label=f"original signal, sf={int(sf1)} Hz")
axs[0].set_ylabel("Pa")
axs[0].legend(loc="upper right")
axs[0].set_ylim([-3, 3])

axs[1].plot(
    t2, data_modified, color="r", label=f"modified signal, sf={int(sf2)} Hz, gain={gain} dBSPL"
)
axs[1].set_xlabel("Time(s)")
axs[1].set_ylabel("Amplitude(Pa)")
axs[1].legend(loc="upper right")
axs[1].set_ylim([-3, 3])

plt.show()

# %%
# Write the signals as wav files
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Write the modified signal in memory using WriteWav class
output_path = path_flute_wav[:-4] + "_modified.wav"  # "[-4]" is to remove the ".wav"
wav_writer = WriteWav(path_to_write=output_path, signal=fc_signal_modified, bit_depth="int16")
wav_writer.process()
