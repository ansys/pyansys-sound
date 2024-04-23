"""Short-time Fourier Transform."""

import warnings

from ansys.dpf.core import Field, FieldsContainer, Operator
import matplotlib.pyplot as plt
import numpy as np
from numpy import typing as npt

from . import SpectrogramProcessingParent
from ..pydpf_sound import PyDpfSoundException, PyDpfSoundWarning


class Stft(SpectrogramProcessingParent):
    """Short-time Fourier Transform.

    This class computes the STFT (Short-time Fourier transform) of a signal.
    """

    def __init__(
        self,
        signal: Field | FieldsContainer = None,
        fft_size: float = 2048,
        window_type: str = "HANN",
        window_overlap: float = 0.5,
    ):
        """Create an STFT class.

        Parameters
        ----------
        signal:
            Mono signal on which to compute the STFT as a DPF Field or Fields Container.
        fft_size:
            Size (as an integer) of the FFT to compute the STFT.
            Use a power of 2 for better performance.
        window_type:
            The window used for the FFT computation, as a string.
            Allowed input strings are :
            'HANNING', 'BLACKMANHARRIS', 'HANN','BLACKMAN', 'HAMMING', 'KAISER', 'BARTLETT' and
            'RECTANGULAR'.
            If no parameter is specified, the default value is 'HANNING'.
        window_overlap:
            The overlap value between two successive FFT computations (value between 0 and 1).
            0 means no overlap, 0.5 means 50 % overlap.
            If no parameter is specified, default value is 0.5.
        """
        super().__init__()
        self.signal = signal
        self.fft_size = fft_size
        self.window_overlap = window_overlap
        self.window_type = window_type
        self.__operator = Operator("compute_stft")

    @property
    def signal(self):
        """Signal property."""
        return self.__signal  # pragma: no cover

    @signal.setter
    def signal(self, signal: Field | FieldsContainer):
        """Set the signal."""
        if type(signal) == FieldsContainer:
            if len(signal) > 1:
                raise PyDpfSoundException(
                    "Input as FieldsContainer can only have one Field (mono signal)."
                )
            else:
                self.__signal = signal[0]
        else:
            self.__signal = signal

    @signal.getter
    def signal(self) -> Field:
        """Get the signal.

        Returns
        -------
        Field
                The signal as a Field.
        """
        return self.__signal

    @property
    def fft_size(self):
        """Fft size property."""
        return self.__fft_size  # pragma: no cover

    @fft_size.setter
    def fft_size(self, fft_size):
        """Set the fft size."""
        if fft_size < 0:
            raise PyDpfSoundException("Fft size must be greater than 0.0.")
        self.__fft_size = fft_size

    @fft_size.getter
    def fft_size(self) -> float:
        """Get the fft size.

        Returns
        -------
        float
                The fft size.
        """
        return self.__fft_size

    @property
    def window_type(self):
        """Window type property."""
        return self.__window_type  # pragma: no cover

    @window_type.setter
    def window_type(self, window_type):
        """Set the window type."""
        if (
            window_type != "BLACKMANHARRIS"
            and window_type != "HANN"
            and window_type != "HAMMING"
            and window_type != "HANNING"
            and window_type != "KAISER"
            and window_type != "BARTLETT"
            and window_type != "RECTANGULAR"
        ):
            raise PyDpfSoundException(
                "Invalid window type, accepted values are 'HANNING', 'BLACKMANHARRIS', 'HANN', \
                    'BLACKMAN','HAMMING', 'KAISER', 'BARTLETT', 'RECTANGULAR'."
            )

        self.__window_type = window_type

    @window_type.getter
    def window_type(self) -> float:
        """Get the window type.

        Returns
        -------
        str
                The window type.
        """
        return self.__window_type

    @property
    def window_overlap(self):
        """Window overlap property."""
        return self.__window_overlap  # pragma: no cover

    @window_overlap.setter
    def window_overlap(self, window_overlap):
        """Set the window overlap."""
        if window_overlap < 0.0 or window_overlap > 1.0:
            raise PyDpfSoundException("Window overlap must be between 0.0 and 1.0.")

        self.__window_overlap = window_overlap

    @window_overlap.getter
    def window_overlap(self) -> float:
        """Get the fft size.

        Returns
        -------
        float
                The window overlap.
        """
        return self.__window_overlap

    def process(self):
        """Compute the STFT.

        Calls the appropriate DPF Sound operator to compute the STFT of the signal.
        """
        if self.signal == None:
            raise PyDpfSoundException("No signal for STFT. Use Stft.signal.")

        self.__operator.connect(0, self.signal)
        self.__operator.connect(1, int(self.fft_size))
        self.__operator.connect(2, str(self.window_type))
        self.__operator.connect(3, float(self.window_overlap))

        # Runs the operator
        self.__operator.run()

        # Stores output in the variable
        self._output = self.__operator.get_output(0, "fields_container")

    def get_output(self) -> FieldsContainer:
        """Return the STFT as a fields container.

        Returns
        -------
        FieldsContainer
                The STFT of the signal in a DPF FieldsContainer.
        """
        if self._output == None:
            # Computing output if needed
            warnings.warn(
                PyDpfSoundWarning("Output has not been yet processed, use Stft.process().")
            )

        return self._output

    def get_output_as_nparray(self) -> npt.ArrayLike:
        """Return the STFT of the signal as a numpy array.

        Returns
        -------
        np.array
                The STFT of the signal in a numpy array.
        """
        output = self.get_output()

        num_time_index = len(output.get_available_ids_for_label("time"))

        f1 = output.get_field({"complex": 0, "time": 0, "channel_number": 0})
        f2 = output.get_field({"complex": 1, "time": 0, "channel_number": 0})

        out_as_np_array = f1.data + 1j * f2.data
        for i in range(1, num_time_index):
            f1 = output.get_field({"complex": 0, "time": i, "channel_number": 0})
            f2 = output.get_field({"complex": 1, "time": i, "channel_number": 0})
            tmp_arr = f1.data + 1j * f2.data
            out_as_np_array = np.vstack((out_as_np_array, tmp_arr))

        # return out_as_np_array
        return np.transpose(out_as_np_array)

    def get_stft_magnitude_as_nparray(self) -> npt.ArrayLike:
        """Return the amplitude of the STFT.

        Returns
        -------
        np.array
                The Amplitude of the STFT of the signal in a numpy array.
        """
        output = self.get_output_as_nparray()
        return np.absolute(output)

    def get_stft_phase_as_nparray(self) -> npt.ArrayLike:
        """Return the phase of the STFT.

        Returns
        -------
        np.array
                The Phase of the STFT of the signal in a numpy array.
        """
        output = self.get_output_as_nparray()
        return np.arctan2(np.imag(output), np.real(output))

    def plot(self):
        """Plot signals.

        Plots the STFT amplitude and the associated phase.
        """
        out = self.get_output_as_nparray()

        # Extracting first half of the STFT (second half is symmetrical)
        half_nfft = int(np.shape(out)[0] / 2) + 1
        magnitude = self.get_stft_magnitude_as_nparray()
        magnitude = 20 * np.log10(magnitude[0:half_nfft, :])
        phase = self.get_stft_phase_as_nparray()
        phase = phase[0:half_nfft, :]
        fs = 1.0 / (
            self.signal.time_freq_support.time_frequencies.data[1]
            - self.signal.time_freq_support.time_frequencies.data[0]
        )
        time_step = np.floor(self.fft_size * (1.0 - self.window_overlap) + 0.5) / fs
        num_time_index = len(self.get_output().get_available_ids_for_label("time"))

        # Boundaries of the plot
        extent = [0, time_step * num_time_index, 0.0, fs / 2.0]

        # Plotting
        f, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
        p = ax1.imshow(magnitude, origin="lower", aspect="auto", cmap="jet", extent=extent)
        f.colorbar(p, ax=ax1, label="dB")
        ax1.set_title("Amplitude")
        ax1.set_ylabel("Frequency (Hz)")
        p = ax2.imshow(phase, origin="lower", aspect="auto", cmap="jet", extent=extent)
        f.colorbar(p, ax=ax2, label="rad")
        ax2.set_title("Phase")
        ax2.set_xlabel("Time (s)")
        ax2.set_ylabel("Frequency (Hz)")

        f.suptitle("STFT")
        plt.show()
