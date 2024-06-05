"""
.. _isolate_orders_example:

Isolate Orders
--------------

This example shows how to isolate orders (harmonic and partial components in the sound related to
the speed of a rotating machine) in a signal containing a RPM profile.
It also uses additional classes from pyansys-sound to compute spectrograms
and the loudness of the isolated signals.

"""

# Maximum frequency for STFT plots, change according to your need
MAX_FREQUENCY_PLOT_STFT = 2000.0

# %%
# Set up analysis
# ~~~~~~~~~~~~~~~
# Setting up the analysis consists of loading Ansys libraries, connecting to the
# DPF server, and retrieving the example files.
#

# Load Ansys libraries.
import pathlib

import matplotlib.pyplot as plt
import numpy as np

from ansys.sound.core.examples_helpers import get_absolute_path_for_accel_with_rpm_wav
from ansys.sound.core.psychoacoustics import LoudnessISO532_1_Stationary
from ansys.sound.core.server_helpers import connect_to_or_start_server
from ansys.sound.core.signal_utilities import LoadWav, WriteWav
from ansys.sound.core.spectrogram_processing import IsolateOrders, Stft

# Connect to remote or start a local server
connect_to_or_start_server()


# %%
# Defining a custom function for STFT plots
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Defining a custom function for STFT plots that will allow us to have
# more control over what we're displaying.
# Note that we could use Stft.plot() but in this example,
# we want to restrict the frequency range of the plot, hence the custom function.
def plot_stft(stft_class, vmax):
    out = stft_class.get_output_as_nparray()

    # Extracting first half of the STFT (second half is symmetrical)
    half_nfft = int(out.shape[0] / 2) + 1
    magnitude = stft_class.get_stft_magnitude_as_nparray()

    # Voluntarily ignoring a numpy warning
    np.seterr(divide="ignore")
    magnitude = 20 * np.log10(magnitude[0:half_nfft, :])
    np.seterr(divide="warn")

    # Obtaining sampling frequency, time steps and number of time samples
    fs = 1.0 / (
        stft_class.signal.time_freq_support.time_frequencies.data[1]
        - stft_class.signal.time_freq_support.time_frequencies.data[0]
    )
    time_step = np.floor(stft_class.fft_size * (1.0 - stft_class.window_overlap) + 0.5) / fs
    num_time_index = len(stft_class.get_output().get_available_ids_for_label("time"))

    # Boundaries of the plot
    extent = [0, time_step * num_time_index, 0.0, fs / 2.0]

    # Plotting
    plt.imshow(
        magnitude,
        origin="lower",
        aspect="auto",
        cmap="jet",
        extent=extent,
        vmin=vmax - 70.0,
        vmax=vmax,
    )
    plt.colorbar(label="Amplitude (dB SPL)")
    plt.ylabel("Frequency (Hz)")
    plt.xlabel("Time (s)")
    plt.ylim(
        [0.0, MAX_FREQUENCY_PLOT_STFT]
    )  # Change the value of MAX_FREQUENCY_PLOT_STFT if needed
    plt.title("STFT")
    plt.show()


# %%
# Load a wav signal with a RPM profile
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Load a wav signal using LoadWav class, the WAV file has been generated with Ansys Sound SAS.
# It contains two channels :
#
# - The actual signal (an acceleration recording)
#
# - The associated RPM profile

# Returning the input data of the example file
path_accel_wav = get_absolute_path_for_accel_with_rpm_wav()

# Load the wav file.
wav_loader = LoadWav(path_accel_wav)
wav_loader.process()
fc_signal = wav_loader.get_output()

# Extract the audio signal and the RPM profile
wav_signal, rpm_signal = wav_loader.get_output_as_nparray()

# Extracting time support associated to the signal
time_support = fc_signal[0].time_freq_support.time_frequencies.data

# Plotting the signal and its associated RPM profile
fig, ax = plt.subplots(nrows=2, sharex=True)
ax[0].plot(time_support, wav_signal)
ax[0].set_title("Audio Signal")
ax[0].set_ylabel("Amplitude (Pa)")
ax[0].grid(True)
ax[1].plot(time_support, rpm_signal, color="red")
ax[1].set_title("RPM profile")
ax[1].set_ylabel("rpm")
ax[1].grid(True)
plt.xlabel("Time (s)")
plt.show()

