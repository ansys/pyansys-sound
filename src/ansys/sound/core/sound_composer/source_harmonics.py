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

"""Sound Composer's harmonics source."""

import warnings

from ansys.dpf.core import Field, FieldsContainer, GenericDataContainer, Operator
from matplotlib import pyplot as plt
import numpy as np

from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ._source_parent import SourceParent
from .source_control_time import SourceControlTime

ID_COMPUTE_LOAD_SOURCE_HARMONICS = "sound_composer_load_source_harmonics"
ID_COMPUTE_GENERATE_SOUND_HARMONICS = "sound_composer_generate_sound_harmonics"


class SourceHarmonics(SourceParent):
    """Sound Composer's harmonics source class.

    This class creates a harmonics source for the Sound Composer. A harmonics source is used to
    generate a sound signal from harmonics source data and one source control.

    The harmonics source data consists of a series of orders whose levels depend on RPM.

    The source control contains the RPM values over time.

    .. seealso::
        :class:`SoundComposer`, :class:`Track`, :class:`SourceControlTime`,
        :class:`SourceHarmonicsTwoParameters`

    Examples
    --------
    Create a harmonics source from a source data file and a source control, and display the
    generated signal.

    >>> from ansys.sound.core.sound_composer import SourceHarmonics
    >>> harmonics_source = SourceHarmonics(
    ...     file="path/to/source_data.txt",
    ...     source_control=source_control_time
    ... )
    >>> harmonics_source.process(sampling_frequency=48000.0)
    >>> harmonics_source.plot()

    .. seealso::
        :ref:`sound_composer_create_project`
            Example demonstrating how to create a Sound Composer project from scratch.
    """

    def __init__(self, file: str = "", source_control: SourceControlTime = None):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        file : str, default: ""
            Path to the harmonics source data file. Supported files are the same XML and text (with
            the header `AnsysSound_Orders`) formats as supported by Ansys Sound SAS.
        source_control : SourceControlTime, default: None
            Source control, consisting of the RPM values over time, to use when generating the
            sound from this source.
        """
        super().__init__()
        self.source_control = source_control

        # Define DPF Sound operators.
        self.__operator_load = Operator(ID_COMPUTE_LOAD_SOURCE_HARMONICS)
        self.__operator_generate = Operator(ID_COMPUTE_GENERATE_SOUND_HARMONICS)

        if len(file) > 0:
            self.load_source_harmonics(file)
        else:
            self.source_harmonics = None

    def __str__(self) -> str:
        """Return the string representation of the object."""
        # Source info.
        if self.source_harmonics is not None:
            orders, control_name, control_values = self.__extract_harmonics_info()

            # Source name.
            str_name = self.source_harmonics.name
            if str_name is None:
                str_name = ""

            # Orders.
            orders = np.round(orders, 1)
            if len(orders) > 10:
                str_order_values = f"{str(orders[:5])[:-1]} ... {str(orders[-5:])[1:]}"
            else:
                str_order_values = str(orders)

            # Order control values.
            control_values = np.round(control_values, 1)
            if len(control_values) > 10:
                str_control_values = (
                    f"{str(control_values[:5])[:-1]} ... {str(control_values[-5:])[1:]}"
                )
            else:
                str_control_values = str(control_values)

            str_source = (
                f"'{str_name}'\n"
                f"\tNumber of orders: {len(orders)}\n"
                f"\t\t{str_order_values}\n"
                f"\tControl parameter: {control_name}, "
                f"{np.round(np.min(control_values), 1)} - "
                f"{np.round(np.max(control_values), 1)} rpm\n"
                f"\t\t{str_control_values}"
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
            str_source_control = "Not set/valid"

        return f"Harmonics source: {str_source}\nSource control: {str_source_control}"

    @property
    def source_control(self) -> SourceControlTime:
        """Source control for the harmonics source.

        Contains the control parameter (RPM) values over time.
        """
        return self.__source_control

    @source_control.setter
    def source_control(self, source_control: SourceControlTime):
        """Set the source control."""
        if not (isinstance(source_control, SourceControlTime) or source_control is None):
            raise PyAnsysSoundException(
                "Specified source control object must be of type SourceControlTime."
            )
        self.__source_control = source_control

    @property
    def source_harmonics(self) -> FieldsContainer:
        """Source data for the harmonics source.

        The harmonics source data consists of a series of orders whose levels depend on RPM. Levels
        must be specified in unit^2 (for example Pa^2/Hz).
        """
        return self.__source_harmonics

    @source_harmonics.setter
    def source_harmonics(self, source: FieldsContainer):
        """Set the harmonics source data."""
        if source is not None:
            if not isinstance(source, FieldsContainer):
                raise PyAnsysSoundException(
                    "Specified harmonics source must be provided as a DPF fields container."
                )

            if (
                len(source) < 1
                or len(source[0].data) < 1
                or len(source[0].time_freq_support.time_frequencies.data) < 1
            ):
                raise PyAnsysSoundException(
                    "Specified harmonics source must contain at least one order level (the "
                    "provided DPF fields container must contain at least one field with at least "
                    "one data point)."
                )

            for field in source:
                if len(field.data) != len(field.time_freq_support.time_frequencies.data):
                    raise PyAnsysSoundException(
                        "Each set of order levels in the specified harmonics source must contain "
                        "as many level values as the number of orders (in the provided DPF fields "
                        "container, each field must contain the same number of data points and "
                        "support values)."
                    )

                if len(field.data) != len(source[0].data):
                    raise PyAnsysSoundException(
                        "Each set of order levels in the specified harmonics source must contain "
                        "the same number of level values (in the provided DPF fields container, "
                        "each field must contain the same number of data points)."
                    )

            support_data = source.get_support("control_parameter_1")
            support_properties = support_data.available_field_supported_properties()
            support_values = support_data.field_support_by_property(support_properties[0])
            if len(support_values) != len(source):
                raise PyAnsysSoundException(
                    "The specified harmonics source must contain as many sets of order levels as "
                    "the number of values in the associated control parameter (in the provided "
                    "DPF fields container, the number of fields should be the same as the number "
                    "of values in the fields container support)."
                )

        self.__source_harmonics = source

    def is_source_control_valid(self) -> bool:
        """Source control verification function.

        Check if the source control is valid, that is, if the source control is set and contains at
        least one control value.

        Returns
        -------
        bool
            True if the source control is valid.
        """
        return (
            self.source_control is not None
            and self.source_control.control is not None
            and len(self.source_control.control.data) > 0
        )

    def load_source_harmonics(self, file: str):
        """Load the harmonics source data from a file.

        Parameters
        ----------
        file : str
            Path to the harmonics source file. Supported files are the same XML and text (with the
            header `AnsysSound_Orders`) formats as supported by Ansys Sound SAS.
        """
        # Set operator inputs.
        self.__operator_load.connect(0, file)

        # Run the operator.
        self.__operator_load.run()

        # Get the loaded sound power level parameters.
        self.source_harmonics = self.__operator_load.get_output(0, "fields_container")

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
        self.source_harmonics = source_data.get_property("sound_composer_source")
        control = source_control_data.get_property("sound_composer_source_control_one_parameter")
        self.source_control = SourceControlTime()
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
        if self.source_harmonics is None:
            warnings.warn(
                PyAnsysSoundWarning(
                    "Cannot create source generic data container because there is no source data."
                )
            )
            source_data = None
        else:
            source_data = GenericDataContainer()
            source_data.set_property("sound_composer_source", self.source_harmonics)

        if not self.is_source_control_valid():
            warnings.warn(
                PyAnsysSoundWarning(
                    "Cannot create source control generic data container, either because there is "
                    "no source control data, or because the source control data is invalid."
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
        """Generate the sound of the harmonics source.

        This method generates the sound of the harmonics source, using the current harmonics
        data and source control (RPM).

        Parameters
        ----------
        sampling_frequency : float, default: 44100.0
            Sampling frequency of the generated sound in Hz.
        """
        if sampling_frequency <= 0.0:
            raise PyAnsysSoundException("Sampling frequency must be strictly positive.")

        if not self.is_source_control_valid():
            raise PyAnsysSoundException(
                "Harmonics source control is not set/valid. "
                f"Use ``{__class__.__name__}.source_control``."
            )

        if self.source_harmonics is None:
            raise PyAnsysSoundException(
                f"Harmonics source data is not set. Use ``{__class__.__name__}.source_harmonics`` "
                f"or method ``{__class__.__name__}.load_source_harmonics()``."
            )

        # Set operator inputs.
        self.__operator_generate.connect(0, self.source_harmonics)
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
        plt.title(output.name if len(output.name) > 0 else "Signal from harmonics source")
        plt.xlabel(f"Time ({time.unit})")
        plt.ylabel(f"Amplitude ({output.unit})")
        plt.grid(True)
        plt.show()

    def plot_control(self):
        """Plot the source control."""
        if not self.is_source_control_valid():
            raise PyAnsysSoundException(
                "Harmonics source control is not set/valid. "
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

    def __extract_harmonics_info(self) -> tuple[list[float], str, list[float]]:
        """Extract the harmonics source information.

        Returns
        -------
        tuple[list[float], str, list[float]]
            Harmonics source information, consisting of the following elements:
                First element: list of order values.

                Second element: name of the control parameter.

                Third element: list of control parameter values.
        """
        if self.source_harmonics is None:
            return ([], "", [])

        # Orders (same values for each field).
        orders = self.source_harmonics[0].time_freq_support.time_frequencies.data

        # Control parameter info.
        support_ids = list(self.source_harmonics.get_label_space(0).keys())
        support = self.source_harmonics.get_support(support_ids[0])
        parameter_ids = support.available_field_supported_properties()
        control_name = support.field_support_by_property(parameter_ids[0]).name
        control_values = list(support.field_support_by_property(parameter_ids[0]).data)

        return orders, control_name, control_values
