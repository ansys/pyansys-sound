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
.. _sound_composer_load_project:

Sound Composer - Load project
-----------------------------

The Sound Composer is a tool that allows to generate the sound of a system
by combining the sound of its components, which are called sources. A source can be
a recording from a test, data coming from test analysis, or from a simulation.
The sources are combined together in a project, each source belonging to a track.

A track is a container that contains a source, a control profile and optionally a filter. It
is used to generate the sound of the component (characterized by the source) given a specific
functioning mode (named the control profile), and a transfer function (the filter).

This example shows how use the :class:`.SoundComposer`. It starts from an existing project file,
loads the project into the Sound Composer and explains the notions of project, track, source,
control profile and filter.

The example shows how to perform these operations:

- Load a project file
- Get the project information and content
- Investigate the content of a track
- Generate the signal of a track
- Generate the signal of the Sound Composer project

"""

# %%
# Set up analysis
# ~~~~~~~~~~~~~~~
# Setting up the analysis consists of loading the required libraries,
# and connecting to the DPF server.

# Load standard libraries.

# Load Ansys libraries.
from ansys.sound.core.examples_helpers import (
    download_sound_composer_project_whatif,
)
from ansys.sound.core.server_helpers import connect_to_or_start_server
from ansys.sound.core.sound_composer import SoundComposer
from ansys.sound.core.spectrogram_processing import Stft

# Connect to a remote server or start a local server.
my_server = connect_to_or_start_server(use_license_context=True)


# %%
# Load a Sound Composer project from a file
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Load a project in the Sound Composer, using the :meth:`.SoundComposer.load` method
# of the :class:`.SoundComposer` class.
# A project is a file with the extension .scn, usually created within Sound SAS.
#

# Download the Sound Composer project used in this example.
path_sound_composer_project_scn = download_sound_composer_project_whatif(server=my_server)

# Create a SoundComposer object and load the project.
# The project is loaded in the Sound Composer object, which contains all the information
sound_composer_project = SoundComposer()
sound_composer_project.load(path_sound_composer_project_scn)


# %%
# Display a summary of the content of the project using print.

print(sound_composer_project)

# %%
# You can see that this project is made of four tracks:
# - the first track contains a source of type Harmonics, it comes form a FEM simulation
# of an e-motor
# - the second track contains a source of type Harmonics, it comes from a a multibody
# simulation of the gearbox
# - the third track contains a source of type Broadband Noise, it comes from a CFD simulation
# of the HVAC system
# - the fourth track contains a source of type Broadband Noise, it comes form the analysis of
# a measurement of the background noise in the cabin, which contains rolling noise and wind noise.

# %%
# Explore the content of the project
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Let us have a closer look at the content of each track by printing individually each track.

for i, track in enumerate(sound_composer_project.tracks, start=1):
    print(f"--- Track n. {i} ---")
    print(track)
    print()


# %%
# For each track you can see some details about the source content, the control parameter
# set in the track, and if there is a filter or not in the track.

# %%
# Access to the content of a track
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# To get a specific track, access the attribute :attr:`.tracks` of the SoundComposer object.
# Let us get the second track of the project, which contains the source of the gearbox.
#
# The track is an object of type :class:`.Track`.
track_gear = sound_composer_project.tracks[1]
print(track_gear)

# %%
# The figure below displays the content of the source, which is of type
# :class:`.SourceHarmonics`, as seen in the print above.
# In that case, the source is a set of 50 harmonics, which are defined by their order number,
# their level, for value of the control parameter (which is the RPM value).
print(track_gear.source.source_harmonics)

# %%
# The source control can be accessed using the :attr:`.SourceHarmonics.source_control` attribute
# of the track. Let us display this control in a figure: it is a linear evolution of the RPM from
# 250 rev/mn to 5000 rev/mn, during 8 seconds.
track_gear.source.source_control.plot()

# %%
# The track also contains a filter, which is an object of type :class:`.Filter`.
# The coefficients of the filter are displayed in the console using
# `print()`. In our case, it is a FIR filter that models the transfer
# between the source and the ears of the receiver.
track_gear.filter
print(track_gear.filter)

# %%
# Let us generate the signal corresponding to the track using :meth:`.Track.process`, and display
# its waveform and spectrogram.
track_gear.process(sampling_frequency=44100.0)
track_gear.plot()

spectrogram_gear = Stft(signal=track_gear.get_output())
spectrogram_gear.process()
spectrogram_gear.plot()

# %%
# If needed, you can access the content of a track using the :meth:`.Track.get_output`,
# and further save or process it.
signal_gear = track_gear.get_output()

# %%
# Generate the signal of the project
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Now, let us generate the signal of the project using the :meth:`.SoundComposer.process` method.
# This method generates the signal of all the tracks, including the potentially defined filters
# of each track, and the performs a combination of the tracks' signals (they are summed
# all together).

sound_composer_project.process(sampling_frequency=44100.0)

# %%
# Display the waveform of the generated signal using the :meth:`.SoundComposer.plot` method,
# and its spectrogram using the :class:`.Stft` class.
sound_composer_project.plot()

spectrogram = Stft(signal=sound_composer_project.get_output())
spectrogram.process()
spectrogram.plot()

# %%
# The signal of the sound composer project allows to analyze and listen the sound of the gearbox
# and the e-motor, in a real condition including the HVAC noise and background noise inside the
# cabin.
#
# You can see in the spectrogram how some harmonic tones from the e-motor and the gearbox may be
# perceived and potentially heard by the passengers in the cabin.
#
# Further investigations may be conducted to validate it, using other tools included in PyAnsys
# Sound, such as :mod:`Standard Levels<ansys.sound.core.standard_levels>`,
# :mod:`Psychoacoustics<ansys.sound.core.psychoacoustics>` and
# :mod:`Spectral Processing<ansys.sound.core.spectral_processing>`.
