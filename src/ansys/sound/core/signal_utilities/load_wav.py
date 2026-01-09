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

"""Loads a signal from a WAV file."""

import warnings

from ansys.dpf.core import DataSources, FieldsContainer, Operator, types
import numpy as np

from ansys.sound.core.server_helpers import requires_dpf_version

from . import SignalUtilitiesParent
from .._pyansys_sound import (
    PyAnsysSoundException,
    PyAnsysSoundWarning,
    convert_fields_container_to_np_array,
)


class LoadWav(SignalUtilitiesParent):
    """Load a signal, and its sampling frequency and format from a WAV file.

    .. seealso::
        :class:`WriteWav`

    Examples
    --------
    Load a signal from a WAV file.

    >>> from ansys.sound.core.signal_utilities import LoadWav
    >>> load_wav = LoadWav(path_to_wav="path/to/file.wav")
    >>> load_wav.process()
    >>> signal = load_wav.get_output()

    .. seealso::
        :ref:`load_resample_amplify_write_wav_files_example`
            Example demonstrating how to load, resample, amplify, and write WAV files.
    """

    def __init__(self, path_to_wav: str = ""):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        path_to_wav : str, default: ""
            Path to the WAV file to load. The path can be set during the instantiation
            of the object or with the ``LoadWav.path_to_wav`` attribute.
        """
        super().__init__()
        self.path_to_wav = path_to_wav
        self.__operator = Operator("load_wav_sas")

    @property
    def path_to_wav(self) -> str:
        """Path to the WAV file."""
        return self.__path_to_wav

    @path_to_wav.setter
    def path_to_wav(self, path_to_wav: str):
        """Set the path to the WAV file."""
        self.__path_to_wav = path_to_wav

    def process(self):
        """Load the WAV file.

        This method calls the appropriate DPF Sound operator to load the WAV file.
        """
        if self.path_to_wav == "":
            raise PyAnsysSoundException(
                "Path for loading WAV file is not specified. Use "
                f"`{self.__class__.__name__}.path_to_wav`."
            )

        # Load a WAV file
        data_source_in = DataSources()

        # Create input path
        data_source_in.add_file_path(self.path_to_wav, ".wav")

        # Load WAV file and store it in a container
        self.__operator.connect(0, data_source_in)

        # Run the operator
        self.__operator.run()

        # Store outputs
        self._output = self.__operator.get_output(0, types.fields_container)
        # Note: sampling frequency and format are retrieved within their respective getter methods,
        # because their availabilility depends on the server version (which is managed by these
        # methods' `requires_dpf_version` decorator).

    def get_output(self) -> FieldsContainer:
        """Get the signal loaded from the WAV file as a DPF fields container.

        Returns
        -------
        FieldsContainer
            Signal loaded from the WAV file in a DPF fields container.
        """
        if self._output is None:
            warnings.warn(
                PyAnsysSoundWarning(
                    f"Output is not processed yet. Use the `{self.__class__.__name__}.process()` "
                    "method."
                )
            )

        return self._output

    def get_output_as_nparray(self) -> np.ndarray:
        """Get the signal loaded from the WAV file as a NumPy array.

        Returns
        -------
        numpy.ndarray
            Signal loaded from the WAV file in a NumPy array.
        """
        return convert_fields_container_to_np_array(self.get_output())

    @requires_dpf_version("11.0")
    def get_sampling_frequency(self) -> float:
        """Get the sampling frequency in Hz of the loaded signal.

        Returns
        -------
        float
            Sampling frequency in Hz of the loaded signal.
        """
        if self._output is None:
            warnings.warn(
                PyAnsysSoundWarning(
                    f"Output is not processed yet. Use the `{self.__class__.__name__}.process()` "
                    "method."
                )
            )
            return None

        return self.__operator.get_output(1, types.double)

    @requires_dpf_version("11.0")
    def get_format(self) -> str:
        """Get the format of the loaded WAV file.

        Returns
        -------
        str
            Format of the loaded WAV file. Can be either "float32", "int32", "int24", "int16", or
            "int8".
        """
        if self._output is None:
            warnings.warn(
                PyAnsysSoundWarning(
                    f"Output is not processed yet. Use the `{self.__class__.__name__}.process()` "
                    "method."
                )
            )
            return None

        return self.__operator.get_output(2, types.string)
