# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.

"""
.. _compute_stft_example:

Compute Stft
------------

This example shows how to compute a STFT.

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
from ansys.dpf.sound.spectrogram_processing import Stft

# Connect to remote or start a local server
connect_to_or_start_server()

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
# Instantiate Stft class

stft = Stft(fc_signal, fft_size=1024)


stft.process()

# stft.get_output_as_nparray()

stft.plot()
