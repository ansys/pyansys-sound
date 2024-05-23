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

import matplotlib.pyplot as plt

from ansys.dpf.sound.examples_helpers import get_absolute_path_for_accel_with_rpm_wav
from ansys.dpf.sound.psychoacoustics import Loudness_ISO532_1_Stationary
from ansys.dpf.sound.server_helpers import connect_to_or_start_server
from ansys.dpf.sound.signal_utilities import LoadWav
from ansys.dpf.sound.spectrogram_processing import IsolateOrders, Stft

# Connect to remote or start a local server
connect_to_or_start_server(ansys_path=r"C:\TempDocker\ansys\dpf\server_2024_2_pre0")
# %%
# Load a wav signal with a RPM profile
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Load a wav signal using LoadWav class, the WAV file has been generated with Ansys Sound SAS.
# It contains two channels :
# - The actual signal (an acceleration recording)
# - The associated RPM profile

# Returning the input data of the example file
path_accel_wav = get_absolute_path_for_accel_with_rpm_wav()

# Load the wav file.
wav_loader = LoadWav(path_accel_wav)
wav_loader.process()
fc_signal = wav_loader.get_output()

# This file contains two channels, one is the RPM profile

signal_as_nparray = wav_loader.get_output_as_nparray()

# Extracting the WAV and the RPM signal
wav_signal = signal_as_nparray[:, 0]
rpm_signal = signal_as_nparray[:, 1]

# Plotting the signal and its associated RPM profile
fig, ax = plt.subplots(nrows=2, sharex=True)
ax[0].plot(wav_signal)
ax[0].set_title("Wav Signal")
ax[0].set_ylabel("Pa")
ax[0].grid(True)
ax[1].plot(rpm_signal, color="red")
ax[1].set_title("RPM profile")
ax[1].set_ylabel("RPM")
ax[1].grid(True)
plt.xlabel("Sample Index")
plt.show()

# %%
# Isolating Orders
# ~~~~~~~~~~~~~~~~
# Isolating orders 20, 40 and 60 with the IsolateOrders class

signal_as_fields_container = wav_loader.get_output()

# Defining parameters for order isolation
field_wav = signal_as_fields_container[0]  # Signal to process as a dpf Field
field_rpm = signal_as_fields_container[1]  # Associated RPM signal as a dpf Field
order_to_isolate = [20, 40, 60]  # Orders indexes to isolate as a list
fft_size = 128  # FFT Size (in samples)
window_type = "HAMMING"  # Window type
window_overlap = 0.9  # Window overlap
width_selection = 10  # Width of the order selection

# Instantiating the isolate orders class with the parameters
isolate_orders = IsolateOrders(
    signal=field_wav,
    rpm_profile=field_rpm,
    orders=order_to_isolate,
    fft_size=1024,
    window_type=window_type,
    window_overlap=window_overlap,
    width_selection=width_selection,
)

# Actually isolating orders
isolate_orders.process()

# Plotting the Spectrogram of the isolated orders
stft = Stft(signal=isolate_orders.get_output())
stft.process()
stft.plot()

# %%
# Isolating different orders
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# Changing fft size, orders indexes and window type and then, re-isolating the orders

# Changing some parameters directly using the setters of the class
isolate_orders.fft_size = 1024
isolate_orders.orders = [20, 80]
isolate_orders.window_type = "BLACKMAN"

# Re-processing (needs to be call explicitly, otherwise the output won't be updated)
isolate_orders.process()


# Plotting the Spectrogram of the isolated orders
stft.signal = isolate_orders.get_output()
stft.process()
stft.plot()
# %%
# Working with the isolated signal
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Plotting the signal containing the isolated orders and computing its Loudness

# Plotting the signal directly using the method from the IsolateOrders class
isolate_orders.plot()

# Using the Loudness class to compute the loudness of the isolate signal
input_loudness = isolate_orders.get_output()
input_loudness.unit = "Pa"
loudness = Loudness_ISO532_1_Stationary(signal=input_loudness)
loudness.process()

print(f"Loudness of the isolated signal is {loudness.get_loudness_level_phon()} phon.")
