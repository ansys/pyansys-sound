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

"""Sound Composer's broadband noise source with two parameters."""
import warnings

from ansys.dpf.core import Field, FieldsContainer, Operator
from matplotlib import pyplot as plt
import numpy as np

from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ._source_parent import SourceParent
from .source_control_time import SourceControlTime

ID_COMPUTE_LOAD_SOURCE_BBN_2PARAMS = "sound_composer_load_source_bbn_two_parameters"
ID_COMPUTE_GENERATE_SOUND_BBN_2PARAMS = "sound_composer_generate_sound_bbn_two_parameters"


class SourceBroadbandNoiseTwoParameters(SourceParent):
    """Sound Composer's broadband noise source with two parameters class.

    This class creates a broadband noise source with two parameters for the Sound Composer. A
    broadband noise source with two parameters is used to generate a sound signal from a given
    broadband noise and its two source controls. The broadband noise consists of a series of noise
    spectra, each corresponding to a pair of control parameter values. The source controls contain
    each a control parameter's values over time.
    """

    def __init__(
        self,
        file: str = "",
        control1: SourceControlTime = None,
        control2: SourceControlTime = None,
    ):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        file : str, default: ""
            Path to the broadband noise with two parameters file. Supported files are text files
            with the header `AnsysSound_BBN_MultipleParameters`.
        control1 : SourceControlTime, default: None
            First Source control, consisting of the control parameter values over time, to use when
            generating the sound from this source.
        control2 : SourceControlTime, default: None
            Second source control, consisting of the control parameter values over time, to use
            when generating the sound from this source.
        """
        super().__init__()
        self.source_control1 = control1
        self.source_control2 = control2

        # Define DPF Sound operators.
        self.__operator_load = Operator(ID_COMPUTE_LOAD_SOURCE_BBN_2PARAMS)
        self.__operator_generate = Operator(ID_COMPUTE_GENERATE_SOUND_BBN_2PARAMS)

        if len(file) > 0:
            self.load_source_bbn_two_parameters(file)
        else:
            self.source_bbn_two_parameters = None

    def __str__(self) -> str:
        """Return the string representation of the object."""
        # Source info.
        if self.source_bbn_two_parameters is not None:
            (
                spectrum_type,
                delta_f,
                control_name1,
                control_unit1,
                control_min_max1,
                control_name2,
                control_unit2,
                control_min_max2,
            ) = self.__extract_bbn_two_parameters_info()

            # Source name.
            str_name = self.source_bbn_two_parameters.name
            if str_name is None:
                str_name = ""

            # # Spectrum type. TODO: reactivate if/else when quantity_type is available in python.
            # if spectrum_type == "NARROWBAND":
            #     str_type = f"{spectrum_type} (DeltaF: {delta_f:.1f} Hz)"
            # else:
            #     str_type = spectrum_type
            str_type = spectrum_type

            str_source = (
                f"'{str_name}'\n"
                f"\tSpectrum type: {str_type}\n"
                f"\tSpectrum count: {len(self.source_bbn_two_parameters)}\n"
                f"\tControl parameter 1: {control_name1}, "
                f"{control_min_max1[0]}-{control_min_max1[1]} {control_unit1}\n"
                f"\tControl parameter 2: {control_name2}, "
                f"{control_min_max2[0]}-{control_min_max2[1]} {control_unit2}"
            )
        else:
            str_source = "Not set"

        # Source control info.
        if self.is_source_control_valid():
            str_source_control1 = (
                f"{self.source_control1.control.name}\n"
                f"\t\tMin: {self.source_control1.control.data.min()}\n"
                f"\t\tMax: {self.source_control1.control.data.max()}\n"
                f"\t\tDuration: "
                f"{self.source_control1.control.time_freq_support.time_frequencies.data[-1]} s"
            )
            str_source_control2 = (
                f"{self.source_control2.control.name}\n"
                f"\t\tMin: {self.source_control2.control.data.min()}\n"
                f"\t\tMax: {self.source_control2.control.data.max()}\n"
                f"\t\tDuration: "
                f"{self.source_control2.control.time_freq_support.time_frequencies.data[-1]} s"
            )
        else:
            str_source_control1 = "Not set"
            str_source_control2 = "Not set"

        return (
            f"Broadband noise source with two parameters: {str_source}\n"
            f"Source control:\n"
            f"\tControl 1: {str_source_control1}\n"
            f"\tControl 2: {str_source_control2}"
        )

    @property
    def source_control1(self) -> SourceControlTime:
        """First source control for broadband noise source with two parameters.

        Contains the first control parameter values over time.
        """
        return self.__source_control1

    @source_control1.setter
    def source_control1(self, source_control: SourceControlTime):
        """Set the source control."""
        if not (isinstance(source_control, SourceControlTime) or source_control is None):
            raise PyAnsysSoundException(
                "Specified first source control object must be of type ``SourceControlTime``."
            )
        self.__source_control1 = source_control

    @property
    def source_control2(self) -> SourceControlTime:
        """First source control for broadband noise source with two parameters.

        Contains the second control parameter values over time.
        """
        return self.__source_control2

    @source_control2.setter
    def source_control2(self, source_control: SourceControlTime):
        """Set the source control."""
        if not (isinstance(source_control, SourceControlTime) or source_control is None):
            raise PyAnsysSoundException(
                "Specified second source control object must be of type ``SourceControlTime``."
            )
        self.__source_control2 = source_control

    @property
    def source_bbn_two_parameters(self) -> FieldsContainer:
        """Source data for broadband noise source with two parameters.

        The broadband noise source with two parameters data consists of a series of spectra, each
        corresponding to a pair of control parameter values. Spectra can be narrowband, PSD,
        octave-band levels, or 1/3-octave-band levels.
        """
        return self.__source_bbn_two_parameters

    @source_bbn_two_parameters.setter
    def source_bbn_two_parameters(self, source_bbn_two_parameters: FieldsContainer):
        """Set the broadband noise source with two parameters data, from a DPF fields container."""
        if source_bbn_two_parameters is not None:
            if not isinstance(source_bbn_two_parameters, FieldsContainer):
                raise PyAnsysSoundException(
                    "Specified broadband noise source with two parameters must be provided as a "
                    "DPF fields container."
                )

            if len(source_bbn_two_parameters) < 1:
                raise PyAnsysSoundException(
                    "Specified broadband noise source with two parameters must contain at least "
                    "one spectrum."
                )

            for spectrum in source_bbn_two_parameters:
                if len(spectrum.data) < 1:
                    raise PyAnsysSoundException(
                        "Each spectrum in the specified broadband noise source with two "
                        "parameters must contain at least one element."
                    )

            support_data = source_bbn_two_parameters.get_support("control_parameter_1")
            support_properties = support_data.available_field_supported_properties()
            support_values = support_data.field_support_by_property(support_properties[0])
            if len(support_values) < 1:
                raise PyAnsysSoundException(
                    "First control data in the specified broadband noise source with two "
                    "parameters must contain at least one element."
                )

            support_data = source_bbn_two_parameters.get_support("control_parameter_2")
            support_properties = support_data.available_field_supported_properties()
            support_values = support_data.field_support_by_property(support_properties[0])
            if len(support_values) < 1:
                raise PyAnsysSoundException(
                    "Second control data in the specified broadband noise source with two "
                    "parameters must contain at least one element."
                )

        self.__source_bbn_two_parameters = source_bbn_two_parameters

    def is_source_control_valid(self) -> bool:
        """Source control verification function.

        Check if the two source controls are set.

        Returns
        -------
        bool
            True if the source control is set.
        """
        return (
            self.source_control1 is not None
            and self.source_control1.control is not None
            and self.source_control2 is not None
            and self.source_control2.control is not None
        )

    def load_source_bbn_two_parameters(self, file: str):
        """Load the broadband noise source with two parameters data from a file.

        Parameters
        ----------
        file : str
            Path to the broadband noise source with two parameters file. Supported files have the
            same text format (with the `AnsysSound_BBN_MultipleParameters` header) as that which is
            supported by Ansys Sound SAS.
        """
        # Set operator inputs.
        self.__operator_load.connect(0, file)

        # Run the operator.
        self.__operator_load.run()

        # Get the loaded sound power level parameters.
        self.source_bbn_two_parameters = self.__operator_load.get_output(0, "fields_container")

    def process(self, sampling_frequency: float = 44100.0):
        """Generate the sound of the broadband noise source with two parameters.

        This method generates the sound of the broadband noise source with two parameters, using
        the current broadband noise data and source controls.

        Parameters
        ----------
        sampling_frequency : float, default: 44100.0
            Sampling frequency of the generated sound in Hz.
        """
        if sampling_frequency <= 0.0:
            raise PyAnsysSoundException("Sampling frequency must be strictly positive.")

        if not self.is_source_control_valid():
            raise PyAnsysSoundException(
                "At least one source control for broadband noise with two parameters is not set. "
                f"Use ``{__class__.__name__}.source_control1`` and/or "
                f"``{__class__.__name__}.source_control2``."
            )

        if self.source_bbn_two_parameters is None:
            raise PyAnsysSoundException(
                "Broadband noise source with two parameters data is not set. Use "
                f"``{__class__.__name__}.source_bbn_two_parameters`` or method "
                f"``{__class__.__name__}.load_source_bbn_two_parameters()``."
            )

        # Set operator inputs.
        self.__operator_generate.connect(0, self.source_bbn_two_parameters)
        self.__operator_generate.connect(1, self.source_control1.control)
        self.__operator_generate.connect(2, self.source_control2.control)
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
            Generated sound (signal samples in Pa) as a NumPy array.
        """
        output = self.get_output()

        return np.array(output.data if output is not None else [])

    def plot(self):
        """Plot the resulting signal in a figure."""
        if self._output == None:
            raise PyAnsysSoundException(
                f"Output is not processed yet. Use the '{__class__.__name__}.process()' method."
            )
        output = self.get_output()

        time_data = output.time_freq_support.time_frequencies.data

        plt.plot(time_data, output.data)
        plt.title(
            output.name
            if len(output.name) > 0
            else "Signal from broadband noise source with two parameters"
        )
        plt.xlabel("Time (s)")
        plt.ylabel("Amplitude (Pa)")
        plt.grid(True)
        plt.show()

    def __extract_bbn_two_parameters_info(
        self,
    ) -> tuple[str, float, str, str, tuple[float], str, str, tuple[float]]:
        """Extract the broadband noise source with two parameters information.

        Returns
        -------
        tuple[str, float, str, str, tuple[float], str, str, tuple[float]]
            Broadband noise source with two parameters information, consisting of the following
            elements:
                First element is the spectrum type ('NARROWBAND', 'OCTAVE1:1', or 'OCTAVE1:3').

                Second element is the spectrum frequency resolution in Hz (only if spectrum type is
                'NARROWBAND', 0.0 otherwise).

                Third element is the first control parameter name.

                Sixth element is the first control parameter unit.

                Seventh element is the first control parameter min and max values in a tuple.

                Eighth element is the second control parameter name.

                Ninth element is the second control parameter unit.

                Tenth element is the second control parameter min and max values in a tuple.

        """
        if self.source_bbn_two_parameters is None:
            return ("", 0.0, "", "", (), "", "", ())

        # Spectrum info.
        # TODO: for now quantity_type can't be accessed in python. When it is, the line below
        # should be uncommented, and replace the one after.
        # type = self.source_bbn[0].field_definition.quantity_type
        type = "Not available"
        frequencies = self.source_bbn_two_parameters[0].time_freq_support.time_frequencies.data
        if len(frequencies) > 1:
            delta_f = frequencies[1] - frequencies[0]
        else:
            delta_f = 0.0

        # Control parameter 1 info.
        control_data = self.source_bbn_two_parameters.get_support("control_parameter_1")
        parameter_ids = control_data.available_field_supported_properties()
        unit1 = parameter_ids[0]
        name1 = control_data.field_support_by_property(unit1).name
        values = control_data.field_support_by_property(unit1).data
        min_max1 = (float(values.min()), float(values.max()))

        # Control parameter 2 info.
        control_data = self.source_bbn_two_parameters.get_support("control_parameter_2")
        parameter_ids = control_data.available_field_supported_properties()
        unit2 = parameter_ids[0]
        name2 = control_data.field_support_by_property(unit2).name
        values = control_data.field_support_by_property(unit2).data
        min_max2 = (float(values.min()), float(values.max()))

        return type, delta_f, name1, unit1, min_max1, name2, unit2, min_max2
