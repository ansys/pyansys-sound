"""Signal Utilities."""
import numpy as np

from ..pydpf_sound import PyDpfSound


class SignalUtilitiesAbstract(PyDpfSound):
    """
    Abstract mother class for signal utilities.

    This is the mother class of all signal utilities classes, should not be used as is.
    """

    def __init__(self):
        """Init.

        Init the class.
        """
        super().__init__()

    def convert_fields_container_to_np_array(self, fc):
        """Convert fields container to numpy array.

        Converts a multichannel signal contained in a DPF Fields Container into a numpy array.
        """
        num_channels = len(fc)
        np_array = fc[0].data

        if num_channels > 1:
            for i in range(1, num_channels):
                np_array = np.vstack((np_array, fc[i].data))

        return np.transpose(np_array)
