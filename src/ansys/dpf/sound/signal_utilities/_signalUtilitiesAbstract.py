"""Signal Utilities."""
from ansys.dpf.core import Field
import matplotlib.pyplot as plt
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

    def plot(self):
        """Plot signals.

        Plots the resampled signals in one plot.
        """
        output = self.get_output()

        if type(output) == Field:
            num_channels = 0
            field = output
        else:
            num_channels = len(output)
            field = output[0]

        time_data = field.time_freq_support.time_frequencies.data
        time_unit = field.time_freq_support.time_frequencies.unit
        unit = field.unit

        for i in range(num_channels):
            plt.plot(time_data, output[i].data, label="Channel {}".format(i))

        plt.title(field.name)
        plt.legend()
        plt.xlabel(time_unit)
        plt.ylabel(unit)
        plt.grid(True)
        plt.show()
