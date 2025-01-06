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

"""Sound Composer's track."""
from typing import Union
import warnings

from ansys.dpf.core import Field, GenericDataContainer
from matplotlib import pyplot as plt
import numpy as np

from ansys.sound.core.signal_processing import Filter
from ansys.sound.core.signal_utilities import ApplyGain
from ansys.sound.core.sound_composer._sound_composer_parent import SoundComposerParent
from ansys.sound.core.sound_composer.source_audio import SourceAudio
from ansys.sound.core.sound_composer.source_broadband_noise import SourceBroadbandNoise
from ansys.sound.core.sound_composer.source_broadband_noise_two_parameters import (
    SourceBroadbandNoiseTwoParameters,
)
from ansys.sound.core.sound_composer.source_harmonics import SourceHarmonics
from ansys.sound.core.sound_composer.source_harmonics_two_parameters import (
    SourceHarmonicsTwoParameters,
)
from ansys.sound.core.sound_composer.source_spectrum import SourceSpectrum

from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning

# Here is defined the list of available source types (class names), as a dictionary where the key
# is the source type ID used in DPF Sound. Whenever a new source type (and corresponding class
# under superclass SourceParent) is added, it must be added to this dictionary to make it available
# to the Sound Composer package.
DICT_SOURCE_TYPE = {
    1: SourceBroadbandNoise,
    2: SourceBroadbandNoiseTwoParameters,
    3: SourceHarmonics,
    4: SourceHarmonicsTwoParameters,
    5: SourceSpectrum,
    6: SourceAudio,
}

# Define the typing Union of all possible source types, as a global variable (for typing only).
AnySourceType = Union[tuple(DICT_SOURCE_TYPE.values())]