# %%
# Plotting spectrogram of the original signal
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Plotting the Spectrogram of the original signal

stft = Stft(signal=fc_signal[0], window_overlap=0.9, fft_size=8192)
stft.process()
max_stft = 20 * np.log10(np.max(stft.get_stft_magnitude_as_nparray()))
plot_stft(stft, max_stft)

# %%
# Isolating Orders
# ~~~~~~~~~~~~~~~~
# Isolating orders 2, 4 and 6 with the IsolateOrders class

field_wav, field_rpm = wav_loader.get_output()

# Defining parameters for order isolation
field_wav.unit = "Pa"
order_to_isolate = [2, 4, 6]  # Orders indexes to isolate as a list
fft_size = 8192  # FFT Size (in samples)
window_type = "HANN"  # Window type
window_overlap = 0.9  # Window overlap
width_selection = 3  # Width of the order selection in Hz

# Instantiating the IsolateOrders class with the parameters
isolate_orders = IsolateOrders(
    signal=field_wav,
    rpm_profile=field_rpm,
    orders=order_to_isolate,
    fft_size=fft_size,
    window_type=window_type,
    window_overlap=window_overlap,
    width_selection=width_selection,
)

# Actually isolating orders
isolate_orders.process()

# Plotting the Spectrogram of the isolated orders
stft.signal = isolate_orders.get_output()
stft.process()
plot_stft(stft, max_stft)

# %%
# Isolating different orders
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# Changing fft size, orders indexes and window type and then, re-isolating the orders

# Changing some parameters directly using the setters of the class
isolate_orders.orders = [2, 6]
isolate_orders.window_type = "BLACKMAN"

# Re-processing (needs to be called explicitly, otherwise the output won't be updated)
isolate_orders.process()


# Plotting the Spectrogram of the isolated orders
stft.signal = isolate_orders.get_output()
stft.process()
plot_stft(stft, max_stft)
# %%
# Working with the isolated signal
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Plotting the signal containing the isolated orders and computing its Loudness

# Plotting the signal directly using the method from the IsolateOrders class
isolate_orders.plot()

# Using the Loudness class to compute the loudness of the isolate signal
input_loudness = isolate_orders.get_output()
input_loudness.unit = "Pa"
loudness = LoudnessISO532_1_Stationary(signal=input_loudness)
loudness.process()

loudness_isolated_signal = loudness.get_loudness_level_phon()

# Computing the loudness for the original signal
loudness.signal = field_wav
loudness.process()

loudness_original_signal = loudness.get_loudness_level_phon()

print(f"Loudness of the original signal: {loudness_original_signal: .1f} phons.")
print(f"Loudness of the isolated signal: {loudness_isolated_signal: .1f} phons.")

# %%
# Isolating orders of several signals in a loop
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Looping over a list of given signals and writing them as a wav file.

# Obtaining parent folder of accel_with_rpm.wav
parent_folder = pathlib.Path(path_accel_wav).parent.absolute()

fft_sizes = [256, 2048, 4096]

wav_writer = WriteWav()

# Isolating orders for all the files containing RPM profiles in this folder
for file, fft_sz in zip(parent_folder.glob("accel_with_rpm_*.wav"), fft_sizes):
    # Loading the file
    wav_loader.path_to_wav = file
    wav_loader.process()

    # Setting Parameters for order isolation
    isolate_orders.signal = wav_loader.get_output()[0]
    isolate_orders.rpm_profile = wav_loader.get_output()[1]
    isolate_orders.fft_size = fft_sz
    isolate_orders.process()

    # Writing the file in memory
    out_name = str(file.stem) + "_isolated_fft_size_" + str(fft_sz) + ".wav"
    path_to_write = parent_folder / "output/" / out_name
    wav_writer.path_to_write = str(path_to_write)
    wav_writer.signal = isolate_orders.get_output()
    wav_writer.process()
