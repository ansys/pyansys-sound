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

"""PyAnsys Sound class to store sound data."""
from ansys.dpf.core import Field, FieldsContainer
import matplotlib.pyplot as plt
import numpy as np

from .._pyansys_sound import PyAnsysSoundException


class Sound(FieldsContainer):
    """PyAnsys Sound class to store sound data."""

    # ctor or not ctor?
    # not ctor: class behaves exactly like a FieldsContainer, so it can be used in the same way (but
    # their is no "sound_factory", the FieldsContainer's would still need to be used)
    # ctor: allow building a sound object by passing np arrays or a list of Fields...

    def __str__(self):
        """Return the string representation of the object."""
        if self.channel_count > 0:
            properties_str = (
                f":\n\tsampling frequency: {self.fs:.1f} Hz" f"\n\tDuration: {self.duration:.2f} s"
            )
        else:
            properties_str = ""
        return f"Sound object with {self.channel_count} channels{properties_str}"

    # This is actually not a good idea as other classes need Fields as input, while Sound will
    # always be returned homgeneously to a FieldsContainer.
    # def __getitem__(self, index: int) -> "Sound":
    #     """Get a channel from the sound data."""
    #     if index < 0 or index >= len(self):
    #         raise PyAnsysSoundException("Channel index is out of range.")
    #     return Sound.create(super().__getitem__(index))

    @property
    def channel_count(self) -> int:
        """Number of channels in the sound data."""
        return len(self)

    @property
    def time(self) -> np.ndarray:
        """Array of times in s where the sound is defined."""
        if self.channel_count == 0:
            raise PyAnsysSoundException("No channels available in the Sound object.")

        return np.array(self[0].time_freq_support.time_frequencies.data)

    @property
    def fs(self) -> float:
        """Sampling frequency in Hz."""
        if self.channel_count == 0:
            raise PyAnsysSoundException("No channels available in the Sound object.")
        if len(self.time) < 2:
            raise PyAnsysSoundException("Not enough time points to determine sampling frequency.")

        return 1 / (self.time[1] - self.time[0])

    @property
    def duration(self) -> float:
        """Duration in s."""
        if self.channel_count == 0:
            raise PyAnsysSoundException("No channels available in the Sound object.")
        return self.time[-1] - self.time[0]

    def update(self) -> None:
        """Update the sound data."""
        # Nothing to update here for now
        # TODO:
        # - check at least one field is present
        # - check all fields are the same size and have the same time frequency support
        # - check support is regularly spaced
        pass

    def get_as_nparray(self) -> list[np.ndarray]:
        """Get the sound data as a NumPy array."""
        # start by update to do required checks?
        self.update()

        if self.channel_count == 1:
            return [np.array(self[0].data)]

        arrays = [np.empty(len(self.time)) for _ in range(self.channel_count)]
        for i, channel in enumerate(self):
            arrays[i] = np.array(channel.data)
        return arrays

    @classmethod
    def create(cls, object: Field | FieldsContainer) -> "Sound":
        """TODO."""
        if isinstance(object, FieldsContainer):
            object.__class__ = cls
            object.update()
            return object
        elif isinstance(object, Field):
            sound = cls()
            sound.labels = ["channel_number"]
            sound.add_field({"channel_number": 0}, object)
            return sound

    def split_channels(self) -> list["Sound"]:
        """Split a multichannel Sound object into a list of Sound objects, one for each channel."""
        channels = []
        for channel in self:
            channels.append(Sound.create(channel))

        return channels

    def plot(self):
        """Plot the sound data."""
        if self.channel_count == 0:
            raise PyAnsysSoundException("No channels available in the Sound object.")

        for i, channel in enumerate(self):
            plt.plot(
                channel.time_freq_support.time_frequencies.data, channel.data, label=f"Channel {i}"
            )

        plt.xlabel("Time (s)")
        plt.ylabel("Amplitude (Pa)")
        if self.channel_count > 1:
            plt.legend()
        plt.title(self.name)
        plt.show()


# class Sound_tmp(Field):
#     """PyAnsys Sound class to store sound data.
#     """

#     def __init__(
#         self,
#         field: Field = None,
#         sound_pressure: list[float] | np.ndarray = None,
#         fs: float = None,
#         time: list[float] | np.ndarray = None,
#     ):
#         """Class instantiation takes the following parameters.

#         Parameters
#         ----------
#         field : Field, default: None
#             DPF field containing the sound data.
#         sound_pressure : list[float] | numpy.ndarray, default: None
#             Sound pressure values in Pa.
#         fs : float, default: None
#             Sampling frequency in Hz.
#         time : list[float] | numpy.ndarray, default: None
#             Time values in seconds.
#         """
#         super().__init__()
#         if field is not None:
#             if any(arg is not None for arg in (sound_pressure, fs, time)):
#                 warnings.warn(
#                     PyAnsysSoundWarning(
#                         "When a DPF field is specified as input, other inputs are ignored."
#                     )
#                 )
#             self.data = field.data
#         else:
#             if sound_pressure is None:
#                 raise PyAnsysSoundException(
#                     "Either a DPF field or sound_pressure must be specified when creating a "
#                     "Sound object."
#                 )
#             self.data = sound_pressure
#             self.time_freq_support = TimeFreqSupport()
#             self.time_freq_support.time_frequencies = fields_factory.create_scalar_field(
#                 num_entities=1, location=locations.time_freq
#             )
#             if time is not None:
#                 if fs is not None:
#                     warnings.warn(
#                         PyAnsysSoundWarning(
#                             "When time is specified, fs is ignored. "
#                             "The sampling frequency is inferred from the time values."
#                         )
#                     )
#                 self.time_freq_support.time_frequencies.append(time, 1)
#             else:
#                 if fs is None:
#                     raise PyAnsysSoundException(
#                         "Either time or fs must be specified when creating a Sound object."
#                     )
#                 self.time_freq_support.time_frequencies.append(
#                     np.arange(0, len(sound_pressure) / fs, 1 / fs), 1
#                 )


#     @property
#     def time(self) -> np.ndarray:
#         """Sampling frequency in Hz."""
#         return np.ndarray(self.time_freq_support.time_frequencies.data)

#     @property
#     def fs(self) -> Field:
#         """Sampling frequency in Hz."""
#         return 1 / (self.time[1] - self.time[0])

#     def update(self) -> None:
#         """Update the sound data."""
#         # Nothing to update here
#         pass

#     def get_as_nparray(self) -> list[np.ndarray]:
#         """Get the sound data as a NumPy array."""
#         return np.array(self.data)


def convert_to_sound(object: Field | FieldsContainer) -> Sound:
    """TODO."""
    if isinstance(object, FieldsContainer):
        object.__class__ = Sound
        object.update()
        return object
    elif isinstance(object, Field):
        sound = Sound()
        sound.labels = ["channel_number"]
        sound.add_field({"channel_number": 0}, object)
        return sound


def split_channels(sound: Sound) -> list[Sound]:
    """Split a multichannel Sound object into a list of Sound objects, one for each channel."""
    if not isinstance(sound, Sound):
        raise PyAnsysSoundException("Input must be a Sound object.")

    channels = []
    for channel in sound:
        channels.append(convert_to_sound(channel))

    return channels
