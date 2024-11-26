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

"""Sound Composer's audio source."""
import warnings

from ansys.dpf.core import Field, Operator
from matplotlib import pyplot as plt
import numpy as np
from numpy import typing as npt

from ansys.sound.core.signal_utilities import LoadWav, Resample

from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ._source_parent import SourceParent

ID_LOAD_FROM_TEXT = "load_sound_samples_from_txt"


class SourceAudio(SourceParent):
    """Sound Composer's audio source class.

    This class creates an audio source for the Sound Composer.
    """

    def __init__(self, file: str = ""):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        file : str, default ""
            Path to the audio file (WAV format).
        """
        super().__init__()

        # Load the audio file, if specified.
        if len(file) > 0:
            loader = LoadWav(file)
            loader.process()
            self.source_audio_data = loader.get_output()[0]
        else:
            self.source_audio_data = None

        # Define DPF Sound operators.
        self.__operator_load = Operator(ID_LOAD_FROM_TEXT)

    def __str__(self) -> str:
        """Return the string representation of the object."""
        if self.source_audio_data is not None:
            support_data = self.source_audio_data.time_freq_support.time_frequencies.data
            str_source = (
                f"'{self.source_audio_data.name}'\n"
                f"\tDuration: {support_data[-1]:.1f} s\n"
                f"\tSampling frequency: {1/(support_data[1] - support_data[0]):.1f} Hz"
            )
        else:
            str_source = "Not set"

        return f"Audio source: {str_source}"

    @property
    def source_audio_data(self) -> Field:
        """Audio source data, as a DPF field.

        Audio samples over time, in Pa, as a DPF field.
        """
        return self.__source_audio_data

    @source_audio_data.setter
    def source_audio_data(self, source_audio_data: Field):
        """Set the audio source data, from a DPF field."""
        if not (isinstance(source_audio_data, Field) or source_audio_data is None):
            raise PyAnsysSoundException(
                "Specified audio source data must be provided as a DPF field."
            )
        self.__source_audio_data = source_audio_data

    def load_source_audio_from_text(self, file: str):
        """Load the audio source data from a text file.

        Parameters
        ----------
        file : str
            Path to the text file containing the audio samples over time. Supported files shall
            have the same text format (with the AnsysSound_SoundSamples header) as supported by
            Ansys Sound SAS.
        """
        # Set operator inputs.
        self.__operator_load.connect(0, file)

        # Run the operator.
        self.__operator_load.run()

        # Get the loaded sound power level parameters.
        self.source_audio_data = self.__operator_load.get_output(0, "field")

    def process(self, sampling_frequency: float = 44100.0):
        """Generate the sound of the audio source.

        Parameters
        ----------
        sampling_frequency : float, default 44100.0
            Sampling frequency of the generated sound in Hz.
        """
        if self.source_audio_data is None:
            raise PyAnsysSoundException(
                f"Source's audio data is not set. Use "
                f"``{__class__.__name__}.source_audio_data`` or method "
                f"``{__class__.__name__}.load_source_audio_from_text()``."
            )

        # Check sampling frequency, and resample if necessary.
        support_data = self.source_audio_data.time_freq_support.time_frequencies.data
        if np.round(1 / (support_data[1] - support_data[0]), 1) != np.round(sampling_frequency, 1):
            resampler = Resample(
                signal=self.source_audio_data, new_sampling_frequency=sampling_frequency
            )
            resampler.process()
            self._output = resampler.get_output()
        else:
            self._output = self.source_audio_data

    def get_output(self) -> Field:
        """Get the generated sound as a DPF field.

        Returns
        -------
        Field
            Generated sound as a DPF field.
        """
        if self._output == None:
            warnings.warn(
                PyAnsysSoundWarning(
                    "Output is not processed yet. "
                    f"Use the ``{__class__.__name__}.process()`` method."
                )
            )
        return self._output

    def get_output_as_nparray(self) -> npt.ArrayLike:
        """Get the generated sound as a numpy array.

        Returns
        -------
        numpy.ndarray
            Generated sound as a numpy array.
        """
        output = self.get_output()

        if output == None:
            return np.array([])

        return np.array(output.data)

    def plot(self):
        """Plot the resulting signal in a figure."""
        if self._output == None:
            raise PyAnsysSoundException(
                f"Output is not processed yet. Use the ``{__class__.__name__}.process()`` method."
            )
        output = self.get_output()

        time_data = output.time_freq_support.time_frequencies.data

        plt.plot(time_data, output.data)
        name = output.name
        if len(name) > 0:
            plt.title(name)
        else:
            plt.title("Signal from audio source")
        plt.xlabel("Time (s)")
        plt.ylabel("Amplitude (Pa)")
        plt.grid(True)
        plt.show()
