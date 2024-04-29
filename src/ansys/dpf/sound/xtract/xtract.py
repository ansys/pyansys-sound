"""Xtract class."""

import warnings
from typing import overload, Tuple

from ansys.dpf.core import Field, FieldsContainer, Operator, GenericDataContainer
import matplotlib.pyplot as plt
from numpy import typing as npt

from . import XtractParent
#from . import XtractDenoiser
#from . import XtractTonal
#from . import XtractTransient

from ..pydpf_sound import PyDpfSoundException, PyDpfSoundWarning

class Xtract(XtractParent):
    """Xtract class.
    
    XTRACT processing: in the same way as in Sound SAS, this operator chains a denoising step, followed by a tonal extraction step and then a transient extraction step. It returns the individual signals processed at each step, as well as the remainder.
    """

    def __init__(
        self,
        input_signal: FieldsContainer | Field = None,
        parameters_denoiser: GenericDataContainer = None,
        parameters_tonal: GenericDataContainer = None,
        parameters_transient: GenericDataContainer = None,
    ):
        """Create a Xtract class.

        Parameters
        ----------
        input_signal: 
            Signal(s) on which to apply the XTRACT processing, as a field or fields_container.
        parameters_denoiser:
            Structure that contains the parameters of the denoising step:
				- Noise levels (Field): level vs frequency of the noise
			This structure is of type Xtract_denoiser_parameters (see this class for more details).
        parameters_tonal:
            Structure that contains the parameters of the tonal extraction step:
				- Nfft (int) in number of samples
				- Regularity setting (float) in percent
				- Maximum slope (float) in dB/Hz
				- Minimum duration (float) in seconds
				- Intertonal gap (float) in Hz
				- Local emergence (float) in dB
			This structure is of type Xtract_tonal_parameters (see this class for more details).
        parameters_transient:
            Structure that contains the parameters of the transient extraction step:
				- Lower threshold (float), between 0 and 100 percent
				- Upper threshold (float), between 0 and 100 percent
			This structure is of type Xtract_transient_parameters (see this class for more details).
        """
        super().__init__()
        self.__input_signal = input_signal
        self.__parameters_denoiser = parameters_denoiser
        self.__parameters_tonal = parameters_tonal
        self.__parameters_transient = parameters_transient

        # Def output fields
        self.__noise_signal = None
        self.__tonal_signal = None
        self.__transient_signal = None
        self.__remainder_signal = None

        self.__operator = Operator("xtract")

    @property
    def input_signal(self) -> FieldsContainer | Field:
        """Get input signal.
        
        Returns
        -------
        FieldsContainer | Field
            Signal(s) on which to apply the XTRACT processing, as a field or fields_container.
        """
        return self.__input_signal  # pragma: no cover
    
    @input_signal.setter
    def input_signal(self, value: FieldsContainer | Field):
        """Set input signal."""
        self.__input_signal = value

    @property
    def parameters_denoiser(self) -> GenericDataContainer:
        """Get parameters of the denoiser step.
        
        Returns
        -------
        GenericDataContainer
            Structure that contains the parameters of the denoising step:
                - Noise levels (Field): level vs frequency of the noise
        """
        return self.__parameters_denoiser
    
    @parameters_denoiser.setter
    def parameters_denoiser(self, value: GenericDataContainer):
        """Set parameters of the denoiser step."""
        self.__parameters_denoiser = value

    @property
    def parameters_tonal(self) -> GenericDataContainer:
        """Get parameters of the tonal extraction step.
        
        Returns
        -------
        GenericDataContainer
            Structure that contains the parameters of the tonal extraction step:
                - Nfft (int) in number of samples
                - Regularity setting (float) in percent
                - Maximum slope (float) in dB/Hz
                - Minimum duration (float) in seconds
                - Intertonal gap (float) in Hz
                - Local emergence (float) in dB
        """
        return self.__parameters_tonal # pragma: no cover
    
    @parameters_tonal.setter
    def parameters_tonal(self, value: GenericDataContainer):
        """Set parameters of the tonal extraction step."""
        self.__parameters_tonal = value

    @property
    def parameters_transient(self) -> GenericDataContainer:
        """Get parameters of the transient extraction step.
        
        Returns
        -------
        GenericDataContainer
            Structure that contains the parameters of the transient extraction step:
                - Lower threshold (float), between 0 and 100 percent
                - Upper threshold (float), between 0 and 100 percent
        """
        return self.__parameters_transient # pragma: no cover
    
    @parameters_transient.setter
    def parameters_transient(self, value: GenericDataContainer):
        """Set parameters of the transient extraction step."""
        self.__parameters_transient = value

    def process(self):
        """Process the XTRACT algorithm.
        
        """
        # Wrapping
        self.__operator.connect(0, self.__input_signal)
        self.__operator.connect(1, self.__parameters_denoiser)
        self.__operator.connect(2, self.__parameters_tonal)
        self.__operator.connect(3, self.__parameters_transient)

        # Runs the operator
        self.__operator.run()

        # Stores the output in the variables
        if type(self.__input_signal) == Field:
            self.__noise_signal = self.__operator.get_output(0, "field")
            self.__tonal_signal = self.__operator.get_output(1, "field")
            self.__transient_signal = self.__operator.get_output(2, "field")
            self.__remainder_signal = self.__operator.get_output(3, "field")
        else:
            self.__noise_signal = self.__operator.get_output(0, "fields_container")
            self.__tonal_signal = self.__operator.get_output(1, "fields_container")
            self.__transient_signal = self.__operator.get_output(2, "fields_container")
            self.__remainder_signal = self.__operator.get_output(3, "fields_container")

    def get_output(self) -> Tuple[FieldsContainer, FieldsContainer, FieldsContainer, FieldsContainer] | Tuple[Field, Field, Field, Field]:
        """Get the output of the XTRACT algorithm.
        
        Returns
        -------
        Tuple[FieldsContainer, FieldsContainer, FieldsContainer, FieldsContainer] | Tuple[Field, Field, Field, Field]
            Noise signal, tonal signal, transient signal, and remainder signal, as fields or fields_containers.
        """
        if (self.__noise_signal is None) or (self.__tonal_signal is None) or (self.__transient_signal is None) or (self.__remainder_signal is None):
            warnings.warn(
                PyDpfSoundWarning("No output available.")
            )
        
        return self.__noise_signal, self.__tonal_signal, self.__transient_signal, self.__remainder_signal
    
    def get_output_as_nparray(self) -> Tuple[npt.ArrayLike, npt.ArrayLike, npt.ArrayLike, npt.ArrayLike]:
        """Get the output of the XTRACT algorithm as numpy arrays.
        
        Returns
        -------
        Tuple[np.array, np.array, np.array, np.array]
            Noise signal, tonal signal, transient signal, and remainder signal, as numpy arrays.
        """
        if (self.__noise_signal is None) or (self.__tonal_signal is None) or (self.__transient_signal is None) or (self.__remainder_signal is None):
            warnings.warn(
                PyDpfSoundWarning("No output available.")
            )

        l_output_noise_signal = self.get_output()[0]
        l_output_tonal_signal = self.get_output()[1]
        l_output_transient_signal = self.get_output()[2]
        l_output_remainder_signal = self.get_output()[3]

        if type(l_output_noise_signal) == Field:
            return l_output_noise_signal.data, l_output_tonal_signal.data, l_output_transient_signal.data, l_output_remainder_signal.data
        
        return self.convert_fields_container_to_np_array(l_output_noise_signal), self.convert_fields_container_to_np_array(l_output_tonal_signal), self.convert_fields_container_to_np_array(l_output_transient_signal), self.convert_fields_container_to_np_array(l_output_remainder_signal)
    
    def plot(self):
        """Plot the XTRACT algorithm results.
        
        """
        ################
        #
        # Plot noise signal
        #
        l_output_noise_signal = self.get_output()[0]

        if type(l_output_noise_signal) == Field:
            l_i_nb_channels = 0
            field = l_output_noise_signal
        else:
            l_i_nb_channels = len(l_output_noise_signal)
            field = l_output_noise_signal[0]
        
        l_time_data = field.time_freq_support.time_frequencies.data
        l_time_unit = field.time_freq_support.time_frequencies.unit
        l_unit = field.unit

        for l_i in range(l_i_nb_channels):
            plt.plot(l_time_data, l_output_noise_signal[l_i].data, label=f"Channel {l_i}")
            plt.xlabel(f"Time ({l_time_unit})")
            plt.ylabel(f"Amplitude ({l_unit})")
            plt.title("Noise signal")
            plt.show()

        ################
        # Delete intermediate variables
        del l_i_nb_channels, field, l_output_noise_signal
        del l_time_data, l_time_unit, l_unit

        ################
        #
        # Plot tonal signal
        #
        l_output_tonal_signal = self.get_output()[1]

        if type(l_output_tonal_signal) == Field:
            l_i_nb_channels = 0
            field = l_output_tonal_signal
        else:
            l_i_nb_channels = len(l_output_tonal_signal)
            field = l_output_tonal_signal[0]

        l_time_data = field.time_freq_support.time_frequencies.data
        l_time_unit = field.time_freq_support.time_frequencies.unit
        l_unit = field.unit

        for l_i in range(l_i_nb_channels):
            plt.plot(l_time_data, l_output_tonal_signal[l_i].data, label=f"Channel {l_i}")
            plt.xlabel(f"Time ({l_time_unit})")
            plt.ylabel(f"Amplitude ({l_unit})")
            plt.title("Tonal signal")
            plt.show()

        ################
        # Delete intermediate variables
        del l_i_nb_channels, field, l_output_tonal_signal
        del l_time_data, l_time_unit, l_unit

        ################
        #
        # Plot transient signal
        #
        l_output_transient_signal = self.get_output()[2]

        if type(l_output_transient_signal) == Field:
            l_i_nb_channels = 0
            field = l_output_transient_signal
        else:
            l_i_nb_channels = len(l_output_transient_signal)
            field = l_output_transient_signal[0]
        
        l_time_data = field.time_freq_support.time_frequencies.data
        l_time_unit = field.time_freq_support.time_frequencies.unit
        l_unit = field.unit

        for l_i in range(l_i_nb_channels):
            plt.plot(l_time_data, l_output_transient_signal[l_i].data, label=f"Channel {l_i}")
            plt.xlabel(f"Time ({l_time_unit})")
            plt.ylabel(f"Amplitude ({l_unit})")
            plt.title("Transient signal")
            plt.show()
        
        ################
        # Delete intermediate variables
        del l_i_nb_channels, field, l_output_transient_signal
        del l_time_data, l_time_unit, l_unit

        ################
        #
        # Plot remainder signal
        #
        l_output_remainder_signal = self.get_output()[3]

        if type(l_output_remainder_signal) == Field:
            l_i_nb_channels = 0
            field = l_output_remainder_signal
        else:
            l_i_nb_channels = len(l_output_remainder_signal)
            field = l_output_remainder_signal[0]
        
        l_time_data = field.time_freq_support.time_frequencies.data
        l_time_unit = field.time_freq_support.time_frequencies.unit
        l_unit = field.unit

        for l_i in range(l_i_nb_channels):
            plt.plot(l_time_data, l_output_remainder_signal[l_i].data, label=f"Channel {l_i}")
            plt.xlabel(f"Time ({l_time_unit})")
            plt.ylabel(f"Amplitude ({l_unit})")
            plt.title("Remainder signal")
            plt.show()
        
        ################
        # Delete intermediate variables
        del l_i_nb_channels, field, l_output_remainder_signal
        del l_time_data, l_time_unit, l_unit



        
        
    