class Track(SoundComposerParent):
    """Sound Composer's track class.

    This class creates a track for the Sound Composer. A track is made of a source (including its
    source control) and a filter. A tracks allows the synthesis of the source's sound, filtered
    with its associated filter.
    """

    def __init__(
        self,
        name: str = "",
        gain: float = 0.0,
        source: AnySourceType = None,
        filter: Filter = None,
    ):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        name : str, default: ""
            Name of the track.
        gain : float, default: 0.0
            Gain of the track, in dB.
        source : SourceSpectrum, SourceBroadbandNoise, SourceBroadbandNoiseTwoParameters, \
            SourceHarmonics, SourceHarmonicsTwoParameters or SourceAudio, default: None
            Source of the track.
        filter : Filter, default: None,
            Filter of the track.
        """
        super().__init__()
        self.name = name
        self.gain = gain
        self.source = source
        self.filter = filter

    def __str__(self) -> str:
        """Return the string representation of the object."""
        return (
            f"{self.name if len(self.name) > 0 else "Unnamed track" }\n"
            f"\tSource:{f"\n{self.source.__str__()}" if self.source is not None else " Not set"}\n"
            f"\tFilter: {"Set" if self.filter is not None else "Not set"}"
        )

    @property
    def name(self) -> str:
        """Name of the track."""
        return self.__name

    @name.setter
    def name(self, string: str):
        """Set the track name."""
        self.__name = string

    @property
    def gain(self) -> float:
        """Track gain in dB.

        Gain in dB to apply to the synthesized signal of the track.
        """
        return self.__gain

    @gain.setter
    def gain(self, value: float):
        """Set the track gain."""
        self.__gain = value

    @property
    def source(self) -> AnySourceType:
        """Source object associated with the track.

        The source of the track is used to synthesize the corresponding signal. Its type can be
        either :class:`SourceSpectrum`, :class:`SourceBroadbandNoise`,
        :class:`SourceBroadbandNoiseTwoParameters`, :class:`SourceHarmonics`,
        :class:`SourceHarmonicsTwoParameters`, or :class:`SourceAudio`.
        """
        return self.__source

    @source.setter
    def source(self, obj: AnySourceType):
        """Set the track source."""
        if (obj is not None) and (not (isinstance(obj, AnySourceType))):
            raise PyAnsysSoundException(
                "Specified source must have a valid type (SourceSpectrum, SourceBroadbandNoise, "
                "SourceBroadbandNoiseTwoParameters, SourceHarmonics, "
                "SourceHarmoncisTwoParameters, or SourceAudio)."
            )
        self.__source = obj

    @property
    def filter(self) -> Filter:
        """Filter object of the track."""
        return self.__filter

    @filter.setter
    def filter(self, obj: Filter):
        """Set the track filter."""
        if (obj is not None) and (not (isinstance(obj, Filter))):
            raise PyAnsysSoundException("Specified filter must be of type Filter.")
        self.__filter = obj

    def set_from_generic_data_container(
        self, gdc_track: GenericDataContainer, sampling_frequency: float = 44100.0
    ):
        """Set the track data from a generic data container.

        This method is meant to set the track data from a generic data container obtained when
        loading a Sound Composer project file (.scn).

        Parameters
        ----------
        gdc_track : GenericDataContainer
            Track data as a DPF generic data container.
        sampling_frequency : float, default: 44100.0
            Sampling frequency in Hz to use in the track's filter to create.
        """
        # Assign name and gain.
        self.name = (gdc_track.get_property("track_name"),)
        self.gain = (gdc_track.get_property("track_gain"),)

        # Create source attribute.
        gdc_source: GenericDataContainer = gdc_track.get_property("track_source")
        gdc_source_control: GenericDataContainer = gdc_track.get_property("track_source_control")
        self.source = DICT_SOURCE_TYPE[gdc_track.get_property("track_type")]()
        self.source.set_from_generic_data_containers(gdc_source, gdc_source_control)

        # Create filter attribute.
        if gdc_track.get_property("track_is_filter") == 1:
            frf = gdc_track.get_property("track_filter")
            self.filter = Filter(sampling_frequency=sampling_frequency)
            filter.design_FIR_from_FRF(frf)
        else:
            filter = None

    # TODO: Save cannot work for now because the FRF is not stored in the Filter class.
    # def get_as_generic_data_container(self) -> GenericDataContainer:
    #     """Get the track data as a generic data container.

    #     This method is meant to return the track data as a generic data container needed to save a
    #     Sound Composer project file (.scn).

    #     Returns
    #     -------
    #     GenericDataContainer
    #         Track data as a generic data container.
    #     """
    #     if self.source is None:
    #         warnings.warn(
    #             PyAnsysSoundWarning(
    #                 "Cannot create track generic data container because there is no source."
    #             )
    #         )
    #         gdc_track = None
    #     else:
    #         # Get source and source control as generic data containers.
    #         gdc_source, gdc_source_control = self.source.get_as_generic_data_containers()

    #         # Create a generic data container for the track.
    #         gdc_track = GenericDataContainer()

    #         # Set track generic data container properties.
    #         gdc_track.set_property(
    #             "track_type",
    #             [i for i in DICT_SOURCE_TYPE if isinstance(self.source, DICT_SOURCE_TYPE[i])][0],
    #         )
    #         gdc_track.set_property("track_source", gdc_source)
    #         gdc_track.set_property("track_source_control", gdc_source_control)

    #         if self.filter is not None:
    #             gdc_track.set_property("track_is_filter", 1)
    #             # TODO: sort out the fact that FRF is not stored in the filter object
    #             gdc_track.set_property("track_filter", self.filter.FRF)
    #         else:
    #             gdc_track.set_property("track_is_filter", 0)

    #     return gdc_track

    def process(self, sampling_frequency: float = 44100.0):
        """Generate the signal of the track, using the current source and filter.

        Parameters
        ----------
        sampling_frequency : float, default: 44100.0
            Sampling frequency of the generated sound in Hz.
        """
        if sampling_frequency <= 0.0:
            raise PyAnsysSoundException("Sampling frequency must be strictly positive.")

        if (
            self.filter is not None
            and np.round(sampling_frequency, 1) != self.filter.get_sampling_frequency()
        ):
            raise PyAnsysSoundException(
                "Specified sampling frequency must be equal to that which is stored in the track's "
                "filter."
            )

        if self.source is None:
            raise PyAnsysSoundException(f"Source is not set. Use {__class__.__name__}.source.")

        self.source.process(sampling_frequency)
        signal = self.source.get_output()

        if self.filter is not None:
            self.filter.signal = signal
            self.filter.process()
            signal = self.filter.get_output()

        if self.gain != 0.0:
            gain_obj = ApplyGain(signal=signal, gain=self.gain, gain_in_db=True)
            gain_obj.process()
            signal = gain_obj.get_output()

        self._output = signal

    def get_output(self) -> Field:
        """Get the generated signal as a DPF field.

        Returns
        -------
        Field
            Generated signal as a DPF field.
        """
        if self._output == None:
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

        if output == None:
            return np.array([])

        return np.array(output.data)

    def plot(self):
        """Plot the resulting signal in a figure."""
        if self._output == None:
            raise PyAnsysSoundException(
                f"Output is not processed yet. Use the {__class__.__name__}.process() method."
            )
        output = self.get_output()

        output_time = output.time_freq_support.time_frequencies.data

        plt.plot(output_time, output.data)
        plt.title(
            f"{self.name if len(self.name) > 0 else "Generated signal"} "
            f"({type(self.source).__name__})"
        )
        plt.xlabel("Time (s)")
        plt.ylabel(f"Amplitude{f" ({output.unit})" if len(output.unit) > 0 else ""}")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

        self.source.plot_control()
