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
.. _sound_composer_create_project:

Create and work with a Sound Composer project
---------------------------------------------

The Sound Composer is a tool that allows you to generate the sound of a system by combining the
sounds of its components, which we call sources here. Each source can be made of data coming from
test analysis, or from a simulation, or simply consist of a single audio recording. The sources are
combined into a Sound Composer project, where each source is assigned to a track.

A track is a data structure made of a source data, a source control data, an output gain, and,
optionally, a transfer function in the form of a digital filter. It can generate the sound of the
component (as characterized by the source data), in specific operating conditions (the source
control), and filtered according to the transfer function (which models the transfer from the
source to the receiver).

This example shows how to create a Sound Composer project, with the :class:`.SoundComposer` class.
It starts by creating a new project, then adds tracks to it, and finally generates the sound of the
project. It illustrates the notions of Sound Composer project, track, source, source control,
and filter.

The example shows how to perform these operations:

- Create a project,
- Create a track with a source of type Harmonics, add it to the project
- Create a track with a source of type Spectrum, add it to the project
- Generate the signal of the project,
Display the spectrogram of the generated signal
- Save the signal as a wav file,
- Save the project as a file.
"""

# %%
# Set up analysis
# ~~~~~~~~~~~~~~~
# Setting up the analysis consists of loading the required libraries,
# connecting to the DPF server, and downloading the data files.

from ansys.sound.core.examples_helpers import (
    download_sound_composer_FRF_eMotor,
    download_sound_composer_source_eMotor,
    download_sound_composer_source_WindRoadNoise,
    download_sound_composer_sourcecontrol_eMotor,
    download_sound_composer_sourcecontrol_WindRoadNoise,
)

# Load Ansys libraries.
from ansys.sound.core.server_helpers import connect_to_or_start_server
from ansys.sound.core.signal_processing import Filter
from ansys.sound.core.signal_utilities.write_wav import WriteWav
from ansys.sound.core.sound_composer import *
from ansys.sound.core.spectrogram_processing import Stft

# sphinx_gallery_start_ignore
# sphinx_gallery_thumbnail_path = '_static/_image/example011_thumbnail.png'
# sphinx_gallery_end_ignore

# Connect to a remote server or start a local server.
my_server, my_license_context = connect_to_or_start_server(use_license_context=True)

# Download the necessary files used in this example, that is the source, FRF and control profile
# files which contains the acoustic definition of the sources, the transfer and the
# conditions of the sources (speed of the engine, speed of the vehicle).
path_sound_composer_source_eMotor = download_sound_composer_source_eMotor(server=my_server)
path_sound_composer_sourcecontrol_eMotor = download_sound_composer_sourcecontrol_eMotor(
    server=my_server
)
path_sound_composer_FRF_eMotor = download_sound_composer_FRF_eMotor(server=my_server)
path_sound_composer_source_WindRoadNoise = download_sound_composer_source_WindRoadNoise(
    server=my_server
)
path_sound_composer_sourcecontrol_WindRoadNoise = (
    download_sound_composer_sourcecontrol_WindRoadNoise(server=my_server)
)

# %%
# Create a new Sound Composer project
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# To create a new Sound Composer project, instantiate the :class:`.SoundComposer` class.
# This instance will be used to create tracks, add sources to them, and generate the sound
# of the project.

sound_composer_project = SoundComposer()

# %%
# Create track #1, with a source of type harmonics
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# To model the noise of an e-motor, we create a track with a source of type harmonics.
# This track contains a source that represents the harmonics of the e-motor noise, a source control
# that defines the operating conditions of the e-motor, and a filter that represents the transfer
# function of the e-motor noise source to the receiver point, usually the driver position.

# Create a new Sound Composer track: it will host the source, FRF and control parameter
# of the eMotor noise
track_eMotor = Track(name="eMotor harmonics noise")

# Create a source of type harmonics, using the :class:`.SourceHarmonics` class, given the
# path to the source file, which contains the data relative to the levels of the harmonics
# of the e-motor noise.
source_eMotor = SourceHarmonics(file=path_sound_composer_source_eMotor)

# Create a source control profile, using the :class:`.SourceControlOneParameter` class,
# and assign it to the source.
# This source control profile defines the operating conditions of the e-motor, in that case the
# speed of the e-motor, evolving from 250 to 5000 rpm in 8 seconds.
source_control_eMotor = SourceControlTime(file_str=path_sound_composer_sourcecontrol_eMotor)

# Assign the source control to the source
source_eMotor.source_control = source_control_eMotor

# Assign the source to the track
track_eMotor.source = source_eMotor

# Create a filter, using the :class:`.Filter` class, and assign it to the track.
# This filter models the transfer function (FRF) of the e-motor noise source to the receiver point.
filter_eMotor = Filter(file=path_sound_composer_FRF_eMotor)
track_eMotor.filter = filter_eMotor

# Assign the track to the Sound Composer project. It is the first track of this project.
sound_composer_project.add_track(track_eMotor)

# %%
# Create track #2, with a source of type broadband noise
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# To model the wind and road noise produced in the cabin during its movement, we create a track
# with a source of type broadband noise, evolving according to a control profile which gives
# the evolution of the speed of the vehicle.

# Create a new Sound Composer track: it will host the source and control parameter of the wind
# and road noise source, that is the background noise produced in the cabin while the vehicle
# is moving.
track_WindRoadNoise = Track(name="Wind and road noise")

# Create a source of type Broadband Noise (BBN), using the :class:`.SourceBroadbandNoise` class.
source_WindRoadNoise = SourceBroadbandNoise(file=path_sound_composer_source_WindRoadNoise)

# Create a source control profile, using the :class:`.SourceControlOneParameter` class,
# and assign it to the source
source_control_WindRoadNoise = SourceControlTime(
    file_str=path_sound_composer_sourcecontrol_WindRoadNoise
)
source_WindRoadNoise.source_control = source_control_WindRoadNoise

# Assign the source to the track
track_WindRoadNoise.source = source_WindRoadNoise

# Assign the track to the Sound Composer project. It is the second track of this project.
sound_composer_project.add_track(track_WindRoadNoise)

# %%
# Generate the signal of the project
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Now, let us generate the signal of the project using the :meth:`.SoundComposer.process()` method.
# This method generates the acoustic signals of each track, filters them with the associated filters,
# whenever specified, applies track's gains, and sums the resulting signals together.
# At the end, the overall noise of this system is displayed, and saved into a file.
sound_composer_project.process(sampling_frequency=44100.0)

# %%
# You can display the waveform of the generated signal using the :meth:`.SoundComposer.plot()`
# method, and its spectrogram using the :class:`.Stft` class.
sound_composer_project.plot()

# %%
# You can use built-in :func:`print()` function to display a summary of the content of the project.
print(sound_composer_project)

# %%
# Get the resulting signal, as a :class:`Field`
generated_signal_from_project = sound_composer_project.get_output()

# %%
# Display the spectrogram of the generated signal using the :class:`.Stft` class.
spectrogram = Stft(signal=generated_signal_from_project)
spectrogram.process()
spectrogram.plot()

# %%
# Save the signal as wav file sing :func:`WriteWav` operator.
WriteWav(
    signal=generated_signal_from_project,
    path_to_write="generated_sound_from_SoundComposer_project.wav",
).process()


# %%
# You can also save the Sound Composer project for later use, using the
# :meth:`.SoundComposer.save()` method. This saves the project in a file with
# the extension ``.scn`` (Sound Composer project file).
# This file can also be loaded in Ansys Sound Analysis & Specification.

sound_composer_project.save(project_path="My_SoundComposer_Project.scn")


# %%
# Conclusion
# ~~~~~~~~~~
# This workflow allows you to analyze and listen to the sound of the e-motor, in
# realistic conditions, that is, including the background noise inside the cabin.
#
# By analyzing the spectrogram, you can anticipate how some harmonic tones from the e-motor
# may be perceived by the passengers in the cabin.
#
# Further investigations can be conducted, using other tools included in PyAnsys
# Sound, such as modules :mod:`Standard levels <ansys.sound.core.standard_levels>`,
# :mod:`Psychoacoustics <ansys.sound.core.psychoacoustics>` and
# :mod:`Spectral processing <ansys.sound.core.spectral_processing>`.
