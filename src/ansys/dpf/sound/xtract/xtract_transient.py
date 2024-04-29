"""Xtract  transient module."""

import warnings
from typing import overload, Tuple

from ansys.dpf.core import Field, FieldsContainer, Operator, GenericDataContainer
import matplotlib.pyplot as plt
from numpy import typing as npt


from . import XtractParent
from ..pydpf_sound import PyDpfSoundException, PyDpfSoundWarning

class XtractTransient(XtractParent):
    """Xtract transient class.
    
    Extract the ransient components of a signal using the XTRACT algorithm.
    """

    def __init__(
        self,
        input_signal: FieldsContainer | Field = None,
        input_parameters: GenericDataContainer = None
    ):
        """Create a XtractTransient class.

        Parameters
        ----------
        input_signal: 
            Signal(s) on which we want to extract transient components, as a field or fields_container. When inputting a fields_container, each signal (each field of the fields_container) is processed individually.
        input_parameters:
            Structure that contains the parameters of the algorithm: 
						- Lower threshold (float), between 0 and 100 percent
						- Upper threshold (float), between 0 and 100 percent
			This structure is of type Xtract_transient_parameters (see this class for more details).
        output_transient_signals:
            Transient signal(s), as a field or fields_container (depending on the input).
        output_non_transient_signals:
            Non-transient signal(s): original signal minus transient signal, as a field or fields_container (depending on the input).
        """
        super().__init__()
        self.__input_signal = input_signal
        self.__input_parameters = input_parameters

        # Def output fields
        self.__output_transient_signals = None
        self.__output_non_transient_signals = None

        self.__operator = Operator("xtract_transient")

    @property
    def input_signal(self) -> FieldsContainer | Field:
        """Get input signal.
        
        Returns
        -------
        FieldsContainer | Field
            Signal(s) on which we want to extract transient components, as a field or fields_container. When inputting a fields_container, each signal (each field of the fields_container) is processed individually.
        """
        return self.__input_signal  # pragma: no cover
    
    @input_signal.setter
    def input_signal(self, value: FieldsContainer | Field):
        """Set input signal.
        
        Parameters
        ----------
        value: FieldsContainer | Field
            Signal(s) on which we want to extract transient components, as a field or fields_container. When inputting a fields_container, each signal (each field of the fields_container) is processed individually.
        """
        self.__input_signal = value

    @property
    def input_parameters(self) -> GenericDataContainer:
        """Get input parameters.
        
        Returns
        -------
        GenericDataContainer
            Structure that contains the parameters of the algorithm: 
                        - Lower threshold (float), between 0 and 100 percent
                        - Upper threshold (float), between 0 and 100 percent
        """
        return self.__input_parameters  # pragma: no cover
    
    @input_parameters.setter
    def input_parameters(self, value: GenericDataContainer):
        """Set input parameters.
        
        Parameters
        ----------
        value: GenericDataContainer
            Structure that contains the parameters of the algorithm: 
                        - Lower threshold (float), between 0 and 100 percent
                        - Upper threshold (float), between 0 and 100 percent
        """
        self.__input_parameters = value

    @property
    def output_transient_signals(self) -> FieldsContainer | Field:
        """Get output transient signals.
        
        Returns
        -------
        FieldsContainer | Field
            Transient signal(s), as a field or fields_container (depending on the input).
        """
        return self.__output_transient_signals  # pragma: no cover
    
    @output_transient_signals.setter
    def output_transient_signals(self, value: FieldsContainer | Field):
        """Set output transient signals.
        
        Parameters
        ----------
        value: FieldsContainer | Field
            Transient signal(s), as a field or fields_container (depending on the input).
        """
        self.__output_transient_signals = value

    @property
    def output_non_transient_signals(self) -> FieldsContainer | Field:
        """Get output non transient signals.
        
        Returns
        -------
        FieldsContainer | Field
            Non-transient signal(s): original signal minus transient signal, as a field or fields_container (depending on the input).
        """
        return self.__output_non_transient_signals  # pragma: no cover
    
    @output_non_transient_signals.setter
    def output_non_transient_signals(self, value: FieldsContainer | Field):
        """Set output non transient signals.
        
        Parameters
        ----------
        value: FieldsContainer | Field
            Non-transient signal(s): original signal minus transient signal, as a field or fields_container (depending on the input).
        """
        self.__output_non_transient_signals = value

    def process(self):
        """Process the transient extraction.
        
        Extract the transient components of the signal(s) using the XTRACT algorithm.
        """
        
        if self.__input_signal is None:
            raise PyDpfSoundException("Input signal is not set.")
        
        if self.__input_parameters is None:
            raise PyDpfSoundException("Input parameters are not set.")
        
        self.__operator.connect(0, self.__input_signal)
        self.__operator.connect(1, self.__input_parameters)

        # Run the operator
        self.__operator.run()

        # Stores the output in the variable
        if type(self.__input_signal) == Field:
            self.__output_transient_signals = self.__operator.get_output(0, "field")
            self.__output_non_transient_signals = self.__operator.get_output(1, "field")
        else:
            self.__output_transient_signals = self.__operator.get_output(0, "fields_container")
            self.__output_non_transient_signals = self.__operator.get_output(1, "fields_container")

    def get_output(self) -> Tuple[FieldsContainer, FieldsContainer] | Tuple[Field, Field]:
        """Get the output of the transient extraction.
        
        Returns
        -------
        Tuple[FieldsContainer, FieldsContainer] | Tuple[Field, Field]
            Transient signal(s) and non-transient signal(s), as a field or fields_container (depending on the input).
        """
        if self.__output_transient_signals is None or self.__output_non_transient_signals is None:
            warnings.warn(
                PyDpfSoundWarning("Output transient signals or output non transient signals are not set.")
            )
        
        return self.__output_transient_signals, self.__output_non_transient_signals
    
    def get_output_as_nparray(self) -> Tuple[npt.ArrayLike, npt.ArrayLike]:
        """Get the output of the transient extraction as numpy arrays.
        
        Returns
        -------
        Tuple[np.ArrayLike, np.ArrayLike]
            Transient signal(s) and non-transient signal(s) as numpy arrays.
        """
        l_output_transient_signals = self.get_output()[0]
        l_output_non_transient_signals = self.get_output()[1]

        if type(l_output_transient_signals) == Field:
            return l_output_transient_signals.data, l_output_non_transient_signals.data
        
        return self.convert_fields_container_to_np_array(l_output_transient_signals), self.convert_fields_container_to_np_array(l_output_non_transient_signals)
    
    def plot(self):
        """Plot signals.

        Plot the transient signal and the non-transient signal.
        """
        ################
        #
        # Plot transient signal
        #
        l_output_transient_signals = self.get_output()[0]

        if type(l_output_transient_signals) == Field:
            l_i_nb_channels = 0
            field = l_output_transient_signals
        else:
            l_i_nb_channels = len(l_output_transient_signals)
            field = l_output_transient_signals[0]
        
        l_time_data = field.time_freq_support.time_frequencies.data
        l_time_unit = field.time_freq_support.time_frequencies.unit
        l_unit = field.unit

        for l_i in range(l_i_nb_channels):
            plt.plot(l_time_data, l_output_transient_signals.data[l_i], label=f"Transient signal {l_i}")
            plt.xlabel(f"Time ({l_time_unit})")
            plt.ylabel(f"Amplitude ({l_unit})")
            plt.title("Transient signal")
            plt.show()

        ################
        # Delete intermediate variables
        del l_i_nb_channels, field, l_output_transient_signals
        del l_time_data, l_time_unit, l_unit

        ################
        #
        # Plot non transient signal
        #
        l_output_non_transient_signals = self.get_output()[1]

        if type(l_output_non_transient_signals) == Field:
            l_i_nb_channels = 0
            field = l_output_non_transient_signals
        else:
            l_i_nb_channels = len(l_output_non_transient_signals)
            field = l_output_non_transient_signals[0]
        
        l_time_data = field.time_freq_support.time_frequencies.data
        l_time_unit = field.time_freq_support.time_frequencies.unit
        l_unit = field.unit

        for l_i in range(l_i_nb_channels):
            plt.plot(l_time_data, l_output_non_transient_signals.data[l_i], label=f"Non transient signal {l_i}")
            plt.xlabel(f"Time ({l_time_unit})")
            plt.ylabel(f"Amplitude ({l_unit})")
            plt.title("Non transient signal")
            plt.show()

        ################
        # Delete intermediate variables
        del l_i_nb_channels, field, l_output_non_transient_signals
        del l_time_data, l_time_unit, l_unit
