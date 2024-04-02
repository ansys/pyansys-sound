"""Apply gain."""
import warnings

from ansys.dpf.core import Field, FieldsContainer, Operator
from numpy import typing as npt

from . import SignalUtilitiesAbstract


class ApplyGain(SignalUtilitiesAbstract):
    """Apply gain.

    This class applies a gain to signals.
    """

    def __init__(
        self, signal: Field | FieldsContainer = None, gain: float = 0.0, gain_in_db: bool = True
    ):
        """Create an apply gain class.

        Parameters
        ----------
        signal:
            Signals on which to apply gain as a DPF Field or FieldsContainer.
        gain:
            Gain value in decibels (dB) or linear unit. By default, gain is specified in decibels.
        gain:
            If value is true, the gain is specified in dB.
            If value is false, the gain is in a linear unit.
        """
        super().__init__()
        self.signal = signal
        self.gain = 0.0
        self.set_gain(gain)
        self.gain_in_db = True
        self.set_gain_in_db(gain_in_db)
        self.operator = Operator("apply_gain")

    def process(self):
        """Apply gain to the signal.

        Calls the appropriate DPF Sound operator to apply gain to the signal.
        """
        if self.get_signal() == None:
            raise RuntimeError("No signal on which to apply gain. Use ApplyGain.set_signal().")

        self.operator.connect(0, self.get_signal())
        self.operator.connect(1, float(self.get_gain()))
        self.operator.connect(2, bool(self.get_gain_in_db()))

        # Runs the operator
        self.operator.run()

        # Stores output in the variable
        if type(self.signal) == FieldsContainer:
            self.output = self.operator.get_output(0, "fields_container")
        elif type(self.signal) == Field:
            self.output = self.operator.get_output(0, "field")

    def get_output(self) -> FieldsContainer | Field:
        """Return the signal with a gain as a fields container.

        Returns the signal with a gain in a dpf.FieldsContainer
        """
        if self.output == None:
            # Computing output if needed
            warnings.warn(
                UserWarning("Output has not been yet processed, use ApplyGain.process().")
            )

        return self.output

    def get_output_as_nparray(self) -> npt.ArrayLike:
        """Return the signal with a gain as a numpy array.

        Returns the signal with a gain signal in a np.array
        """
        output = self.get_output()

        if type(output) == Field:
            return output.data

        return self.convert_fields_container_to_np_array(output)

    def set_gain(self, new_gain: float):
        """Set the new gain.

        Parameters
        ----------
        new_gain:
            New gain.
        """
        self.gain = new_gain

    def get_gain(self) -> float:
        """Get the gain."""
        return self.gain

    def set_gain_in_db(self, new_gain_in_db: bool):
        """Set the new gain_in_db value.

        Parameters
        ----------
        new_gain_in_db:
            True to set the gain in dB, false otherwise.
        """
        if type(new_gain_in_db) is not bool:
            raise RuntimeError("new_gain_in_db must be a boolean value, either True or False.")

        self.gain_in_db = new_gain_in_db

    def get_gain_in_db(self) -> bool:
        """Get the gain."""
        return self.gain_in_db

    def set_signal(self, signal: Field | FieldsContainer):
        """Set the signal."""
        self.signal = signal

    def get_signal(self) -> Field | FieldsContainer:
        """Get the signal."""
        return self.signal
