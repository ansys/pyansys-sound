"""Spectrogram Processing."""
from ..pyansys_sound import PyAnsysSound


class SpectrogramProcessingParent(PyAnsysSound):
    """
    Abstract mother class for spectrogram processing.

    This is the mother class of all spectrogram processing, should not be used as is.
    """

    def __init__(self):
        """Init.

        Init the class.
        """
        super().__init__()
