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

"""Sound Composer's harmonics source with two parameters."""
import warnings

from ansys.dpf.core import Field, FieldsContainer, Operator
from matplotlib import pyplot as plt
import numpy as np

from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ._source_parent import SourceParent
from .source_control_time import SourceControlTime

ID_COMPUTE_LOAD_SOURCE_HARMONICS_2PARAMS = "sound_composer_load_source_harmonics_two_parameters"
ID_COMPUTE_GENERATE_SOUND_HARMONICS_2PARAMS = (
    "sound_composer_generate_sound_harmonics_two_parameters"
)


class SourceHarmonicsTwoParameters(SourceParent):
    """Sound Composer's harmonics source with two parameters class.

    This class creates a harmonics source with two parameters for the Sound Composer. A harmonics
    source with two parameters is used to generate a sound signal from a given harmonics source
    data and its two source controls. The harmonics source data consists of a series of orders
    whose levels depend on the values of two parameters, the first of which is always RPM. The
    source controls contain each a control parameter's values over time.
    """

    def __init__(
        self,
        file: str = "",
        source_control_rpm: SourceControlTime = None,
        source_control2: SourceControlTime = None,
    ):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        file : str, default: ""
            Path to the harmonics source with two parameters file. Supported files are text files
            with the header `AnsysSound_Orders_MultipleParameters`.
        source_control_rpm : SourceControlTime, default: None
            First Source control, consisting of the RPM values over time, to use when generating
            the sound from this source.
        source_control2 : SourceControlTime, default: None
            Second source control, consisting of the control parameter values over time, to use
            when generating the sound from this source.
        """
        super().__init__()
        self.source_control_rpm = source_control_rpm
        self.source_control2 = source_control2

        # Define DPF Sound operators.
        self.__operator_load = Operator(ID_COMPUTE_LOAD_SOURCE_HARMONICS_2PARAMS)
        self.__operator_generate = Operator(ID_COMPUTE_GENERATE_SOUND_HARMONICS_2PARAMS)

        if len(file) > 0:
            self.load_source_harmonics_two_parameters(file)
        else:
            self.source_harmonics_two_parameters = None

    def __str__(self) -> str:
        """Return the string representation of the object."""
        # Source info.
        if self.source_harmonics_two_parameters is not None:
            (
                orders,
                rpm_name,
                rpm_min_max,
                control_name,
                control_unit,
                control_min_max,
            ) = self.__extract_harmonics_two_parameters_info()

            # Source name.
            str_name = self.source_harmonics_two_parameters.name
            if str_name is None:
                str_name = ""

            # Orders.
            orders = np.round(orders, 1)
            if len(orders) > 10:
                str_order_values = f"{str(orders[:5])[:-1]} ... {str(orders[-5:])[1:]}"
            else:
                str_order_values = str(orders)

            str_source = (
                f"'{str_name}'\n"
                f"\tNumber of orders: {len(orders)}\n"
                f"\t\t{str_order_values}\n"
                f"\tControl parameter 1: {rpm_name}, "
                f"{rpm_min_max[0]} - {rpm_min_max[1]} rpm\n"
                f"\tControl parameter 2: {control_name}, "
                f"{control_min_max[0]} - {control_min_max[1]} {control_unit}"
            )
        else:
            str_source = "Not set"

        # Source control info.
        if self.is_source_control_valid():
            str_control_rpm = (
                f"{self.source_control_rpm.control.name}\n"
                f"\t\tMin: {self.source_control_rpm.control.data.min()}\n"
                f"\t\tMax: {self.source_control_rpm.control.data.max()}\n"
                f"\t\tDuration: "
                f"{self.source_control_rpm.control.time_freq_support.time_frequencies.data[-1]} s"
            )
            str_control2 = (
                f"{self.source_control2.control.name}\n"
                f"\t\tMin: {self.source_control2.control.data.min()}\n"
                f"\t\tMax: {self.source_control2.control.data.max()}\n"
                f"\t\tDuration: "
                f"{self.source_control2.control.time_freq_support.time_frequencies.data[-1]} s"
            )
        else:
            str_control_rpm = "Not set"
            str_control2 = "Not set"

        return (
            f"Harmonics source with two parameters: {str_source}\n"
            f"Source control:\n"
            f"\tControl 1: {str_control_rpm}\n"
            f"\tControl 2: {str_control2}"
        )

    @property
    def source_control_rpm(self) -> SourceControlTime:
        """First source control, that is, RPM, for harmonics source with two parameters.

        Contains the RPM values over time.
        """
        return self.__control_rpm

    @source_control_rpm.setter
    def source_control_rpm(self, control: SourceControlTime):
        """Set the source control."""
        if not (isinstance(control, SourceControlTime) or control is None):
            raise PyAnsysSoundException(
                "Specified RPM source control object must be of type SourceControlTime."
            )
        self.__control_rpm = control

    @property
    def source_control2(self) -> SourceControlTime:
        """Second source control for harmonics source with two parameters.

        Contains the second control parameter values over time.
        """
        return self.__control2

    @source_control2.setter
    def source_control2(self, control: SourceControlTime):
        """Set the source control."""
        if not (isinstance(control, SourceControlTime) or control is None):
            raise PyAnsysSoundException(
                "Specified second source control object must be of type SourceControlTime."
            )
        self.__control2 = control

    @property
    def source_harmonics_two_parameters(self) -> FieldsContainer:
        """Source data for harmonics source with two parameters.

        The harmonics source with two parameters data consists of a series of orders whose levels
        depend on the values of two parameters, the first of which is always RPM.
        """
        return self.__source_harmonics_two_parameters

    @source_harmonics_two_parameters.setter
    def source_harmonics_two_parameters(self, source: FieldsContainer):
        """Set the harmonics source with two parameters data, from a DPF fields container."""
        if source is not None:
            if not isinstance(source, FieldsContainer):
                raise PyAnsysSoundException(
                    "Specified harmonics source with two parameters must be provided as a DPF "
                    "fields container."
                )

            if (
                len(source) < 1
                or len(source[0].data) < 1
                or len(source[0].time_freq_support.time_frequencies.data) < 1
            ):
                raise PyAnsysSoundException(
                    "Specified harmonics source with two parameters must contain at least one "
                    "order level (the provided DPF fields container must contain at least one "
                    "field with at least one data point)."
                )

            for field in source:
                if len(field.data) != len(field.time_freq_support.time_frequencies.data):
                    raise PyAnsysSoundException(
                        "Each set of order levels in the specified harmonics source with two "
                        "parameters must contain as many level values as the number of orders (in "
                        "the provided DPF fields container, each field must contain the same "
                        "number of data points and support values)."
                    )

                if len(field.data) != len(source[0].data):
                    raise PyAnsysSoundException(
                        "Each set of order levels in the specified harmonics source with two "
                        "parameters must contain the same number of level values (in the provided "
                        "DPF fields container, each field must contain the same number of data "
                        "points)."
                    )

            support_data = source.get_support("control_parameter_1")
            support_properties = support_data.available_field_supported_properties()
            support1_values = support_data.field_support_by_property(support_properties[0])
            support_data = source.get_support("control_parameter_2")
            support_properties = support_data.available_field_supported_properties()
            support2_values = support_data.field_support_by_property(support_properties[0])
            if len(support1_values) != len(source) or len(support2_values) != len(source):
                raise PyAnsysSoundException(
                    "Specified harmonics source with two parameters must contain as many sets of"
                    "order levels as the number of values in both associated control parameters "
                    "(in the provided DPF fields container, the number of fields should be the "
                    "same as the number of values in both fields container supports)."
                )

        self.__source_harmonics_two_parameters = source

    def is_source_control_valid(self) -> bool:
        """Source control verification function.

        Checks if both source controls are set.

        Returns
        -------
        bool
            True if both source controls are set.
        """
        return (
            self.source_control_rpm is not None
            and self.source_control_rpm.control is not None
            and self.source_control2 is not None
            and self.source_control2.control is not None
        )

    def load_source_harmonics_two_parameters(self, file: str):
        """Load the harmonics source with two parameters data from a file.

        Parameters
        ----------
        file : str
            Path to the harmonics source with two parameters file. Supported files have the same
            text format (with the `AnsysSound_Orders_MultipleParameters` header) as that which is
            supported by Ansys Sound SAS.
        """
        # Set operator inputs.
        self.__operator_load.connect(0, file)

        # Run the operator.
        self.__operator_load.run()

        # Get the loaded sound power level parameters.
        self.source_harmonics_two_parameters = self.__operator_load.get_output(
            0, "fields_container"
        )

    def process(self, sampling_frequency: float = 44100.0):
        """Generate the sound of the harmonics source with two parameters.

        This method generates the sound of the harmonics source with two parameters, using the
        current harmonics source data and source controls.

        Parameters
        ----------
        sampling_frequency : float, default: 44100.0
            Sampling frequency of the generated sound in Hz.
        """
        if sampling_frequency <= 0.0:
            raise PyAnsysSoundException("Sampling frequency must be strictly positive.")

        if not self.is_source_control_valid():
            raise PyAnsysSoundException(
                "At least one source control for harmonics source with two parameters is not set. "
                f"Use ``{__class__.__name__}.control_rpm`` and/or "
                f"``{__class__.__name__}.control2``."
            )

        if self.source_harmonics_two_parameters is None:
            raise PyAnsysSoundException(
                "Harmonics source with two parameters data is not set. Use "
                f"``{__class__.__name__}.source_harmonics_two_parameters`` or method "
                f"``{__class__.__name__}.load_source_harmonics_two_parameters()``."
            )

        # Set operator inputs.
        self.__operator_generate.connect(0, self.source_harmonics_two_parameters)
        self.__operator_generate.connect(1, self.source_control_rpm.control)
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
            else "Signal from harmonics source with two parameters"
        )
        plt.xlabel("Time (s)")
        plt.ylabel("Amplitude (Pa)")
        plt.grid(True)
        plt.show()

    def __extract_harmonics_two_parameters_info(
        self,
    ) -> tuple[list[float], str, tuple[float], str, str, tuple[float]]:
        """Extract the harmonics source with two parameters information.

        Returns
        -------
        tuple[list[float], str, tuple[float], str, str, tuple[float]]
            Harmonics source with two parameters information, consisting of the following elements:
                First element is the list of order values.

                Second element is the RPM control name.

                Third element is the RPM control min and max values.

                Fourth element is the second control parameter name.

                Fifth element is the second control parameter unit.

                Sixth element is the second control parameter min and max values.
        """
        if self.source_harmonics_two_parameters is None:
            return ([], "", (), "", "", ())

        # Orders (same values for each field).
        orders = self.source_harmonics_two_parameters[0].time_freq_support.time_frequencies.data

        # RPM control info.
        rpm_data = self.source_harmonics_two_parameters.get_support("control_parameter_1")
        parameter_ids = rpm_data.available_field_supported_properties()
        rpm_unit = parameter_ids[0]
        rpm_name = rpm_data.field_support_by_property(rpm_unit).name
        rpm_values = rpm_data.field_support_by_property(rpm_unit).data
        rpm_min_max = (float(rpm_values.min()), float(rpm_values.max()))

        # Control parameter 2 info.
        control_data = self.source_harmonics_two_parameters.get_support("control_parameter_2")
        parameter_ids = control_data.available_field_supported_properties()
        control_unit = parameter_ids[0]
        control_name = control_data.field_support_by_property(control_unit).name
        control_values = control_data.field_support_by_property(control_unit).data
        control_min_max = (float(control_values.min()), float(control_values.max()))

        return list(orders), rpm_name, rpm_min_max, control_name, control_unit, control_min_max