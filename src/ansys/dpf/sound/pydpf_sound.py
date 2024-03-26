"""PyDpf sound interface."""
from ansys.dpf.core import FieldsContainer, fields_container
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
        self.output = FieldsContainer

    def plot(self):
        """Plot stuff.

        This method plots stuff.
        """
        return None

    def compute(self):
        """Compute stuff.

        This method computes stuff.
        """
        return None

    def get_output(self) -> fields_container:
        """Output stuff.

        Method for returning output.
        """
        return self.output

    def get_output_as_nparray(self) -> ArrayLike:
        """Output stuff as nparray.

        Method for returning output as np array.
        """
        return np.empty(0)
