"""Apply gain."""
import warnings

from ansys.dpf.core import Field, Operator
import numpy as np
from numpy import typing as npt

from . import SignalUtilitiesAbstract


class CreateSoundField(SignalUtilitiesAbstract):
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
        self.sampling_frequency = 0.0
        self.set_sampling_frequency(sampling_frequency)
        self.unit = 0.0
        self.set_unit(unit)
        self.operator = Operator("create_field_from_vector")

    def process(self):
        """Create the sound field.

        Calls the appropriate DPF Sound operator to create the sound field.
        """
        if np.size(self.get_data()) == 0:
            raise RuntimeError("No data to use. Use CreateSoundField.set_data().")

        self.operator.connect(0, self.get_data().tolist())
        self.operator.connect(1, float(self.get_sampling_frequency()))
        self.operator.connect(2, str(self.get_unit()))

        # Runs the operator
        self.operator.run()

        # Stores output in the variable
        self.output = self.operator.get_output(0, "field")

    def get_output(self) -> Field:
        """Return the data as a field.

        Returns the data in a dpf.Field
        """
        if self.output == None:
            # Computing output if needed
            warnings.warn(
                UserWarning("Output has not been yet processed, use CreateSoundField.process().")
            )

        return self.output

    def get_output_as_nparray(self) -> npt.ArrayLike:
        """Return the data as a numpy array.

        Returns the data in a np.array
        """
        output = self.get_output()
        return output.data

    def set_sampling_frequency(self, new_sampling_frequency: float):
        """Set the new sampling frequency.

        Parameters
        ----------
        new_sampling_frequency:
            New sampling frequency (in Hz).
        """
        if new_sampling_frequency < 0.0:
            raise RuntimeError("Sampling frequency must be greater than or equal to 0.0.")
        self.sampling_frequency = new_sampling_frequency

    def get_sampling_frequency(self) -> float:
        """Get the sampling frequency."""
        return self.sampling_frequency

    def set_unit(self, new_unit: str):
        """Set the new unit.

        Parameters
        ----------
        new_unit:
            New unit as a string.
        """
        self.unit = new_unit

    def get_unit(self) -> str:
        """Get the unit."""
        return self.unit

    def set_data(self, data: npt.ArrayLike):
        """Set the data."""
        self.data = data

    def get_data(self) -> npt.ArrayLike:
        """Get the data."""
        return self.data
