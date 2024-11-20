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

"""Loads a signal from a WAV file."""

import warnings

from ansys.dpf.core import DataSources, FieldsContainer, Operator
from numpy import typing as npt

from . import SignalUtilitiesParent
from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning


class LoadWav(SignalUtilitiesParent):
    """Loads a signal from a WAV file."""

    def __init__(self, path_to_wav: str = ""):
        """Create a ``LoadWav`` instance.

        Parameters
        ----------
        path_to_wav: str, default: ""
            Path to the WAV file to load. The path can be set during the instantiation
            of the object or with the ``LoadWav.set_path()`` method.
        """
        super().__init__()
        self.path_to_wav = path_to_wav
        self.__operator = Operator("load_wav_sas")

    @property
    def path_to_wav(self):
        """Path to the WAV file."""
        return self.__path_to_wav  # pragma: no cover

    @path_to_wav.setter
    def path_to_wav(self, path_to_wav: str):
        """Set the path to the WAV file.

        Parameters
        ----------
        path_to_wav: str
            Path to the WAV file.
        """
        self.__path_to_wav = path_to_wav

    @path_to_wav.getter
    def path_to_wav(self) -> str:
        """Path to the WAV file.

        Returns
        -------
        str
            Path to the WAV file.
        """
        return self.__path_to_wav

    def process(self):
        """Load the WAV file.

        This method calls the appropriate DPF Sound operator to load the WAV file.
        """
        if self.path_to_wav == "":
            raise PyAnsysSoundException(
                "Path for loading WAV file is not specified. Use 'LoadWav.set_path'."
            )

        # Load a WAV file
        data_source_in = DataSources()

        # Create input path
        data_source_in.add_file_path(self.path_to_wav, ".wav")

        # Load WAV file and store it in a container
        self.__operator.connect(0, data_source_in)

        # Run the operator
        self.__operator.run()

        # Store output in the variable
        self._output = self.__operator.get_output(0, "fields_container")

    def get_output(self) -> FieldsContainer:
        """Get the signal loaded from the WAV file as a DPF fields container.

        Returns
        -------
        FieldsContainer
            Signal loaded from the WAV file in a DPF fields container.
        """
        if self._output == None:
            # Computing output if needed
            warnings.warn(
                PyAnsysSoundWarning(
                    "Output is not processed yet. \
                        Use the 'LoadWav.process()' method."
                )
            )

        return self._output

    def get_output_as_nparray(self) -> npt.ArrayLike:
        """Get the signal loaded from the WAV file as a NumPy array.

        Returns
        -------
        np.array
            Signal loaded from the WAV file in a NumPy array.
        """
        fc = self.get_output()

        return self.convert_fields_container_to_np_array(fc)
