"""Apply gain."""
import warnings

from ansys.dpf.core import Field, Operator
import numpy as np
from numpy import typing as npt

from . import SignalUtilitiesParent


class CreateSoundField(SignalUtilitiesParent):
    """Create a sound field.

    This class creates a DPF Field with Sound metadata from a vector.
    """

    def __init__(
        self,
        data: npt.ArrayLike = np.empty(0),
        sampling_frequency: float = 44100.0,
        unit: str = "Pa",
    ):
        """Create a sound field creator class.

        Parameters
        ----------
        data:
            Data to use to create the sound field as a 1D numpy array.
        sampling_frequency:
            Sampling frequency of the data.
        unit:
            Unit of the data.
        """
        super().__init__()
        self.data = data
        self.sampling_frequency = sampling_frequency
        self.unit = unit
        self.operator = Operator("create_field_from_vector")

    @property
    def data(self):
        """Data property."""
        return self.__data  # pragma: no cover

    @data.setter
    def data(self, data: npt.ArrayLike):
        """Set the data."""
        self.__data = data

    @data.getter
    def data(self) -> npt.ArrayLike:
        """Get the data.

        Returns
        -------
        np.array
                The data as a numpy array.
        """
        return self.__data

    @property
    def unit(self):
        """Unit property."""
        return self.__unit  # pragma: no cover

    @unit.setter
    def unit(self, new_unit: str):
        """Set the new unit.

        Parameters
        ----------
        new_unit:
            New unit as a string.
        """
        self.__unit = new_unit

    @unit.getter
    def unit(self) -> str:
        """Get the unit.

        Returns
        -------
        str
                The unit.
        """
        return self.__unit

    @property
    def sampling_frequency(self):
        """Sampling frequency property."""
        return self.__sampling_frequency  # pragma: no cover

    @sampling_frequency.setter
    def sampling_frequency(self, new_sampling_frequency: float):
        """Set the new sampling frequency.

        Parameters
        ----------
        new_sampling_frequency:
            New sampling frequency (in Hz).
        """
        if new_sampling_frequency < 0.0:
            raise RuntimeError("Sampling frequency must be greater than or equal to 0.0.")
        self.__sampling_frequency = new_sampling_frequency

    @sampling_frequency.getter
    def sampling_frequency(self) -> float:
        """Get the sampling frequency.

        Returns
        -------
        float
                The sampling frequency.
        """
        return self.__sampling_frequency

    def process(self):
        """Create the sound field.

        Calls the appropriate DPF Sound operator to create the sound field.
        """
        if np.size(self.data) == 0:
            raise RuntimeError("No data to use. Use CreateSoundField.set_data().")

        self.operator.connect(0, self.data.tolist())
        self.operator.connect(1, float(self.sampling_frequency))
        self.operator.connect(2, str(self.unit))

        # Runs the operator
        self.operator.run()

        # Stores output in the variable
        self._output = self.operator.get_output(0, "field")

    def get_output(self) -> Field:
        """Return the data as a field.

        Returns
        -------
        Field
                The data in a DPF Field.
        """
        if self._output == None:
            # Computing output if needed
            warnings.warn(
                UserWarning("Output has not been yet processed, use CreateSoundField.process().")
            )

        return self._output

    def get_output_as_nparray(self) -> npt.ArrayLike:
        """Return the data as a numpy array.

        Returns
        -------
        np.array
                The data in a numpy array.
        """
        output = self.get_output()
        return output.data
