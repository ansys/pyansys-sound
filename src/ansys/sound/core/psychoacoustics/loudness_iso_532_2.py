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

"""Computes ISO 532-2:2017 loudness."""

import warnings

from ansys.dpf.core import Field, FieldsContainer, Operator, types
import matplotlib.pyplot as plt
import numpy as np

from . import FIELD_DIFFUSE, FIELD_FREE, PsychoacousticsParent
from .._pyansys_sound import (
    PyAnsysSoundException,
    PyAnsysSoundWarning,
    convert_fields_container_to_np_array,
)

# Name of the DPF Sound operator used in this module.
ID_COMPUTE_LOUDNESS_ISO_532_2 = "compute_loudness_iso532_2"

RECORDING_MIC = "Mic"
RECORDING_HEAD = "Head"


class LoudnessISO532_2(PsychoacousticsParent):
    """Computes ISO 532-2:2017 loudness.

    This class computes the binaural and monaural loudness of a signal according to the
    ISO 532-2:2017 standard, corresponding to the "Moore-Glasberg method".

    .. seealso::
        :class:`LoudnessISO532_1_Stationary`

    Examples
    --------
    Compute the binaural loudness of a single-microphone signal in free field, presented diotically
    (same signal at both ears), and display the binaural specific loudness.

    >>> from ansys.sound.core.psychoacoustics import LoudnessISO532_2
    >>> loudness = LoudnessISO532_2(
    ...     signal=my_microphone_signal,
    ...     field_type="Free",
    ...     recording_type="Mic"
    ... )
    >>> loudness.process()
    >>> binaural_loudness_value = loudness.get_binaural_loudness_sone()
    >>> binaural_loudness_level_value = loudness.get_binaural_loudness_level_phon()
    >>> loudness.plot()

    Compute the monaural loudness at each ear of a head-and-torso-simulator or binaural-microphone
    signal in free field, presented dichotically (different signal at each ear), and display the
    binaural specific loudness.

    >>> from ansys.sound.core.psychoacoustics import LoudnessISO532_2
    >>> loudness = LoudnessISO532_2(
    ...     signal=my_binaual_signal,
    ...     field_type="Free",
    ...     recording_type="Head"
    ... )
    >>> loudness.process()
    >>> monaural_loudness_value = loudness.get_monaural_loudness_sone()
    >>> monaural_loudness_level_value = loudness.get_monaural_loudness_level_phon()
    >>> loudness.plot()

    .. seealso::
        :ref:`calculate_psychoacoustic_indicators`
            Example demonstrating how to compute various psychoacoustic indicators.
    """

    def __init__(
        self,
        signal: Field | FieldsContainer = None,
        field_type: str = FIELD_FREE,
        recording_type: str = RECORDING_MIC,
    ):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        signal : Field | FieldsContainer, default: None
            Signal in Pa on which to compute loudness. If ``signal`` is a
            :class:`Field <ansys.dpf.core.field.Field>`, the listening assumption is diotic (same
            signal presented at both ears). If ``signal`` is a
            :class:`FieldsContainer <ansys.dpf.core.fields_container.FieldsContainer>`, with
            exactly 2 fields, the listening assumption is dichotic (each field's signal presented
            at each ear).
        field_type : str, default: "Free"
            Sound field type. Available options are `"Free"` and `"Diffuse"`.
        recording_type : str, default: "Mic"
            Recording type. Available options are `"Mic"` for a single microphone and `"Head"` for
            a head and torso simulator.
        """
        super().__init__()
        self.signal = signal
        self.field_type = field_type
        self.recording_type = recording_type
        self.__operator = Operator(ID_COMPUTE_LOUDNESS_ISO_532_2)

    def __str__(self):
        """Return the string representation of the class."""
        if self.signal is not None:
            str_assumption = "Diotic" if isinstance(self.signal, Field) else "Dichotic"
            signal_str = (
                f'\tSignal name: "{self.signal.name}"\n'
                f"\tListening assumption: {str_assumption}\n"
            )
        else:
            signal_str = "\tSignal name: Not set\n"

        if self.recording_type == RECORDING_MIC:
            rec_str = "Single microphone"
        else:
            rec_str = "Head and torso simulator"

        if self._output is not None:
            output_str = (
                f"Binaural loudness: {self.get_binaural_loudness_sone():.3} sones\n"
                f"Binaural loudness level: {self.get_binaural_loudness_level_phon():.1f} phons"
            )
        else:
            output_str = "Binaural loudness: Not processed\nBinaural loudness level: Not processed"

        return (
            f"{__class__.__name__} object.\n"
            "Data\n"
            f"{signal_str}"
            f"\tField type: {self.field_type}\n"
            f"\tRecording type: {self.recording_type} ({rec_str})\n"
            f"{output_str}"
        )

    @property
    def signal(self) -> Field | FieldsContainer:
        """Input sound signal in Pa.

        Signal in Pa on which to compute loudness. If ``signal`` is a
        :class:`Field <ansys.dpf.core.field.Field>`, the listening assumption is diotic (same
        signal presented at both ears). If ``signal`` is a
        :class:`FieldsContainer <ansys.dpf.core.fields_container.FieldsContainer>`, with exactly 2
        fields, the listening assumption is dichotic (each field's signal presented at each ear).
        """
        return self.__signal

    @signal.setter
    def signal(self, signal: Field | FieldsContainer):
        """Set the signal."""
        if signal is not None:
            if isinstance(signal, FieldsContainer):
                if len(signal) != 2:
                    raise PyAnsysSoundException(
                        "The input FieldsContainer signal must contain exactly 2 fields "
                        "corresponding to the signals presented at the two ears."
                    )
            elif not isinstance(signal, Field):
                raise PyAnsysSoundException(
                    "Signal must be specified as a DPF field or fields container."
                )
        self.__signal = signal

    @property
    def field_type(self) -> str:
        """Sound field type.

        Available options are `"Free"` and `"Diffuse"`.
        """
        return self.__field_type

    @field_type.setter
    def field_type(self, field_type: str):
        """Set the sound field type."""
        if field_type.lower() not in [FIELD_FREE.lower(), FIELD_DIFFUSE.lower()]:
            raise PyAnsysSoundException(
                f'Invalid field type "{field_type}". Available options are "{FIELD_FREE}" and '
                f'"{FIELD_DIFFUSE}".'
            )
        self.__field_type = field_type

    @property
    def recording_type(self) -> str:
        """Recording type.

        Available options are `"Mic"` for a single microphone and `"Head"` for a head and torso
        simulator.
        """
        return self.__recording_type

    @recording_type.setter
    def recording_type(self, recording_type: str):
        """Set the recording type."""
        if recording_type.lower() not in [RECORDING_MIC.lower(), RECORDING_HEAD.lower()]:
            raise PyAnsysSoundException(
                f'Invalid recording type "{recording_type}". Available options are '
                f'"{RECORDING_MIC}" and "{RECORDING_HEAD}".'
            )
        self.__recording_type = recording_type

    def process(self):
        """Compute the loudness.

        This method calls the appropriate DPF Sound operator to compute the loudness of the signal.
        """
        if self.signal == None:
            raise PyAnsysSoundException(f"No input signal set. Use `{__class__.__name__}.signal`.")

        self.__operator.connect(0, self.signal)
        self.__operator.connect(1, self.field_type)
        self.__operator.connect(2, self.recording_type)

        # Runs the operator
        self.__operator.run()

        self._output = (
            self.__operator.get_output(0, types.double),
            self.__operator.get_output(1, types.double),
            self.__operator.get_output(2, types.vec_double),
            self.__operator.get_output(3, types.vec_double),
            self.__operator.get_output(4, types.field),
            self.__operator.get_output(5, types.fields_container),
        )

    def get_output(self) -> tuple:
        """Get the binaural and monaural loudness, loudness level, and specific loudness.

        Returns
        -------
        tuple
            -   First element (float): binaural loudness in sone.

            -   Second element (float): binaural loudness level in phon.

            -   Third element (DPFarray): monaural loudness in sone at each ear.

            -   Fourth element (DPFarray): monaural loudness level in phon at each ear.

            -   Fifth element (Field): binaural specific loudness in sone/Cam, as a function of the
                ERB center frequency.

            -   Sixth element (FieldsContainer): monaural specific loudness in sone/Cam at each ear,
                as a function of the ERB center frequency.
        """
        if self._output == None:
            warnings.warn(
                PyAnsysSoundWarning(
                    "Output is not processed yet. Use the "
                    f"`{__class__.__name__}.process()` method."
                )
            )

        return self._output

    def get_output_as_nparray(self) -> tuple[np.ndarray]:
        """Get loudness data in a tuple of NumPy arrays.

        Returns
        -------
        tuple[numpy.ndarray]
            -   First element: binaural loudness in sone.

            -   Second element: binaural loudness level in phon.

            -   Third element: monaural loudness in sone at each ear.

            -   Fourth element: monaural loudness level in phon at each ear.

            -   Fifth element: binaural specific loudness in sone/Cam, as a function of the ERB
                center frequency.

            -   Sixth element: monaural specific loudness in sone/Cam at each ear, as a function of
                the ERB center frequency.

            -   Seventh element: ERBn-number scale in Cam, where specific loudness is defined.
        """
        output = self.get_output()

        if output == None:
            return (
                np.nan,
                np.nan,
                np.array([]),
                np.array([]),
                np.array([]),
                np.array([]),
                np.array([]),
            )

        return (
            np.array(output[0]),
            np.array(output[1]),
            np.array(output[2]),
            np.array(output[3]),
            np.array(output[4].data),
            convert_fields_container_to_np_array(output[5]),
            np.array(output[4].time_freq_support.time_frequencies.data),
        )

    def get_binaural_loudness_sone(self) -> float:
        """Get the binaural loudness in sone.

        Returns
        -------
        float
            Binaural loudness in sone.
        """
        return self.get_output()[0]

    def get_binaural_loudness_level_phon(self) -> float:
        """Get the binaural loudness level in phon.

        Returns
        -------
        float
            Binaural loudness level in phon.
        """
        return self.get_output()[1]

    def get_monaural_loudness_sone(self) -> np.ndarray:
        """Get the monaural loudness in sone at each ear.

        Returns
        -------
        numpy.ndarray
            Monaural loudness in sone at each ear.
        """
        output = self.get_output_as_nparray()[2]
        if len(output) == 1:
            return np.array([output[0], output[0]])
        else:
            return output

    def get_monaural_loudness_level_phon(self) -> np.ndarray:
        """Get the monaural loudness level in phon at each ear.

        Returns
        -------
        numpy.ndarray
            Monaural loudness level in phon at each ear.
        """
        output = self.get_output_as_nparray()[3]
        if len(output) == 1:
            return np.array([output[0], output[0]])
        else:
            return output

    def get_binaural_specific_loudness(self) -> np.ndarray:
        """Get the binaural specific loudness.

        Returns
        -------
        numpy.ndarray
            Binaural specific loudness array in sone/Cam, as a function of the ERB center frequency.
        """
        return self.get_output_as_nparray()[4]

    def get_monaural_specific_loudness(self) -> np.ndarray:
        """Get the monaural specific loudness at each ear.

        Returns
        -------
        numpy.ndarray
            Monaural specific loudness array in sone/Cam at each ear, as a function of the ERB
            center frequency.
        """
        output = self.get_output_as_nparray()[5]

        # If signal is a FieldsContainer, then output's length is 2.
        # However, here, if signal is a Field, then it is not 1, it is the length of the specific
        # loudness. So the test below has to compare the length to 2, not 1.
        if len(output) != 2:
            return np.array([output, output])
        else:
            return output

    def get_erb_center_frequencies(self) -> np.ndarray:
        """Get the ERB center frequencies in Hz.

        This method returns the center frequencies in Hz of the equivalent rectangular bandwidths
        (ERB), where the specific loudness is defined.

        Returns
        -------
        numpy.ndarray
            Array of ERB center frequencies in Hz.
        """
        return (pow(10, self.get_erbn_numbers() / 21.366) - 1) / 0.004368

    def get_erbn_numbers(self) -> np.ndarray:
        """Get the ERBn-number scale in Cam.

        This method uses the equation (6) in ISO 532-2:2017 to convert the ERB center frequencies
        into the ERBn-number scale in Cam.

        Returns
        -------
        numpy.ndarray
            ERBn-number scale in Cam.
        """
        return self.get_output_as_nparray()[6]

    def plot(self):
        """Plot the binaural specific loudness.

        This method displays the binaural specific loudness in sone/Cam as a function of the ERB
        center frequency.
        """
        if self._output == None:
            raise PyAnsysSoundException(
                "Output is not processed yet. Use the " f"`{__class__.__name__}.process()` method."
            )

        center_frequency = self.get_erb_center_frequencies()
        specific_loudness = self.get_binaural_specific_loudness()
        unit = self.get_output()[4].unit

        plt.plot(center_frequency, specific_loudness)
        plt.title("Binaural specific loudness")
        plt.xlabel(f"ERB center frequency (Hz)")
        plt.ylabel(f"N' ({unit})")
        plt.grid(True)
        plt.show()
