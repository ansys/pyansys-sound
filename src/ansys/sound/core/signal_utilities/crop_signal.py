"""Crop signal."""
import warnings

from ansys.dpf.core import Field, FieldsContainer, Operator
from numpy import typing as npt

from . import SignalUtilitiesParent
from ..pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning


class CropSignal(SignalUtilitiesParent):
    """Crop signal.

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
        self.start_time = start_time
        self.end_time = end_time
        self.__operator = Operator("get_cropped_signal")

    @property
    def start_time(self):
        """Start time property."""
        return self.__start_time  # pragma: no cover

    @start_time.setter
    def start_time(self, new_start: float):
        """Set the new start time.

        Parameters
        ----------
        new_start:
            New start time (in seconds).
        """
        if new_start < 0.0:
            raise PyAnsysSoundException("Start time must be greater than or equal to 0.0.")
        self.__start_time = new_start

    @start_time.getter
    def start_time(self) -> float:
        """Get the start time.

        Returns
        -------
        float
                The start time.
        """
        return self.__start_time

    @property
    def end_time(self):
        """End time property."""
        return self.__end_time  # pragma: no cover

    @end_time.setter
    def end_time(self, new_end: bool):
        """Set the new end time.

        Parameters
        ----------
        new_end:
            New end time (in seconds).
        """
        if new_end < 0.0:
            raise PyAnsysSoundException("End time must be greater than or equal to 0.0.")

        if new_end < self.start_time:
            raise PyAnsysSoundException("End time must be greater than or equal to the start time.")

        self.__end_time = new_end

    @end_time.getter
    def end_time(self) -> float:
        """Get the end time.

        Returns
        -------
        float
                The end time.
        """
        return self.__end_time

    @property
    def signal(self):
        """Signal property."""
        return self.__signal  # pragma: no cover*

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

    def process(self):
        """Crop the signal.

        Calls the appropriate DPF Sound operator to crop the signal.
        """
        if self.signal == None:
            raise PyAnsysSoundException("No signal to crop. Use CropSignal.set_signal().")

        self.__operator.connect(0, self.signal)
        self.__operator.connect(1, float(self.start_time))
        self.__operator.connect(2, float(self.end_time))

        # Runs the operator
        self.__operator.run()

        # Stores output in the variable
        if type(self.signal) == FieldsContainer:
            self._output = self.__operator.get_output(0, "fields_container")
        elif type(self.signal) == Field:
            self._output = self.__operator.get_output(0, "field")

    def get_output(self) -> FieldsContainer | Field:
        """Return the cropped signal as a fields container.

        Returns
        -------
        FieldsContainer | Field
                The cropped signal in a dpf.FieldsContainer.
        """
        if self._output == None:
            # Computing output if needed
            warnings.warn(
                PyAnsysSoundWarning("Output has not been yet processed, use CropSignal.process().")
            )

        return self._output

    def get_output_as_nparray(self) -> npt.ArrayLike:
        """Return the cropped signal as a numpy array.

        Returns
        -------
        np.array
                The cropped signal in a numpy array.
        """
        output = self.get_output()

        if type(output) == Field:
            return output.data

        return self.convert_fields_container_to_np_array(output)
