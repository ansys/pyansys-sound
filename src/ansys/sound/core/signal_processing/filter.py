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

"""Filter a signal."""

import warnings

from ansys.dpf.core import Field, Operator
import matplotlib.pyplot as plt
import numpy as np

from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from ..signal_processing import SignalProcessingParent

ID_OPERATOR_DESIGN = "filter_design_minimum_phase_FIR_filter_from_FRF"
ID_OPERATOR_LOAD = "load_FRF_from_txt"
ID_OPERATOR_FILTER = "filter_signal"


class Filter(SignalProcessingParent):
    r"""Filter class.

    This class allows designing, loading, and applying a digital filter to a signal. The filter
    coefficients can be provided directly, using the attributes :attr:`b_coefficients` and
    :attr:`a_coefficients`, or computed from a specific frequency response function (FRF), using
    the methods :meth:`design_FIR_from_FRF` or :meth:`design_FIR_from_FRF_file`. In this latter
    case, the filter is designed as a minimum-phase FIR filter, and the filter denominator
    (:attr:`a_coefficients`) is set to 1 as a consequence.

    Filtering a signal consists in applying the filter coefficients :math:`b[k]` and :math:`a[k]`
    in the following difference equation, with :math:`x[n]` the input signal, and :math:`y[n]` the
    output signal:

    .. math::
        y[n] = \sum_{k=0}^{N} b[k] \cdot x[n-k] - \sum_{k=1}^{N} a[k] \cdot y[n-k]

    .. note::
        Whether they are derived from the provided FRF or specified directly, the filter
        coefficients are linked to the sampling frequency value that is given in the parameter
        ``sampling_frequency`` of the ``Filter`` class. As a consequence, the signal to filter
        :attr:`signal` must have the same sampling frequency. If necessary, use the
        :class:`.Resample` class to resample the signal prior to using the ``Filter`` class.
    """

    def __init__(
        self,
        b_coefficients: list[float] = None,
        a_coefficients: list[float] = None,
        sampling_frequency: float = 44100.0,
        file: str = "",
        signal: Field = None,
    ):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        a_coefficients : list[float], default: None
            Denominator coefficients of the filter.
        b_coefficients : list[float], default: None
            Numerator coefficients of the filter.
        sampling_frequency : float, default: 44100.0
            Sampling frequency associated with the filter coefficients, in Hz.
        file : str, default: ""
            Path to the file containing the frequency response function (FRF) to load. The text
            file shall have the same text format (with the header `AnsysSound_FRF`), as supported
            by Ansys Sound SAS. If ``file`` is specified, parameters ``a_coefficients`` and
            ``b_coefficients`` are ignored.
        signal : Field, default: None
            Signal to filter.
        """
        super().__init__()

        self.__operator_design = Operator(ID_OPERATOR_DESIGN)
        self.__operator_load = Operator(ID_OPERATOR_LOAD)
        self.__operator_filter = Operator(ID_OPERATOR_FILTER)

        self.__sampling_frequency = sampling_frequency

        if file != "":
            if a_coefficients is not None or b_coefficients is not None:
                warnings.warn(
                    PyAnsysSoundWarning(
                        "Specified parameters a_coefficients and b_coefficients are ignored "
                        "because FRF file is also specified."
                    )
                )
            self.design_FIR_from_FRF_file(file)
        else:
            self.a_coefficients = a_coefficients
            self.b_coefficients = b_coefficients

        self.signal = signal

    def __str__(self) -> str:
        """Return the string representation of the object."""
        if self.a_coefficients is None:
            str_a = "Not set"
        elif len(self.a_coefficients) > 5:
            str_a = str(self.a_coefficients[:5])[:-1] + ", ... ]"
        else:
            str_a = str(self.a_coefficients)

        if self.b_coefficients is None:
            str_b = "Not set"
        elif len(self.b_coefficients) > 5:
            str_b = str(self.b_coefficients[:5])[:-1] + ", ... ]"
        else:
            str_b = str(self.b_coefficients)

        return (
            f"Sampling frequency: {self.__sampling_frequency:.1f} Hz\n"
            f"Numerator coefficients (B): {str_b}\n"
            f"Denominator coefficients (A): {str_a}"
        )

    @property
    def a_coefficients(self) -> list[float]:
        """Denominator coefficients of the filter's transfer function."""
        return self.__a_coefficients

    @a_coefficients.setter
    def a_coefficients(self, coefficients: list[float]):
        """Set filter's denominator coefficients."""
        self.__a_coefficients = coefficients

    @property
    def b_coefficients(self) -> list[float]:
        """Numerator coefficients of the filter's transfer function."""
        return self.__b_coefficients

    @b_coefficients.setter
    def b_coefficients(self, coefficients: list[float]):
        """Set filter's numerator coefficients."""
        self.__b_coefficients = coefficients

    @property
    def signal(self) -> Field:
        """Input signal."""
        return self.__signal

    @signal.setter
    def signal(self, signal: Field):
        """Set input signal."""
        if signal is not None:
            if not (isinstance(signal, Field)):
                raise PyAnsysSoundException("Specified signal must be provided as a DPF field.")

            time_data = signal.time_freq_support.time_frequencies.data
            if len(signal.data) < 2 or len(time_data) < 2:
                raise PyAnsysSoundException("Specified signal must have at least two samples.")

            signal_fs = 1 / (time_data[1] - time_data[0])
            if np.round(signal_fs, 1) != np.round(self.__sampling_frequency, 1):
                raise PyAnsysSoundException(
                    f"Specified signal's sampling frequency ({signal_fs:.1f} Hz) must match the "
                    f"filter's sampling frequency ({self.__sampling_frequency:.1f} Hz) that was "
                    f"specified as an instantiation argument of the class {__class__.__name__}."
                )
        self.__signal = signal

    def get_sampling_frequency(self) -> float:
        """Get the filter sampling frequency.

        Returns
        -------
        float
            Sampling frequency, in Hz, associated with the filter coefficients.
        """
        return self.__sampling_frequency

    def design_FIR_from_FRF_file(self, file: str):
        """Design a minimum-phase FIR filter from a frequency response function (FRF) file.

        Computes the filter coefficients according to the filter sampling frequency and the FRF
        data that is loaded from the specified file.

        .. note::
            If the maximum frequency specified in the FRF file extends beyond half the filter
            sampling frequency, the FRF data is truncated to this frequency. If, on the contrary,
            the FRF file's maximum frequency is lower than half the filter sampling frequency, the
            FRF is zero-padded between the two.

        Parameters
        ----------
        file : str
            Path to the file containing the frequency response function (FRF) to load. The text
            file shall have the same text format (with the header `AnsysSound_FRF`), as supported
            by Ansys Sound SAS.
        """
        # Set operator inputs.
        self.__operator_load.connect(0, file)

        # Run the operator.
        self.__operator_load.run()

        # Get the output.
        frf = self.__operator_load.get_output(0, "field")

        # Compute the filter coefficients.
        self.design_FIR_from_FRF(frf)

    def design_FIR_from_FRF(self, frf: Field):
        """Design a minimum-phase FIR filter from a frequency response function (FRF).

        Computes the filter coefficients according to the filter sampling frequency and the
        provided FRF data.

        .. note::
            If the maximum frequency specified in the FRF extends beyond half the filter sampling
            frequency, the FRF data is truncated to this frequency. If, on the contrary, the FRF
            maximum frequency is lower than half the filter sampling frequency, the FRF is
            zero-padded between the two.

        Parameters
        ----------
        frf : Field
            Frequency response function (FRF).
        """
        # Set operator inputs.
        self.__operator_design.connect(0, frf)
        self.__operator_design.connect(1, self.__sampling_frequency)

        # Run the operator.
        self.__operator_design.run()

        # Get the output.
        self.b_coefficients = list(map(float, self.__operator_design.get_output(0, "vec_double")))
        self.a_coefficients = list(map(float, self.__operator_design.get_output(1, "vec_double")))

    def process(self):
        """Filter the signal with the current coefficients."""
        # Check input signal.
        if self.signal is None:
            raise PyAnsysSoundException(
                f"Input signal is not set. Use {__class__.__name__}.signal."
            )

        if self.a_coefficients is None or len(self.a_coefficients) == 0:
            raise PyAnsysSoundException(
                "Filter's denominator coefficients (a_coefficients) must be defined and cannot be "
                f"empty. Use {__class__.__name__}.a_coefficients, or the methods "
                f"{__class__.__name__}.design_FIR_from_FRF() or "
                f"{__class__.__name__}.design_FIR_from_FRF_file()."
            )

        if self.b_coefficients is None or len(self.b_coefficients) == 0:
            raise PyAnsysSoundException(
                "Filter's numerator coefficients (b_coefficients) must be defined and cannot be "
                f"empty. Use {__class__.__name__}.b_coefficients, or the methods "
                f"{__class__.__name__}.design_FIR_from_FRF() or "
                f"{__class__.__name__}.design_FIR_from_FRF_file()."
            )

        # Set operator inputs.
        self.__operator_filter.connect(0, self.signal)
        self.__operator_filter.connect(1, list(self.b_coefficients))
        self.__operator_filter.connect(2, list(self.a_coefficients))

        # Run the operator.
        self.__operator_filter.run()

        # Get the output.
        self._output = self.__operator_filter.get_output(0, "field")

    def get_output(self) -> Field:
        """Get the filtered signal as a DPF field.

        Returns
        -------
        Field
            Filtered signal as a DPF field.
        """
        if self._output == None:
            warnings.warn(
                PyAnsysSoundWarning(
                    "Output is not processed yet. "
                    f"Use the {__class__.__name__}.process() method."
                )
            )
        return self._output

    def get_output_as_nparray(self) -> np.ndarray:
        """Get the filtered signal as a NumPy array.

        Returns
        -------
        numpy.ndarray
            Filtered signal as a NumPy array.
        """
        output = self.get_output()

        if output == None:
            return np.array([])

        return np.array(output.data)

    def plot(self):
        """Plot the filtered signal in a figure."""
        if self._output == None:
            raise PyAnsysSoundException(
                f"Output is not processed yet. Use the {__class__.__name__}.process() method."
            )
        output = self.get_output()

        time_data = output.time_freq_support.time_frequencies.data

        plt.plot(time_data, output.data)
        plt.title("Filtered signal")
        plt.xlabel("Time (s)")
        plt.ylabel("Amplitude")
        plt.grid(True)
        plt.show()
