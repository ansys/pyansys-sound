"""Apply gain."""
import warnings

from ansys.dpf.core import Field, FieldsContainer, Operator
from numpy import typing as npt

from . import SignalUtilitiesAbstract


class CropSignal(SignalUtilitiesAbstract):
    """Crop Signal.

    This class crops signals.
    """

    def __init__(
        self, signal: Field | FieldsContainer = None, start_time: float = 0.0, end_time: float = 0.0
    ):
        """Create an apply gain class.

        Parameters
        ----------
        signal:
            Signal to resample as a DPF Field or FieldsContainer.
        start_time:
            Start time of the part to crop, in seconds.
        end_time:
            End time of the part to crop, in seconds.
        """
        super().__init__()
        self.signal = signal
        self.start_time = 0.0
        self.set_start_time(start_time)
        self.end_time = 0.0
        self.set_end_time(end_time)
        self.operator = Operator("get_cropped_signal")

    def process(self):
        """Crop the signal.

        Calls the appropriate DPF Sound operator to crop the signal.
        """
        if self.get_signal() == None:
            raise RuntimeError("No signal to crop. Use CropSignal.set_signal().")

        self.operator.connect(0, self.get_signal())
        self.operator.connect(1, float(self.get_start_time()))
        self.operator.connect(2, float(self.get_end_time()))

        # Runs the operator
        self.operator.run()

        # Stores output in the variable
        if type(self.signal) == FieldsContainer:
            self.output = self.operator.get_output(0, "fields_container")
        elif type(self.signal) == Field:
            self.output = self.operator.get_output(0, "field")

    def get_output(self) -> FieldsContainer | Field:
        """Return the cropped signal as a fields container.

        Returns the cropped signal in a dpf.FieldsContainer
        """
        if self.output == None:
            # Computing output if needed
            warnings.warn(
                UserWarning("Output has not been yet processed, use CropSignal.process().")
            )

        return self.output

    def get_output_as_nparray(self) -> npt.ArrayLike:
        """Return the cropped signal as a numpy array.

        Returns the cropped signal in a np.array
        """
        output = self.get_output()

        if type(output) == Field:
            return output.data

        return self.convert_fields_container_to_np_array(output)

    def set_start_time(self, new_start: float):
        """Set the new start time.

        Parameters
        ----------
        new_start:
            New start time (in seconds).
        """
        if new_start < 0.0:
            raise RuntimeError("Start time must be greater than or equal to 0.0.")
        self.start_time = new_start

    def get_start_time(self) -> float:
        """Get the start time."""
        return self.start_time

    def set_end_time(self, new_end: bool):
        """Set the new end time.

        Parameters
        ----------
        new_end:
            New end time (in seconds).
        """
        if new_end < 0.0:
            raise RuntimeError("End time must be greater than or equal to 0.0.")

        if new_end < self.get_start_time():
            raise RuntimeError("End time must be greater than or equal to the start time.")

        self.end_time = new_end

    def get_end_time(self) -> float:
        """Get the end time."""
        return self.end_time

    def set_signal(self, signal: Field | FieldsContainer):
        """Set the signal."""
        self.signal = signal

    def get_signal(self) -> Field | FieldsContainer:
        """Get the signal."""
        return self.signal
