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

"""Sound Composer's sound_composer."""
import warnings

from ansys.dpf.core import Field, GenericDataContainersCollection, Operator
from matplotlib import pyplot as plt
import numpy as np

from ansys.sound.core.sound_composer._sound_composer_parent import SoundComposerParent
from ansys.sound.core.sound_composer.track import Track

from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning

ID_OPERATOR_LOAD = "sound_composer_load_project"
ID_OPERATOR_SAVE = "sound_composer_save_project"


class SoundComposer(SoundComposerParent):
    """Sound Composer project class.

    This class creates a Sound Composer project. A project is made of several tracks, each
    containing a source and a filter.
    """

    def __init__(
        self,
        project_path: str = "",
    ):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        project_path : str, default: ""
            Path to the Sound Composer project file to load (.scn).
        """
        super().__init__()
        self.__operator_load = Operator(ID_OPERATOR_LOAD)
        self.__operator_save = Operator(ID_OPERATOR_SAVE)

        if len(project_path) > 0:
            self.load(project_path)
        else:
            self.tracks = []

    def __str__(self) -> str:
        """Return the string representation of the object."""
        str_tracks = ""
        for i, track in enumerate(self.tracks):
            str_tracks += (
                f"\n\tTrack {i+1}: "
                f"{"Source not set" if track.source is None else track.source.__class__.__name__}, "
                f'"{track.name if len(track.name) > 0 else "Unnamed"}", '
                f"gain = {np.round(track.gain, 1):+} dB"
            )

        return f"Sound Composer object ({len(self.tracks)} track(s)){str_tracks}"

    @property
    def tracks(self) -> list[Track]:
        """List of Sound Composer tracks.

        List of tracks of the Sound Composer. Each track is a :class:`Track` object, and contains a
        source and a filter.
        """
        return self.__tracks

    @tracks.setter
    def tracks(self, tracks: list[Track]):
        """Set the track list."""
        self.__tracks = tracks

    def add_track(self, track: Track):
        """Add a Sound Composer track.

        Parameters
        ----------
        track : Track
            Track object to add.
        """
        if not isinstance(track, Track):
            raise PyAnsysSoundException("Input track object must be of type Track.")

        self.__tracks.append(track)

    def load(self, project_path: str):
        """Load a Sound Composer project.

        Parameters
        ----------
        project_path : str
            Path to the Sound Composer project file to load (.scn).
        """
        self.__operator_load.connect(0, project_path)

        self.__operator_load.run()

        gdcc_project = self.__operator_load.get_output(0, GenericDataContainersCollection)

        for i in range(len(gdcc_project)):
            track = Track()
            track.set_from_generic_data_container(gdcc_project.get_entry({"track_index": i}))
            self.add_track(track)

    # TODO: Save cannot work for now because the FRF is not stored in the Filter class.
    # def save(self, project_path: str):
    #     """Save the Sound Composer project.

    #     Parameters
    #     ----------
    #     project_path : str
    #         Path and file (.scn) name where the Sound Composer project shall be saved.
    #     """
    #     gdcc_project = GenericDataContainersCollection()

    #     for i, track in enumerate(self.tracks):
    #         gdcc_project.add_entry({"track_index": i}, track.get_as_generic_data_container())

    #     # Save the Sound Composer project.
    #     self.__operator_save.connect(0, project_path)
    #     self.__operator_save.connect(1, gdcc_project)

    #     self.__operator_save.run()

    def process(self, sampling_frequency: float = 44100.0):
        """Generate the signal of the Sound Composer, using the current tracks.

        Parameters
        ----------
        sampling_frequency : float, default: 44100.0
            Sampling frequency of the generated sound in Hz.
        """
        if len(self.tracks) == 0:
            warnings.warn(
                PyAnsysSoundWarning(
                    f"There are no track to process. Use {__class__.__name__}.add_track() or "
                    f"{__class__.__name__}.load()."
                )
            )
            self._output = None
        else:
            self._output = Field()
            for track in self.tracks:
                track.process(sampling_frequency)
                self._output += track.get_output()

    def get_output(self) -> Field:
        """Get the generated signal as a DPF field.

        Returns
        -------
        Field
            Generated signal as a DPF field.
        """
        if self._output is None:
            warnings.warn(
                PyAnsysSoundWarning(
                    f"Output is not processed yet. Use the {__class__.__name__}.process() method."
                )
            )
        return self._output

    def get_output_as_nparray(self) -> np.ndarray:
        """Get the generated signal as a NumPy array.

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
        """Plot the resulting signal in a figure."""
        if self._output is None:
            raise PyAnsysSoundException(
                f"Output is not processed yet. Use the {__class__.__name__}.process() method."
            )
        output_time = self._output.time_freq_support.time_frequencies.data

        plt.plot(output_time, self._output.data)
        plt.title("Generated signal")
        plt.xlabel("Time (s)")
        plt.ylabel(f"Amplitude{f' ({self._output.unit})' if len(self._output.unit) > 0 else ''}")
        plt.grid(True)
        plt.show()