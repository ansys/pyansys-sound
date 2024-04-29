"""Xtract denoiser class."""

import warnings
from typing import overload, Tuple

from ansys.dpf.core import Field, FieldsContainer, Operator, GenericDataContainer
import matplotlib.pyplot as plt
from numpy import typing as npt

from . import XtractParent
from ..pydpf_sound import PyDpfSoundException, PyDpfSoundWarning


class XtractDenoiser(XtractParent):
    """Xtract denoiser class.
    
    Signal denoising using the XTRACT algorithm.
    """

    def __init__(
        self,
        input_signal: FieldsContainer | Field = None,
        input_parameters: GenericDataContainer = None,
        output_denoised_signals: FieldsContainer | Field = None,
        output_noise_signals: FieldsContainer | Field = None
    ):
        """Create a XtractDenoiser class.

        Parameters
        ----------
        input_signal: 
            Signal(s) to denoise, as a field or fields_container. When inputting a fields_container, each signal (each field of the fields_container) is processed individually.
        input_parameters:
            Structure that contains the parameters of the algorithm:
				- Noise levels (Field): level vs frequency of the noise
			This structure is of type Xtract_denoiser_parameters (see this class for more details).
        output_denoised_signals:
            Denoised signal(s), as a field or fields_container (depending on the input).
        output_noise_signals:
            Noise signal, as a field or fields_container (depending on the input). The noise signal is the original signal minus the denoised signal.
        """
        super().__init__()
        self.__input_signal = input_signal
        self.__input_parameters = input_parameters
        self.__output_denoised_signals = output_denoised_signals
        self.__output_noise_signals = output_noise_signals
        self.__operator = Operator("xtract_denoiser")

    @property
    def input_signal(self) -> FieldsContainer | Field:
        """Get input signal.
        
        Returns
        -------
        FieldsContainer | Field
            Signal(s) to denoise, as a field or fields_container. When inputting a fields_container, each signal (each field of the fields_container) is processed individually.
        """
        return self.__input_signal  # pragma: no cover
    
    @input_signal.setter
    def input_signal(self, value: FieldsContainer | Field):
        """Set input signal."""
        self.__input_signal = value

    @property
    def input_parameters(self) -> GenericDataContainer:
        """Get input parameters.
        
        Returns
        -------
        GenericDataContainer
            Structure that contains the parameters of the algorithm:    
            - TODO
        """
        return self.__input_parameters  # pragma: no cover
    
    @input_parameters.setter
    def input_parameters(self, value: GenericDataContainer):
        """Set input parameters."""
        self.__input_parameters = value

    @property
    def output_denoised_signals(self) -> FieldsContainer | Field:
        """Get output denoised signals.
        
        Returns
        -------
        FieldsContainer | Field
            Denoised signal(s), as a field or fields_container (depending on the input)."""
        return self.__output_denoised_signals  # pragma: no cover
    
    @output_denoised_signals.setter
    def output_denoised_signals(self, value: FieldsContainer | Field):
        """Set output denoised signals."""
        self.__output_denoised_signals = value

    @property
    def output_noise_signals(self) -> FieldsContainer | Field:
        """Get output noise signals.
        
        Returns
        -------
        FieldsContainer | Field
            Noise signal, as a field or fields_container (depending on the input). The noise signal is the original signal minus the denoised signal."""
        return self.__output_noise_signals  # pragma: no cover
    
    @output_noise_signals.setter
    def output_noise_signals(self, value: FieldsContainer | Field):
        """Set output noise signals."""
        self.__output_noise_signals = value

    @overload
    def process(self):
        """Process the denoising.
        TODO
        """

        if self.__input_signal is None:
            raise PyDpfSoundException("Input signal is not set.")
        

        if self.__input_parameters is None:
            raise PyDpfSoundException("Input parameters are not set.")
        
        self.__operator.connect(0, self.__input_signal)
        self.__operator.connect(1, self.__input_parameters)

        # Runs the operator
        self.__operator.run()

        # Stores the output in the variable
        if type(self.__input_signal) == Field:
            self.__output_denoised_signals = self.__operator.get_output(0, "field")
            self.__output_noise_signals = self.__operator.get_output(1, "field")
        else:
            self.__output_denoised_signals = self.__operator.get_output(0, "fields_container")
            self.__output_noise_signals = self.__operator.get_output(1, "fields_container")

    @overload
    def get_output(self) -> Tuple[FieldsContainer, FieldsContainer] | Tuple[Field, Field]:
        """Get the output of the denoising.
        TODO
        """

        if self.__output_denoised_signals == None or self.__output_noise_signals == None :
            warnings.warn(
                PyDpfSoundWarning("Output denoised or noise signals are not set.")
            )
        
        return self.__output_denoised_signals, self.__output_noise_signals

    @overload
    def get_output_as_nparray(self) -> Tuple[npt.ArrayLike, npt.ArrayLike]:
        """Get the output of the denoising as numpy arrays.
        TODO
        """
        l_output_denoised_signals = self.get_output()[0]
        l_output_noise_signals = self.get_output()[1]

        if type(l_output_denoised_signals) == Field:
            return l_output_denoised_signals.data, l_output_noise_signals.data

        return self.convert_fields_container_to_np_array(l_output_denoised_signals), self.convert_fields_container_to_np_array(l_output_noise_signals)

    @overload
    def plot(self):
        """Plot signals.
        
        Plot the denoised signal and the noise signal."""
        
        ################
        #
        # Plot denoised signal
        #
        l_output_denoised_signals = self.get_output()[0]

        if type(l_output_denoised_signals) == Field:
            l_i_nb_channels = 0
            field = l_output_denoised_signals
        else:
            l_i_nb_channels = len(l_output_denoised_signals)
            field = l_output_denoised_signals[0]

        l_time_data = field.time_freq_support.time_frequencies.data
        l_time_unit = field.time_freq_support.time_frequencies.unit
        l_unit = field.unit

        for l_i in range(l_i_nb_channels):
            plt.plot(l_time_data, l_output_denoised_signals.data[l_i], label=f"Channel {l_i}")
            plt.xlabel("Time (" + l_time_unit + ")")
            plt.ylabel("Amplitude (" + l_unit + ")")
            plt.title("Denoised signal")        
            plt.show()

        ################
        # Delete intermediate variables
        del l_i_nb_channels, field, l_output_denoised_signals
        del l_time_data, l_time_unit, l_unit

        ################
        #
        # Plot noise signal
        #
        l_output_noise_signals = self.get_output()[1]

        if type(l_output_noise_signals) == Field:
            l_i_nb_channels = 0
            field = l_output_noise_signals
        else:
            l_i_nb_channels = len(l_output_noise_signals)
            field = l_output_noise_signals[0]

        l_time_data = field.time_freq_support.time_frequencies.data
        l_time_unit = field.time_freq_support.time_frequencies.unit
        l_unit = field.unit

        for l_i in range(l_i_nb_channels):
            plt.plot(l_time_data, l_output_noise_signals.data[l_i], label=f"Channel {l_i}")
            plt.xlabel("Time (" + l_time_unit + ")")
            plt.ylabel("Amplitude (" + l_unit + ")")
            plt.title("Noise signal")
            plt.show()

        ################
        # Delete intermediate variables
        del l_i_nb_channels, field, l_output_noise_signals
        del l_time_data, l_time_unit, l_unit
