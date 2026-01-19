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

"""Sound Composer's audio source."""

import warnings

from ansys.dpf.core import Field, GenericDataContainer, Operator
from matplotlib import pyplot as plt
import numpy as np

from ansys.sound.core.signal_utilities import LoadWav, Resample

from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ._source_parent import SourceParent

ID_LOAD_FROM_TEXT = "load_sound_samples_from_txt"


class SourceAudio(SourceParent):
    """Sound Composer's audio source class.

    This class creates an audio source for the Sound Composer. An audio source simply consists of a
    time-domain - typically audio - signal. Unlike other source types, it requires no `source
    control`.

    .. seealso::
        :class:`SoundComposer`, :class:`Track`

    Examples
    --------
    Create an audio source from a sound signal stored in a WAV file.

    >>> from ansys.sound.core.sound_composer import SourceAudio
    >>> source_audio = SourceAudio(file="path/to/audio.wav")
    >>> source_audio.process(sampling_frequency=48000.0)
    >>> source_audio.plot()
    """

    def __init__(self, file: str = ""):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        file : str, default: ""
            Path to the audio source file. Supported files are WAV files and and text files with
            the header `AnsysSound_SoundSamples`.
        """
        super().__init__()

        # Define DPF Sound operators.
        self.__operator_load = Operator(ID_LOAD_FROM_TEXT)

        # Load the audio file, if specified.
        if len(file) > 0:
            if file.endswith(".wav"):
                self.load_from_wave_file(file)
            else:
                self.load_from_text_file(file)
        else:
            self.source_audio_data = None

    def __str__(self) -> str:
        """Return the string representation of the object."""
        if self.source_audio_data is not None:
            support_data = self.source_audio_data.time_freq_support.time_frequencies.data

            if len(support_data) < 1:
                str_duration = "N/A"
            else:
                str_duration = f"{support_data[-1]:.1f} s"

            if len(support_data) < 2:
                str_fs = "N/A"
            else:
                str_fs = f"{1/(support_data[1] - support_data[0]):.1f} Hz"

            str_source = (
                f"'{self.source_audio_data.name}'\n"
                f"\tDuration: {str_duration}\n"
                f"\tSampling frequency: {str_fs}"
            )
        else:
            str_source = "Not set"

        return f"Audio source: {str_source}"

    @property
    def source_audio_data(self) -> Field:
        """Source data of the audio source.

        The audio source data consists of the audio samples over time, in Pa.
        """
        return self.__source_audio_data

    @source_audio_data.setter
    def source_audio_data(self, source_audio_data: Field):
        """Set the audio source data."""
        if not (isinstance(source_audio_data, Field) or source_audio_data is None):
            raise PyAnsysSoundException(
                "Specified audio source data must be provided as a DPF field."
            )
        self.__source_audio_data = source_audio_data

    def load_from_wave_file(self, file: str):
        """Load the audio source data from a WAV file.

        Parameters
        ----------
        file : str
            Path to the WAV file.
        """
        loader = LoadWav(file)
        loader.process()
        self.source_audio_data = loader.get_output()[0]

    def load_from_text_file(self, file: str):
        """Load the audio source data from a text file.

        Parameters
        ----------
        file : str
            Path to the text file containing the samples over time. Supported files have the same
            text format (with the `AnsysSound_SoundSamples` header) as supported by Ansys Sound SAS.
        """
        # Set operator inputs.
        self.__operator_load.connect(0, file)

        # Run the operator.
        self.__operator_load.run()

        # Get the loaded sound power level parameters.
        self.source_audio_data = self.__operator_load.get_output(0, "field")

    def set_from_generic_data_containers(
        self,
        source_data: GenericDataContainer,
        source_control_data: GenericDataContainer,
    ):
        """Set the source and source control data from generic data containers.

        This method is meant to set the source data from generic data containers obtained when
        loading a Sound Composer project file (.scn) with the method :meth:`SoundComposer.load()`.

        Parameters
        ----------
        source_data : GenericDataContainer
            Source data as a DPF generic data container.
        source_control_data : GenericDataContainer
            Source control data as a DPF generic data container. In the case of
            :class:`SourceAudio`, source control data is ignored.
        """
        self.source_audio_data = source_data.get_property("sound_composer_source")

    def get_as_generic_data_containers(self) -> tuple[GenericDataContainer]:
        """Get the source data as generic data containers.

        This method is meant to return the source data as generic data containers, in the format
        needed to save a Sound Composer project file (.scn) with the method
        :meth:`SoundComposer.save()`.

        Returns
        -------
        tuple[GenericDataContainer]
            Source as two generic data containers, for source and source control data, respectively.
            In the case of :class:`SourceAudio`, there is no source control data, so ``None`` is
            always returned as the second element.
        """
        if self.source_audio_data is None:
            warnings.warn(
                PyAnsysSoundWarning(
                    "Cannot create source generic data container because there is no source data."
                )
            )
            return (None, None)
        else:
            source_data = GenericDataContainer()
            source_data.set_property("sound_composer_source", self.source_audio_data)
            return (source_data, None)

    def process(self, sampling_frequency: float = 44100.0):
        """Generate the sound of the audio source.

        This method simply copies the audio source data to the output, possibly after having
        resampled it to the sampling frequency given as input.

        Parameters
        ----------
        sampling_frequency : float, default: 44100.0
            Sampling frequency of the generated sound in Hz.
        """
        if sampling_frequency <= 0.0:
            raise PyAnsysSoundException("Sampling frequency must be strictly positive.")

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

    def get_output_as_nparray(self) -> np.ndarray:
        """Get the generated sound as a NumPy array.

        Returns
        -------
        numpy.ndarray
            Generated sound as a NumPy array.
        """
        output = self.get_output()

        if output == None:
            return np.array([])

        return np.array(output.data)

    def plot(self):
        """Plot the generated sound."""
        if self._output == None:
            raise PyAnsysSoundException(
                f"Output is not processed yet. Use the ``{__class__.__name__}.process()`` method."
            )
        output = self.get_output()

        time = output.time_freq_support.time_frequencies

        plt.plot(time.data, output.data)
        name = output.name
        if len(name) > 0:
            plt.title(name)
        else:
            plt.title("Sound generated from the audio source")
        plt.xlabel(f"Time ({time.unit})")
        plt.ylabel(f"Amplitude ({output.unit})")
        plt.grid(True)
        plt.show()
