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

"""Sound Composer's source control over time."""
from ansys.dpf.core import Field, Operator
from matplotlib import pyplot as plt

from ansys.sound.core.signal_utilities.load_wav import LoadWav

from .._pyansys_sound import PyAnsysSoundException
from ._source_control_parent import SourceControlParent

ID_LOAD_FROM_TEXT = "load_sound_samples_from_txt"


class SourceControlTime(SourceControlParent):
    """Sound Composer's time source control class.

    This class stores the source control, that is the control parameter values over time, used by
    the Sound Composer to generate a sound from a BBN or harmonic source.
    """

    def __init__(self, file_str: str = ""):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        file_str : str, default: ""
            Path to the control data file (WAV format or text format with header
            `AnsysSound_SoundSamples`).
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
            support_data = self.control.time_freq_support.time_frequencies.data
            str_duration = f"{support_data[-1]:.1f} s" if len(support_data) > 0 else "N/A"
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
            Path to the text file. The text file shall have the same text format (with the header
            `AnsysSound_SoundSamples`), as supported by Ansys Sound SAS.
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
        """Plot the control profile in a figure."""
        time_data = self.control.time_freq_support.time_frequencies.data

        plt.plot(time_data, self.control.data)
        plt.title(self.control.name if len(self.control.name) > 0 else "Control profile")
        plt.xlabel("Time (s)")
        str_unit = f" ({self.control.unit})" if len(self.control.unit) > 0 else ""
        plt.ylabel("Control parameter" + str_unit)
        plt.grid(True)
        plt.show()
