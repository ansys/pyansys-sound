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

"""Sound Composer's source control over time."""

from ansys.dpf.core import Field, Operator
from matplotlib import pyplot as plt

from ansys.sound.core.signal_utilities.load_wav import LoadWav

from .._pyansys_sound import PyAnsysSoundException
from ._source_control_parent import SourceControlParent

ID_LOAD_FROM_TEXT = "load_sound_samples_from_txt"


class SourceControlTime(SourceControlParent):
    """Sound Composer's time source control class.

    This class stores the source control (that is, the control parameter values over time) used by
    the Sound Composer to generate a sound from sources of types broadband noise and harmonics
    (with one or two control parameters).

    .. seealso::
        :class:`SourceBroadbandNoise`, :class:`SourceBroadbandNoiseTwoParameters`,
        :class:`SourceHarmonics`, :class:`SourceHarmonicsTwoParameters`

    Examples
    --------
    Create a time source control by loading the control data from a text file.

    >>> from ansys.sound.core.sound_composer import SourceControlTime
    >>> source_control = SourceControlTime(file_str="path/to/control/file.txt")
    >>> source_control.description = "Source control data from text file."

    .. seealso::
        :ref:`sound_composer_create_project`
            Example demonstrating how to create a Sound Composer project from scratch.
    """

    def __init__(self, file_str: str = ""):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        file_str : str, default: ""
            Path to the control data file. Supported files are WAV files and and text files with
            the header `AnsysSound_SoundSamples`.
        """
        super().__init__()

        # Define DPF Sound operators.
        self.__operator_load = Operator(ID_LOAD_FROM_TEXT)

        if len(file_str) > 0:
            if file_str.endswith(".wav"):
                self.load_from_wave_file(file_str)
            else:
                self.load_from_text_file(file_str)
        else:
            self.control = None

    def __str__(self) -> str:
        """Return the string representation of the object."""
        if self.control is None:
            return "Not set"
        else:
            time = self.control.time_freq_support.time_frequencies
            str_duration = f"{time.data[-1]:.1f} {time.unit}" if len(time.data) > 0 else "N/A"
            return (
                f"Unit: {self.control.unit}\n"
                f"Duration: {str_duration}\n"
                f"Min - max: {self.control.data.min():.1f} - {self.control.data.max():.1f} "
                f"{self.control.unit}"
            )

    @property
    def control(self) -> Field:
        """Control profile (control parameter values over time)."""
        return self.__control

    @control.setter
    def control(self, control: Field):
        """Set the control."""
        if control is not None:
            if not (isinstance(control, Field) or control is None):
                raise PyAnsysSoundException(
                    "Specified control profile must be provided as a DPF field."
                )

        self.__control = control

        # Reset the description to store when saving a Sound Composer project (.scn file).
        self.description = "Profile created in PyAnsys Sound."

    @property
    def description(self) -> str:
        """Description of the control profile.

        This description is used when saving a Sound Composer project (.scn file). When loading the
        project file in the Sound Composer module of SAS, this description is displayed in the
        track's source control tab.

        .. note::
            The description is reset every time the attribute :attr:`control` is modified.
        """
        return self.__description

    @description.setter
    def description(self, description: str):
        """Set the description."""
        if not isinstance(description, str):
            raise PyAnsysSoundException("Description must be a string.")
        self.__description = description

    def load_from_wave_file(self, file_str: str):
        """Load control data from a WAV file.

        Parameters
        ----------
        file_str : str
            Path to the WAV file.
        """
        loader = LoadWav(file_str)
        loader.process()
        self.control = loader.get_output()[0]

    def load_from_text_file(self, file_str: str):
        """Load control data from a text file.

        Parameters
        ----------
        file_str : str
            Path to the text file. Supported files have the same text format (with the header
            `AnsysSound_SoundSamples`) as supported by Ansys Sound SAS.
        """
        # Set operator inputs.
        self.__operator_load.connect(0, file_str)

        # Run the operator.
        self.__operator_load.run()

        # Get the loaded sound power level parameters.
        self.control = self.__operator_load.get_output(0, "field")

        # Clear the control unit, as this operator always returns the unit as "Pa".
        self.control.unit = ""

    def plot(self):
        """Plot the control profile."""
        time = self.control.time_freq_support.time_frequencies

        plt.plot(time.data, self.control.data)
        plt.title(self.control.name if len(self.control.name) > 0 else "Control profile")
        plt.xlabel(f"Time ({time.unit})")
        str_unit = f" ({self.control.unit})" if len(self.control.unit) > 0 else ""
        plt.ylabel("Control parameter" + str_unit)
        plt.grid(True)
        plt.show()
