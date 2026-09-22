# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

"""Short-time Fourier transform."""

import warnings

from ansys.dpf.core import Field, FieldsContainer, Operator, types
import matplotlib.pyplot as plt
import numpy as np

from ansys.sound.core.server_helpers._check_version import _check_sound_version

from . import SpectrogramProcessingParent
from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning


class Stft(SpectrogramProcessingParent):
    """Compute the short-time Fourier transform (STFT) of a signal.

    .. seealso::
        :class:`Istft`, :class:`PowerSpectralDensity`

    Examples
    --------
    Compute the STFT of a signal, and display the resulting spectrogram in a colormap.

    >>> from ansys.sound.core.spectrogram_processing import Stft
    >>> stft = Stft(signal=signal)
    >>> stft.process()
    >>> spectrogram = stft.get_output()
    >>> stft.plot()

    .. seealso::
        :ref:`compute_stft_example`
            Example demonstrating how to compute the STFT and ISTFT.
    """

    def __init__(
        self,
        signal: Field = None,
        fft_size: int = 2048,
        window_type: str = "HANN",
        window_overlap: float = 0.5,
    ):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        signal : Field, default: None
            Input signal on which to compute the STFT.
        fft_size : int, default: 2048
            Size of the FFT to compute the STFT.
            Use a power of 2 for better performance.
        window_type : str, default: 'HANN'
            Window type used for the FFT computation. Options are ``'TRIANGULAR'``, ``'BLACKMAN'``,
            ``'BLACKMANHARRIS'``, ``'HAMMING'``, ``'HANN'``, ``'GAUSS'``, ``'FLATTOP'``,
            ``'RECTANGULAR'``, and ``'BARTLETT'``.
        window_overlap : float, default: 0.5
            Overlap value between two successive FFT computations. Values can range from 0 to 1.
            For example, ``0`` means no overlap, and ``0.5`` means 50% overlap.
        """
        super().__init__()
        self.signal = signal
        self.fft_size = fft_size
        self.window_overlap = window_overlap
        self.window_type = window_type
        self.__operator = Operator("compute_stft")

    @property
    def signal(self) -> Field:
        """Input signal as a DPF field."""
        return self.__signal

    @signal.setter
    def signal(self, signal: Field):
        """Signal."""
        if signal is not None and not isinstance(signal, Field):
            raise PyAnsysSoundException("Input signal must be provided as a DPF Field.")

        self.__signal = signal

    @property
    def fft_size(self) -> int:
        """Number of FFT points."""
        return self.__fft_size

    @fft_size.setter
    def fft_size(self, fft_size: int):
        """Set the FFT size."""
        if fft_size < 0:
            raise PyAnsysSoundException("FFT size must be greater than 0.0.")
        self.__fft_size = fft_size

    @property
    def window_type(self) -> str:
        """Window type.

        Supported options are ``'TRIANGULAR'``, ``'BLACKMAN'``, ``'BLACKMANHARRIS'``, ``'HAMMING'``,
        ``'HANN'``, ``'GAUSS'``, ``'FLATTOP'``, ``'RECTANGULAR'``, and ``'BARTLETT'``.
        """
        return self.__window_type

    @window_type.setter
    def window_type(self, window_type: str):
        """Set the window type."""
        if window_type not in [
            "TRIANGULAR",
            "BLACKMAN",
            "BLACKMANHARRIS",
            "HAMMING",
            "HANN",
            "GAUSS",
            "FLATTOP",
            "RECTANGULAR",
            "BARTLETT",
        ]:
            raise PyAnsysSoundException(
                "Window type is invalid. Options are 'TRIANGULAR', 'BLACKMAN', 'BLACKMANHARRIS', "
                "'HAMMING', 'HANN', 'GAUSS', 'FLATTOP', 'RECTANGULAR', and 'BARTLETT'."
            )

        self.__window_type = window_type

    @property
    def window_overlap(self) -> float:
        """Window overlap in %."""
        return self.__window_overlap

    @window_overlap.setter
    def window_overlap(self, window_overlap: float):
        """Window overlap."""
        if window_overlap < 0.0 or window_overlap > 1.0:
            raise PyAnsysSoundException("Window overlap must be between 0.0 and 1.0.")

        self.__window_overlap = window_overlap

    def process(self):
        """Compute the STFT.

        This method calls the appropriate DPF Sound operator to compute the STFT of the signal.
        """
        if self.signal is None:
            raise PyAnsysSoundException("No signal found for STFT. Use 'Stft.signal'.")

        self.__operator.connect(0, self.signal)
        self.__operator.connect(1, int(self.fft_size))
        self.__operator.connect(2, str(self.window_type))
        self.__operator.connect(3, float(self.window_overlap))

        # Runs the operator
        self.__operator.run()

        # Stores output in the variable
        self._output = self.__operator.get_output(0, types.fields_container)

    def get_output(self) -> FieldsContainer:
        """Get the STFT of the signal as a DPF fields container.

        Returns
        -------
        FieldsContainer
            Complex STFT, as a fields container, indexed by labels "time" and "complex". Each
            indexed field corresponds to the real or imaginary part of a time-wise STFT slice.

            The label "complex" indicates whether the field corresponds to the real (0) or imaginary
            (1) part of the STFT slice. The module of each STFT slice is a two-sided RMS spectrum
            between 0 Hz and the sampling frequency, at a specific time, as indexed with label
            "time". The spectrum values are in the input signal's unit.

            The support of the fields container, labeled "time", provides the actual time values, in
            seconds, corresponding to each "time" label index.

            For more information, see `RMS spectrum <https://ansyshelp.ansys.com/public/account/
            secured?returnurl=/Views/Secured/corp/v261/en/Sound_SAS_UG/Sound/UG_SAS/
            rms_spectrum.html>`_.

        Notes
        -----
        Prior to Sound version 2027.1.0, RMS spectrum scaling is not applied in the returned STFT.
        As a consequence, the stored STFT values are not in the input signal's unit if the used
        Sound version is not 2027.1.0 or higher. In such case, to scale the STFT values, you need to
        divide them by the sum of the values of the window function that is specified with
        attributes :attr:`window_type` and :attr:`fft_size` (the window size is equal to the FFT
        size in :attr:`fft_size`).
        """
        if self._output == None:
            warnings.warn(PyAnsysSoundWarning("Output is not processed yet. \
                    Use the 'Stft.process()' method."))

        if not _check_sound_version("2027.1.0"):
            warnings.warn(
                PyAnsysSoundWarning(
                    "Output STFT is not scaled for RMS spectrum in Sound version prior to "
                    "2027.1.0. You can scale it by dividing the STFT values by the sum of the "
                    "window values."
                )
            )

        return self._output

    def get_output_as_nparray(self) -> np.ndarray:
        """Get the STFT of the signal as a NumPy array.

        Returns
        -------
        numpy.ndarray
            Complex STFT of the signal, in the signal's unit. The returned STFT is one-sided, which
            means it only contains the positive frequency components up to half the signal's
            sampling frequency.

        Notes
        -----
        Prior to Sound version 2027.1.0, RMS spectrum scaling is not applied in the returned STFT.
        As a consequence, the stored STFT values are not in the input signal's unit if the used
        Sound version is not 2027.1.0 or higher. In such case, to scale the STFT values, you need to
        divide them by the sum of the values of the window function that is specified with
        attributes :attr:`window_type` and :attr:`fft_size` (the window size is equal to the FFT
        size in :attr:`fft_size`).
        """
        output = self.get_output()

        time_indexes = output.get_available_ids_for_label("time")
        Ntime = len(time_indexes)
        Nfft = output.get_field({"complex": 0, "time": 0, "channel_number": 0}).data.shape[0]

        # Pre-allocate memory for the output array.
        out_as_np_array = np.empty((Ntime, Nfft), dtype=np.complex128)

        for i in time_indexes:
            f1 = output.get_field({"complex": 0, "time": i, "channel_number": 0})
            f2 = output.get_field({"complex": 1, "time": i, "channel_number": 0})
            out_as_np_array[i] = f1.data + 1j * f2.data

        return np.transpose(out_as_np_array)

    def get_magnitude(self) -> np.ndarray:
        """Get the magnitude of the STFT.

        Returns
        -------
        numpy.ndarray
            Magnitude of the STFT, in the input signal's unit. The returned STFT magnitude is
            one-sided, which means it only contains the positive frequency components up to half the
            signal's sampling  frequency.

        Notes
        -----
        Prior to Sound version 2027.1.0, RMS spectrum scaling is not applied in the returned STFT.
        As a consequence, the stored STFT values are not in the input signal's unit if the used
        Sound version is not 2027.1.0 or higher. In such case, to scale the STFT values, you need to
        divide them by the sum of the values of the window function that is specified with
        attributes :attr:`window_type` and :attr:`fft_size` (the window size is equal to the FFT
        size in :attr:`fft_size`).
        """
        output = self.get_output_as_nparray()

        # Only extract the first half of the two-sided STFT, as it is symmetrical
        half_nfft = int(np.floor(output.shape[0] / 2)) + 1

        # Scale the STFT by sqrt(2) to account for the energy sum of the positive and negative
        # frequency bins (two-sided to one-sided STFT conversion).
        output = np.sqrt(2) * output[:half_nfft, :]

        return np.absolute(output)

    def get_phase(self) -> np.ndarray:
        """Get the phase of the STFT.

        Returns
        -------
        numpy.ndarray
            Phase of the STFT, in rad. The returned STFT phase is one-sided, which means it only
            contains the positive frequency components up to half the signal's sampling frequency.
        """
        output = self.get_output_as_nparray()

        # Only extract the first half of the two-sided STFT, as it is symmetrical
        half_nfft = int(np.floor(output.shape[0] / 2)) + 1

        return np.angle(output[:half_nfft, :])

    def plot(self, reference_value: float = 1.0):
        """Plot signals.

        This method plots the STFT magnitude and the associated phase.

        Parameters
        ----------
        reference_value : float, default: 1.0
            STFT reference value for dB conversion. For example, for an input sound pressure signal,
            the reference value is typically 2e-5 (Pa).

        Notes
        -----
        Prior to Sound version 2027.1.0, RMS spectrum scaling is not applied in the returned STFT.
        As a consequence, the displayed STFT magnitude will be incorrect with Sound versions prior
        to 2027.1.0.
        """
        if self._output is None:
            raise PyAnsysSoundException(
                f"Output is not processed yet. Use the `{__class__.__name__}.process()` method."
            )

        if reference_value <= 0:
            raise PyAnsysSoundException(
                "Reference value for dB conversion must be strictly greater than 0."
            )

        unit = self.get_output()[0].unit
        linear_unit = unit if isinstance(unit, str) else unit[1]
        frequency_unit = self.get_output()[0].time_freq_support.time_frequencies.unit
        time_unit = self.get_output().time_freq_support.time_frequencies.unit

        np.seterr(divide="ignore")
        magnitude_dB = 20 * np.log10(self.get_magnitude() / reference_value)
        np.seterr(divide="warn")
        phase = self.get_phase()
        time_data_signal = self.signal.time_freq_support.time_frequencies.data
        time_step = time_data_signal[1] - time_data_signal[0]
        fs = 1.0 / time_step

        time_data_spectrogram = self.get_output().time_freq_support.time_frequencies.data

        # Boundaries of the plot
        extent = [time_data_spectrogram[0], time_data_spectrogram[-1], 0.0, fs / 2.0]

        # Plotting
        f, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
        p = ax1.imshow(magnitude_dB, origin="lower", aspect="auto", cmap="jet", extent=extent)
        f.colorbar(p, ax=ax1, label=f"Amplitude (dB re. {reference_value} {linear_unit})")
        ax1.set_title("Amplitude")
        ax1.set_ylabel(f"Frequency ({frequency_unit})")
        p = ax2.imshow(phase, origin="lower", aspect="auto", cmap="jet", extent=extent)
        f.colorbar(p, ax=ax2, label="Phase (rad)")
        ax2.set_title("Phase")
        ax2.set_xlabel(f"Time ({time_unit})")
        ax2.set_ylabel(f"Frequency ({frequency_unit})")

        f.suptitle("STFT")
        plt.show()
