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

"""Computes ISO 3744 sound power level."""
import warnings

from ansys.dpf.core import Field, FieldsContainer, Operator
import matplotlib.pyplot as plt
import numpy as np
from numpy import typing as npt

from . import SoundPowerParent
from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning

ID_COMPUTE_SOUND_POWER_LEVEL = "compute_sound_power_level_iso3744"
ID_LOAD_SOUND_POWER_LEVEL = "load_project_sound_power_level_iso3744"
LW = 0
LWA = 1
LW_OCTAVE = 2
LW_THIRDOCTAVE = 3
LW_OCTAVE_NP = 2
OCTAVE_CENTER_FREQUENCIES = 3
LW_THIRDOCTAVE_NP = 4
THIRDOCTAVE_CENTER_FREQUENCIES = 5


class SoundPowerLevelISO3744(SoundPowerParent):
    """Computes ISO 3744 sound power level.

    This class computes the sound power level following the ISO 3744 standard.
    """

    def __init__(
        self,
        surface_shape: str = "Hemisphere",
        surface_radius: float = 1,
        K1: float = 0,
        K2: float = 0,
        C1: float = 0,
        C2: float = 0,
    ):
        """Create a ``SoundPowerLevelISO3744`` object.

        Parameters
        ----------
        surface_shape: str, default: 'Hemisphere'
            Shape of measurement surface. Available options are 'Hemisphere' (default) and
            'Half-hemisphere'.
        surface_radius: float, default: 1
            Radius in m of the hemisphere or half-hemisphere measurement surface.
            By default, 1 meter.
        K1: float, default: 0
            Background noise correction K1 in dB (section 8.2.3 of ISO 3744).
            By default, 0 dB.
        K2: float, default: 0
            Environmental correction K2 in dB (Annex A of ISO 3744). By default, 0 dB.
        C1: float, default: 0
            Meteorological reference quantity correction C1 in dB (Annex G of ISO 3744).
            By default, 0 dB.
        C2: float, default: 0
            Meteorological radiation impedance correction C2 in dB (Annex G of ISO 3744).
            By default, 0 dB.
        """
        super().__init__()
        self.surface_shape = surface_shape
        self.surface_radius = surface_radius
        self.K1 = K1
        self.K2 = K2
        self.C1 = C1
        self.C2 = C2

        # Initialize an empty dictionary meant to store microphone signals.
        self.__signals = {}

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
            + f"    Radius: {self.surface_radius} m\n"
            + f"    Area: {np.round(self.__get_surface_area(), 1)} m^2\n"
            + f"    Number of microphone signals: {len(self.__signals)}\n"
            + "  Correction coefficient:\n"
            + f"    K1 (background noise): {self.K1} dB\n"
            + f"    K2 (measurement environment): {self.K2} dB\n"
            + f"    C1 (meteorological reference quantity): {self.C1} dB\n"
            + f"    C2 (meteorological radiation impedance): {self.C2} dB\n"
            + "  Sound power level (Lw):\n"
            + f"    Unweighted: {self.get_Lw()} dB\n"
            + f"    A-weighted: {self.get_Lw_A()} dBA\n"
        )
        # TODO (maybe): add microphone positions

        return string

    @property
    def surface_shape(self):
        """Surface shape."""
        return self.__surface_shape  # pragma: no cover

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
    def surface_radius(self):
        """Surface radius."""
        return self.__surface_radius  # pragma: no cover

    @surface_radius.setter
    def surface_radius(self, surface_radius: float):
        """Set the radius of measurement surface."""
        if surface_radius <= 0:
            raise PyAnsysSoundException("Input surface radius must be strictly positive.")
        self.__surface_radius = surface_radius

    @property
    def K1(self):
        """K1 correction."""
        return self.__K1  # pragma: no cover

    @K1.setter
    def K1(self, K1: str):
        """Set the K1 correction."""
        self.__K1 = K1

    @property
    def K2(self):
        """K2 correction."""
        return self.__K2  # pragma: no cover

    @K2.setter
    def K2(self, K2: str):
        """Set the  correction."""
        self.__K2 = K2

    @property
    def C1(self):
        """C1 correction."""
        return self.__C1  # pragma: no cover

    @C1.setter
    def C1(self, C1: str):
        """Set the C1 correction."""
        self.__C1 = C1

    @property
    def C2(self):
        """C2 correction."""
        return self.__C2  # pragma: no cover

    @C2.setter
    def C2(self, C2: str):
        """Set the C2 correction."""
        self.__C2 = C2

    def add_microphone_signal(self, signal: Field, name: str):
        """Add microphone signal.

        Adds a microphone-recorded signal, along with a signal name.
        Note: It is assumed that the microphone positions where the signals were recorded follow
        Annex B of ISO 3744 for the specific measurement surface shape used.

        Parameters
        ----------
        signal: Field
            Recorded signal in Pa from one specific position.
        name: str
            Signal name. Must be unique.
        """
        self.__signals[name] = signal

    def get_microphone_signal(self, name: str) -> Field:
        """Get microphone signal.

        Gets the microphone signal that corresponds to the specified name.

        Parameters
        ----------
        name: str
            Signal name.

        Returns
        -------
        Field
            Microphone signal in Pa for the specified name.
        """
        try:
            return self.__signals[name]
        except KeyError:
            raise PyAnsysSoundException("No microphone signal associated with this name.")

    def delete_microphone_signal(self, name: str):
        """Delete microphone signal.

        Deletes the microphone signal that corresponds to the specified name.

        Parameters
        ----------
        name: str
            Signal name.
        """
        try:
            del self.__signals[name]
        except KeyError:
            warnings.warn(PyAnsysSoundWarning("No microphone signal associated with this name."))

    def get_all_signal_names(self) -> tuple:
        """Get all signal names.

        Gets the list of the names of all signals that were added.

        Returns
        -------
        tuple
            List of all signal names.
        """
        return tuple(self.__signals.keys())

    def set_C1_C2_from_meteo_parameters(
        self, pressure: float = 101.325, temperature: float = 23.0
    ) -> tuple:
        """Set C1 and C2 from static pressure and temperature.

        Sets C1 and C2 following Annex G of ISO 3744, based on specified static pressure and
        temperature.

        Parameters
        ----------
        pressure: float, default: 101.325
            Static pressure in kPa.
        temperature: float, default: 23.0
            Temperature in °C.

        Returns
        -------
        tuple[float]
            First element is the correction C1 in dB.
            Second element is the correction C2 in dB.
        """
        ps0 = 101.325  # Reference static pressure in kPa.
        theta0 = 314.0  # Reference temperature in K under an air impedance of 400 N s/m^3.
        theta1 = 296.0  # Reference temperature in K (equal to 23 °C).

        C1 = -10.0 * np.log10(pressure / ps0) + 5.0 * np.log10((273.15 + temperature) / theta0)

        C2 = -10.0 * np.log10(pressure / ps0) + 15.0 * np.log10((273.15 + temperature) / theta1)

        return (C1, C2)

    def set_K2_from_room_properties(
        self, length: float, width: float, height: float, alpha: float
    ) -> float:
        """Set K2 from measurement room properties.

        Sets K2 following Annex A of ISO 3744, based on specified room dimensions and averaged
        sound absorption coefficient.

        Parameters
        ----------
            length: float
                Measurement room length in m.
            width: float
                Measurement room width in m.
            height: float
                Measurement room height in m.
            alpha: float
                Mean sound absorption coefficient between 0 and 1. Typical example values are
                given in Table A.1 of ISO 3744.
        """
        # Equation A.7 of ISO 3744.
        A = alpha * 2 * (length * width + length * height + width * height)

        S = self.__get_surface_area()

        # Equation A.2 of ISO 3744.
        K2 = 10 * np.log10(1 + 4 * S / A)

        return K2

    def load_project(self, filename: str):
        """Set all sound power level parameters according to a project file created in SAS.

        Sets measurement surface shape and area, K1, K2, C1, C2, and list of signals as specified
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

        # Convert signals stored as a fields container into a dictionary.
        del self.__signals
        self.__signals = {}
        for i in range(len(fc_signals)):
            name = fc_signals[i].name
            self.__signals[name] = fc_signals[i]

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
        fc_signals = FieldsContainer()
        i = 0
        for signal in self.__signals.values():
            fc_signals.add_field({"index": i}, signal)
            i += 1

        # Set operator inputs.
        self.__operator_compute.connect(0, self.__get_surface_area())
        self.__operator_compute.connect(1, self.K1)
        self.__operator_compute.connect(2, self.K2)
        self.__operator_compute.connect(3, self.C1)
        self.__operator_compute.connect(4, self.C2)
        self.__operator_compute.connect(5, fc_signals)

        # Run the operator.
        self.__operator_compute.run()

        # Get the output.
        self._output = (
            self.__operator_compute.get_output(0, "double"),
            self.__operator_compute.get_output(1, "double"),
            self.__operator_compute.get_output(2, "field"),
            self.__operator_compute.get_output(3, "field"),
        )

        # # (DEBUG) For testing purpose while DPF sound operators are being developed
        # out1 = fields_factory.create_scalar_field(num_entities=1,location=locations.time_freq)
        # out1.append([1,2,3],1)
        # sup = TimeFreqSupport()
        # tmp = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
        # tmp.append([25,50,100], 1)
        # sup.time_frequencies = tmp
        # out1.time_freq_support = sup
        # out2 = fields_factory.create_scalar_field(num_entities=1,location=locations.time_freq)
        # out2.append([5,9,2,3,8,9,7,6,3],1)
        # sup = TimeFreqSupport()
        # tmp = fields_factory.create_scalar_field(num_entities=1, location=locations.time_freq)
        # tmp.append([20,25,31.5,40,50,63,80,100,125], 1)
        # sup.time_frequencies = tmp
        # out2.time_freq_support = sup

        # self._output = (
        #     6,
        #     61.8,
        #     out1,
        #     out2,
        # )

    def get_output(self) -> tuple:
        """Get the sound power level data as floats and DPF fields.

        Returns
        -------
        tuple
            First element is the unweighted sound power level (Lw) in dB.

            Second element is the A-weighted sound power level (Lw(A)) in dBA.

            Third element is a DPF field containing an array of the octave-band sound power
            levels, in dB.

            Fourth element is a DPF field containing an array of the one-third-octave-band sound
            power levels, in dB.
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
            First element is the unweighted sound power level (Lw) in dB.

            Second element is the A-weighted sound power level (Lw(A)) in dBA.

            Third element is a NumPy array of the octave-band sound power levels, in dB.

            Fourth element is a NumPy array of the octave-band center frequencies, in Hz.

            Fifth element is a NumPy array of the one-third-octave-band sound power levels, in dB.

            Sixth element is a NumPy array of the one-third-octave-band center frequencies, in Hz.
        """
        output = self.get_output()

        if output == None:
            return None

        return (
            output[LW],
            output[LWA],
            np.array(output[LW_OCTAVE].data),
            np.array(output[LW_OCTAVE].time_freq_support.time_frequencies.data),
            np.array(output[LW_THIRDOCTAVE].data),
            np.array(output[LW_THIRDOCTAVE].time_freq_support.time_frequencies.data),
        )

    def get_Lw(self) -> float:
        """Get unweighted sound power  level.

        Returns
        -------
        float
            Unweighted sound power level (Lw) in dB.
        """
        output = self.get_output()

        if output == None:
            return None

        return output[LW]

    def get_Lw_A(self) -> float:
        """Get A-weighted sound power level.

        Returns
        -------
        float
            A-weighted sound power level (Lw(A)) in dBA.
        """
        output = self.get_output()

        if output == None:
            return None

        return output[LWA]

    def get_Lw_thirdoctave(self) -> npt.ArrayLike:
        """Get octave-band power sound levels.

        Returns
        -------
        numpy.ndarray
            Array of octave-band sound power levels in dB.
        """
        output = self.get_output_as_nparray()

        if output == None:
            return None

        return output[LW_OCTAVE_NP]

    def get_octave_center_frequencies(self) -> npt.ArrayLike:
        """Get octave-band center frequencies.

        Returns
        -------
        numpy.ndarray
            Array of octave-band center frequencies in Hz.
        """
        output = self.get_output_as_nparray()

        if output == None:
            return None

        return output[OCTAVE_CENTER_FREQUENCIES]

    def get_Lw_thirdoctave(self) -> npt.ArrayLike:
        """Get one-third-octave-band power sound levels.

        Returns
        -------
        numpy.ndarray
            Array of one-third-octave-band sound power levels in dB.
        """
        output = self.get_output_as_nparray()

        if output == None:
            return None

        return output[LW_THIRDOCTAVE_NP]

    def get_thirdoctave_center_frequencies(self) -> npt.ArrayLike:
        """Get one-third-octave-band center frequencies.

        Returns
        -------
        numpy.ndarray
            Array of one-third-octave-band center frequencies in Hz.
        """
        output = self.get_output_as_nparray()

        if output == None:
            return None

        return output[THIRDOCTAVE_CENTER_FREQUENCIES]

    def plot(self, bands: str = "Third", logfreq: bool = False):
        """Plot the sound power level in octave or one-third-octave bands.

        Parameters
        ----------
        bands: str, default: 'Third'
            Parameter that specifies whether the sound power level should be plotted in octave
            ('Octave') or one-third-octave ('Third') bands.
        logfreq: bool, default: False
            Parameter that specifies whether the sound power level should be plotted over a linear
            (False) or logarithmic (True) frequency scale.
        """
        if self._output == None:
            raise PyAnsysSoundException(
                "Output is not processed yet. Use the 'SoundPowerLevelISO3744.process()' method."
            )
        output = self.get_output_as_nparray()

        # Assign each octave Lw value to its lower and upper boundary frequencies (in order to
        # display the Lw values over the entire bands).
        N = len(output[LW_OCTAVE_NP])
        Lw = np.repeat(output[LW_OCTAVE_NP], 2)
        f_lower = output[OCTAVE_CENTER_FREQUENCIES] * 2 ** (-1 / 2)
        f_higher = output[OCTAVE_CENTER_FREQUENCIES] * 2 ** (1 / 2)
        f_boundary = np.stack((f_lower, f_higher)).flatten("F")

        # Check that every lower boundary is higher than previous band's upper boundary.
        # If not, assign the previous band's upper boundary to the lower boundary value.
        for i in range(int(len(f_boundary) / 2 - 1)):
            if f_boundary[2 * i + 2] < f_boundary[2 * i + 1]:
                f_boundary[2 * i + 2] = f_boundary[2 * i + 1]

        plt.subplot(211)
        if logfreq == True:
            plt.semilogx(f_boundary, Lw)
        else:
            plt.plot(f_boundary, Lw)
        plt.title("Sound power level (SWL)")
        plt.ylabel(r"$\mathregular{L_w}$ (dB)")

        # Assign each third-octave Lw value to its lower and upper boundary frequencies (in order
        # to display the Lw values over the entire bands).
        N = len(output[LW_THIRDOCTAVE_NP])
        Lw = np.repeat(output[LW_THIRDOCTAVE_NP], 2)
        f_lower = output[THIRDOCTAVE_CENTER_FREQUENCIES] * 2 ** (-1 / 6)
        f_higher = output[THIRDOCTAVE_CENTER_FREQUENCIES] * 2 ** (1 / 6)
        f_boundary = np.stack((f_lower, f_higher)).flatten("F")

        # Check that every lower boundary is higher than the previous band's upper boundary.
        # If not, assign the previous band's upper boundary to the lower boundary value of the
        # next band.
        for i in range(int(len(f_boundary) / 2 - 1)):
            if f_boundary[2 * i + 2] < f_boundary[2 * i + 1]:
                f_boundary[2 * i + 2] = f_boundary[2 * i + 1]

        plt.subplot(212)
        if logfreq == True:
            plt.semilogx(f_boundary, Lw)
        else:
            plt.plot(f_boundary, Lw)
        plt.ylabel(r"$\mathregular{L_w}$ (dB)")
        plt.xlabel("Frequency (Hz)")
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
