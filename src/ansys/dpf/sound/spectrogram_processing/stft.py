"""Short-time Fourier Transform."""


from ansys.dpf.core import Field, FieldsContainer, Operator

from . import SpectrogramProcessingParent
from ..pydpf_sound import PyDpfSoundException


class Stft(SpectrogramProcessingParent):
    """Short-time Fourier Transform.

    This class computes the STFT (Short-time Fourier transform) of a signal.
    """

    def __init__(
        self,
        signal: Field | FieldsContainer = None,
        fft_size: float = 2048,
        window_type: str = "HANNING",
        window_overlap: float = 0.5,
    ):
        """Create an apply gain class.

        Parameters
        ----------
        signal:
            Signals on which to apply gain as a DPF Field or FieldsContainer.
        fft_size:
            Size (as an integer) of the FFT to compute the STFT.
            Use a power of 2 for better performance.
        window_type:
            The window used for the FFT computation, as a string.
            Allowed input strings are :
            'BLACKMANHARRIS', 'HANN','BLACKMAN', 'HAMMING', 'KAISER', 'BARTLETT', 'RECTANGULAR'.
            If no parameter is specified, the default value is 'HANNING'.
        window_overlap:
            The overlap value between two successive FFT computations (value between 0 and 1).
            0 means no overlap, 0.5 means 50 % overlap.
            If no parameter is specified, default value is 0.5.
        """
        super().__init__()
        self.signal = signal
        self.operator = Operator("compute_stft")

    @property
    def signal(self):
        """Signal property."""
        return self.__signal  # pragma: no cover

    @signal.setter
    def signal(self, signal: Field | FieldsContainer):
        """Set the signal."""
        self.__signal = signal

    @signal.getter
    def signal(self) -> Field | FieldsContainer:
        """Get the signal.

        Returns
        -------
        FieldsContainer | Field
                The signal as a Field or a FieldsContainer
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
            raise PyDpfSoundException("Fft size must be greater than 0.0")
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
            and window_type != "KAISER"
            and window_type != "BARTLETT"
            and window_type != "RECTANGULAR"
        ):
            raise PyDpfSoundException(
                "Invalid window type, accepted values are 'BLACKMANHARRIS', 'HANN','BLACKMAN', \
                    'HAMMING', 'KAISER', 'BARTLETT', 'RECTANGULAR'."
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
