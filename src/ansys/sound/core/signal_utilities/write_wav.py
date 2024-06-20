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

"""Write a signal to a WAV file."""

import warnings

from ansys.dpf.core import DataSources, FieldsContainer, Operator

from . import SignalUtilitiesParent
from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning


class WriteWav(SignalUtilitiesParent):
    """Write a signal to a WAV file."""

    def __init__(
        self, signal: FieldsContainer = None, path_to_write: str = "", bit_depth: str = "float32"
    ):
        """Create a ``WriteWav`` class.

        Parameters
        ----------
        signal: FieldsContainer, default: None
            Signal to write to a WAV file. Each channel in the DPF fields container is a field.
        path_to_write: str, default: ''
            Path for the WAV file. This parameter can be set during the instantiation
            of the object or with the ``LoadWav.set_path()`` method.
        bit_depth: str, default: 'float32'
            Bit depth. Options are ``'float32'``, ``'int32'``, ``'int16'``, and ``'int8'``.
            This means that the samples are respectively coded into the WAV file
            using 32 bits (32-bit IEEE Float), 32 bits (int), 16 bits (int), or 8 bits (int).
        """
        super().__init__()
        self.path_to_write = path_to_write
        self.signal = signal
        self.bit_depth = bit_depth
        self.__operator = Operator("write_wav_sas")

    @property
    def signal(self):
        """Signal."""
        return self.__signal  # pragma: no cover

    @signal.setter
    def signal(self, signal: FieldsContainer):
        """Setter for the signal.

        Sets the value of the signal to write to the disk.
        """
        self.__signal = signal

    @signal.getter
    def signal(self) -> FieldsContainer:
        """Signal.

        Returns
        -------
        FieldsContainer
            Signal to write to the disk as a DPF fields container.
        """
        return self.__signal

    @property
    def bit_depth(self):
        """Bit depth."""
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
                "Bit depth is invalid. Accepted values are 'float32', 'int32', 'int16', and 'int8'."
            )

        self.__bit_depth = bit_depth

    @bit_depth.getter
    def bit_depth(self) -> str:
        """Bit depth.

        Returns
        -------
        str
            Bit depth.
        """
        return self.__bit_depth

    @property
    def path_to_write(self):
        """Path to write the WAV file to."""
        return self.__path_to_write  # pragma: no cover

    @path_to_write.setter
    def path_to_write(self, path_to_write: str):
        """Path to write the WAV file to."""
        self.__path_to_write = path_to_write

    @path_to_write.getter
    def path_to_write(self) -> str:
        """Path to write the the WAV file to.

        Returns
        -------
        str
            Path to write the WAV file to.
        """
        return self.__path_to_write

    def process(self):
        """Write the signal to a WAV file.

        This method calls the appropriate DPF Sound operator to write the signal to a WAV file.
        """
        if self.path_to_write == "":
            raise PyAnsysSoundException(
                "Path for writing WAV file is not specified. Use 'WriteWav.set_path'."
            )

        if self.signal == None:
            raise PyAnsysSoundException(
                "No signal is specified for writing to a WAV file. \
                    Use 'WriteWav.set_signal'."
            )

        data_source_out = DataSources()
        data_source_out.add_file_path(self.path_to_write, ".wav")

        self.__operator.connect(0, self.signal)
        self.__operator.connect(1, data_source_out)
        self.__operator.connect(2, self.bit_depth)

        self.__operator.run()

    def plot(self):
        """Plot the output.

        There is nothing to plot for the ``WriteWav`` class.
        """
        warnings.warn(PyAnsysSoundWarning("Nothing to plot for this class."))
