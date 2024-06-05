"""Compute sharpness according to Zwicker & Fastl's model."""
import warnings

from ansys.dpf.core import Field, FieldsContainer, Operator
import numpy as np
from numpy import typing as npt

from . import PsychoacousticsParent
from ..pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning


class Sharpness(PsychoacousticsParent):
    """Sharpness.

    This class computes the sharpness of a signal according to Zwicker & Fastl's model.
    """

    def __init__(self, signal: Field | FieldsContainer = None):
        """Create a Sharpness object.

        Parameters
        ----------
        signal: Field | FieldsContainer
            Signal in Pa on which to compute sharpness, as a DPF Field or Fields Container.
        """
        super().__init__()
        self.signal = signal
        self.__operator = Operator("compute_sharpness")

    @property
    def signal(self):
        """Signal property."""
        return self.__signal  # pragma: no cover

    @signal.setter
    def signal(self, signal: Field | FieldsContainer):
        """Set the signal.

        Parameters
        -------
        signal: FieldsContainer | Field
            Signal in Pa on which to compute sharpness, as a DPF Field or Fields Container.

        """
        self.__signal = signal

    @signal.getter
    def signal(self) -> Field | FieldsContainer:
        """Get the signal.

        Returns
        -------
        FieldsContainer | Field
            The signal in Pa as a Field or a FieldsContainer.
        """
        return self.__signal

    def process(self):
        """Compute sharpness.

        Calls the appropriate DPF Sound operator to compute the sharpness of the signal.
        """
        if self.__signal == None:
            raise PyAnsysSoundException(
                "No signal for sharpness computation. Use Sharpness.signal."
            )

        self.__operator.connect(0, self.signal)

        # Runs the operator
        self.__operator.run()

        # Stores outputs in the tuple variable
        if type(self.signal) == FieldsContainer:
            self._output = self.__operator.get_output(0, "fields_container")
        elif type(self.signal) == Field:
            self._output = self.__operator.get_output(0, "field")

    def get_output(self) -> FieldsContainer | Field:
        """Return sharpness in a tuple of field or fields container.

        Returns
        -------
        FieldsContainer | Field
            Sharpness in acum.
        """
        if self._output == None:
            warnings.warn(
                PyAnsysSoundWarning("Output has not been processed yet, use Sharpness.process().")
            )

        return self._output

    def get_output_as_nparray(self) -> npt.ArrayLike:
        """Return sharpness as a numpy array.

        Returns
        -------
        numpy.ndarray:
            Array of sharpness values, in acum.
        """
        output = self.get_output()

        if output == None:
            return None

        if type(output) == Field:
            return np.array(output.data)

        return self.convert_fields_container_to_np_array(output)

    def get_sharpness(self, channel_index: int = 0) -> np.float64:
        """Return sharpness as a float.

        Returns sharpness in acum for the specified channel.

        Parameters
        ----------
        channel_index: int
            Index of the signal channel (0 by default) for which to return the sharpness value.

        Returns
        -------
        numpy.float64
            Sharpness value in acum.
        """
        if self.get_output() == None:
            return None

        sharpness_data = self.get_output_as_nparray()

        # Get last channel index.
        channel_max = len(sharpness_data) - 1

        # Check that specified channel index exists.
        if channel_index > channel_max:
            raise PyAnsysSoundException(
                f"Specified channel index ({channel_index}) does not exist."
            )

        # Return sharpness for the specified channel.
        if channel_max > 0:
            return sharpness_data[channel_index][0]
        else:
            return sharpness_data[0]
