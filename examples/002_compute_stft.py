# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.

"""
.. _compute_stft_example:

Compute the STFT and ISTFT
--------------------------

This example shows how to compute a STFT (Short-Time Fourier Transform) of a signal.

It also shows how to compute the inverse-STFT of a signal.

"""
# %%
# Set up analysis
# ~~~~~~~~~~~~~~~
# Setting up the analysis consists of loading Ansys libraries, connecting to the
# DPF server, and retrieving the example files.
#
# Load Ansys libraries.

from ansys.dpf.sound.examples_helpers import get_absolute_path_for_flute_wav
from ansys.dpf.sound.server_helpers import connect_to_or_start_server
from ansys.dpf.sound.signal_utilities import LoadWav
from ansys.dpf.sound.spectrogram_processing import Istft, Stft

# Connect to remote or start a local server
connect_to_or_start_server()

# %%
# Load a wav signal using LoadWav class

# Returning the input data of the example file
path_flute_wav = get_absolute_path_for_flute_wav()

# Loading the wav file
wav_loader = LoadWav(path_flute_wav)
wav_loader.process()
fc_signal = wav_loader.get_output()

# Plotting the input signal
wav_loader.plot()

# %%
# Instantiate an STFT class using the previously loaded signal as an input
# Using an FFT Size of 1024

stft = Stft(fc_signal, fft_size=1024)

# Processing the STFT
stft.process()

# Plotting the output
stft.plot()

# %%
# Modifying STFT parameters using the setters of the Stft class.

stft.fft_size = 4096
stft.window_overlap = 0.1
stft.window_type = "BARTLETT"

# Re-processing the STFT with newly set parameters
stft.process()

# Plotting the modified output
stft.plot()

# %%
# Re-obtaining time-domain signal by using the Istft class.
# The input of the Istft class is the output stft previously computed.

fc_stft = stft.get_output()

# Instantiating the class
istft = Istft(fc_stft)

# Processing the ISTFT
istft.process()

# %%
# Finally plotting the output which is the original signal

istft.plot()