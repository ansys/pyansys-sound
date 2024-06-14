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

"""Write Wav."""

import warnings

from ansys.dpf.core import DataSources, FieldsContainer, Operator

from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ._signal_utilities_parent import SignalUtilitiesParent


class WriteWav(SignalUtilitiesParent):
    """Write wav.

    This class writes wav signals.
    """

    def __init__(
        self, signal: FieldsContainer = None, path_to_write: str = "", bit_depth: str = "float32"
    ):
        """Create a write wav class.

        Parameters
        ----------
        signal:
            Signal to save: fields_container with each channel as a field.
        path_to_write:
            Path where to write the wav file.
            Can be set during the instantiation of the object or with LoadWav.set_path().
        bit_depth:
            Bit depth. Supported values are: 'float32', 'int32', 'int16', 'int8'.
            This means that the samples will be respectively coded into the wav file
            using 32 bits (32-bit IEEE Float), 32 bits (int), 16 bits (int) or 8 bits (int).
        """
        super().__init__()
        self.path_to_write = path_to_write
        self.signal = signal
        self.bit_depth = bit_depth
        self.__operator = Operator("write_wav_sas")

    @property
    def signal(self):
        """Signal property."""
        return self.__signal  # pragma: no cover

    @signal.setter
    def signal(self, signal: FieldsContainer):
        """Setter for the signal.

        Sets the value of the signal to write on the disk.
        """
        self.__signal = signal

    @signal.getter
    def signal(self) -> FieldsContainer:
        """Getter for the signal.

        Returns
        -------
        FieldsContainer
                The signal that is to be written on the disk as a FieldsContainer.
        """
        return self.__signal

    @property
    def bit_depth(self):
        """Bit depth property."""
        return self.__bit_depth  # pragma: no cover

    @bit_depth.setter
    def bit_depth(self, bit_depth: str):
        """Setter for the bit depth.

        Sets the bit depth.
        """
        if (
            bit_depth != "int8"
            and bit_depth != "int16"
            and bit_depth != "int32"
            and bit_depth != "float32"
        ):
            raise PyAnsysSoundException(
                "Invalid bit depth, accepted values are 'float32', 'int32', 'int16', 'int8'."
            )

        self.__bit_depth = bit_depth

    @bit_depth.getter
    def bit_depth(self) -> str:
        """Getter for the bit depth.

        Returns
        -------
        str
                The bit depth.
        """
        return self.__bit_depth

    @property
    def path_to_write(self):
        """Path to write property."""
        return self.__path_to_write  # pragma: no cover

    @path_to_write.setter
    def path_to_write(self, path_to_write: str):
        """Setter for the write path.

        Sets the path for writing the signal on the disk.
        """
        self.__path_to_write = path_to_write

    @path_to_write.getter
    def path_to_write(self) -> str:
        """Getter for the write path.

        Returns
        -------
        str
                The path for writing the signal on the disk.
        """
        return self.__path_to_write

    def process(self):
        """Write the wav file.

        Calls the appropriate DPF Sound operator to writes the wav file.
        """
        if self.path_to_write == "":
            raise PyAnsysSoundException(
                "Path for write wav file is not specified. Use WriteWav.set_path."
            )

        if self.signal == None:
            raise PyAnsysSoundException(
                "No signal is specified for writing, use WriteWav.set_signal."
            )

        data_source_out = DataSources()
        data_source_out.add_file_path(self.path_to_write, ".wav")

        self.__operator.connect(0, self.signal)
        self.__operator.connect(1, data_source_out)
        self.__operator.connect(2, self.bit_depth)

        self.__operator.run()

    def plot(self):
        """Plot the output.

        Nothing to plot for this class.
        """
        warnings.warn(PyAnsysSoundWarning("Nothing to plot."))
