"""
.. _xtract_module_example:

Xtract Module
-------------

This example shows how to use the "Xtract" module in PyAnsys Sound.
It displays the different features of this module such as :
- Noise extraction.
- Tonal Extraction.
- Transient Extraction.

"""

# Maximum frequency for STFT plots, change according to your need
MAX_FREQUENCY_PLOT_STFT = 5000.0

# %%
# Set up analysis
# ~~~~~~~~~~~~~~~
# Setting up the analysis consists of loading Ansys libraries, connecting to the
# DPF server, and retrieving the example files.
#
# Load Ansys libraries.

import matplotlib.pyplot as plt
import numpy as np

from ansys.dpf.sound.examples_helpers import (
    get_absolute_path_for_xtract_demo_signal_1_wav,
    get_absolute_path_for_xtract_demo_signal_2_wav,
)
from ansys.dpf.sound.server_helpers import connect_to_or_start_server
from ansys.dpf.sound.signal_utilities import CropSignal, LoadWav
from ansys.dpf.sound.spectrogram_processing import Stft
from ansys.dpf.sound.xtract import (
    Xtract,
    XtractDenoiser,
    XtractDenoiserParameters,
    XtractTonal,
    XtractTonalParameters,
    XtractTransient,
    XtractTransientParameters,
)

# Connect to remote or start a local server
connect_to_or_start_server(use_license_context=True)


# %%
# Defining a custom function for STFT plots
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Defining a custom function for STFT plots that will allow us to have
# more control over what we're displaying.
# Note that we could use Stft.plot() but in this example,
# we want to restrict the frequency range of the plot, hence the custom function.
def plot_stft(stft_class, vmax=None):
    out = stft_class.get_output_as_nparray()

    # Extracting first half of the STFT (second half is symmetrical)
    half_nfft = int(out.shape[0] / 2) + 1
    magnitude = stft_class.get_stft_magnitude_as_nparray()

    if vmax is None:
        vmax = np.max(magnitude)

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
    plt.figure()
    plt.imshow(
        magnitude,
        origin="lower",
        aspect="auto",
        cmap="jet",
        extent=extent,
    )
    plt.colorbar(label="dB")
    plt.ylabel("Frequency (Hz)")
    plt.ylim(
        [0.0, MAX_FREQUENCY_PLOT_STFT]
    )  # Change the value of MAX_FREQUENCY_PLOT_STFT if needed
    plt.title("STFT Amplitudes")
    plt.show()


# %%
# Load a demo signal for Xtract
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Load a wav signal using LoadWav class, the WAV file contains harmonics and shocks.

# Returning the input data of the example file
path_xtract_demo_signal_1 = get_absolute_path_for_xtract_demo_signal_1_wav()

# Load the wav file.
wav_loader = LoadWav(path_to_wav=path_xtract_demo_signal_1)
wav_loader.process()

# Plot the signal in time domain
time_domain_signal = wav_loader.get_output()[0]
time_vector = time_domain_signal.time_freq_support.time_frequencies.data
plt.plot(time_vector, time_domain_signal.data)
plt.title("Xtract Demo Signal 1")
plt.grid(True)
plt.xlabel("Time (s)")
plt.ylabel("Amplitude (Pa)")
plt.show()

# Compute the spectrogram of the signal and plot it
stft_original = Stft(signal=wav_loader.get_output()[0], fft_size=1024, window_overlap=0.9)
stft_original.process()
stft_original.plot()

# %%
# 1. Use single source extraction algorithm
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# In this first part of the example, we will showcase how to use
# the different components of the Xtract module independently.

# %%
# Noise Extraction
# ~~~~~~~~~~~~~~~~
# There is a noisy fan in the demo signal that we will try to isolate.

# Creating a noise pattern using the first two seconds of the signal.
# To do that, we first crop the first two seconds of the signal.
signal_cropper = CropSignal(signal=time_domain_signal, start_time=0.0, end_time=2.0)
signal_cropper.process()
cropped_signal = signal_cropper.get_output()

# Then we use the class XtractDenoiserParameters to create the noise pattern.
xtract_denoiser_params = XtractDenoiserParameters()
xtract_denoiser_params.noise_psd = xtract_denoiser_params.create_noise_psd_from_noise_samples(
    signal=cropped_signal, sampling_frequency=44100.0
)


# Finally we can actually denoise the signal using the class XtractDenoiser
xtract_denoiser = XtractDenoiser(
    input_signal=time_domain_signal, input_parameters=xtract_denoiser_params
)
xtract_denoiser.process()

noise_signal = xtract_denoiser.get_output()[1]

# Plotting on the same window the original signal and the noise signal
plt.plot(time_vector, time_domain_signal.data, label="Original Signal")
plt.plot(time_vector, noise_signal.data, label="Noise Signal")
plt.grid(True)
plt.xlabel("Time (s)")
plt.ylabel("Amplitude (Pa)")
plt.title("Original Signal and Noise signal")
plt.legend()
plt.show()

