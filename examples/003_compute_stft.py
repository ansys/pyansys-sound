# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
.. _compute_stft_example:

Compute the STFT and ISTFT
--------------------------

This example shows how to compute an STFT (Short-Time Fourier Transform) of a signal.

It also shows how to compute the inverse-STFT from a STFT matrix and get a signal.

"""
# %%
# Set up analysis
# ~~~~~~~~~~~~~~~
# Setting up the analysis consists of loading Ansys libraries, connecting to the
# DPF server, and retrieving the example files.

# Load Ansys libraries.
from ansys.sound.core.examples_helpers import download_flute_wav
from ansys.sound.core.server_helpers import connect_to_or_start_server
from ansys.sound.core.signal_utilities import LoadWav
from ansys.sound.core.spectrogram_processing import Istft, Stft

# Connect to remote or start a local server
my_server = connect_to_or_start_server(use_license_context=True)

# %%
# Load a wav signal using LoadWav class.

# Returning the input data of the example file
path_flute_wav = download_flute_wav()

# Loading the wav file
wav_loader = LoadWav(path_flute_wav)
wav_loader.process()
fc_signal = wav_loader.get_output()

# Plotting the input signal
wav_loader.plot()

# %%
# Instantiate an Stft class using the previously loaded signal as an input,
# using an FFT size of 1024 points, then display the STFT colormap.

stft = Stft(fc_signal, fft_size=1024)

# Processing the STFT
stft.process()

# Plotting the output
stft.plot()

# %%
# Modify the STFT parameters using the setters of the Stft class,
# then display the new STFT colormap.

stft.fft_size = 4096
stft.window_overlap = 0.95
stft.window_type = "BARTLETT"

# Re-processing the STFT with newly set parameters
stft.process()

# Plotting the modified output
stft.plot()

# %%
# Re-obtain a time-domain signal by using the Istft class.
# The input of the Istft class is the output STFT object previously computed.

fc_stft = stft.get_output()

# Instantiating the class
istft = Istft(fc_stft)

# Processing the ISTFT
istft.process()

# %%
# Finally plot the output, which is the original signal.

istft.plot()
