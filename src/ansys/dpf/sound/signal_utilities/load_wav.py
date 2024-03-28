"""Load Wav."""
import warnings

from ansys.dpf.core import DataSources, Operator, fields_container
import matplotlib.pyplot as plt
import numpy as np
from numpy import typing as npt

from . import SignalUtilitiesAbstract


class LoadWav(SignalUtilitiesAbstract):
    """Load wav.

    This class loads wav signals.
    """

    def __init__(self, path_to_wav=""):
        """Create a load wav class.

        Parameters
        ----------
        path_to_wav:
            Path to the wav file to load.
            Can be set during the instantiation of the object or with LoadWav.set_path().
        """
        super().__init__()
        self.path_to_wav = path_to_wav
        self.operator = Operator("load_wav_sas")

    def process(self):
        """Load the wav file.

        Calls the appropriate DPF Sound operator to load the wav file.
        """
        if self.path_to_wav == "":
            raise RuntimeError("Path for loading wav file is not specified. Use LoadWav.set_path.")

        # Loading a WAV file
        data_source_in = DataSources()

        # Creating input path
        data_source_in.add_file_path(self.path_to_wav, ".wav")

        # Loading wav file and storing it into a container
        self.operator.connect(0, data_source_in)

        # Runs the operator
        self.operator.run()

        # Stores output in the variable
        self.output = self.operator.get_output(0, "fields_container")

    def get_output(self) -> fields_container:
        """Return the loaded wav signal as a fields container.

        Returns the loaded wav signal in a dpf.FieldsContainer
        """
        if self.output == None:
            # Computing output if needed
            warnings.warn(UserWarning("Output has not been yet processed, use LoadWav.process()."))

        return self.output

    def get_output_as_nparray(self) -> npt.ArrayLike:
        """Return the loaded wav signal as a numpy array.

        Returns the loaded wav signal in a np.array
        """
        fc = self.get_output()

        num_channels = len(fc)
        np_array = fc[0].data

        if num_channels > 1:
            for i in range(1, num_channels):
                np_array = np.vstack((np_array, fc[i].data))

        return np.transpose(np_array)

    def plot(self):
        """Plot signals.

        Plots the loaded signals in one plot.
        """
        fc_signal = self.get_output()
        time_data = fc_signal[0].time_freq_support.time_frequencies.data
        time_unit = fc_signal[0].time_freq_support.time_frequencies.unit
        num_channels = len(fc_signal)
        unit = fc_signal[0].unit

        for i in range(num_channels):
            plt.plot(time_data, fc_signal[i].data, label="Channel {}".format(i))

        plt.title(fc_signal[0].name)
        plt.legend()
        plt.xlabel(time_unit)
        plt.ylabel(unit)
        plt.show()

    def set_path(self, path_to_wav):
        """Set the path of the wav to load.

        Parameters
        ----------
        path_to_wav:
            Path to the wav file to load.
        """
        self.path_to_wav = path_to_wav

    def get_path(self) -> str:
        """Get the path of the wav to load."""
        return self.path_to_wav
