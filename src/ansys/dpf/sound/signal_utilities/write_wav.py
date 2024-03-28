"""Write Wav."""


from ansys.dpf.core import DataSources, Operator, fields_container

from . import SignalUtilitiesAbstract


class WriteWav(SignalUtilitiesAbstract):
    """Write wav.

    This class writes wav signals.
    """

    def __init__(
        self, signal: fields_container = None, path_to_write: str = "", bit_depth: str = "float32"
    ):
        """Create a write wav class.

        Parameters
        ----------
        signal:
            Signal to save: fields_container with each channel as a field.
        path_to_write:
            Path where to write the wav file.
            Can be set during the instantiation of the object or with LoadWav.set_path().
        bit_depth:
            Bit depth. Supported values are: 'float32', 'int32', 'int16', 'int8'.
            This means that the samples will be respectively coded into the wav file
            using 32 bits (32-bit IEEE Float), 32 bits (int), 16 bits (int) or 8 bits (int).
        """
        super().__init__()
        self.path_to_write = path_to_write
        self.signal = signal
        self.bit_depth = ""
        self.set_bit_depth(bit_depth=bit_depth)
        self.operator = Operator("write_wav_sas")

    def process(self):
        """Write the wav file.

        Calls the appropriate DPF Sound operator to writes the wav file.
        """
        if self.path_to_write == "":
            raise RuntimeError("Path for write wav file is not specified. Use WriteWav.set_path.")

        if self.signal == None:
            raise RuntimeError("No signal is specified for writing, use WriteWav.set_signal.")

        data_source_out = DataSources()
        data_source_out.add_file_path(self.path_to_write, ".wav")

        self.operator.connect(0, self.signal)
        self.operator.connect(1, data_source_out)
        self.operator.connect(2, self.bit_depth)

        self.operator.run()

    def set_signal(self, signal):
        """Setter for the signal.

        Sets the value of the signal to write in memory.
        """
        self.signal = signal

    def get_signal(self):
        """Getter for the signal.

        Returns the signal that is to be written in memory.
        """
        return self.signal

    def set_path(self, path_to_write):
        """Setter for the write path.

        Sets the path for writing the signal in memory.
        """
        self.path_to_write = path_to_write

    def get_path(self):
        """Getter for the write path.

        Gets the path for writing the signal in memory.
        """
        return self.path_to_write

    def set_bit_depth(self, bit_depth):
        """Setter for the bit depth.

        Sets the bit depth.
        """
        if (
            bit_depth != "int8"
            and bit_depth != "int16"
            and bit_depth != "int32"
            and bit_depth != "float32"
        ):
            raise RuntimeError(
                "Invalid bit depth, accepted values are 'float32', 'int32', 'int16', 'int8'."
            )

        self.bit_depth = bit_depth

    def get_bit_depth(self):
        """Getter for the bit depth.

        Gets the bit_depth.
        """
        return self.bit_depth
