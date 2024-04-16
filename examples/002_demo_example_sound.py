# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.

"""

Demo Example Sound
------------------

This example shows how to load and crop a wav signal.

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
from ansys.dpf.sound.signal_utilities import CropSignal, LoadWav

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
wav_loader.plot()

# %%
# Let's crop the signal

cropper = CropSignal(signal=fc_signal, start_time=1.0, end_time=2.0)

cropper.process()

cropper.plot()
