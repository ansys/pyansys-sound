# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
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

from ansys.dpf.core import Field, GenericDataContainer, GenericDataContainersCollection, Operator
from ansys.dpf.core.collection import Collection
from matplotlib import pyplot as plt
import numpy as np

from ansys.sound.core.signal_processing import Filter
from ansys.sound.core.sound_composer._sound_composer_parent import SoundComposerParent
from ansys.sound.core.sound_composer.track import DICT_SOURCE_TYPE, Track

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
        sampling_frequency: float = 44100.0,
    ):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        project_path : str, default: ""
            Path to the Sound Composer project file to load (.scn).
        sampling_frequency : float, default: 44100.0
            Project sampling frequency in Hz.
        """
        super().__init__()
        self.__sampling_frequency = sampling_frequency

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
                f"{track.name if len(track.name) > 0 else "Unnamed"}, "
                f"gain = {np.round(track.gain, 1):+} dB"
            )

        return (
            f"Sound Composer object ({len(self.tracks)} track(s), "
            f"sampling frequency: {self.__sampling_frequency} Hz)"
            f"{str_tracks}"
        )

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

        if (
            track.filter is not None
            and track.filter.get_sampling_frequency() != self.__sampling_frequency
        ):
            raise PyAnsysSoundException(
                f"Track's filter sampling frequency ({track.filter.get_sampling_frequency()} Hz) "
                "must be equal to the Sound Composer's sampling frequency "
                f"({self.__sampling_frequency} Hz)."
            )

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

        gdcc_project: Collection = self.__operator_load.get_output(
            0, GenericDataContainersCollection
        )

        for i in range(len(gdcc_project)):
            gdc_track: GenericDataContainer = gdcc_project.get_entry({"track_index": i})

            # Create source attribute.
            gdc_source: GenericDataContainer = gdc_track.get_property("track_source")
            gdc_source_control: GenericDataContainer = gdc_track.get_property(
                "track_source_control"
            )
            source = DICT_SOURCE_TYPE[gdc_track.get_property("track_type")]()
            source.set_from_generic_data_containers(gdc_source, gdc_source_control)

            # Create filter attribute.
            if gdc_track.get_property("track_is_filter") == 1:
                frf = gdc_track.get_property("track_filter")
                filter = Filter(sampling_frequency=self.__sampling_frequency)
                filter.design_FIR_from_FRF(frf)
            else:
                filter = None

            # Add track to the Sound Composer with created source and filter.
            self.add_track(
                Track(
                    name=gdc_track.get_property("track_name"),
                    gain=gdc_track.get_property("track_gain"),
                    source=source,
                    filter=filter,
                )
            )

    def save(self, project_path: str):
        """Save the Sound Composer project.

        Parameters
        ----------
        project_path : str
            Path and file (.scn) name where the Sound Composer project shall be saved.
        """
        gdcc_project = GenericDataContainersCollection()

        for i, track in enumerate(self.tracks):
            # Get source and source control as generic data containers.
            gdc_source, gdc_source_control = track.source.get_as_generic_data_containers()

            # Create a generic data container for the track.
            gdc_track = GenericDataContainer()

            # Set track generic data container properties.
            gdc_track.set_property(
                "track_type",
                [i for i in DICT_SOURCE_TYPE if isinstance(track.source, DICT_SOURCE_TYPE[i])][0],
            )
            gdc_track.set_property("track_source", gdc_source)
            gdc_track.set_property("track_source_control", gdc_source_control)
            gdcc_project.add_entry({"track_index": i}, gdc_track)

        # Save the Sound Composer project.
        self.__operator_save.connect(0, project_path)
        self.__operator_save.connect(1, gdcc_project)

        self.__operator_save.run()

    def process(self):
        """Generate the signal of the Sound Composer, using the current tracks."""
        if len(self.tracks) == 0:
            warnings.warn(
                PyAnsysSoundWarning(
                    f"There are no track to process. Use {__class__.__name__}.add_track() or "
                    f"{__class__.__name__}.load()."
                )
            )
        else:
            self._output = Field()
            for track in self.tracks:
                track.process(self.__sampling_frequency)
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
