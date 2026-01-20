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

"""Write a signal to a WAV file."""

import warnings

from ansys.dpf.core import DataSources, Field, FieldsContainer, Operator

from . import SignalUtilitiesParent
from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning


class WriteWav(SignalUtilitiesParent):
    """Write a signal into a WAV file.

    .. seealso::
        :class:`LoadWav`

    Examples
    --------
    Write a signal to a standard 16-bit WAV file.

    >>> from ansys.sound.core.signal_utilities import WriteWav
    >>> write_wav = WriteWav(
    ...     signal=my_signal,
    ...     path_to_write="path/to/output.wav",
    ...     bit_depth="int16",
    ... )
    >>> write_wav.process()

    .. seealso::
        :ref:`load_resample_amplify_write_wav_files_example`
            Example demonstrating how to load, resample, amplify, and write WAV files.
    """

    def __init__(
        self,
        signal: Field | FieldsContainer = None,
        path_to_write: str = "",
        bit_depth: str = "float32",
    ):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        signal : Field | FieldsContainer, default: None
            Signal to write to a WAV file. Signal may be single-channel (``Field``, or
            ``FieldsContainer`` with one ``Field``) or multichannel (``FieldsContainer`` with more
            than one ``Field``). If necessary, the classes :class:`CreateSignalField` (for
            single-channel signals) and :class:`CreateSignalFieldsContainer` (for single- or
            multi-channel signals) can help create such input from signal data.
        path_to_write : str, default: ''
            Path for the WAV file.
        bit_depth : str, default: 'float32'
            Bit depth. Options are `'float32'`, `'int32'`, `'int16'`, and `'int8'`.
            These mean that the samples are coded into the WAV file using 32 bits (32-bit IEEE
            Float), 32 bits (int), 16 bits (int), or 8 bits (int), respectively.
        """
        super().__init__()
        self.path_to_write = path_to_write
        self.signal = signal
        self.bit_depth = bit_depth
        self.__operator = Operator("write_wav_sas")

    @property
    def signal(self) -> Field | FieldsContainer:
        """Input signal.

        Signal may be single-channel (``Field``, or ``FieldsContainer`` with one ``Field``) or
        multichannel (``FieldsContainer`` with more than one ``Field``).
        """
        return self.__signal

    @signal.setter
    def signal(self, signal: Field | FieldsContainer):
        """Setter for the signal."""
        if not isinstance(signal, (Field, FieldsContainer)) and signal is not None:
            raise PyAnsysSoundException(
                "Signal must be specified as a `Field` or `FieldsContainer`."
            )
        self.__signal = signal

    @property
    def bit_depth(self) -> str:
        """Bit depth.

        Options are `'float32'`, `'int32'`, `'int16'`, and `'int8'`. These mean that the
        samples are coded into the WAV file using 32 bits (32-bit IEEE Float), 32 bits (int),
        16 bits (int), or 8 bits (int), respectively.
        """
        return self.__bit_depth

    @bit_depth.setter
    def bit_depth(self, bit_depth: str):
        """Set the bit depth."""
        if bit_depth not in ("int8", "int16", "int32", "float32"):
            raise PyAnsysSoundException(
                "Bit depth is invalid. Accepted values are 'float32', 'int32', 'int16', and 'int8'."
            )

        self.__bit_depth = bit_depth

    @property
    def path_to_write(self) -> str:
        """Path of the WAV file to write."""
        return self.__path_to_write

    @path_to_write.setter
    def path_to_write(self, path_to_write: str):
        """Path of the WAV file to write."""
        self.__path_to_write = path_to_write

    def process(self):
        """Write the signal to a WAV file.

        This method calls the appropriate DPF Sound operator to write the signal to a WAV file.
        """
        if self.path_to_write == "":
            raise PyAnsysSoundException(
                "Path for writing WAV file is not specified. Use `WriteWav.path_to_write`."
            )

        if self.signal == None:
            raise PyAnsysSoundException("No signal is specified for writing to a WAV file. \
                    Use `WriteWav.signal`.")

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
