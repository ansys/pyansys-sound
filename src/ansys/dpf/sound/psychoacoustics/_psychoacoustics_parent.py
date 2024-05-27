"""Psychoacoustics functions."""
from ..pydpf_sound import PyDpfSound


class PsychoacousticsParent(PyDpfSound):
    """
    Abstract mother class for psychoacoustics calculations.

    This is the mother class of all pychoacoustics indicators classes, should not be used as is.
    """

    def __init__(self):
        """Init.

        Init the class.
        """
        super().__init__()
