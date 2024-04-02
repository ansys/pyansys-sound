"""Load Wav."""
import warnings

from ansys.dpf.core import Field, FieldsContainer, Operator
from numpy import typing as npt

from . import SignalUtilitiesAbstract


class Resample(SignalUtilitiesAbstract):
    """Resample.

    This class resamples signals.
    """

    def __init__(self, signal: Field | FieldsContainer = None, new_sampling_frequency=44100.0):
        """Create a load wav class.

        Parameters
        ----------
        signal:
            Signal to resample as a DPF Field or FieldsContainer.
        new_sampling_frequency:
            New sampling frequency to use
        """
        super().__init__()
        self.signal = signal
        self.new_sampling_frequency = 0.0
        self.set_sampling_frequency(new_sampling_frequency)
        self.operator = Operator("resample")

    def process(self):
        """Resample the signal.

        Calls the appropriate DPF Sound operator to load the wav file.
        """
        if self.get_signal() == None:
            raise RuntimeError("No signal to resample. Use Resample.set_signal().")

        self.operator.connect(0, self.get_signal())
        self.operator.connect(1, float(self.get_sampling_frequency()))

        # Runs the operator
        self.operator.run()

        # Stores output in the variable
        if type(self.signal) == FieldsContainer:
            self.output = self.operator.get_output(0, "fields_container")
        elif type(self.signal) == Field:
            self.output = self.operator.get_output(0, "field")

    def get_output(self) -> FieldsContainer | Field:
        """Return the resampled signal as a fields container.

        Returns the resampled signal in a dpf.FieldsContainer
        """
        if self.output == None:
            # Computing output if needed
            warnings.warn(UserWarning("Output has not been yet processed, use Resample.process()."))

        return self.output

    def get_output_as_nparray(self) -> npt.ArrayLike:
        """Return the resampled signal as a numpy array.

        Returns the resampled signal in a np.array
        """
        output = self.get_output()

        if type(output) == Field:
            return output.data

        return self.convert_fields_container_to_np_array(output)

    def set_sampling_frequency(self, new_sampling_frequency: float):
        """Set the new sampling frequency.

        Parameters
        ----------
        new_sampling_frequency:
            New sampling frequency.
        """
        if new_sampling_frequency < 0.0:
            raise RuntimeError("Sampling frequency must be strictly greater than 0.0.")

        self.new_sampling_frequency = new_sampling_frequency

    def get_sampling_frequency(self):
        """Get the sampling frequency."""
        return self.new_sampling_frequency

    def set_signal(self, signal: Field | FieldsContainer):
        """Set the signal."""
        self.signal = signal

    def get_signal(self) -> Field | FieldsContainer:
        """Get the signal."""
        return self.signal
