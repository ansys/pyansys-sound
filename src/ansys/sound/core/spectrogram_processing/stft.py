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

"""Short-time Fourier transform."""

import warnings

from ansys.dpf.core import Field, FieldsContainer, Operator
import matplotlib.pyplot as plt
import numpy as np

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
        signal: Field | FieldsContainer = None,
        fft_size: int = 2048,
        window_type: str = "HANN",
        window_overlap: float = 0.5,
    ):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        signal : Field | FieldsContainer, default: None
            Input signal on which to compute the STFT.
        fft_size : int, default: 2048
            Size of the FFT to compute the STFT.
            Use a power of 2 for better performance.
        window_type : str, default: 'HANN'
            Window type used for the FFT computation. Options are ``'TRIANGULAR'``, ``'BLACKMAN'``,
            ``'BLACKMANHARRIS'``, ``'HAMMING'``, ``'HANN'``, ``'GAUSS'``, ``'FLATTOP'``, and
            ``'RECTANGULAR'``.
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
        """Input signal.

        Can be provided as a DPF field or fields container, but will be stored as DPF field
        regardless.
        """
        return self.__signal

    @signal.setter
    def signal(self, signal: Field | FieldsContainer):
        """Signal."""
        if type(signal) == FieldsContainer:
            if len(signal) > 1:
                raise PyAnsysSoundException(
                    "Input as a DPF fields container can only have one field (mono signal)."
                )
            else:
                self.__signal = signal[0]
        else:
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
        ``'HANN'``, ``'GAUSS'``, ``'FLATTOP'``, and ``'RECTANGULAR'``.
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
        ]:
            raise PyAnsysSoundException(
                "Window type is invalid. Options are 'TRIANGULAR', 'BLACKMAN', 'BLACKMANHARRIS', "
                "'HAMMING', 'HANN', 'GAUSS', 'FLATTOP' and 'RECTANGULAR'."
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
        if self.signal == None:
            raise PyAnsysSoundException("No signal found for STFT. Use 'Stft.signal'.")

        self.__operator.connect(0, self.signal)
        self.__operator.connect(1, int(self.fft_size))
        self.__operator.connect(2, str(self.window_type))
        self.__operator.connect(3, float(self.window_overlap))

        # Runs the operator
        self.__operator.run()

        # Stores output in the variable
        self._output = self.__operator.get_output(0, "fields_container")

    def get_output(self) -> FieldsContainer:
        """Get the STFT of the signal as a DPF fields container.

        Returns
        -------
        FieldsContainer
            STFT of the signal in a DPF fields container.
        """
        if self._output == None:
            # Computing output if needed
            warnings.warn(PyAnsysSoundWarning("Output is not processed yet. \
                    Use the 'Stft.process()' method."))

        return self._output

    def get_output_as_nparray(self) -> np.ndarray:
        """Get the STFT of the signal as a NumPy array.

        Returns
        -------
        numpy.ndarray
            STFT of the signal in a NumPy array.
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

    def get_stft_magnitude_as_nparray(self) -> np.ndarray:
        """Get the amplitude of the STFT as a NumPy array.

        Returns
        -------
        numpy.ndarray
            Amplitude of the STFT in a NumPy array.
        """
        output = self.get_output_as_nparray()
        return np.absolute(output)

    def get_stft_phase_as_nparray(self) -> np.ndarray:
        """Get the phase of the STFT as a NumPy array.

        Returns
        -------
        numpy.ndarray
            Phase of the STFT in a NumPy array.
        """
        output = self.get_output_as_nparray()
        return np.arctan2(np.imag(output), np.real(output))

    def plot(self):
        """Plot signals.

        This method plots the STFT amplitude and the associated phase.
        """
        if self._output is None:
            raise PyAnsysSoundException(
                f"Output is not processed yet. Use the `{__class__.__name__}.process()` method."
            )
        magnitude = self.get_stft_magnitude_as_nparray()
        mag_unit = self.get_output()[0].unit
        freq_unit = self.get_output()[0].time_freq_support.time_frequencies.unit
        time_unit = self.get_output().time_freq_support.time_frequencies.unit

        # Only extract the first half of the STFT, as it is symmetrical
        half_nfft = int(np.shape(magnitude)[0] / 2) + 1

        np.seterr(divide="ignore")
        magnitude = 20 * np.log10(magnitude[0:half_nfft, :])
        np.seterr(divide="warn")
        phase = self.get_stft_phase_as_nparray()
        phase = phase[0:half_nfft, :]
        time_data_signal = self.signal.time_freq_support.time_frequencies.data
        time_step = time_data_signal[1] - time_data_signal[0]
        fs = 1.0 / time_step

        time_data_spectrogram = self.get_output().time_freq_support.time_frequencies.data

        # Boundaries of the plot
        extent = [time_data_spectrogram[0], time_data_spectrogram[-1], 0.0, fs / 2.0]

        # Plotting
        f, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
        p = ax1.imshow(magnitude, origin="lower", aspect="auto", cmap="jet", extent=extent)
        f.colorbar(p, ax=ax1, label=f"Amplitude ({mag_unit})")
        ax1.set_title("Amplitude")
        ax1.set_ylabel(f"Frequency ({freq_unit})")
        p = ax2.imshow(phase, origin="lower", aspect="auto", cmap="jet", extent=extent)
        f.colorbar(p, ax=ax2, label="Phase (rad)")
        ax2.set_title("Phase")
        ax2.set_xlabel(f"Time ({time_unit})")
        ax2.set_ylabel(f"Frequency ({freq_unit})")

        f.suptitle("STFT")
        plt.show()
