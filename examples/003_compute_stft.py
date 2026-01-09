# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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

Spectrogram: compute the STFT and ISTFT
---------------------------------------

This example shows how to compute the short-time Fourier transform (STFT) of a signal.
It also shows how to compute the inverse short-time Fourier transform (ISTFT) from a
STFT matrix and get a signal.

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

# sphinx_gallery_start_ignore
# sphinx_gallery_thumbnail_path = '_static/_image/example003_thumbnail.png'
# sphinx_gallery_end_ignore

# Connect to a remote DPF server or start a local DPF server.
my_server, my_license_context = connect_to_or_start_server(use_license_context=True)

# %%
# Load a signal
# ~~~~~~~~~~~~~
# Load a signal from a WAV file using the ``LoadWav`` class. It is returned as a DPF
# field container. For more information, see `fields_container
# <https://dpf.docs.pyansys.com/version/stable/api/ansys.dpf.core.operators.utility.fields_container.html>`_
# in the DPF-Core API documentation.

# Return the input data of the example file
path_flute_wav = download_flute_wav(server=my_server)

# Load the WAV file
wav_loader = LoadWav(path_flute_wav)
wav_loader.process()
fc_signal = wav_loader.get_output()

# Plot the input signal
wav_loader.plot()

# %%
# Compute and plot STFT
# ~~~~~~~~~~~~~~~~~~~~~

# Instantiate an instance of the ``Stft`` class using the previously loaded signal
# as an input. Use an FFT size of 1024 points and then display the STFT colormap.

stft = Stft(fc_signal, fft_size=1024)

# Process the STFT
stft.process()

# Plot the output
stft.plot()

# %%
# Modify the STFT parameters using the setters of the ``Stft`` class.
# Display the new STFT colormap.

stft.fft_size = 4096
stft.window_overlap = 0.95
stft.window_type = "TRIANGULAR"

# Reprocess the STFT with the new parameters
stft.process()

# Plot the modified output
stft.plot()

# %%
# Compute and plot ISTFT
# ~~~~~~~~~~~~~~~~~~~~~~

# Obtain a time-domain signal using the ``Istft`` class.
# The input of the ``Istft`` class is the output STFT object previously computed.

fc_stft = stft.get_output()

# Instantiate the class
istft = Istft(fc_stft)

# Process the ISTFT
istft.process()

# %%
# Plot the output, which is the original signal.

istft.plot()
