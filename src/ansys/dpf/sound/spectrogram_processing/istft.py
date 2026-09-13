"""Inverse Short-time Fourier Transform."""

import warnings

from ansys.dpf.core import Field, FieldsContainer, Operator
import matplotlib.pyplot as plt
import numpy as np
from numpy import typing as npt

from . import SpectrogramProcessingParent
from ..pydpf_sound import PyDpfSoundException, PyDpfSoundWarning


class Istft(SpectrogramProcessingParent):
    """Inverse Short-time Fourier Transform.

    This class computes the ISTFT (Inverse Short-time Fourier transform) of a signal.
    """

    def __init__(self, stft: FieldsContainer = None):
        """Create an Istft class.

        Parameters
        ----------
        stft:
            A FieldsContainer containing an STFT computed with the Stft class.
        """
        super().__init__()
        self.stft = stft
        self.__operator = Operator("compute_istft")

    @property
    def stft(self):
        """STFT property."""
        return self.__stft  # pragma: no cover

    @stft.setter
    def stft(self, stft: FieldsContainer):
        """Set the STFT."""
        if type(stft) != FieldsContainer and stft != None:
            raise PyDpfSoundException("Input must be a Fields container.")

        if stft != None and (
            not stft.has_label("time")
            or not stft.has_label("complex")
            or not stft.has_label("channel_number")
        ):
            raise PyDpfSoundException(
                "STFT is in the wrong format, make sure it has been computed with the Stft class."
            )

        self.__stft = stft

    @stft.getter
    def stft(self) -> FieldsContainer:
        """Get the STFT.

        Returns
        -------
        FieldsContainer
                The STFT as a FieldsContainer.
        """
        return self.__stft

    def process(self):
        """Compute the ISTFT.

        Calls the appropriate DPF Sound operator to compute the Inverse STFT of the STFT.
        """
        if self.stft == None:
            raise PyDpfSoundException("No STFT input for ISTFT computation. Use Istft.stft.")

        self.__operator.connect(0, self.stft)

        # Runs the operator
        self.__operator.run()

        # Stores output in the variable
        self._output = self.__operator.get_output(0, "field")

    def get_output(self) -> Field:
        """Return the ISTFT resulting signal as a field.

        Returns
        -------
        Field
                The signal resulting from the ISTFT as a DPF Field.
        """
        if self._output == None:
            # Computing output if needed
            warnings.warn(
                PyDpfSoundWarning("Output has not been yet processed, use Istft.process().")
            )

        return self._output

    def get_output_as_nparray(self) -> npt.ArrayLike:
        """Return the ISTFT resulting signal as a numpy array.

        Returns
        -------
        np.array
                The ISTFT resulting signal in a numpy array.
        """
        output = self.get_output()
        out_as_np_array = output.data

        # return out_as_np_array
        return np.transpose(out_as_np_array)

    def plot(self):
        """Plot signals.

        Plots the signal resulting from ISTFT.
        """
        output = self.get_output()
        field = output

        time_data = output.time_freq_support.time_frequencies.data
        time_unit = output.time_freq_support.time_frequencies.unit
        unit = field.unit
        plt.plot(time_data, field.data, label="Signal")

        plt.title(field.name)
        plt.legend()
        plt.xlabel(time_unit)
        plt.ylabel(unit)
        plt.grid(True)
        plt.show()
