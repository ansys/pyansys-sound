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

"""Load Wav."""

import warnings

from ansys.dpf.core import DataSources, FieldsContainer, Operator
from numpy import typing as npt

from . import SignalUtilitiesParent
from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning


class LoadWav(SignalUtilitiesParent):
    """Load wav.

    This class loads wav signals.
    """

    def __init__(self, path_to_wav: str = ""):
        """Create a load wav class.

        Parameters
        ----------
        path_to_wav:
            Path to the wav file to load.
            Can be set during the instantiation of the object or with LoadWav.set_path().
        """
        super().__init__()
        self.path_to_wav = path_to_wav
        self.__operator = Operator("load_wav_sas")

    @property
    def path_to_wav(self):
        """Path to wav property."""
        return self.__path_to_wav  # pragma: no cover

    @path_to_wav.setter
    def path_to_wav(self, path_to_wav: str):
        """Set the path of the wav to load.

        Parameters
        ----------
        path_to_wav:
            Path to the wav file to load.
        """
        self.__path_to_wav = path_to_wav

    @path_to_wav.getter
    def path_to_wav(self) -> str:
        """Get the path of the wav to load.

        Returns
        -------
        str
                The path to the wav to load.
        """
        return self.__path_to_wav

    def process(self):
        """Load the wav file.

        Calls the appropriate DPF Sound operator to load the wav file.
        """
        if self.path_to_wav == "":
            raise PyAnsysSoundException(
                "Path for loading wav file is not specified. Use LoadWav.set_path."
            )

        # Loading a WAV file
        data_source_in = DataSources()

        # Creating input path
        data_source_in.add_file_path(self.path_to_wav, ".wav")

        # Loading wav file and storing it into a container
        self.__operator.connect(0, data_source_in)

        # Runs the operator
        self.__operator.run()

        # Stores output in the variable
        self._output = self.__operator.get_output(0, "fields_container")

    def get_output(self) -> FieldsContainer:
        """Return the loaded wav signal as a fields container.

        Returns
        -------
        FieldsContainer
                The loaded wav signal in a dpf.FieldsContainer.
        """
        if self._output == None:
            # Computing output if needed
            warnings.warn(
                PyAnsysSoundWarning("Output has not been yet processed, use LoadWav.process().")
            )

        return self._output

    def get_output_as_nparray(self) -> npt.ArrayLike:
        """Return the loaded wav signal as a numpy array.

        Returns
        -------
        np.array
                The loaded wav signal in a numpy array.
        """
        fc = self.get_output()

        return self.convert_fields_container_to_np_array(fc)