# %%
# Tone Extraction
# ~~~~~~~~~~~~~~~
# The goal is to isolate the tones using the right setting.

# We will try a first attempt of tone extraction with a
# first set of parameters using XtractTonalParameters
xtract_tonal_params = XtractTonalParameters()
xtract_tonal_params.regularity = 1.0
xtract_tonal_params.maximum_slope = 1000.0
xtract_tonal_params.minimum_duration = 0.22
xtract_tonal_params.intertonal_gap = 10.0
xtract_tonal_params.local_emergence = 2.0
xtract_tonal_params.fft_size = 2048

# Now we perform the tonal extraction using XtractTonal
xtract_tonal = XtractTonal(input_signal=time_domain_signal, input_parameters=xtract_tonal_params)
xtract_tonal.process()

# We can plot the spectrogram to assess the quality of the output
stft_modified_signal = Stft(signal=xtract_tonal.get_output()[0], fft_size=1024, window_overlap=0.9)
stft_modified_signal.process()

# Spectrogram of the original signal
plot_stft(stft_original)

# Spectrogram of the modified signal
plot_stft(stft_modified_signal)

# We can see from the obtained plot that the tones are not properly extracted.
# We try again with a different parameter for the maximum slope
xtract_tonal_params.maximum_slope = 5000.0
xtract_tonal.process()

# Rechecking visually the plots
plot_stft(stft_original)

# Spectrogram of the modified signal
stft_modified_signal.signal = xtract_tonal.get_output()[0]
stft_modified_signal.process()
plot_stft(stft_modified_signal)

# %%
# Transient Extraction
# ~~~~~~~~~~~~~~~~~~~~
# The goal is to isolate the transient using the right setting.
# These setting are less easy to handle and are well explained in the tutorial videos
# installed with Ansys Sound SAS standalone application (with the user interface).

# We create a set of transient parameters
# (for this example, we assume that we already "know" the best values)
xtract_transient_params = XtractTransientParameters(lower_threshold=51.5, upper_threshold=60.0)

# We then perform the transient extraction using XtractTransient
xtract_transient = XtractTransient(
    input_signal=time_domain_signal, input_parameters=xtract_transient_params
)
xtract_transient.process()
transient_signal = xtract_transient.get_output()[0]

# Plotting on the same window the original signal and the transient signal
plt.plot(time_vector, time_domain_signal.data, label="Original Signal")
plt.plot(time_vector, transient_signal.data, label="Transient Signal")
plt.grid(True)
plt.xlabel("Time (s)")
plt.ylabel("Amplitude (Pa)")
plt.title("Original Signal and Transient signal")
plt.legend()
plt.show()


# %%
# 2. Use combination of source extraction algorithms and loop on several signal
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# The idea here is to loop over several signals and use the Xtract class that combines
# all previous classes.


path_xtract_demo_signal_2 = get_absolute_path_for_xtract_demo_signal_2_wav()

paths = [path_xtract_demo_signal_1, path_xtract_demo_signal_2]

# Instantiating the Xtract class with the parameters previously set
xtract = Xtract(
    parameters_denoiser=xtract_denoiser_params,
    parameters_tonal=xtract_tonal_params,
    parameters_transient=xtract_transient_params,
)

# Looping over all signal paths contained in the "paths" variable
for p in paths:
    # Load the signal
    wav_loader.path_to_wav = p
    wav_loader.process()
    time_domain_signal = wav_loader.get_output()[0]

    # Plot the time domain signal
    ylims = [-3.0, 3.0]
    plt.plot(time_vector, time_domain_signal.data, label="Original Signal")
    plt.ylim(ylims)
    plt.grid()
    plt.legend()
    plt.title(p)
    plt.show()

    # Compute and plot the stft
    stft_original.signal = time_domain_signal
    stft_original.process()
    stft_original.plot()

    # Use Xtract with the loaded signal
    xtract.input_signal = time_domain_signal
    xtract.process()

    # Collecting outputs and plotting everything in one window
    noise_signal, tonal_signal, transient_signal, remainder_signal = xtract.get_output()

    f, axs = plt.subplots(nrows=5)
    axs[0].plot(time_vector, time_domain_signal.data, label="Original Signal", color="blue")
    axs[1].plot(time_vector, noise_signal.data, label="Noise Signal", color="red")
    axs[2].plot(time_vector, tonal_signal.data, label="Tonal Signal", color="green")
    axs[3].plot(time_vector, transient_signal.data, label="Transient Signal", color="purple")
    axs[4].plot(time_vector, remainder_signal.data, label="Remainder Signal", color="black")

    for ax in axs:
        ax.set_ylim(ylims)
        ax.grid()
        ax.legend()
        ax.set_aspect("auto")

    plt.legend()
    plt.suptitle("Original and extracted signals")
    plt.show()
