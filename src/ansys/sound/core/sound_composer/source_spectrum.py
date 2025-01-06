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

"""Sound Composer's spectrum source."""
import warnings

from ansys.dpf.core import Field, GenericDataContainer, Operator
from matplotlib import pyplot as plt
import numpy as np

from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ._source_parent import SourceParent
from .source_control_spectrum import SourceControlSpectrum

ID_COMPUTE_LOAD_SOURCE_SPECTRUM = "sound_composer_load_source_spectrum"
ID_COMPUTE_GENERATE_SOUND_SPECTRUM = "sound_composer_generate_sound_spectrum"


class SourceSpectrum(SourceParent):
    """Sound Composer's spectrum source class.

    This class creates a spectrum source for the Sound Composer. A spectrum source is used to
    generate a sound signal from a given spectrum and its source control. The source control
    contains the duration of the sound and the method used to generate it.
    """

    def __init__(self, file_source: str = "", source_control: SourceControlSpectrum = None):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        file_source : str, default: ""
            Path to the spectrum file.
        source_control : SourceControlSpectrum, default: None
            Source control to use when generating the sound from this source.
        """
        super().__init__()
        self.source_control = source_control

        # Define DPF Sound operators.
        self.__operator_load = Operator(ID_COMPUTE_LOAD_SOURCE_SPECTRUM)
        self.__operator_generate = Operator(ID_COMPUTE_GENERATE_SOUND_SPECTRUM)

        # load_source_spectrum can only be called after __operator_load is defined.
        if len(file_source) > 0:
            self.load_source_spectrum(file_source)
        else:
            self.source_spectrum_data = None

    def __str__(self) -> str:
        """Return the string representation of the object."""
        if self.source_spectrum_data is not None:
            support_data = self.source_spectrum_data.time_freq_support.time_frequencies.data

            if len(support_data) < 2:
                str_deltaf = "N/A"
            else:
                str_deltaf = f"{support_data[1] - support_data[0]:.1f} Hz"

            str_source = (
                f"'{self.source_spectrum_data.name}'\n"
                f"\tFmax: {support_data[-1]:.0f} Hz\n"
                f"\tDeltaF: {str_deltaf}"
            )
        else:
            str_source = "Not set"

        if self.is_source_control_valid():
            str_source_control = (
                f"{self.source_control.get_method_name()}, {self.source_control.duration} s"
            )
        else:
            str_source_control = "Not set/valid"

        return f"Spectrum source: {str_source}\nSource control: {str_source_control}"

    @property
    def source_control(self) -> SourceControlSpectrum:
        """Spectrum source control object.

        Contains the duration in seconds, and the method used to generate the sound.
        """
        return self.__source_control

    @source_control.setter
    def source_control(self, source_control: SourceControlSpectrum):
        """Set the spectrum source control."""
        if not (isinstance(source_control, SourceControlSpectrum) or source_control is None):
            raise PyAnsysSoundException(
                "Specified source control object must be of type ``SourceControlSpectrum``."
            )
        self.__source_control = source_control

    @property
    def source_spectrum_data(self) -> Field:
        """Spectrum source data, as a DPF field.

        Power spectral density (PSD) as a DPF field, which contains the frequencies in Hz and
        the levels in unit^2/Hz (for example Pa^2/Hz).
        """
        return self.__source_spectrum_data

    @source_spectrum_data.setter
    def source_spectrum_data(self, source_spectrum_data: Field):
        """Set the spectrum source data, from a DPF field."""
        if source_spectrum_data is not None:
            if not isinstance(source_spectrum_data, Field):
                raise PyAnsysSoundException(
                    "Specified spectrum source must be provided as a DPF field."
                )

            support_data = source_spectrum_data.time_freq_support.time_frequencies.data
            if len(source_spectrum_data.data) < 1 or len(support_data) < 1:
                raise PyAnsysSoundException(
                    "Specified spectrum source must contain at least one element."
                )

        self.__source_spectrum_data = source_spectrum_data

    def is_source_control_valid(self) -> bool:
        """Source control verification function.

        Check if the source control is set and its duration is strictly positive.

        Returns
        -------
        bool
            True if the source control is set and its duration is strictly positive, False
            otherwise.
        """
        return (self.source_control is not None) and (self.source_control.duration > 0.0)

    def load_source_spectrum(self, file_source: str):
        """Load the spectrum source data from a spectrum file.

        Parameters
        ----------
        file_source : str
            Path to the spectrum file. Supported files are the same XML and text (with the
            AnsysSound_Spectrum header) formats as supported by Ansys Sound SAS.
        """
        # Set operator inputs.
        self.__operator_load.connect(0, file_source)

        # Run the operator.
        self.__operator_load.run()

        # Get the loaded sound power level parameters.
        self.source_spectrum_data = self.__operator_load.get_output(0, "field")

    def set_from_generic_data_containers(
        self,
        gdc_source: GenericDataContainer,
        gdc_source_control: GenericDataContainer,
    ):
        """Set the source and source control data from generic data containers.

        This method is meant to set the source data from generic data containers obtained when
        loading a Sound Composer project file (.scn).

        Parameters
        ----------
        gdc_source : GenericDataContainer
            Source data as a DPF generic data container.
        gdc_source_control : GenericDataContainer
            Source control data as a DPF generic data container.
        """
        self.source_spectrum_data = gdc_source.get_property("sound_composer_source")
        duration = gdc_source_control.get_property(
            "sound_composer_source_control_spectrum_duration"
        )
        method = gdc_source_control.get_property("sound_composer_source_control_spectrum_method")
        self.source_control = SourceControlSpectrum(duration=duration, method=method)

    def get_as_generic_data_containers(self) -> tuple[GenericDataContainer]:
        """Get the source and source control data as generic data containers.

        This method is meant to return the source data as generic data containers needed to save a
        Sound Composer project file (.scn).

        Returns
        -------
        tuple[GenericDataContainer]
            Source as two generic data containers, respectively for source and source control data.
        """
        if self.source_spectrum_data is None:
            warnings.warn(
                PyAnsysSoundWarning(
                    "Cannot create source generic data container because there is no source data."
                )
            )
            source_container = None
        else:
            source_container = GenericDataContainer()
            source_container.set_property("sound_composer_source", self.source_spectrum_data)

        if not self.is_source_control_valid():
            warnings.warn(
                PyAnsysSoundWarning(
                    "Cannot create source control generic data container because there is no "
                    "source control data."
                )
            )
            source_control_container = None
        else:
            source_control_container = GenericDataContainer()
            source_control_container.set_property(
                "sound_composer_source_control_spectrum_duration", self.source_control.duration
            )
            source_control_container.set_property(
                "sound_composer_source_control_spectrum_method", self.source_control.method
            )

        return (source_container, source_control_container)

    def process(self, sampling_frequency: float = 44100.0):
        """Generate the sound of the spectrum source, using the current spectrum and source control.

        Parameters
        ----------
        sampling_frequency : float, default: 44100.0
            Sampling frequency of the generated sound in Hz.
        """
        if sampling_frequency <= 0.0:
            raise PyAnsysSoundException("Sampling frequency must be strictly positive.")

        if not self.is_source_control_valid():
            raise PyAnsysSoundException(
                "Spectrum source control is not valid. Either it is not set "
                f"(use ``{__class__.__name__}.source_control``) "
                "or its duration is not strictly positive "
                f"(use ``{__class__.__name__}.source_control.duration``)."
            )

        if self.source_spectrum_data is None:
            raise PyAnsysSoundException(
                f"Source spectrum is not set. Use ``{__class__.__name__}.source_spectrum_data`` "
                f"or method ``{__class__.__name__}.load_source_spectrum()``."
            )

        # Set operator inputs.
        self.__operator_generate.connect(0, self.source_spectrum_data)
        self.__operator_generate.connect(1, self.source_control.duration)
        self.__operator_generate.connect(2, self.source_control.get_method_name())
        self.__operator_generate.connect(3, sampling_frequency)

        # Run the operator.
        self.__operator_generate.run()

        # Get the loaded sound power level parameters.
        self._output = self.__operator_generate.get_output(0, "field")

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
        """Plot the resulting signal in a figure."""
        if self._output == None:
            raise PyAnsysSoundException(
                f"Output is not processed yet. Use the '{__class__.__name__}.process()' method."
            )
        output = self.get_output()

        time_data = output.time_freq_support.time_frequencies.data

        plt.plot(time_data, output.data)
        plt.title(output.name if len(output.name) > 0 else "Signal from spectrum source")
        plt.xlabel("Time (s)")
        plt.ylabel("Amplitude (Pa)")
        plt.grid(True)
        plt.show()
