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

"""Sound Composer's track."""
from typing import Union
import warnings

from ansys.dpf.core import Field
from matplotlib import pyplot as plt
import numpy as np

from ansys.sound.core.signal_utilities.apply_gain import ApplyGain
from ansys.sound.core.sound_composer import (
    SoundComposerParent,
    SourceAudio,
    SourceBroadbandNoise,
    SourceBroadbandNoiseTwoParameters,
    SourceHarmonics,
    SourceHarmonicsTwoParameters,
    SourceParent,
    SourceSpectrum,
)
from ansys.sound.core.spectral_processing import Filter

from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning

# Define the typing Union of all possible source types, as a global variable (for typing only).
AnySourceType = Union[tuple(SourceParent.__subclasses__())]


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
        if self.source is not None:
            if isinstance(self.source, SourceAudio):
                # SourceAudio is different, as it has no control attribute. The corresponding line
                # is thus not displayed.
                data = self.source.source_audio_data
                str_source = (
                    f"{"Data not set" if data is None else data.name}\n\t\tType: SourceAudio"
                )

            else:
                match self.source:
                    case SourceSpectrum():
                        data = self.source.source_spectrum_data
                        type_str = "SourceSpectrum"

                    case SourceBroadbandNoise():
                        data = self.source.source_bbn
                        type_str = "SourceBroadbandNoise"

                    case SourceBroadbandNoiseTwoParameters():
                        data = self.source.source_bbn_two_parameters
                        type_str = "SourceBroadbandNoiseTwoParameters"

                    case SourceHarmonics():
                        data = self.source.source_harmonics
                        type_str = "SourceHarmonics"

                    case SourceHarmonicsTwoParameters():
                        data = self.source.source_harmonics_two_parameters
                        type_str = "SourceHarmonicsTwoParameters"

                str_source = (
                    f"{"Data not set" if data is None else data.name}\n"
                    f"\t\tType: {type_str}\n"
                    f"\tSource control: "
                    f"{"Set" if self.source.is_source_control_valid() else "Not set"}"
                )

        else:
            str_source = "Not set"

        return (
            f"{self.name}\n"
            f"\tSource: {str_source}\n"
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
        :class:`SourceHarmoncisTwoParameters`, or :class:`SourceAudio`.
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

    def process(self, sampling_frequency: float = 44100.0):
        """Generate the signal of the track, using the current source and filter.

        Parameters
        ----------
        sampling_frequency : float, default: 44100.0
            Sampling frequency of the generated sound in Hz.
        """
        if sampling_frequency <= 0.0:
            raise PyAnsysSoundException("Sampling frequency must be strictly positive.")

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
                    "Output is not processed yet. "
                    f"Use the {__class__.__name__}.process() method."
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

        if isinstance(self.source, SourceSpectrum | SourceAudio):
            additional_info_str = ""
            if isinstance(self.source, SourceSpectrum):
                additional_info_str = f" - {self.source.source_control.get_method_name()}"
            plt.plot(output_time, output.data)
            plt.title(
                f"{self.name if len(self.name) > 0 else "Generated signal"} "
                f"({type(self.source).__name__}{additional_info_str})"
            )
            plt.xlabel("Time (s)")
            plt.ylabel(f"Amplitude{f" ({output.unit})" if len(output.unit) > 0 else ""}")
            plt.grid(True)
        elif isinstance(self.source, SourceBroadbandNoise | SourceHarmonics):
            _, axes = plt.subplots(2, 1, sharex=True)
            axes[0].plot(output_time, output.data)
            axes[0].set_title(
                f"{self.name if len(self.name) > 0 else "Generated signal"} "
                f"({type(self.source).__name__})"
            )
            axes[0].set_ylabel(f"Amplitude{f" ({output.unit})" if len(output.unit) > 0 else ""}")
            axes[0].grid(True)

            time = self.source.source_control.control.time_freq_support.time_frequencies.data
            unit = self.source.source_control.control.unit
            unit_str = f" ({unit})" if len(unit) > 0 else ""
            name = self.source.source_control.control.name
            name_str = name if len(name) > 0 else "Amplitude"
            axes[1].plot(time, self.source.source_control.control.data)
            axes[1].set_title("Control profile")
            axes[1].set_ylabel(f"{name_str}{unit_str}")
            axes[1].set_xlabel("Time (s)")
            axes[1].grid(True)
        else:
            _, axes = plt.subplots(3, 1, sharex=True)
            axes[0].plot(output_time, output.data)
            axes[0].set_title(
                f"{self.name if len(self.name) > 0 else "Generated signal"} "
                f"({type(self.source).__name__})"
            )
            axes[0].set_ylabel(f"Amplitude{f" ({output.unit})" if len(output.unit) > 0 else ""}")
            axes[0].grid(True)

            if isinstance(self.source, SourceBroadbandNoiseTwoParameters):
                data = self.source.source_control1.control.data
                time = self.source.source_control1.control.time_freq_support.time_frequencies.data
                unit = self.source.source_control1.control.unit
                name = self.source.source_control1.control.name
            else:
                # SourceHarmonicsTwoParameters case: Control 1 is always RPM.
                data = self.source.source_control_rpm.control.data
                time = (
                    self.source.source_control_rpm.control.time_freq_support.time_frequencies.data
                )
                unit = self.source.source_control_rpm.control.unit
                name = self.source.source_control_rpm.control.name
            unit_str = f" ({unit})" if len(unit) > 0 else ""
            name_str = name if len(name) > 0 else "Amplitude"
            axes[1].plot(time, data)
            axes[1].set_title("Control profile 1")
            axes[1].set_ylabel(f"{name_str}{unit_str}")
            axes[1].grid(True)

            data = self.source.source_control2.control.data
            time = self.source.source_control2.control.time_freq_support.time_frequencies.data
            unit = self.source.source_control2.control.unit
            name = self.source.source_control2.control.name
            unit_str = f" ({unit})" if len(unit) > 0 else ""
            name_str = name if len(name) > 0 else "Amplitude"
            axes[2].plot(time, data)
            axes[2].set_title("Control profile 2")
            axes[2].set_ylabel(f"{name_str}{unit_str}")
            axes[2].set_xlabel("Time (s)")
            axes[2].grid(True)

        plt.tight_layout()
        plt.show()
