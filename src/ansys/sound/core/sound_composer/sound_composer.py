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

"""Sound Composer project class."""

import os
import warnings

from ansys.dpf.core import Field, GenericDataContainersCollection, Operator, types
from matplotlib import pyplot as plt
import numpy as np

from ansys.sound.core.signal_utilities import SumSignals
from ansys.sound.core.signal_utilities.create_signal_fields_container import (
    CreateSignalFieldsContainer,
)
from ansys.sound.core.sound_composer._sound_composer_parent import SoundComposerParent
from ansys.sound.core.sound_composer.track import Track

from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning

ID_OPERATOR_LOAD = "sound_composer_load_project"
ID_OPERATOR_SAVE = "sound_composer_save_project"


class SoundComposer(SoundComposerParent):
    """Sound Composer project class.

    This class creates a Sound Composer project. A project is made of several tracks
    (:class:`Track`), each containing a source, to generate the sound, and an optional filter, to
    model the transfer between the source and the receiver.

    .. seealso::
        :class:`Track`

    Examples
    --------
    Load a Sound Composer project created in Ansys Sound SAS, and plot the generated signal.

    >>> from ansys.sound.core.sound_composer import SoundComposer
    >>> sound_composer = SoundComposer(project_path="path/to/project.scn")
    >>> sound_composer.process(sampling_frequency=48000.0)
    >>> sound_composer.plot()

    .. seealso::
        :ref:`sound_composer_load_project`
            Example demonstrating how to load and work with an existing Sound Composer project.
        :ref:`sound_composer_create_project`
            Example demonstrating how to create a Sound Composer project from scratch.
    """

    def __init__(
        self,
        project_path: str = "",
    ):
        """Class instantiation takes the following parameter.

        Parameters
        ----------
        project_path : str, default: ""
            Path to the Sound Composer project file to load (.scn).
        """
        super().__init__()
        self.__operator_load = Operator(ID_OPERATOR_LOAD)
        self.__operator_save = Operator(ID_OPERATOR_SAVE)

        self.tracks = []
        self.name = "Unnamed"

        if len(project_path) > 0:
            self.load(project_path)

    def __str__(self) -> str:
        """Return the string representation of the object."""
        str_tracks = ""
        for i, track in enumerate(self.tracks):
            str_track_source = (
                "Source not set" if track.source is None else track.source.__class__.__name__
            )
            str_tracks += (
                f"\n\tTrack {i+1}: {str_track_source}, "
                f'"{track.name if len(track.name) > 0 else "Unnamed"}", '
                f"gain = {np.round(track.gain, 1):+} dB"
            )

        return f'SoundComposer object: "{self.name}" ({len(self.tracks)} track(s)){str_tracks}'

    @property
    def tracks(self) -> list[Track]:
        """List of tracks.

        List of the tracks available in this Sound Composer instance (project).

        Each track is a :class:`Track` object, and contains a source and a filter.
        """
        return self.__tracks

    @tracks.setter
    def tracks(self, tracks: list[Track]):
        """Set the track list."""
        for track in tracks:
            if not isinstance(track, Track):
                raise PyAnsysSoundException("Each item in the track list must be of type `Track`.")
        self.__tracks = tracks

    @property
    def name(self) -> str:
        """Name of the Sound Composer project."""
        return self.__name

    @name.setter
    def name(self, name: str):
        """Set the name of the Sound Composer project."""
        self.__name = name

    def add_track(self, track: Track):
        """Add a track to the project.

        Parameters
        ----------
        track : Track
            Track object to add.
        """
        if not isinstance(track, Track):
            raise PyAnsysSoundException("Input track object must be of type `Track`.")

        self.tracks.append(track)

    def load(self, project_path: str):
        """Load a Sound Composer project.

        Parameters
        ----------
        project_path : str
            Path to the Sound Composer project file to load (.scn).
        """
        self.__operator_load.connect(0, project_path)

        self.__operator_load.run()

        track_collection = self.__operator_load.get_output(0, GenericDataContainersCollection)
        self.name = self.__operator_load.get_output(1, types.string)

        if len(track_collection) == 0:
            warnings.warn(
                PyAnsysSoundWarning(
                    f"The project file `{os.path.basename(project_path)}` does not contain any "
                    "track."
                )
            )

        self.tracks = []
        for i in range(len(track_collection)):
            track = Track()
            track.set_from_generic_data_containers(track_collection.get_entry({"track_index": i}))
            self.add_track(track)

    def save(self, project_path: str):
        """Save the Sound Composer project.

        Parameters
        ----------
        project_path : str
            Path and file name (.scn) where the Sound Composer project shall be saved.
        """
        if len(self.tracks) == 0:
            warnings.warn(
                PyAnsysSoundWarning(
                    "There are no tracks to save. The saved project will be empty. To add tracks "
                    f"before saving the project, use `{__class__.__name__}.tracks`, "
                    f"`{__class__.__name__}.add_track()` or `{__class__.__name__}.load()`."
                )
            )

        track_collection = GenericDataContainersCollection()
        track_collection.add_label("track_index")

        for i, track in enumerate(self.tracks):
            track_collection.add_entry({"track_index": i}, track.get_as_generic_data_containers())

        # Save the Sound Composer project.
        self.__operator_save.connect(0, project_path)
        self.__operator_save.connect(1, track_collection)
        self.__operator_save.connect(2, self.name)

        self.__operator_save.run()

    def process(self, sampling_frequency: float = 44100.0):
        """Generate the signal of the current Sound Composer project.

        Generates the project's signal corresponding to the sum of all the track signals.

        Parameters
        ----------
        sampling_frequency : float, default: 44100.0
            Sampling frequency of the generated sound in Hz.
        """
        if len(self.tracks) == 0:
            warnings.warn(
                PyAnsysSoundWarning(
                    f"There are no tracks to process. Use `{__class__.__name__}.tracks`, "
                    f"`{__class__.__name__}.add_track()` or `{__class__.__name__}.load()`."
                )
            )
            self._output = None
        else:
            track_signals = []
            for track in self.tracks:
                track.process(sampling_frequency)
                track_signal = track.get_output()
                # Make sure all tracks have the same unit to avoid raising an error in SumSignals.
                track_signal.unit = ""
                track_signals.append(track_signal)

            fc_creator = CreateSignalFieldsContainer(track_signals)
            fc_creator.process()
            track_signals_fc = fc_creator.get_output()

            track_sum = SumSignals(signals=track_signals_fc)
            track_sum.process()

            self._output = track_sum.get_output()

    def get_output(self) -> Field:
        """Get the generated signal of the Sound Composer project as a DPF field.

        Returns
        -------
        Field
            Generated signal as a DPF field.
        """
        if self._output is None:
            warnings.warn(
                PyAnsysSoundWarning(
                    f"Output is not processed yet. Use the `{__class__.__name__}.process()` method."
                )
            )
        return self._output

    def get_output_as_nparray(self) -> np.ndarray:
        """Get the generated signal of the Sound Composer project as a NumPy array.

        Returns
        -------
        numpy.ndarray
            Generated signal as a NumPy array.
        """
        output = self.get_output()

        if output is None:
            return np.array([])

        return np.array(output.data)

    def plot(self):
        """Plot the generated signal of the Sound Composer project."""
        if self._output is None:
            raise PyAnsysSoundException(
                f"Output is not processed yet. Use the `{__class__.__name__}.process()` method."
            )
        output_signal = self.get_output()
        str_output_unit = f" ({output_signal.unit})" if len(output_signal.unit) > 0 else ""
        time = output_signal.time_freq_support.time_frequencies

        plt.plot(time.data, output_signal.data)
        plt.title("Generated signal")
        plt.xlabel(f"Time ({time.unit})")
        plt.ylabel(f"Amplitude{str_output_unit}")
        plt.grid(True)
        plt.show()
