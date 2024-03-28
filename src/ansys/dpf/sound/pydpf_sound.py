"""PyDpf sound interface."""
import warnings

from ansys.dpf.core import FieldsContainer
import numpy as np
from numpy.typing import ArrayLike


class PyDpfSound:
    """
    Abstract mother class for PyDpf Sound.

    This is the mother of all PyDpfSound classes, should not be used as is.
    """

    def __init__(self):
        """Init class PyDpfSound.

        This function inits the class by filling its attributes.
        """
        self.output = None

    def plot(self):
        """Plot stuff.

        This method plots stuff.
        """
        warnings.warn(UserWarning("Nothing to plot."))
        return None

    def process(self):
        """Process stuff.

        This method processes stuff.
        """
        warnings.warn(UserWarning("Nothing to process."))
        return None

    def get_output(self) -> None | FieldsContainer:
        """Output stuff.

        Method for returning output.
        """
        warnings.warn(UserWarning("Nothing to output."))
        return self.output

    def get_output_as_nparray(self) -> ArrayLike:
        """Output stuff as nparray.

        Method for returning output as np array.
        """
        warnings.warn(UserWarning("Nothing to output."))
        return np.empty(0)
