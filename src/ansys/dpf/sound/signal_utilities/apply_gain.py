"""Apply gain."""

import warnings

from ansys.dpf.core import Field, FieldsContainer, Operator
from numpy import typing as npt

from . import SignalUtilitiesParent
from ..pydpf_sound import PyDpfSoundException, PyDpfSoundWarning


class ApplyGain(SignalUtilitiesParent):
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
        self.gain = gain
        self.gain_in_db = gain_in_db
        self.__operator = Operator("apply_gain")

    @property
    def signal(self):
        """Signal property."""
        return self.__signal  # pragma: no cover

    @signal.setter
    def signal(self, signal: Field | FieldsContainer):
        """Set the signal."""
        self.__signal = signal

    @signal.getter
    def signal(self) -> Field | FieldsContainer:
        """Get the signal.

        Returns
        -------
        FieldsContainer | Field
                The signal as a Field or a FieldsContainer
        """
        return self.__signal

    @property
    def gain(self):
        """Gain property."""
        return self.__gain  # pragma: no cover

    @gain.setter
    def gain(self, new_gain: float):
        """Set the new gain.

        Parameters
        ----------
        new_gain:
            New gain.
        """
        self.__gain = new_gain

    @gain.getter
    def gain(self) -> float:
        """Get the gain.

        Returns
        -------
        float
                Gain value.
        """
        return self.__gain

    @property
    def gain_in_db(self):
        """Gain in dB property."""
        return self.__gain_in_db  # pragma: no cover

    @gain_in_db.setter
    def gain_in_db(self, new_gain_in_db: bool):
        """Set the new gain_in_db value.

        Parameters
        ----------
        new_gain_in_db:
            True to set the gain in dB, false otherwise.
        """
        if type(new_gain_in_db) is not bool:
            raise PyDpfSoundException(
                "new_gain_in_db must be a boolean value, either True or False."
            )

        self.__gain_in_db = new_gain_in_db

    @gain_in_db.getter
    def gain_in_db(self) -> bool:
        """Get the gain in dB.

        Returns
        -------
        bool
                Boolean value that indicates if the gain is in dB.
        """
        return self.__gain_in_db

    def process(self):
        """Apply gain to the signal.

        Calls the appropriate DPF Sound operator to apply gain to the signal.
        """
        if self.signal == None:
            raise PyDpfSoundException(
                "No signal on which to apply gain. Use ApplyGain.set_signal()."
            )

        self.__operator.connect(0, self.signal)
        self.__operator.connect(1, float(self.gain))
        self.__operator.connect(2, bool(self.gain_in_db))

        # Runs the operator
        self.__operator.run()

        # Stores output in the variable
        if type(self.signal) == FieldsContainer:
            self._output = self.__operator.get_output(0, "fields_container")
        elif type(self.signal) == Field:
            self._output = self.__operator.get_output(0, "field")

    def get_output(self) -> FieldsContainer | Field:
        """Return the signal with a gain as a fields container.

        Returns
        -------
        FieldsContainer
                Signal with applied gain as a FieldContainer.
        """
        if self._output == None:
            # Computing output if needed
            warnings.warn(
                PyDpfSoundWarning("Output has not been yet processed, use ApplyGain.process().")
            )

        return self._output

    def get_output_as_nparray(self) -> npt.ArrayLike:
        """Return the signal with a gain as a numpy array.

        Returns
        -------
        np.array
                Signal with applied gain as a numpy array.
        """
        output = self.get_output()

        if type(output) == Field:
            return output.data

        return self.convert_fields_container_to_np_array(output)
