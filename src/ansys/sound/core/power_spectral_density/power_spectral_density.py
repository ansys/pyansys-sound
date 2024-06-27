"""Power Spectral Density (PSD) module."""

import warnings

from ansys.dpf.core import Field, Operator
import matplotlib.pyplot as plt
import numpy as np
from numpy import typing as npt

from . import PowerSpectralDensityParent

from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning

ID_POWER_SPECTRAL_DENSITY = "compute_power_spectral_density"

class PowerSpectralDensity(PowerSpectralDensityParent):
    """Power Spectral Density (PSD) class.

    This class provides the Power Spectral Density (PSD) calculation for a given signal.
    """

    def __init__(self, input_signal: Field, window_type: str = "HANN", window_length: int = 2048, fft_size: int = 2048, overlap: int = 1536):
        """Init.

        Init the class.
        """
        super().__init__()

        # Input parameters
        self.input_signal = input_signal
        self.window_type = window_type
        self.window_length = window_length
        self.fft_size = fft_size
        self.overlap = overlap

        # Define output fields
        self._output = None

        self.__operator = Operator(ID_POWER_SPECTRAL_DENSITY)

    @property
    def input_signal(self) -> Field:
        """Input signal.
        """
        return self.__input_signal  # pragma: no cover
    
    @input_signal.setter
    def input_signal(self, value: Field):
        """Set input signal."""
        self.__input_signal = value

    @property
    def window_type(self) -> str:
        """Window type.
        """
        return self.__window_type  # pragma: no cover
    
    @window_type.setter
    def window_type(self, value: str):
        """Set window type."""
        self.__window_type = value

    @property
    def window_length(self) -> int:
        """Window length.
        """
        return self.__window_length  # pragma: no cover
    
    @window_length.setter
    def window_length(self, value: int):
        """Set window length."""
        self.__window_length = value

    @property
    def fft_size(self) -> int:
        """FFT size.
        """
        return self.__fft_size  # pragma: no cover
    
    @fft_size.setter
    def fft_size(self, value: int):
        """Set FFT size."""
        self.__fft_size = value

    @property
    def overlap(self) -> int:
        """Overlap.
        """
        return self.__overlap  # pragma: no cover
    
    @overlap.setter
    def overlap(self, value: int):
        """Set overlap."""
        self.__overlap = value
