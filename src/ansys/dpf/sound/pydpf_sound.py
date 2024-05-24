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
        self._output = None

    def plot(self):
        """Plot stuff.

        This method plots stuff.
        """
        warnings.warn(PyDpfSoundWarning("Nothing to plot."))
        return None

    def process(self):
        """Process stuff.

        This method processes stuff.

        Returns
        -------
        None
                None.
        """
        warnings.warn(PyDpfSoundWarning("Nothing to process."))
        return None

    def get_output(self) -> None | FieldsContainer:
        """Output stuff.

        Method for returning output.

        Returns
        -------
        FieldsContainer
                Empty fields container.
        """
        warnings.warn(PyDpfSoundWarning("Nothing to output."))
        return self._output

    def get_output_as_nparray(self) -> ArrayLike:
        """Output stuff as nparray.

        Method for returning output as np array.

        Returns
        -------
        np.array
                Empty numpy array.
        """
        warnings.warn(PyDpfSoundWarning("Nothing to output."))
        return np.empty(0)

    def convert_fields_container_to_np_array(self, fc):
        """Convert fields container to numpy array.

        Converts a multichannel signal contained in a DPF Fields Container into a numpy array.

        Returns
        -------
        np.array
                The fields container as a numpy array.
        """
        num_channels = len(fc)
        np_array = np.array(fc[0].data)

        if num_channels > 1:
            for i in range(1, num_channels):
                np_array = np.vstack((np_array, fc[i].data))

        return np_array


class PyDpfSoundException(Exception):
    """PyDPF Sound Exception."""

    def __init__(self, *args: object) -> None:
        """Init method."""
        super().__init__(*args)


class PyDpfSoundWarning(Warning):
    """PyDPF Sound Warning."""

    def __init__(self, *args: object) -> None:
        """Init method."""
        super().__init__(*args)
