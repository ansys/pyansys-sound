"""Xtract."""
from ..pyansys_sound import PyAnsysSound


class XtractParent(PyAnsysSound):
    """
    Abstract mother class for Xtract.

    This is the mother class of all Xtract classes, should not be used as is.
    """

    def __init__(self):
        """Init.

        Init the class.
        """
        super().__init__()