"""Signal Utilities."""
from ..pydpf_sound import PyDpfSound


class SignalUtilities(PyDpfSound):
    """
    Abstract mother class for signal utilities.

    This is the mother class of all signal utilities classes, should not be used as is.
    """

    def __init__(self):
        """Init.

        Init the class.
        """
        PyDpfSound.__init__(self)
