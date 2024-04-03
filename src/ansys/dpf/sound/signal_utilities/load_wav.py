"""Load Wav."""
import warnings

from ansys.dpf.core import DataSources, FieldsContainer, Operator
from numpy import typing as npt

from . import SignalUtilitiesAbstract


class LoadWav(SignalUtilitiesAbstract):
    """Load wav.

    This class loads wav signals.
    """

    def __init__(self, path_to_wav: str = ""):
        """Create a load wav class.

        Parameters
        ----------
        path_to_wav:
            Path to the wav file to load.
            Can be set during the instantiation of the object or with LoadWav.set_path().
        """
        super().__init__()
        self.path_to_wav = ""
        self.set_path(path_to_wav=path_to_wav)
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

    def get_output(self) -> FieldsContainer:
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

        return self.convert_fields_container_to_np_array(fc)

    def set_path(self, path_to_wav: str):
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
