"""Spectrogram Processing."""
from ..pydpf_sound import PyDpfSound


class SpectrogramProcessingParent(PyDpfSound):
    """
    Abstract mother class for spectrogram processing.

    This is the mother class of all spectrogram processing, should not be used as is.
    """

    def __init__(self):
        """Init.

        Init the class.
        """
        super().__init__()
