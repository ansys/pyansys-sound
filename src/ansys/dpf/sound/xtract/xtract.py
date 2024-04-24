"""Xtract class."""

import warnings

from ansys.dpf.core import Field, FieldsContainer, Operator

from . import XtractParent
from ..pydpf_sound import PyDpfSoundException, PyDpfSoundWarning

class Xtract(XtractParent):
    """Xtract class."""

    def __init__(self):
        """Init.

        Init the class.
        """
        super().__init__()