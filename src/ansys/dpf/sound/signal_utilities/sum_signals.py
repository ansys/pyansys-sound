"""Sum signals."""
import warnings

from ansys.dpf.core import Field, FieldsContainer, Operator
from numpy import typing as npt

from . import SignalUtilitiesAbstract


class SumSignals(SignalUtilitiesAbstract):
    """Sum Signals.

    This class sum signals.
    """

    def __init__(self, signals: FieldsContainer = None):
        """Create a sum signal class.

        Parameters
        ----------
        signals:
            Input signals to sum, each field of the signal will be summed.
        """
        super().__init__()
        self.signals = None
        self.set_signals(signals=signals)
        self.operator = Operator("sum_signals")

    def process(self):
        """Sum signals.

        Calls the appropriate DPF Sound operator to sum signals.
        """
        if self.get_signals() == None:
            raise RuntimeError("No signal on which to apply gain. Use SumSignals.set_signal().")

        self.operator.connect(0, self.get_signals())

        # Runs the operator
        self.operator.run()

        # Stores output in the variable
        self.output = self.operator.get_output(0, "field")

    def get_output(self) -> Field:
        """Return the summed signals as a field.

        Returns the summed signals in a dpf.Field
        """
        if self.output == None:
            # Computing output if needed
            warnings.warn(
                UserWarning("Output has not been yet processed, use SumSignals.process().")
            )

        return self.output

    def get_output_as_nparray(self) -> npt.ArrayLike:
        """Return the signal with a gain as a numpy array.

        Returns the signal with a gain signal in a np.array
        """
        output = self.get_output()
        return output.data

    def set_signals(self, signals: FieldsContainer):
        """Set the signals to sum."""
        self.signals = signals

    def get_signals(self) -> Field | FieldsContainer:
        """Get the signal."""
        return self.signals
