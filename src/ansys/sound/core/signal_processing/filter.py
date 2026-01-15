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

"""Filter a signal."""

import warnings

from ansys.dpf.core import Field, Operator, TimeFreqSupport, fields_factory, locations
import matplotlib.pyplot as plt
import numpy as np

from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning, scipy_required
from ..signal_processing import SignalProcessingParent

ID_OPERATOR_DESIGN = "filter_design_minimum_phase_FIR_filter_from_FRF"
ID_OPERATOR_LOAD = "load_FRF_from_txt"
ID_OPERATOR_FILTER = "filter_signal"


class Filter(SignalProcessingParent):
    r"""Filter class.

    This class allows designing, loading, and applying a digital filter to a signal. The filter
    coefficients can be provided directly, using the attributes :attr:`b_coefficients` and
    :attr:`a_coefficients`, or computed from a specific frequency response function (FRF), using
    the attribute :attr:`frf` or the method :meth:`design_FIR_from_FRF_file`. In this latter case,
    the filter is designed as a minimum-phase FIR filter, and the filter denominator
    (:attr:`a_coefficients`) is set to 1 as a consequence.

    Note that only one filter definition source (coefficients, FRF, or FRF file) can be provided
    when instantiating the class. After class instantiation, any time the coefficients are
    changed, the FRF is updated accordingly, and vice versa.

    Filtering a signal consists of applying the filter coefficients :math:`b[k]` and :math:`a[k]`
    in the following difference equation, with :math:`x[n]` the input signal, and :math:`y[n]` the
    output signal:

    .. math::
        y[n] = \sum_{k=0}^{N} b[k] \cdot x[n-k] - \sum_{k=1}^{N} a[k] \cdot y[n-k]

    .. note::
        Whether they are derived from the provided FRF or specified directly, the filter
        coefficients are linked to the sampling frequency value that is given in the
        ``sampling_frequency`` parameter of the ``Filter`` class. As a consequence, the signal to
        filter :attr:`signal` must have the same sampling frequency. If necessary, use the
        :class:`.Resample` class to resample the signal prior to using the ``Filter`` class.

    .. seealso::
        :class:`.Resample`

    Examples
    --------
    Filter a signal according to a given frequency response function (FRF).

    >>> from ansys.sound.core.signal_processing import Filter
    >>> filter = Filter(
    ...     frf=my_frf,
    ...     sampling_frequency=44100.0,
    ...     signal=my_signal,
    ... )
    >>> filter.process()
    >>> filtered_signal = filter.get_output()
    >>> filter.plot()

    Create a digital filter from a set of numerator and denominator coefficients, display
    the resulting frequency response function (FRF), and apply the filter to a signal.

    >>> from ansys.sound.core.signal_processing import Filter
    >>> filter = Filter(
    ...     b_coefficients=[0.2, 0.2, 0.2, 0.2, 0.2],
    ...     a_coefficients=[1.0],
    ...     sampling_frequency=44100.0,
    ... )
    >>> filter.plot_FRF()
    >>> filter.signal = my_signal
    >>> filter.process()
    >>> filtered_signal = filter.get_output()
    >>> filter.plot()
    """

    def __init__(
        self,
        b_coefficients: list[float] = None,
        a_coefficients: list[float] = None,
        sampling_frequency: float = 44100.0,
        frf: Field = None,
        file: str = "",
        signal: Field = None,
    ):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        a_coefficients : list[float], default: None
            Denominator coefficients of the filter. This is mutually exclusive with parameters
            ``frf`` and ``file``.
        b_coefficients : list[float], default: None
            Numerator coefficients of the filter. This is mutually exclusive with parameters ``frf``
            and ``file``.
        sampling_frequency : float, default: 44100.0
            Sampling frequency associated with the filter coefficients, in Hz.
        frf : Field, default: None
            Frequency response function (FRF) of the filter, in dB. This is mutually exclusive with
            parameters ``a_coefficients``, ``b_coefficients``, and ``file``.
        file : str, default: ""
            Path to the file containing the frequency response function (FRF) to load. The text
            file shall have the same text format (with the header `AnsysSound_FRF`), as supported
            by Ansys Sound SAS. This is mutually exclusive with parameters ``a_coefficients``,
            ``b_coefficients``, and ``frf``.
        signal : Field, default: None
            Signal to filter.
        """
        super().__init__()

        self.__operator_design = Operator(ID_OPERATOR_DESIGN)
        self.__operator_load = Operator(ID_OPERATOR_LOAD)
        self.__operator_filter = Operator(ID_OPERATOR_FILTER)

        self.__sampling_frequency = sampling_frequency

        # Initialize attributes before processing arguments (because of their mutual dependencies).
        self.__a_coefficients = None
        self.__b_coefficients = None
        self.__frf = None

        # Check which filter definition source (coefficients, FRF, or FRF file) is provided (there
        # should be less than 2).
        is_coefficients_specified = not (a_coefficients is None and b_coefficients is None)
        is_frf_specified = frf is not None
        is_frf_file_specified = file != ""
        if (is_coefficients_specified + is_frf_specified + is_frf_file_specified) > 1:
            raise PyAnsysSoundException(
                "Only one filter definition source (coefficients, FRF, or FRF file) must be "
                "provided. Specify either `a_coefficients` and `b_coefficients`, `frf`, or `file`."
            )
        elif a_coefficients is not None or b_coefficients is not None:
            self.a_coefficients = a_coefficients
            self.b_coefficients = b_coefficients
        elif frf is not None:
            self.frf = frf
        elif file != "":
            self.design_FIR_from_FRF_file(file)

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

        # Update the FRF to match the new coefficients (if both are set).
        self.__compute_FRF_from_coefficients()

    @property
    def b_coefficients(self) -> list[float]:
        """Numerator coefficients of the filter's transfer function."""
        return self.__b_coefficients

    @b_coefficients.setter
    def b_coefficients(self, coefficients: list[float]):
        """Set filter's numerator coefficients."""
        self.__b_coefficients = coefficients

        # Update the FRF to match the new coefficients (if both are set).
        self.__compute_FRF_from_coefficients()

    @property
    def frf(self) -> Field:
        """Frequency response function (FRF) of the filter.

        Contains the response magnitude in dB of the filter as a function of frequency.
        """
        return self.__frf

    @frf.setter
    def frf(self, frf: Field):
        """Set frequency response function."""
        if frf is not None:
            if not (isinstance(frf, Field)):
                raise PyAnsysSoundException("Specified FRF must be provided as a DPF field.")

            freq_data = frf.time_freq_support.time_frequencies.data
            if len(frf.data) < 2 or len(freq_data) < 2:
                raise PyAnsysSoundException(
                    "Specified FRF must have at least two frequency points."
                )
        self.__frf = frf

        # Update coefficients to match the FRF.
        self.__compute_coefficients_from_FRF()

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
        self.frf = self.__operator_load.get_output(0, "field")

    def process(self):
        """Filter the signal with the current coefficients."""
        # Check input signal.
        if self.signal is None:
            raise PyAnsysSoundException(
                f"Input signal is not set. Use `{__class__.__name__}.signal`."
            )

        if self.a_coefficients is None or len(self.a_coefficients) == 0:
            raise PyAnsysSoundException(
                "Filter's denominator coefficients (a_coefficients) must be defined and cannot be "
                f"empty. Use `{__class__.__name__}.a_coefficients`, "
                f"`{__class__.__name__}.frf`, or the "
                f"`{__class__.__name__}.design_FIR_from_FRF_file()` method."
            )

        if self.b_coefficients is None or len(self.b_coefficients) == 0:
            raise PyAnsysSoundException(
                "Filter's numerator coefficients (b_coefficients) must be defined and cannot be "
                f"empty. Use `{__class__.__name__}.b_coefficients`, "
                f"`{__class__.__name__}.frf`, or the "
                f"`{__class__.__name__}.design_FIR_from_FRF_file()` method."
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
                    f"Use the `{__class__.__name__}.process()` method."
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
                f"Output is not processed yet. Use the `{__class__.__name__}.process()` method."
            )
        output = self.get_output()

        time = output.time_freq_support.time_frequencies

        plt.plot(time.data, output.data)
        plt.title("Filtered signal")
        plt.xlabel(f"Time ({time.unit})")
        plt.ylabel(f"Amplitude ({output.unit})")
        plt.grid(True)
        plt.show()

    def plot_FRF(self):
        """Plot the frequency response function (FRF) of the filter."""
        if self.frf is None:
            raise PyAnsysSoundException(
                "Filter's frequency response function (FRF) is not set. Use "
                f"`{__class__.__name__}.frf`, or `{__class__.__name__}.a_coefficients` and "
                f"`{__class__.__name__}.b_coefficients`, or the "
                f"`{__class__.__name__}.design_FIR_from_FRF_file()` method."
            )
        frequencies = self.frf.time_freq_support.time_frequencies

        plt.plot(frequencies.data, self.frf.data)
        plt.title("Frequency response function (FRF) of the filter")
        plt.xlabel(f"Frequency ({frequencies.unit})")
        plt.ylabel(f"Magnitude ({self.frf.unit})")
        plt.grid(True)
        plt.show()

    def __compute_coefficients_from_FRF(self):
        """Design a minimum-phase FIR filter from the frequency response function (FRF).

        Computes the filter coefficients according to the filter sampling frequency and the
        currently set FRF.

        .. note::
            If the maximum frequency in the FRF extends beyond half the filter sampling frequency,
            the FRF data is truncated to this frequency to compute the coefficients. If, on the
            contrary, the FRF maximum frequency is lower than half the filter sampling frequency,
            the FRF data is zero-padded between the two.
        """
        if self.frf is None:
            self.__a_coefficients = None
            self.__b_coefficients = None
        else:
            self.__operator_design.connect(0, self.frf)
            self.__operator_design.connect(1, self.__sampling_frequency)

            self.__operator_design.run()

            # Bypass the coefficients setters to avoid infinite loops.
            self.__b_coefficients = list(
                map(float, self.__operator_design.get_output(0, "vec_double"))
            )
            self.__a_coefficients = list(
                map(float, self.__operator_design.get_output(1, "vec_double"))
            )

    @scipy_required
    def __compute_FRF_from_coefficients(self):
        """Compute the frequency response function (FRF) from the filter coefficients.

        Computes the FRF from the filter coefficients, using the function ``scipy.signal.freqz()``.
        If either the numerator or denominator coefficients are empty or not set, the FRF is set to
        ``None``.

        .. note::
            The computed FRF length is equal to the number of coefficients in the filter's
            numerator.
        """
        if (
            self.b_coefficients is None
            or self.a_coefficients is None
            or len(self.b_coefficients) == 0
            or len(self.a_coefficients) == 0
        ):
            self.__frf = None
        else:
            import scipy

            freq, complex_response = scipy.signal.freqz(
                b=self.b_coefficients,
                a=self.a_coefficients,
                worN=len(self.b_coefficients),
                whole=False,
                plot=None,
                fs=self.__sampling_frequency,
                include_nyquist=True,
            )

            f_freq = fields_factory.create_scalar_field(
                num_entities=1, location=locations.time_freq
            )
            f_freq.append(freq, 1)

            frf_support = TimeFreqSupport()
            frf_support.time_frequencies = f_freq

            # Bypass the FRF setter to avoid infinite loops.
            self.__frf = fields_factory.create_scalar_field(
                num_entities=1, location=locations.time_freq
            )
            self.__frf.append(20 * np.log10(abs(complex_response)), 1)
            self.__frf.time_freq_support = frf_support
