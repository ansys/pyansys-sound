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

"""Sound Composer's harmonics source with two parameters."""
import warnings

from ansys.dpf.core import Field, FieldsContainer, GenericDataContainer, Operator
from matplotlib import pyplot as plt
import numpy as np

from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ..data_management import HarmonicsSource
from ._source_parent import SourceParent
from .source_control_time import SourceControlTime

ID_COMPUTE_LOAD_SOURCE_HARMONICS_2PARAMS = "sound_composer_load_source_harmonics_two_parameters"
ID_COMPUTE_GENERATE_SOUND_HARMONICS_2PARAMS = (
    "sound_composer_generate_sound_harmonics_two_parameters"
)


class SourceHarmonicsTwoParameters(SourceParent):
    """Sound Composer's harmonics source with two parameters class.

    This class creates a harmonics source with two parameters for the Sound Composer. A harmonics
    source with two parameters is used to generate a sound signal from harmonics source data and
    two source controls.

    The harmonics source data consists of a series of orders whose levels depend on the values of
    two control parameters.

    Each of the two source controls contains one control parameter's values over time.

    .. note::
        The first control parameter must correspond to RPM over time.
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
            with the header `AnsysSound_Orders_MultipleParameters` and should be created using
            Ansys Sound SAS.
        source_control_rpm : SourceControlTime, default: None
            First source control, consisting of the RPM values over time, to use when generating
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
            # Source name.
            str_name = self.source_harmonics_two_parameters.name
            if str_name is None:
                str_name = ""

            # Orders.
            orders = np.round(self.source_harmonics_two_parameters.orders, 1)
            if len(orders) > 10:
                str_order_values = f"{str(orders[:5])[:-1]} ... {str(orders[-5:])[1:]}"
            else:
                str_order_values = str(orders)

            str_source = (
                f"'{str_name}'\n"
                f"\tNumber of orders: {len(orders)}\n"
                f"\t\t{str_order_values}\n"
                f"\tControl parameter 1: {self.source_harmonics_two_parameters.control_names[0]}, "
                f"{self.source_harmonics_two_parameters.control_mins[0]} - "
                f"{self.source_harmonics_two_parameters.control_maxs[0]} rpm\n"
                f"\tControl parameter 2: {self.source_harmonics_two_parameters.control_names[1]}, "
                f"{self.source_harmonics_two_parameters.control_mins[1]} - "
                f"{self.source_harmonics_two_parameters.control_maxs[1]} "
                f"{self.source_harmonics_two_parameters.control_units[1]}"
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
        """First source control (must be RPM) for the harmonics source with two parameters.

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
        """Second source control for the harmonics source with two parameters.

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
    def source_harmonics_two_parameters(self) -> HarmonicsSource:
        """Source data for the harmonics source with two parameters.

        The harmonics source with two parameters data consists of a series of orders whose levels
        depend on the values of two parameters, the first of which is always RPM. Levels must be
        specified in unit^2 (for example Pa^2/Hz).
        """
        return self.__source_harmonics_two_parameters

    @source_harmonics_two_parameters.setter
    def source_harmonics_two_parameters(self, source: HarmonicsSource):
        """Set the harmonics source with two parameters data."""
        if source is not None:
            if not isinstance(source, FieldsContainer):
                raise PyAnsysSoundException(
                    "Specified harmonics source with two parameters must be provided as a DPF "
                    "fields container."
                )
        if type(source) is FieldsContainer:
            # convert to HarmonicsSource to make sure necessary checks are done
            source = HarmonicsSource.create(source)

        # shape tests npw handled in HarmonicsSource class

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
            text format (with the `AnsysSound_Orders_MultipleParameters` header) as supported by
            Ansys Sound SAS.
        """
        # Set operator inputs.
        self.__operator_load.connect(0, file)

        # Run the operator.
        self.__operator_load.run()

        # Get the loaded sound power level parameters.
        tmp = self.__operator_load.get_output(0, "fields_container")
        self.source_harmonics_two_parameters = HarmonicsSource.create(tmp)

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
        self.source_harmonics_two_parameters = HarmonicsSource.create_from_generic_data_container(
            source_data
        )
        control = source_control_data.get_property("sound_composer_source_control_parameter_1")
        self.source_control_rpm = SourceControlTime()
        self.source_control_rpm.control = control
        self.source_control_rpm.description = source_control_data.get_property(
            "sound_composer_source_control_two_parameter_displayed_string1"
        )
        control = source_control_data.get_property("sound_composer_source_control_parameter_2")
        self.source_control2 = SourceControlTime()
        self.source_control2.control = control
        self.source_control2.description = source_control_data.get_property(
            "sound_composer_source_control_two_parameter_displayed_string2"
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
        if self.source_harmonics_two_parameters is None:
            warnings.warn(
                PyAnsysSoundWarning(
                    "Cannot create source generic data container because there is no source data."
                )
            )
            source_data = None
        else:
            source_data = self.source_harmonics_two_parameters.get_as_generic_data_containers()

        if not self.is_source_control_valid():
            warnings.warn(
                PyAnsysSoundWarning(
                    "Cannot create source control generic data container because at least one "
                    "source control data is missing."
                )
            )
            source_control_data = None
        else:
            source_control_data = GenericDataContainer()
            source_control_data.set_property(
                "sound_composer_source_control_parameter_1", self.source_control_rpm.control
            )
            source_control_data.set_property(
                "sound_composer_source_control_parameter_2", self.source_control2.control
            )
            source_control_data.set_property(
                "sound_composer_source_control_two_parameter_displayed_string1",
                self.source_control_rpm.description,
            )
            source_control_data.set_property(
                "sound_composer_source_control_two_parameter_displayed_string2",
                self.source_control2.description,
            )

        return (source_data, source_control_data)

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
                f"Use ``{__class__.__name__}.source_control_rpm`` and/or "
                f"``{__class__.__name__}.source_control2``."
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
        """Plot the resulting signal."""
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

    def plot_control(self):
        """Plot the source controls."""
        if not self.is_source_control_valid():
            raise PyAnsysSoundException(
                "At least one source control for harmonics source with two parameters is not set. "
                f"Use ``{__class__.__name__}.source_control_rpm`` and/or "
                f"``{__class__.__name__}.source_control2``."
            )

        _, axes = plt.subplots(2, 1, sharex=True)

        data = self.source_control_rpm.control.data
        time = self.source_control_rpm.control.time_freq_support.time_frequencies.data
        unit = self.source_control_rpm.control.unit
        name = self.source_control_rpm.control.name
        unit_str = f" ({unit})" if len(unit) > 0 else ""
        name_str = name if len(name) > 0 else "Amplitude"
        axes[0].plot(time, data)
        axes[0].set_title("Control profile 1")
        axes[0].set_ylabel(f"{name_str}{unit_str}")
        axes[0].grid(True)

        data = self.source_control2.control.data
        time = self.source_control2.control.time_freq_support.time_frequencies.data
        unit = self.source_control2.control.unit
        name = self.source_control2.control.name
        unit_str = f" ({unit})" if len(unit) > 0 else ""
        name_str = name if len(name) > 0 else "Amplitude"
        axes[1].plot(time, data)
        axes[1].set_title("Control profile 2")
        axes[1].set_ylabel(f"{name_str}{unit_str}")
        axes[1].set_xlabel("Time (s)")
        axes[1].grid(True)

        plt.tight_layout()
        plt.show()
