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

"""Computes ECMA-418-2 tonality."""

import warnings

from ansys.dpf.core import Field, Operator, _global_server, types
import matplotlib.pyplot as plt
import numpy as np

from . import FIELD_DIFFUSE, FIELD_FREE, PsychoacousticsParent
from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning

# Name of the DPF Sound operator used in this module.
ID_COMPUTE_TONALITY_ECMA_418_2 = "compute_tonality_ecma418_2"


class TonalityECMA418_2(PsychoacousticsParent):
    """Computes ECMA-418-2 tonality.

    This class is used to compute the tonality according to the ECMA-418-2 standard (Sottek Hearing
    Model), formerly known as ECMA-74, annex G.

    .. note::
        The releases of DPF Sound 2026 R1 and PyAnsys Sound 0.2 introduce the 3rd edition of
        ECMA-418-2, in addition to the 1st edition implemented in previous versions. Theoretically,
        the 1st and 3rd editions of ECMA-418-2 are supposed to describe the same algorithm of
        psychoacoustic tonality calculation. However, the standard does not include any real
        verification data and its 1st edition noticeably included errors and unclear computation
        details open to interpretation. The 3rd edition was largely improved in that regard, and
        now allows producing consistent results throughout distinct implementations of the standard.
        As a consequence, this 3rd edition is strongly recommended in most cases, while the 1st
        edition should only be used when backward compatibility is required.

    .. note::
        Prior to release 0.2 of PyAnsys Sound, only the 1st edition of ECMA-418-2 was proposed.
        Similarly, the calculation was only available in free field. Release 0.2 includes the
        possibility to use the 3rd edition of ECMA-418-2, and perform the calculation in diffuse
        field (with either edition), using the two new attributes :attr:`edition` and
        :attr:`field_type`. This means that older code using this class needs be updated with
        values assigned to these two attributes. This can be done either when instantiating the
        class:``my_tonality = TonalityECMA418_2(my_signal, my_field_type, my_edition)``, or later,
        by setting the :attr:`field_type` and :attr:`edition` attributes:
        ``my_tonality.field_type = my_field_type`` and ``my_tonality.edition = my_edition``.

    .. seealso::
        :class:`TonalityDIN45681`, :class:`TonalityISOTS20065`, :class:`TonalityISO1996_2`,
        :class:`TonalityISO1996_2_OverTime`, :class:`TonalityAures`

    Examples
    --------
    Compute and display the tonality of a signal according to the ECMA-418-2 standard.

    >>> from ansys.sound.core.psychoacoustics import TonalityECMA418_2
    >>> tonality = TonalityECMA418_2(signal=my_signal, field_type="Free", edition="3rd")
    >>> tonality.process()
    >>> tonality_value = tonality.get_tonality()
    >>> tonality.plot()

    .. seealso::
        :ref:`calculate_tonality_indicators`
            Example demonstrating how to compute various tonality indicators.
    """

    def __init__(self, signal: Field = None, field_type: str = None, edition: str = None):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        signal: Field, default: None
            Signal in Pa on which to calculate the tonality.
        field_type: str, default: None
            Sound field type. Available options are `"Free"` and `"Diffuse"`.
        edition: str, default: None
            Edition of the ECMA-418-2 standard to use. Available options are `"1st"` and `"3rd"`,
            which correspond to the 2020 and 2024 versions of the ECMA-418-2 standard, respectively.
        """
        super().__init__()

        # Determine if the server version is higher than or equal to 11.0.
        self.__server_meets_version_11 = _global_server().meet_version("11.0")

        self.signal = signal
        self.field_type = field_type
        self.edition = edition
        self.__operator = Operator(ID_COMPUTE_TONALITY_ECMA_418_2)

    def __str__(self):
        """Return the string representation of the object."""
        if self._output is None:
            str_tonality = "Not processed\n"
        else:
            str_tonality = f"{self.get_tonality():.2f} tuHMS\n"

        if self.signal is not None:
            str_name = f'"{self.signal.name}"'
        else:
            str_name = "Signal not set"

        return (
            f"{__class__.__name__} object.\n"
            "Data\n"
            f"\tSignal name: {str_name}\n"
            f"\tField type: {self.field_type}\n"
            f"\tEdition of the standard: {self.edition}\n"
            f"Tonality: {str_tonality}"
        )

    @property
    def signal(self) -> Field:
        """Input signal in Pa."""
        return self.__signal

    @signal.setter
    def signal(self, signal: Field):
        """Set signal."""
        if not (isinstance(signal, Field) or signal is None):
            raise PyAnsysSoundException("Signal must be specified as a DPF field.")
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
        if field_type is not None:
            if field_type.lower() not in [FIELD_FREE.lower(), FIELD_DIFFUSE.lower()]:
                raise PyAnsysSoundException(
                    f'Invalid field type "{field_type}". Available options are "{FIELD_FREE}" and '
                    f'"{FIELD_DIFFUSE}".'
                )

            if field_type.lower() == FIELD_DIFFUSE.lower() and not self.__server_meets_version_11:
                # Until DPF Sound 2025 R2 (server version 10), ECMA-418-2 calculation is only
                # available in free field.
                raise PyAnsysSoundException(
                    "Computing ECMA-418-2 tonality in diffuse field requires version 2026 R1 of "
                    "DPF Sound or higher. Please use free field instead."
                )

        self.__field_type = field_type

    @property
    def edition(self) -> str:
        """Edition of the ECMA-418-2 standard to use.

        Available options are `"1st"` for the 2020 version, and `"3rd"` for the 2024 version.
        """
        return self.__edition

    @edition.setter
    def edition(self, edition: str):
        """Set the edition of the ECMA-418-2 standard to use."""
        if edition is not None:
            if edition.lower() not in ["1st", "3rd"]:
                raise PyAnsysSoundException(
                    f'Invalid edition "{edition}". Available options are "1st" and "3rd".'
                )

            if edition.lower() == "3rd" and not self.__server_meets_version_11:
                # Until DPF Sound 2025 R2 (server version 10), only the 1st edition of ECMA-418-2
                # is available.
                raise PyAnsysSoundException(
                    "The 3rd edition of ECMA-418-2 tonality requires version 2026 R1 of DPF Sound "
                    "or higher. Please use the 1st edition instead."
                )

        self.__edition = edition

    def process(self):
        """Compute the ECMA-418-2 tonality.

        This method calls the appropriate DPF Sound operator.
        """
        if self.signal is None:
            raise PyAnsysSoundException(
                f"No input signal defined. Use ``{__class__.__name__}.signal``."
            )
        if self.field_type is None:
            raise PyAnsysSoundException(
                f"No field type specified. Use ``{__class__.__name__}.field_type``."
            )
        if self.edition is None:
            raise PyAnsysSoundException(
                f"No edition of the standard specified. Use ``{__class__.__name__}.edition``."
            )

        # Connect the operator input(s).
        self.__operator.connect(0, self.signal)
        if self.__server_meets_version_11:
            self.__operator.connect(1, self.field_type)
            # 1st letter in self.edition is the value (as an int) expected by the operator.
            self.__operator.connect(2, int(self.edition[0]))

        # Run the operator.
        self.__operator.run()

        # Store the operator outputs in a tuple.
        self._output = (
            self.__operator.get_output(0, types.double),
            self.__operator.get_output(1, types.field),
            self.__operator.get_output(2, types.field),
        )

    def get_output(self) -> tuple[float, Field, Field]:
        """Get the ECMA-418-2 tonality data, in a tuple containing data of various types.

        Returns
        -------
        tuple
            -   First element (float): ECMA-418-2 tonality, in tuHMS.

            -   Second element (Field): ECMA-418-2 tonality over time, in tuHMS.

            -   Third element (Field): ECMA-418-2 tone frequency over time, in Hz.
        """
        if self._output == None:
            warnings.warn(
                PyAnsysSoundWarning(
                    f"Output is not processed yet. "
                    f"Use the ``{__class__.__name__}.process()`` method."
                )
            )

        return self._output

    def get_output_as_nparray(self) -> tuple[float, np.ndarray, np.ndarray]:
        """Get the ECMA-418-2 tonality data, in a tuple of NumPy arrays.

        Returns
        -------
        tuple[numpy.ndarray]
            -   First element: ECMA-418-2 tonality, in tuHMS.

            -   Second element: ECMA-418-2 tonality over time, in tuHMS.

            -   Third element: ECMA-418-2 tone frequency over time, in Hz.

            -   Fourth element: associated time scale for tonality, in s.

            -   Fifth element: associated time scale for tone frequency, in s.
        """
        output = self.get_output()

        if output == None:
            return (
                np.nan,
                np.array([]),
                np.array([]),
                np.array([]),
                np.array([]),
            )

        return (
            np.array(output[0]),
            np.array(output[1].data),
            np.array(output[2].data),
            np.array(output[1].time_freq_support.time_frequencies.data),
            np.array(output[2].time_freq_support.time_frequencies.data),
        )

    def get_tonality(self) -> float:
        """Get the ECMA-418-2 tonality, in tuHMS.

        Returns
        -------
        float
            ECMA-418-2 tonality, in tuHMS.
        """
        return self.get_output_as_nparray()[0]

    def get_tonality_over_time(self) -> np.ndarray:
        """Get the ECMA-418-2 tonality over time, in tuHMS.

        Returns
        -------
        numpy.ndarray
            ECMA-418-2 tonality over time, in tuHMS.
        """
        return self.get_output_as_nparray()[1]

    def get_tone_frequency_over_time(self) -> np.ndarray:
        """Get the ECMA-418-2 tone frequency over time, in Hz.

        Returns
        -------
        numpy.ndarray
            ECMA-418-2 tone frequency over time, in Hz.
        """
        return self.get_output_as_nparray()[2]

    def get_tonality_time_scale(self) -> np.ndarray:
        """Get the ECMA-418-2 tonality time scale, in s.

        Returns
        -------
        numpy.ndarray
            Time array, in seconds, of the ECMA-418-2 tonality over time.
        """
        return self.get_output_as_nparray()[3]

    def get_tone_frequency_time_scale(self) -> np.ndarray:
        """Get the ECMA-418-2 tone frequency time scale, in s.

        Returns
        -------
        numpy.ndarray
            Time array, in seconds, of the ECMA-418-2 tone frequency over time.
        """
        return self.get_output_as_nparray()[4]

    def plot(self):
        """Plot the ECMA-418-2's tonality and tone frequency over time.

        This method displays the tonality in dB and the tone frequency in Hz, over time.
        """
        if self._output == None:
            raise PyAnsysSoundException(
                f"Output is not processed yet. Use the ``{__class__.__name__}.process()`` method."
            )

        # Get data to plot
        tonality_over_time = self.get_tonality_over_time()
        ft_over_time = self.get_tone_frequency_over_time()
        time_scale_tonality = self.get_tonality_time_scale()
        time_scale_ft = self.get_tone_frequency_time_scale()
        tonality_unit = self.get_output()[1].unit
        time_unit = self.get_output()[1].time_freq_support.time_frequencies.unit
        frequency_unit = self.get_output()[2].unit

        # Plot ECMA-418-2 parameters over time.
        _, axes = plt.subplots(2, 1, sharex=True)
        axes[0].plot(time_scale_tonality, tonality_over_time)
        axes[0].set_title("ECMA-418-2 psychoacoustic tonality")
        axes[0].set_ylabel(f"T ({tonality_unit})")
        axes[0].grid(True)

        axes[1].plot(time_scale_ft, ft_over_time)
        axes[1].set_title("ECMA-418-2 tone frequency")
        axes[1].set_ylabel(r"$\mathregular{f_{ton}}$" + f" ({frequency_unit})")
        axes[1].grid(True)
        axes[1].set_xlabel(f"Time ({time_unit})")

        plt.tight_layout()
        plt.show()
