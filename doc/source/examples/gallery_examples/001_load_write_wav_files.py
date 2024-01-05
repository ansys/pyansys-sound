"""
.. _load_write_wav_iles_example:

Load / Write Wav Files
--------------------------

This example shows how to load and write wav files, access the corresponding data and display it using numpy.

"""
# %%
# Set up analysis
# ~~~~~~~~~~~~~~~
# Setting up the analysis consists of loading Ansys libraries, connecting to the
# DPF server, and retrieving the example files.
#
# Load Ansys libraries.

from ansys.dpf.sound.sound_helpers import write_wav_signal, load_wav_signal
import ansys.dpf.core as dpf
import matplotlib.pyplot as plt
import sys

# Start a DPF server and copy the example files into the current working directory.
dpf.server_context.set_default_server_context(dpf.AvailableServerContexts.premium)
print("Server Context successfully created")

# Change this path according to your needs
path_to_dpf_server = r"C:\Program Files\ANSYS Inc\v242"
s = dpf.start_local_server(ansys_path=path_to_dpf_server)

# %%
# Load DPF Sound plugin Actually loading the DPF Sound plugin
try:
    # Make sure the path below is correct
    dpf.load_library(
        r"C:\Program Files\ANSYS Inc\v242\Acoustics\SAS\ads\dpf_sound.dll",
        "dpf_sound",
    )
    print("DPF Sound successfully loaded")

except Exception as e:
    # If we didn't manage to load the DLL, we end up here
    print(e.args)
    sys.exit("Error while loading dpf_sound.dll ! Aborting.")

# %%
# Load a wav signal usging load_wav_signal, it will be returned as a [DPF Field Container](https://dpf.docs.pyansys.com/version/stable/api/ansys.dpf.core.operators.utility.fields_container.html)

# Modify the input path according to your needs
fc_signal = load_wav_signal(r"C:\example_files\flute.wav")

# %%
# Create a modified version of the signal and plot the signals
fc_signal_modified = dpf.FieldsContainer.deep_copy(fc_signal)
fc_signal_modified[0].data = fc_signal[0].data * 0.2

# Obtaining the [Time Frequency support](https://dpf.docs.pyansys.com/version/stable/api/ansys.dpf.core.time_freq_support.html) that contains the associated times of the signal
time_support = fc_signal[0].time_freq_support.time_frequencies.data

plt.plot(time_support, fc_signal[0].data, label="Original Signal")
plt.plot(time_support, fc_signal_modified[0].data, label="Modified Signal")
plt.title("My signals")
plt.legend()
plt.xlabel("s")
plt.ylabel("Pa")
plt.show()

# %%
# Write the modified signal in memory using write_wav_signal

write_wav_signal(
    r"C:\example_files\flute_modified.wav", fc_signal_modified, "int16"
)

print("End of script reached")
