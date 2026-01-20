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

"""Computes ISO 3744 sound power level."""

import warnings

from ansys.dpf.core import Field, Operator
import matplotlib.pyplot as plt
import numpy as np

from ansys.sound.core.signal_utilities.create_signal_fields_container import (
    CreateSignalFieldsContainer,
)

from . import SoundPowerParent
from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning

ID_COMPUTE_SOUND_POWER_LEVEL = "compute_sound_power_level_iso3744"
ID_LOAD_SOUND_POWER_LEVEL = "load_project_sound_power_level_iso3744"


class SoundPowerLevelISO3744(SoundPowerParent):
    """Computes ISO 3744 sound power level.

    This class computes the sound power level according to the ISO 3744 standard.

    Examples
    --------
    Compute and display sound power level following the ISO 3744 standard.

    >>> from ansys.sound.core.sound_power import SoundPowerLevelISO3744
    >>> swl = SoundPowerLevelISO3744(
    ...     surface_shape="Hemisphere",
    ...     surface_radius=2.0,
    ... )
    >>> swl.add_microphone_signal(signal1)
    >>> # Repeat for all microphone signals.
    >>> swl.process()
    >>> Lw = swl.get_Lw()
    >>> swl.plot()

    Alternatively, load sound power level data from a project file created in Ansys Sound: Analysis
    and Specifications (SAS).

    >>> swl = SoundPowerLevelISO3744()
    >>> swl.load_project("path/to/project_file.spw")
    >>> swl.process()
    >>> Lw = swl.get_Lw()
    >>> swl.plot()
    """

    def __init__(
        self,
        surface_shape: str = "Hemisphere",
        surface_radius: float = 1.0,
        K1: float = 0.0,
        K2: float = 0.0,
        C1: float = 0.0,
        C2: float = 0.0,
    ):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        surface_shape : str, default: 'Hemisphere'
            Shape of measurement surface. Available options are 'Hemisphere' (default) and
            'Half-hemisphere'.
        surface_radius : float, default: 1.0
            Radius in m of the hemisphere or half-hemisphere measurement surface.
            By default, 1.0 meter.
        K1 : float, default: 0.0
            Background noise correction K1 in dB (section 8.2.3 of ISO 3744).
            By default, 0.0 dB.
        K2 : float, default: 0.0
            Environmental correction K2 in dB (Annex A of ISO 3744). By default, 0.0 dB.
        C1 : float, default: 0.0
            Meteorological reference quantity correction C1 in dB (Annex G of ISO 3744).
            By default, 0.0 dB.
        C2 : float, default: 0.0
            Meteorological radiation impedance correction C2 in dB (Annex G of ISO 3744).
            By default, 0.0 dB.
        """
        super().__init__()
        self.surface_shape = surface_shape
        self.surface_radius = surface_radius
        self.K1 = K1
        self.K2 = K2
        self.C1 = C1
        self.C2 = C2

        # Initialize an empty list meant to store microphone signals.
        self.__signals = []

        # Define output field.
        self._output = None

        # Define DPF Sound operators.
        self.__operator_compute = Operator(ID_COMPUTE_SOUND_POWER_LEVEL)
        self.__operator_load = Operator(ID_LOAD_SOUND_POWER_LEVEL)

    def __str__(self):
        """Overloads the __str__ method."""
        string = (
            "SoundPowerLevelISO3744 object\n"
            + "Data:\n"
            + "  Measurement surface:\n"
            + f"    Shape: {self.surface_shape}\n"
            + f"    Radius: {np.round(self.surface_radius, 1)} m\n"
            + f"    Area: {np.round(self.__get_surface_area(), 1)} m^2\n"
            + f"    Number of microphone signals: {len(self.__signals)}\n"
            + "  Correction coefficient:\n"
            + f"    K1 (background noise): {np.round(self.K1, 1)} dB\n"
            + f"    K2 (measurement environment): {np.round(self.K2, 1)} dB\n"
            + f"    C1 (meteorological reference quantity): {np.round(self.C1, 1)} dB\n"
            + f"    C2 (meteorological radiation impedance): {np.round(self.C2, 1)} dB\n"
            + "  Sound power level (Lw):\n"
            + f"    Unweighted: {np.round(self.get_Lw(), 1)} dB\n"
            + f"    A-weighted: {np.round(self.get_Lw_A(), 1)} dBA\n"
        )

        return string

    @property
    def surface_shape(self) -> str:
        """Shape of the measurement surface.

        Available options are 'Hemisphere' and 'Half-hemisphere'.
        """
        return self.__surface_shape

    @surface_shape.setter
    def surface_shape(self, surface_shape: str):
        """Set the shape of measurement surface."""
        if surface_shape.lower() not in ("hemisphere", "half-hemisphere"):
            raise PyAnsysSoundException(
                "Input surface shape is invalid. Available options are 'Hemisphere' and "
                "'Half-hemisphere'."
            )
        self.__surface_shape = surface_shape

    @property
    def surface_radius(self) -> float:
        """Radius of the measurement surface in m."""
        return self.__surface_radius

    @surface_radius.setter
    def surface_radius(self, surface_radius: float):
        """Set the radius of measurement surface."""
        if surface_radius <= 0:
            raise PyAnsysSoundException("Input surface radius must be strictly positive.")
        self.__surface_radius = surface_radius

    @property
    def K1(self) -> float:
        """Background noise correction K1 in dB.

        See section 8.2.3 of ISO 3744.
        """
        return self.__K1

    @K1.setter
    def K1(self, K1: str):
        """Set the K1 correction."""
        self.__K1 = K1

    @property
    def K2(self) -> float:
        """Environmental correction K2 in dB.

        See annex A of ISO 3744..
        """
        return self.__K2

    @K2.setter
    def K2(self, K2: str):
        """Set the  correction."""
        self.__K2 = K2

    @property
    def C1(self) -> float:
        """Meteorological reference quantity correction C1 in dB.

        See annex G of ISO 3744.
        """
        return self.__C1

    @C1.setter
    def C1(self, C1: str):
        """Set the C1 correction."""
        self.__C1 = C1

    @property
    def C2(self) -> float:
        """Meteorological radiation impedance correction C2 in dB.

        See annex G of ISO 3744).
        """
        return self.__C2

    @C2.setter
    def C2(self, C2: str):
        """Set the C2 correction."""
        self.__C2 = C2

    def add_microphone_signal(self, signal: Field):
        """Add microphone signal.

        Adds a microphone-recorded signal.

        .. note::
            It is assumed that the microphone positions where the signals were recorded follow
            Annex B of ISO 3744 for the specific measurement surface shape used.

        Parameters
        ----------
        signal : Field
            Recorded signal in Pa from one specific position.
        """
        if type(signal) is not Field:
            raise PyAnsysSoundException("Added signal must be provided as a DPF field.")

        self.__signals.append(signal)

    def get_microphone_signal(self, index: int) -> Field:
        """Get microphone signal.

        Gets the microphone signal that corresponds to the specified index.

        Parameters
        ----------
        index : int
            Signal index.

        Returns
        -------
        Field
            Microphone signal in Pa for the specified index.
        """
        if index > len(self.__signals) - 1:
            raise PyAnsysSoundException("No microphone signal associated with this index.")

        return self.__signals[index]

    def delete_microphone_signal(self, index: int):
        """Delete microphone signal.

        Deletes the microphone signal that corresponds to the specified index.

        Parameters
        ----------
        index : int
            Signal index.
        """
        if index > len(self.__signals) - 1:
            warnings.warn(PyAnsysSoundWarning("No microphone signal associated with this index."))
        else:
            self.__signals.pop(index)

    def get_all_signal_names(self) -> dict[int, str]:
        """Get all signal names.

        Gets all added signal names in a dictionary.

        Returns
        -------
        dict[int, str]
            Dictionary of all signal indexes and names.
        """
        signal_names = {}
        for isig in range(len(self.__signals)):
            signal_names[isig] = self.__signals[isig].name

        return signal_names

    def set_K2_from_room_properties(
        self, length: float, width: float, height: float, alpha: float
    ) -> float:
        """Set K2 from measurement room properties and measurement surface area.

        Sets K2 following Annex A of ISO 3744, based on specified room dimensions and averaged
        sound absorption coefficient, and current measurement surface area (that is,
        shape and radius).

        Parameters
        ----------
        length : float
            Measurement room length in m.
        width : float
            Measurement room width in m.
        height : float
            Measurement room height in m.
        alpha : float
            Mean sound absorption coefficient between 0 and 1. Typical example values are
            given in Table A.1 of ISO 3744.

        Returns
        -------
        float
            Calculated correction K2 in dB
        """
        if length <= 0.0 or width <= 0.0 or height <= 0.0:
            raise PyAnsysSoundException(
                "Specified room length, width and height must be all strictly greater than 0 m."
            )

        if alpha <= 0 or alpha > 1.0:
            raise PyAnsysSoundException(
                "Specified mean absorption coefficient alpha must be strictly greater than 0, "
                "and smaller than 1."
            )

        # Equation A.7 of ISO 3744.
        A = alpha * 2 * (length * width + length * height + width * height)

        S = self.__get_surface_area()

        # Equation A.2 of ISO 3744.
        K2 = 10 * np.log10(1 + 4 * S / A)

        self.K2 = K2

        return K2

    def set_C1_C2_from_meteo_parameters(
        self, pressure: float = 101.325, temperature: float = 23.0
    ) -> tuple:
        """Set C1 and C2 from static pressure and temperature.

        Sets C1 and C2 following Annex G of ISO 3744, based on specified static pressure and
        temperature.

        Parameters
        ----------
        pressure : float, default: 101.325
            Static pressure in kPa.
        temperature : float, default: 23.0
            Temperature in °C.

        Returns
        -------
        tuple[float]
            First element: correction C1 in dB.
            Second element: correction C2 in dB.
        """
        ps0 = 101.325  # Reference static pressure in kPa.
        theta0 = 314.0  # Reference temperature in K under an air impedance of 400 N s/m^3.
        theta1 = 296.0  # Reference temperature in K (equal to 23 °C).

        C1 = -10.0 * np.log10(pressure / ps0) + 5.0 * np.log10((273.15 + temperature) / theta0)
        C2 = -10.0 * np.log10(pressure / ps0) + 15.0 * np.log10((273.15 + temperature) / theta1)

        self.C1, self.C2 = C1, C2

        return (C1, C2)

    def load_project(self, filename: str):
        """Set all sound power level parameters according to a project file created in SAS.

        Sets measurement surface shape and radius, K1, K2, C1, C2, and list of signals as specified
        in a sound power level project created in Ansys Sound Analysis & Specification.

        Parameters
        ----------
        filename: string
            Sound power level project file.
        """
        # Set operator inputs.
        self.__operator_load.connect(0, filename)

        # Run the operator.
        self.__operator_load.run()

        # Get the loaded sound power level parameters.
        self.surface_shape = self.__operator_load.get_output(0, "string")
        self.surface_radius = self.__operator_load.get_output(1, "double")
        self.K1 = self.__operator_load.get_output(2, "double")
        self.K2 = self.__operator_load.get_output(3, "double")
        self.C1 = self.__operator_load.get_output(4, "double")
        self.C2 = self.__operator_load.get_output(5, "double")
        fc_signals = self.__operator_load.get_output(6, "fields_container")

        # Convert signals stored as a fields container into a list of fields.
        del self.__signals
        self.__signals = []
        for isig in range(len(fc_signals)):
            self.__signals.append(fc_signals[isig])

    def process(self):
        """Calculate the sound power level.

        This method calls the appropriate DPF Sound operator to compute the sound power level.
        """
        # Check that at least one signal is defined.
        if len(self.__signals) < 1:
            raise PyAnsysSoundException(
                "No microphone signal was defined. "
                "Use SoundPowerLevelISO3744.add_microphone_signal()."
            )

        # Create a fields container containing all microphone signals.
        fc_creator = CreateSignalFieldsContainer(self.__signals)
        fc_creator.process()
        fc_signals = fc_creator.get_output()

        # Set operator inputs.
        self.__operator_compute.connect(0, self.surface_shape)
        self.__operator_compute.connect(1, self.surface_radius)
        self.__operator_compute.connect(2, self.K1)
        self.__operator_compute.connect(3, self.K2)
        self.__operator_compute.connect(4, self.C1)
        self.__operator_compute.connect(5, self.C2)
        self.__operator_compute.connect(6, fc_signals)

        # Run the operator.
        self.__operator_compute.run()

        # Get the output.
        self._output = (
            self.__operator_compute.get_output(0, "double"),
            self.__operator_compute.get_output(1, "double"),
            self.__operator_compute.get_output(2, "field"),
            self.__operator_compute.get_output(3, "field"),
        )

    def get_output(self) -> tuple:
        """Get the sound power level data as floats and DPF fields.

        Returns
        -------
        tuple
            -   First element: unweighted sound power level (Lw) in dB.

            -   Second element: A-weighted sound power level (Lw(A)) in dBA.

            -   Third element is a DPF field containing an array of the octave-band sound power
                levels, in dB.

            -   Fourth element is a DPF field containing an array of the one-third-octave-band
                sound power levels, in dB.
        """
        if self._output == None:
            warnings.warn(
                PyAnsysSoundWarning(
                    "Output is not processed yet. "
                    "Use the 'SoundPowerLevelISO3744.process()' method."
                )
            )

        return self._output

    def get_output_as_nparray(self) -> tuple:
        """Get sound power level data as floats and NumPy arrays.

        Returns
        -------
        tuple
            -   First element: unweighted sound power level (Lw) in dB.

            -   Second element: A-weighted sound power level (Lw(A)) in dBA.

            -   Third element: NumPy array of the octave-band sound power levels, in dB.

            -   Fourth element: NumPy array of the octave-band center frequencies, in Hz.

            -   Fifth element: NumPy array of the one-third-octave-band sound power levels, in dB.

            -   Sixth element: NumPy array of the one-third-octave-band center frequencies, in Hz.
        """
        output = self.get_output()

        if output == None:
            return (np.nan, np.nan, np.array([]), np.array([]), np.array([]), np.array([]))

        return (
            output[0],
            output[1],
            np.array(output[2].data),
            np.array(output[2].time_freq_support.time_frequencies.data),
            np.array(output[3].data),
            np.array(output[3].time_freq_support.time_frequencies.data),
        )

    def get_Lw(self) -> float:
        """Get unweighted sound power level.

        Returns
        -------
        float
            Unweighted sound power level (Lw) in dB.
        """
        output = self.get_output_as_nparray()

        return output[0]

    def get_Lw_A(self) -> float:
        """Get A-weighted sound power level.

        Returns
        -------
        float
            A-weighted sound power level (Lw(A)) in dBA.
        """
        output = self.get_output_as_nparray()

        return output[1]

    def get_Lw_octave(self) -> np.ndarray:
        """Get octave-band power sound levels.

        Returns
        -------
        numpy.ndarray
            Array of octave-band sound power levels in dB.
        """
        output = self.get_output_as_nparray()

        return output[2]

    def get_octave_center_frequencies(self) -> np.ndarray:
        """Get octave-band center frequencies.

        Returns
        -------
        numpy.ndarray
            Array of octave-band center frequencies in Hz.
        """
        output = self.get_output_as_nparray()

        return output[3]

    def get_Lw_thirdoctave(self) -> np.ndarray:
        """Get one-third-octave-band power sound levels.

        Returns
        -------
        numpy.ndarray
            Array of one-third-octave-band sound power levels in dB.
        """
        output = self.get_output_as_nparray()

        return output[4]

    def get_thirdoctave_center_frequencies(self) -> np.ndarray:
        """Get one-third-octave-band center frequencies.

        Returns
        -------
        numpy.ndarray
            Array of one-third-octave-band center frequencies in Hz.
        """
        output = self.get_output_as_nparray()

        return output[5]

    def plot(self):
        """Plot the sound power level in octave or one-third-octave bands.

        Creates a figure that displays the sound power level in each octave band in the upper graph,
        and in each 1/3-octave band in the lower graph.
        """
        if self._output == None:
            raise PyAnsysSoundException(
                "Output is not processed yet. Use the 'SoundPowerLevelISO3744.process()' method."
            )

        # Display octave-band levels in the upper subplot.
        Lw = self.get_Lw_octave()
        Lw_unit = self.get_output()[2].unit
        f_center = self.get_octave_center_frequencies()

        plt.subplot(211)
        plt.bar(range(len(Lw)), Lw)
        plt.xticks(range(len(Lw)), f_center.astype(int), rotation=45, fontsize=9)
        plt.title("Octave-band sound power level")
        plt.ylabel(r"$\mathregular{L_w}$" + f" ({Lw_unit})")

        # Display 1/3-octave-band levels in the lower subplot.
        Lw = self.get_Lw_thirdoctave()
        Lw_unit = self.get_output()[3].unit
        f_center = self.get_thirdoctave_center_frequencies()
        f_unit = self.get_output()[3].time_freq_support.time_frequencies.unit

        plt.subplot(212)
        plt.bar(range(len(Lw)), Lw)
        plt.xticks(range(len(Lw)), f_center.astype(int), rotation=45, fontsize=9)
        plt.title("1/3-octave-band sound power level")
        plt.ylabel(r"$\mathregular{L_w}$" + f" ({Lw_unit})")
        plt.xlabel(f"Frequency ({f_unit})")

        plt.tight_layout()
        plt.show()

    def __get_surface_area(self) -> float:
        """Calculate measurement surface.

        Calculates measurement surface area from its shape and radius, as indicated in section
        7.2.3 of ISO 3744.

        Returns
        -------
        float
            Measurement surface area in m^2.
        """
        match self.surface_shape.lower():
            case "hemisphere":
                return 2 * np.pi * self.surface_radius**2
            case "half-hemisphere":
                return np.pi * self.surface_radius**2
