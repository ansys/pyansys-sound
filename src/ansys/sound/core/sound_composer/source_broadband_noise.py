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

"""Sound Composer's broadband noise source."""

import warnings

from ansys.dpf.core import Field, FieldsContainer, GenericDataContainer, Operator
from matplotlib import pyplot as plt
import numpy as np

from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ._source_parent import SourceParent
from .source_control_time import SourceControlTime

ID_COMPUTE_LOAD_SOURCE_BBN = "sound_composer_load_source_bbn"
ID_COMPUTE_GENERATE_SOUND_BBN = "sound_composer_generate_sound_bbn"


class SourceBroadbandNoise(SourceParent):
    """Sound Composer's broadband noise source class.

    This class creates a broadband noise source for the Sound Composer. A broadband noise source is
    used to generate a sound signal from broadband noise source data and one source control.

    The broadband noise source data consists of a series of noise spectra, each corresponding to a
    control parameter value.

    The source control contains the control parameter values over time.

    .. seealso::
        :class:`SoundComposer`, :class:`Track`, :class:`SourceControlTime`,
        :class:`SourceBroadbandNoiseTwoParameters`

    Examples
    --------
    Create a broadband noise source from a source data file and a source control, and display the
    generated signal.

    >>> from ansys.sound.core.sound_composer import SourceBroadbandNoise
    >>> bbn_source = SourceBroadbandNoise(
    ...     file="path/to/source_data.txt",
    ...     source_control=source_control_time
    ... )
    >>> bbn_source.process(sampling_frequency=48000.0)
    >>> bbn_source.plot()

    .. seealso::
        :ref:`sound_composer_create_project`
            Example demonstrating how to create a Sound Composer project from scratch.
    """

    def __init__(self, file: str = "", source_control: SourceControlTime = None):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        file : str, default: ""
            Path to the broadband noise file. Supported files are text files with the header
            `AnsysSound_BBN`.
        source_control : SourceControlTime, default: None
            Source control, consisting of the control parameter values over time to use when
            generating the sound from this source.
        """
        super().__init__()
        self.source_control = source_control

        # Define DPF Sound operators.
        self.__operator_load = Operator(ID_COMPUTE_LOAD_SOURCE_BBN)
        self.__operator_generate = Operator(ID_COMPUTE_GENERATE_SOUND_BBN)

        if len(file) > 0:
            self.load_source_bbn(file)
        else:
            self.source_bbn = None

    def __str__(self) -> str:
        """Return the string representation of the object."""
        # Source info.
        if self.source_bbn is not None:
            spectrum_type, delta_f, control_name, control_unit, control_values = (
                self.__extract_bbn_info()
            )

            # Source name.
            str_name = self.source_bbn.name
            if str_name is None:
                str_name = ""

            # Spectrum type.
            if spectrum_type == "Narrow band":
                str_type = f"{spectrum_type} (DeltaF: {delta_f:.1f} Hz)"
            else:
                str_type = spectrum_type

            # Spectrum control values.
            control_values = np.round(control_values, 1)
            if len(control_values) > 10:
                str_values = f"{str(control_values[:5])[:-1]} ... {str(control_values[-5:])[1:]}"
            else:
                str_values = str(control_values)

            str_source = (
                f"'{str_name}'\n"
                f"\tSpectrum type: {str_type}\n"
                f"\tSpectrum count: {len(self.source_bbn)}\n"
                f"\tControl parameter: {control_name}, {control_unit}\n"
                f"\t\t{str_values}"
            )
        else:
            str_source = "Not set"

        # Source control info.
        if self.is_source_control_valid():
            control = self.source_control.control
            time = control.time_freq_support.time_frequencies
            str_source_control = (
                f"{control.name}\n"
                f"\tMin: {control.data.min()} {control.unit}\n"
                f"\tMax: {control.data.max()} {control.unit}\n"
                f"\tDuration: {time.data[-1]} {time.unit}"
            )
        else:
            str_source_control = "Not set"

        return f"Broadband noise source: {str_source}\nSource control: {str_source_control}"

    @property
    def source_control(self) -> SourceControlTime:
        """Source control of the broadband noise source.

        Contains the control parameter values over time.
        """
        return self.__source_control

    @source_control.setter
    def source_control(self, source_control: SourceControlTime):
        """Set the source control."""
        if not (isinstance(source_control, SourceControlTime) or source_control is None):
            raise PyAnsysSoundException(
                "Specified source control object must be of type ``SourceControlTime``."
            )
        self.__source_control = source_control

    @property
    def source_bbn(self) -> FieldsContainer:
        """Source data of the broadband noise source.

        The broadband noise source data consists of a series of spectra, each corresponding to a
        control parameter value.

        Each field contains the level over frequency of the noise at a given value of the control
        parameter. Level over frequency may be specified as a power spectral density (PSD) in
        Pa^2/Hz, as octave-band levels in Pa^2, or as 1/3-octave-band levels in Pa^2. The unit must
        be indicated in each field's unit. The type of data ('Narrow band', 'Octave', or
        'Third octave') must be indicated in the field's FieldDefinition attribute, as a
        quantity type.

        The control parameter values corresponding to each spectrum must be stored in the fields
        container's support named "control_parameter_1".
        """
        return self.__source_bbn

    @source_bbn.setter
    def source_bbn(self, source_bbn: FieldsContainer):
        """Set the broadband noise source data, from a DPF fields container."""
        if source_bbn is not None:
            if not isinstance(source_bbn, FieldsContainer):
                raise PyAnsysSoundException(
                    "Specified broadband noise source must be provided as a DPF fields container."
                )

            if len(source_bbn) < 1:
                raise PyAnsysSoundException(
                    "Specified broadband noise source must contain at least one spectrum."
                )

            for spectrum in source_bbn:
                if len(spectrum.data) < 1:
                    raise PyAnsysSoundException(
                        "Each spectrum in the specified broadband noise source must contain at "
                        "least one element."
                    )

            support_data = source_bbn.get_support("control_parameter_1")
            support_properties = support_data.available_field_supported_properties()
            support_values = support_data.field_support_by_property(support_properties[0])
            if len(support_values) != len(source_bbn):
                raise PyAnsysSoundException(
                    "Broadband noise source must contain as many spectra as the number of values "
                    "in the associated control parameter (in the provided DPF fields container, "
                    "the number of fields should be the same as the number of values in the fields "
                    "container support)."
                )

        self.__source_bbn = source_bbn

    def is_source_control_valid(self) -> bool:
        """Source control verification function.

        Check if the source control is set.

        Returns
        -------
        bool
            True if the source control is set.
        """
        return self.source_control is not None and self.source_control.control is not None

    def load_source_bbn(self, file: str):
        """Load the broadband noise source data from a file.

        Parameters
        ----------
        file : str
            Path to the broadband noise source file. Supported files have the same text format
            (with the `AnsysSound_BBN` header) as supported by Ansys Sound SAS.
        """
        # Set operator inputs.
        self.__operator_load.connect(0, file)

        # Run the operator.
        self.__operator_load.run()

        # Get the loaded sound power level parameters.
        self.source_bbn = self.__operator_load.get_output(0, "fields_container")

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
            Source control data as a DPF generic data container.
        """
        self.source_bbn = source_data.get_property("sound_composer_source")
        self.source_control = SourceControlTime()
        control = source_control_data.get_property("sound_composer_source_control_one_parameter")
        self.source_control.control = control
        self.source_control.description = source_control_data.get_property(
            "sound_composer_source_control_one_parameter_displayed_string"
        )

    def get_as_generic_data_containers(self) -> tuple[GenericDataContainer]:
        """Get the source and source control data as generic data containers.

        This method is meant to return the source data as generic data containers, in the format
        needed to save a Sound Composer project file (.scn) with the method
        :meth:`SoundComposer.save()`.

        Returns
        -------
        tuple[GenericDataContainer]
            Source as two generic data containers, for source and source control data, respectively.
        """
        if self.source_bbn is None:
            warnings.warn(
                PyAnsysSoundWarning(
                    "Cannot create source generic data container because there is no source data."
                )
            )
            source_data = None
        else:
            source_data = GenericDataContainer()
            source_data.set_property("sound_composer_source", self.source_bbn)

        if not self.is_source_control_valid():
            warnings.warn(
                PyAnsysSoundWarning(
                    "Cannot create source control generic data container because there is no "
                    "source control data."
                )
            )
            source_control_data = None
        else:
            source_control_data = GenericDataContainer()
            source_control_data.set_property(
                "sound_composer_source_control_one_parameter", self.source_control.control
            )
            source_control_data.set_property(
                "sound_composer_source_control_one_parameter_displayed_string",
                self.source_control.description,
            )

        return (source_data, source_control_data)

    def process(self, sampling_frequency: float = 44100.0):
        """Generate the sound of the broadband noise source.

        This method generates the sound of the broadband noise source, using the current broadband
        noise data and source control.

        Parameters
        ----------
        sampling_frequency : float, default: 44100.0
            Sampling frequency of the generated sound in Hz.
        """
        if sampling_frequency <= 0.0:
            raise PyAnsysSoundException("Sampling frequency must be strictly positive.")

        if not self.is_source_control_valid():
            raise PyAnsysSoundException(
                "Broadband noise source control is not set. "
                f"Use ``{__class__.__name__}.source_control``."
            )

        if self.source_bbn is None:
            raise PyAnsysSoundException(
                f"Broadband noise source data is not set. Use ``{__class__.__name__}.source_bbn`` "
                f"or method ``{__class__.__name__}.load_source_bbn()``."
            )

        # Set operator inputs.
        self.__operator_generate.connect(0, self.source_bbn)
        self.__operator_generate.connect(1, self.source_control.control)
        self.__operator_generate.connect(2, sampling_frequency)

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
            Generated sound (signal samples in Pa) as a NumPy array.
        """
        output = self.get_output()

        return np.array(output.data if output is not None else [])

    def plot(self):
        """Plot the resulting signal."""
        if self._output == None:
            raise PyAnsysSoundException(
                f"Output is not processed yet. Use the '{__class__.__name__}.process()' method."
            )
        output = self.get_output()

        time = output.time_freq_support.time_frequencies

        plt.plot(time.data, output.data)
        plt.title(output.name if len(output.name) > 0 else "Signal from broadband noise source")
        plt.xlabel(f"Time ({time.unit})")
        plt.ylabel(f"Amplitude ({output.unit})")
        plt.grid(True)
        plt.show()

    def plot_control(self):
        """Plot the source control."""
        if not self.is_source_control_valid():
            raise PyAnsysSoundException(
                "Broadband noise source control is not set. "
                f"Use ``{__class__.__name__}.source_control``."
            )

        control = self.source_control.control
        time = control.time_freq_support.time_frequencies
        unit_str = f" ({control.unit})" if len(control.unit) > 0 else ""
        name_str = control.name if len(control.name) > 0 else "Amplitude"
        plt.plot(time.data, control.data)
        plt.title("Control profile 1")
        plt.ylabel(f"{name_str}{unit_str}")
        plt.xlabel(f"Time ({time.unit})")
        plt.grid(True)

        plt.tight_layout()
        plt.show()

    def __extract_bbn_info(self) -> tuple[str, float, str, str, list[float]]:
        """Extract the broadband noise source information.

        Returns
        -------
        tuple[str, float, str, str, list[float]]
            Broadband noise source information, consisting of the following elements:
                -   First element: spectrum type ('Narrow band', 'Octave', or 'Third octave').

                -   Second element: spectrum frequency resolution in Hz (only if spectrum type is
                    'Narrow band', 0.0 otherwise).

                -   Third element: name of the control parameter.

                -   Fourth element: unit of the control parameter.

                -   Fifth element: list of control parameter values.
        """
        if self.source_bbn is None:
            return ("", 0.0, "", "", [])

        # Spectrum info.
        spectrum_support = self.source_bbn[0].time_freq_support
        spectrum_type: str = spectrum_support.time_frequencies.field_definition.quantity_types[0]
        spectrum_type = spectrum_type.replace("_", " ").capitalize()
        frequencies = self.source_bbn[0].time_freq_support.time_frequencies.data
        if len(frequencies) > 1:
            delta_f = frequencies[1] - frequencies[0]
        else:
            delta_f = 0.0

        # Control parameter info.
        support_ids = list(self.source_bbn.get_label_space(0).keys())
        control_data = self.source_bbn.get_support(support_ids[0])
        parameter_ids = control_data.available_field_supported_properties()
        control_unit = parameter_ids[0]
        control_name = control_data.field_support_by_property(control_unit).name
        control_values = list(control_data.field_support_by_property(control_unit).data)

        return spectrum_type, delta_f, control_name, control_unit, control_values
