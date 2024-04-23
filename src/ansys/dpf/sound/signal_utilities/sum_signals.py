"""Sum signals."""
import warnings

from ansys.dpf.core import Field, FieldsContainer, Operator
from numpy import typing as npt

from . import SignalUtilitiesParent
from ..pydpf_sound import PyDpfSoundException, PyDpfSoundWarning


class SumSignals(SignalUtilitiesParent):
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
        self.signals = signals
        self.__operator = Operator("sum_signals")

    @property
    def signals(self):
        """Signals property."""
        return self.__signals  # pragma: no cover

    @signals.setter
    def signals(self, signals: FieldsContainer):
        """Set the signals to sum."""
        self.__signals = signals

    @signals.getter
    def signals(self) -> FieldsContainer:
        """Get the signal.

        Returns
        -------
        FieldsContainer
                The signal as a FieldsContainer
        """
        return self.__signals

    def process(self):
        """Sum signals.

        Calls the appropriate DPF Sound operator to sum signals.
        """
        if self.signals == None:
            raise PyDpfSoundException(
                "No signal on which to apply gain. Use SumSignals.set_signal()."
            )

        self.__operator.connect(0, self.signals)

        # Runs the operator
        self.__operator.run()

        # Stores output in the variable
        self._output = self.__operator.get_output(0, "field")

    def get_output(self) -> Field:
        """Return the summed signals as a field.

        Returns
        -------
        Field
                The summed signal in a Field.
        """
        if self._output == None:
            # Computing output if needed
            warnings.warn(
                PyDpfSoundWarning("Output has not been yet processed, use SumSignals.process().")
            )

        return self._output

    def get_output_as_nparray(self) -> npt.ArrayLike:
        """Return the signal with a gain as a numpy array.

        Returns
        -------
        np.array
                The summed signal in a numpy array.
        """
        output = self.get_output()
        return output.data
