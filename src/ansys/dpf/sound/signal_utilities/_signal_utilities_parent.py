"""Signal Utilities."""
from ansys.dpf.core import Field
import matplotlib.pyplot as plt

from ..pydpf_sound import PyDpfSound


class SignalUtilitiesParent(PyDpfSound):
    """
    Abstract mother class for signal utilities.

    This is the mother class of all signal utilities classes, should not be used as is.
    """

    def __init__(self):
        """Init.

        Init the class.
        """
        super().__init__()

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
