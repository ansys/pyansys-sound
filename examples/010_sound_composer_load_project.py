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
.. _sound_composer_load_project:

Use an existing Sound Composer project file
-------------------------------------------

The Sound Composer is a tool that allows you to generate the sound of a system by combining the
sounds of its components, which we call sources here. Each source can be made of data coming from
test analysis, or from a simulation, or simply consist of a single audio recording. The sources are
combined into a Sound Composer project, where each source is assigned to a track.

A track is a data structure made of a source data, a source control data, an output gain, and,
optionally, a transfer function in the form of a digital filter (which models the transfer from the
source to the listening/recording position). It can generate the sound of the
component (as characterized by the source data), in specific operating conditions (the source
control), and filtered according to the transfer function.

This example shows how to use the Sound Composer, with the :class:`.SoundComposer` class. It starts
from an existing Sound Composer project file, and illustrates the notions of Sound Composer project,
track, source, source control, and filter.

The example shows how to perform these operations:

- Load a project file,
- Get the project information and content,
- Investigate the content of a track,
- Generate the signal of a track,
- Generate the signal of the entire Sound Composer project.
"""

# %%
# Set up analysis
# ~~~~~~~~~~~~~~~
# Setting up the analysis consists of loading the required libraries,
# and connecting to the DPF server.

# Load Ansys libraries.
from ansys.sound.core.examples_helpers import download_sound_composer_project_whatif
from ansys.sound.core.server_helpers import connect_to_or_start_server
from ansys.sound.core.sound_composer import SoundComposer
from ansys.sound.core.spectrogram_processing import Stft

# sphinx_gallery_start_ignore
# sphinx_gallery_thumbnail_path = '_static/_image/example010_thumbnail.png'
# sphinx_gallery_end_ignore

# Connect to a remote DPF server or start a local DPF server.
my_server, my_license_context = connect_to_or_start_server(use_license_context=True)


# %%
# Load a Sound Composer project from a file
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Load a Sound Composer project, using the :meth:`.SoundComposer.load()` method. A Sound Composer
# project file has the extension .scn, and can be created with Ansys Sound SAS.

# Download the Sound Composer project file used in this example.
path_sound_composer_project_scn = download_sound_composer_project_whatif(server=my_server)

# Create a SoundComposer object and load the project.
sound_composer_project = SoundComposer()
sound_composer_project.load(path_sound_composer_project_scn)

# %%
# You can use the built-in :func:`print()` function to display a summary of the content of the project.
print(sound_composer_project)

# %%
# You can see that this project is made of 4 tracks:

# %%
# - a track with a harmonics source, coming from the FEM simulation of an e-motor,
# - a track with another harmonics source, coming from the multibody simulation of a gearbox,
# - a track with a broadband noise source, coming from the CFD simulation of a HVAC system,
# - a track with another broadband noise source, coming from the analysis of a background noise
#   measurement in the cabin, which would correspond to the rolling noise and the wind noise.

# %%
# Explore the project's list of tracks
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Let us have a closer look at the content of each individual track by printing it.

for i, track in enumerate(sound_composer_project.tracks, start=1):
    print(f"--- Track n. {i} ---\n{track}\n")

# %%
# For each track, you can see some details about the source content, the associated control profile,
# and whether the track includes a filter or not.

# %%
# Explore the content of a track
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# To look at a specific track, use the attribute :attr:`.tracks` of the :class:`.SoundComposer`
# object, containing the list of the tracks included.
# For example, let us extract the second track of the project, which contains the gearbox source.
#
# The track object returned is of type :class:`.Track`. You can print it to display its content,
# as shown in the previous section.
track_gear = sound_composer_project.tracks[1]

# %%
# This track contains a harmonics source, stored in its :attr:`.Track.source` attribute of
# type :class:`.SourceHarmonics`. Here, it consists of a set of 50 harmonics, which are defined by
# their order numbers, and their levels over 249 values of the control parameter (RPM).
#
# These data are stored in the :attr:`.SourceHarmonics.source_harmonics`
# attribute of the track's source object, as a :class:`FieldsContainer
# <ansys.dpf.core.fields_container.FieldsContainer>` object. It contains 249 fields, each
# corresponding to a specific value of the control parameter (RPM), and containing
# the levels in Pa² of the 50 harmonics at this RPM value.
print(
    f"Number of RPM points defined in the source dataset: "
    f"{len(track_gear.source.source_harmonics)}"
)

# %%
# The source control data (that is, the RPM values over time) can be accessed using the
# :attr:`.SourceHarmonics.source_control` attribute of the source in the track. Let us display this
# control profile in a figure: it is a linear ramp-up from 250 rpm to 5000 rpm, over 8 seconds.
track_gear.source.plot_control()

# %%
# The track also contains a filter, stored as a :class:`.Filter` object.
# Here, it is a finite impulse response (FIR) filter that models the transfer between the source
# and the listening position.
track_gear.filter
print(track_gear.filter)

# %%
# Let us generate the signal corresponding to the track using the :meth:`.Track.process()` method,
# plot its waveform, and display its spectrogram with the :class:`.Stft` class.
track_gear.process(sampling_frequency=44100.0)
track_gear.plot()

spectrogram_gear = Stft(signal=track_gear.get_output())
spectrogram_gear.process()
spectrogram_gear.plot()

# %%
# If needed, you can access the output signal of a track using :meth:`.Track.get_output()`.
signal_gear = track_gear.get_output()

# %%
# Generate the signal of the project
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Now, let us generate the signal of the project using the :meth:`.SoundComposer.process()` method.
# This method generates, for each track, the acoustic signal of the source, filters it with the
# associated filter, if any, and applies the track gain, and finally sums all resulting tracks'
# signals together.

# %%
# Generate the signal of the project, using a sampling frequency of 44100 Hz.
sound_composer_project.process(sampling_frequency=44100.0)

# %%
# You can display the waveform of the generated signal using the :meth:`.SoundComposer.plot()`
# method, and its spectrogram using the :class:`.Stft` class.
sound_composer_project.plot()

spectrogram = Stft(signal=sound_composer_project.get_output())
spectrogram.process()
spectrogram.plot()

# %%
# Conclusion
# ~~~~~~~~~~
# This workflow allows you to analyze and listen to the sound of the gearbox and the e-motor, in
# realistic conditions, that is, including the HVAC noise and the background noise inside the cabin.
#
# By analyzing the spectrogram, you can anticipate how some harmonic tones from the e-motor and the
# gearbox may be perceived by the passengers in the cabin.
#
# Further investigations can be conducted, using other tools included in PyAnsys
# Sound, such as modules :mod:`Standard levels <ansys.sound.core.standard_levels>`,
# :mod:`Psychoacoustics <ansys.sound.core.psychoacoustics>` and
# :mod:`Spectral processing <ansys.sound.core.spectral_processing>`.
