# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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
.. _calculate_levels:

Calculate RMS, dBSPL and dBA levels
-----------------------------------

This example shows how to calculate RMS, dBSPL and dBA levels from two signals.
The following indicators are included:

- Overall RMS level
- Overall dBSPL level
- Overall dBA level
- RMS level vs time
- dBSPL level vs time
- dBA level vs time

The example shows how to perform these operations:

- Set up the analysis.
- Calculate levels on loaded WAV files.
- Get calculation outputs.
- Plot some corresponding curves.
- Export levels into a .csv files.

"""

# %%
# Set up analysis
# ~~~~~~~~~~~~~~~
# Setting up the analysis consists of loading Ansys libraries, connecting to the
# DPF server, and retrieving the example files.

# Load Ansys libraries.
import os
import csv
import matplotlib.pyplot as plt

from ansys.sound.core.examples_helpers import (
    download_fan_wav,
    download_aircraft_wav,
)

from ansys.sound.core.server_helpers import connect_to_or_start_server
from ansys.sound.core.signal_utilities import LoadWav
from ansys.sound.core.standard_levels import OverallLevel, LevelOverTime

# Connect to a remote server or start a local server.
my_server = connect_to_or_start_server(use_license_context=True)


# %%
# Calculate overall RMS, dBSPL and dBA levels
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Load a signal from a WAV file using the :class:`.LoadWav` class. It is returned as a
# :class:`FieldsContainer <ansys.dpf.core.fields_container.FieldsContainer>` object.

# Load example data from two wav files
path_fan_wav = download_fan_wav(server=my_server)
path_aircraft_wav = download_aircraft_wav(server=my_server)


# %%
# Create a first .csv file in which the overall levels will be written, and write the first row.
file = open(os.path.join('Overall_Results.csv'), 'w+', newline='') 
csv_writer1 = csv.writer(file)
csv_writer1.writerow(['Signal name', 'overall level [RMS]', 'overall level [dBSPL]', 'overall level [dBA]'])


# %%
# In a loop, for each sound, create a :class:`.OverallLevel` object, set its signals, 
# get and the overall RMS, dBSPL and dBA levels, then Write the results into the first .csv file.

for file_name in (path_fan_wav, path_aircraft_wav):
    # Load wav.
    wav_loader = LoadWav(file_name)
    wav_loader.process()
    fc_signal = wav_loader.get_output()[0]

    # Calculate RMS.
    level_RMS = OverallLevel(signal=fc_signal,  scale='RMS', reference_value=1.0)
    level_RMS.process()
    RMS = level_RMS.get_level()
        
    # Calculate dBSPL.
    level_dBSPL = OverallLevel(signal=fc_signal,  scale='dB', reference_value=0.00002)
    level_dBSPL.process()
    dBSPL = level_dBSPL.get_level()

    # Calculate dBA.
    level_dBA = OverallLevel(signal=fc_signal, scale='dB', reference_value = 0.00002, frequency_weighting = 'A')
    level_dBA.process()
    dBA = level_dBA.get_level()

    # Print the results.
    file = os.path.basename(file_name)
    print(
    f"\nThe RMS level of sound file {file} is {RMS:.1f} Pa, its dBSPL level is {dBSPL:.1f} dBSPL and its dBA level is {dBA:.1f} dBA  "
        )

    # Write the results in .csv.
    row1 = [file[:-4], RMS, dBSPL, dBA]
    csv_writer1.writerow(row1)


# %%
# Calculate RMS, dBSPL and dBA levels versus time
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Initialize empty lists to store the levels in order to plot them.
t = []
RMS_levels = []
dBSPL_levels = []
dBA_levels = []

# %%
# In a loop, for each sound, create a :class:`.OverallLevel` object, set its signals, 
# get and the overall RMS, dBSPL and dBA levels, then Write the results into the one .csv file per sound.

for file_name in (path_fan_wav, path_aircraft_wav):
    # Write a .csv file for each sound with the first row.
    file = os.path.basename(file_name)
    file2 = open(os.path.join(file[:-4]+'_Levels_vs_time_Results.csv'), 'w+', newline='')
    csv_writer2 = csv.writer(file2)
    csv_writer2.writerow(['time steps [s]', 'RMS level', 'dBSPL level', 'dBA level'])

    # Load wav.
    wav_loader = LoadWav(file_name)
    wav_loader.process()
    fc_signal = wav_loader.get_output()[0]
        
    # Calculate RMS vs time and get the time steps.
    RMS_time_varying = LevelOverTime(signal=fc_signal, scale='RMS', reference_value=1.0, frequency_weighting='', time_weighting='Fast')
    RMS_time_varying.process()
    time_steps=RMS_time_varying.get_time_scale()
    t.append(time_steps.tolist())
    
    # Calculate dBSPL vs time.
    dBSPL_time_varying = LevelOverTime(signal=fc_signal, scale='dB', reference_value=0.00002, frequency_weighting='', time_weighting='Fast')
    dBSPL_time_varying.process()
    dBSPL = dBSPL_time_varying.get_level_over_time()
        
    # Calculate dBA vs time.
    dBA_time_varying = LevelOverTime(signal=fc_signal, scale='dB', reference_value=0.00002, frequency_weighting='A', time_weighting='Fast')
    dBA_time_varying.process()
    dBA = dBA_time_varying.get_level_over_time()
    
    # Append all the results to the empty lists previously created.
    RMS = RMS_time_varying.get_level_over_time()
    RMS_levels.append(RMS.tolist())
    dBSPL_levels.append(dBSPL.tolist())
    dBA_levels.append(dBA.tolist())
    
    # Write the results in the .csv files.
    for i in range(len(time_steps)):
        csv_writer2.writerow([time_steps[i], RMS[i], dBSPL[i], dBA[i]])
 

# %%
# Plot the results versus time for both signals into three graphs.

fig, axs = plt.subplots(3)
fig.suptitle("Time varying RMS, dBSPL and dBA levels")

axs[0].plot(t[0], RMS_levels[0], color="b", label="Fan")
axs[0].plot(t[1], RMS_levels[1], color="r", label="Airplane")
axs[0].set_ylabel("RMS (Pa)")
axs[0].legend(loc="upper right")

axs[1].plot(t[0],dBSPL_levels[0], color="b", label="Fan")
axs[1].plot(t[1],dBSPL_levels[1], color="r", label="Airplane")
axs[1].set_ylabel("dBSPL")
axs[1].legend(loc="upper right")

axs[2].plot(t[0], dBA_levels[0], color="b", label="Fan")
axs[2].plot(t[1], dBA_levels[1], color="r", label="Airplane")
axs[2].set_ylabel("dBA")
axs[2].legend(loc="upper right")
axs[2].set_xlabel("Time (s)")

plt.show()