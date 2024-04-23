"""Xtract."""
from ..pydpf_sound import PyDpfSound


class XtractParent(PyDpfSound):
    """
    Abstract mother class for Xtract.

    This is the mother class of all Xtract classes, should not be used as is.
    """

    def __init__(self):
        """Init.

        Init the class.
        """
        super().__init__()