"""Zero pad."""
import warnings

from ansys.dpf.core import Field, FieldsContainer, Operator
from numpy import typing as npt

from . import SignalUtilitiesAbstract


class ZeroPad(SignalUtilitiesAbstract):
    """ZeroPad.

    This class zero pads (adds zeros at the end of) signals.
    """

    def __init__(self, signal: Field | FieldsContainer = None, duration_zeros: float = 0.0):
        """Create a zero pad class.

        Parameters
        ----------
        signal:
            Signal to resample as a DPF Field or FieldsContainer.
        duration_zeros:
            Duration, in seconds, of the zeros to append to the input signal
        """
        super().__init__()
        self.signal = None
        self.set_signal(signal=signal)
        self.duration_zeros = 0.0
        self.set_duration_zeros(duration_zeros)
        self.operator = Operator("append_zeros_to_signal")

    def process(self):
        """Zero pad the signal.

        Calls the appropriate DPF Sound operator to append zeros to the signal.
        """
        if self.get_signal() == None:
            raise RuntimeError("No signal to zero-pad. Use ZeroPad.set_signal().")

        self.operator.connect(0, self.get_signal())
        self.operator.connect(1, float(self.get_duration_zeros()))

        # Runs the operator
        self.operator.run()

        # Stores output in the variable
        if type(self.signal) == FieldsContainer:
            self.output = self.operator.get_output(0, "fields_container")
        elif type(self.signal) == Field:
            self.output = self.operator.get_output(0, "field")

    def get_output(self) -> FieldsContainer | Field:
        """Return the zero-padded signal as a fields container.

        Returns
        -------
        FieldsContainer
                The zero-padded signal signal in a dpf.FieldsContainer.
        """
        if self.output == None:
            # Computing output if needed
            warnings.warn(UserWarning("Output has not been yet processed, use ZeroPad.process()."))

        return self.output

    def get_output_as_nparray(self) -> npt.ArrayLike:
        """Return the zero-padded signal as a numpy array.

        Returns
        -------
        np.array
                The zero-padded signal signal in a np.array.
        """
        output = self.get_output()

        if type(output) == Field:
            return output.data

        return self.convert_fields_container_to_np_array(output)

    def set_duration_zeros(self, new_duration_zeros: float):
        """Set the new duration of zeros.

        Parameters
        ----------
        new_duration_zeros:
            New duration for the zero padding (in seconds).
        """
        if new_duration_zeros < 0.0:
            raise RuntimeError("Zero duration must be strictly greater than 0.0.")

        self.duration_zeros = new_duration_zeros

    def get_duration_zeros(self) -> float:
        """Get the sampling frequency.

        Returns
        -------
        float
                The sampling frequency.
        """
        return self.duration_zeros

    def set_signal(self, signal: Field | FieldsContainer):
        """Set the signal."""
        self.signal = signal

    def get_signal(self) -> Field | FieldsContainer:
        """Get the signal.

        Returns
        -------
        FieldsContainer | Field
                The signal as a Field or a FieldsContainer
        """
        return self.signal
