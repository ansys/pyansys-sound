"""Xtract tonal module."""

from typing import Tuple
import warnings

from ansys.dpf.core import Field, FieldsContainer, GenericDataContainer, Operator
import matplotlib.pyplot as plt
import numpy as np
from numpy import typing as npt

from . import XtractParent
from ..pydpf_sound import PyDpfSoundException, PyDpfSoundWarning


class XtractTonal(XtractParent):
    """Xtract tonal class.

    Signal tonal analysis using the XTRACT algorithm.
    """

    def __init__(
        self,
        input_signal: FieldsContainer | Field = None,
        input_parameters: GenericDataContainer = None,
    ):
        """Create a XtractTonal class.

        Parameters
        ----------
        input_signal:
            Signal(s) from which we want to extract tonal components,
            as a field or fields_container.
            When inputting a fields_container,
            each signal (each field of the fields_container) is processed individually.
        input_parameters:
            Structure that contains the parameters of the algorithm:
                                - Nfft (int) in number of samples
                                - Regularity setting (float) in percent
                                - Maximum slope (float) in dB/Hz
                                - Minimum duration (float) in seconds
                                - Intertonal gap (float) in Hz
                                - Local smergence (float) in dB
                        This structure is of type Xtract_tonal_parameters
                        (see this class for more details).
        output_tonal_signals:
            Tonal signal(s), as a field or fields_container (depending on the input).
        """
        super().__init__()
        self.__input_signal = input_signal
        self.__input_parameters = input_parameters

        # Def output fields
        self.__output_tonal_signals = None
        self.__output_non_tonal_signals = None

        self._output = (self.__output_tonal_signals, self.__output_non_tonal_signals)

        self.__operator = Operator("xtract_tonal")

    @property
    def input_signal(self) -> FieldsContainer | Field:
        """Get input signal.

        Returns
        -------
        FieldsContainer | Field
            Signal(s) from which we want to extract tonal components,
            as a field or fields_container.
            When inputting a fields_container, each signal (each field of the fields_container)
            is processed individually.
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
                - Nfft (int) in number of samples
                - Regularity setting (float) in percent
                - Maximum slope (float) in dB/Hz
                - Minimum duration (float) in seconds
                - Intertonal gap (float) in Hz
                - Local smergence (float) in dB
        """
        return self.__input_parameters

    @input_parameters.setter
    def input_parameters(self, value: GenericDataContainer):
        """Set input parameters."""
        self.__input_parameters = value

    @property
    def output_tonal_signals(self) -> FieldsContainer | Field:
        """Get output tonal signals.

        Returns
        -------
        FieldsContainer | Field
            Tonal signal(s), as a field or fields_container (depending on the input).
        """
        return self.__output_tonal_signals  # pragma: no cover

    @property
    def output_non_tonal_signals(self) -> FieldsContainer | Field:
        """Get output non tonal signals.

        Returns
        -------
        FieldsContainer | Field
            Non tonal signal(s), as a field or fields_container (depending on the input).
        """
        return self.__output_non_tonal_signals  # pragma: no cover

    def process(self):
        """Process the tonal analysis."""
        if self.__input_signal is None:
            raise PyDpfSoundException("No input signal for tonal analysis.")

        if self.__input_parameters is None:
            raise PyDpfSoundException("Input parameters are not set.")

        self.__operator.connect(0, self.__input_signal)
        self.__operator.connect(1, self.__input_parameters)

        # Run the operator
        self.__operator.run()

        # Stores the output in the variable
        if type(self.__input_signal) == Field:
            self.__output_tonal_signals = self.__operator.get_output(0, "field")
            self.__output_non_tonal_signals = self.__operator.get_output(1, "field")
        else:
            self.__output_tonal_signals = self.__operator.get_output(0, "fields_container")
            self.__output_non_tonal_signals = self.__operator.get_output(1, "fields_container")

        self._output = (self.__output_tonal_signals, self.__output_non_tonal_signals)

    def get_output(self) -> Tuple[FieldsContainer, FieldsContainer] | Tuple[Field, Field]:
        """Get the output of the tonal."""
        if self.__output_tonal_signals == None or self.__output_non_tonal_signals == None:
            warnings.warn(PyDpfSoundWarning("Output tonal or non tonal signals are not set"))

        return self.__output_tonal_signals, self.__output_non_tonal_signals

    def get_output_as_nparray(self) -> Tuple[npt.ArrayLike, npt.ArrayLike]:
        """Get the output of the tonal as numpy arrays.

        Returns
        -------
        Tuple[npt.ArrayLike, npt.ArrayLike]
            Tonal and non tonal signals as numpy arrays.
        """
        if self.__output_tonal_signals == None or self.__output_non_tonal_signals == None:
            warnings.warn(PyDpfSoundWarning("Output tonal or non tonal signals are not set"))

        l_output_tonal_signals = self.get_output()[0]
        l_output_non_tonal_signals = self.get_output()[1]

        if type(l_output_tonal_signals) == Field:
            return np.array(l_output_tonal_signals.data), np.array(l_output_non_tonal_signals.data)
        else:
            if self.__output_tonal_signals == None or self.__output_non_tonal_signals == None:
                return np.array([]), np.array([])
            else:
                return np.array(
                    self.convert_fields_container_to_np_array(l_output_tonal_signals)
                ), np.array(self.convert_fields_container_to_np_array(l_output_non_tonal_signals))

    def plot(self):
        """Plot the output of the tonal analysis.

        Plot the tonal and non tonal signals.
        """
        l_output_tonal_signals = self.get_output()[0]
        field = (
            l_output_tonal_signals
            if type(l_output_tonal_signals) == Field
            else l_output_tonal_signals[0]
        )

        l_np_output_tonal_signals, l_np_output_non_tonal_signals = self.get_output_as_nparray()

        l_time_data = field.time_freq_support.time_frequencies.data
        l_time_unit = field.time_freq_support.time_frequencies.unit
        l_unit = field.unit

        ################
        # Note: by design, we have l_np_output_tonal_signals.ndim
        # == l_np_output_non_tonal_signals.ndim
        if l_np_output_tonal_signals.ndim == 1:
            ################
            # Field type
            plt.figure()
            plt.plot(l_time_data, l_np_output_tonal_signals, label=f"Channel 0")
            plt.xlabel(f"Time ({l_time_unit})")
            plt.ylabel(f"Amplitude ({l_unit})")
            plt.title("Tonal signal - channel 0")

            plt.figure()
            plt.plot(l_time_data, l_np_output_non_tonal_signals, label=f"Channel 0")
            plt.xlabel(f"Time ({l_time_unit})")
            plt.ylabel(f"Amplitude ({l_unit})")
            plt.title("Non tonal signal - channel 0")
        else:
            ################
            # FieldsContainer type
            for l_i in range(len(l_np_output_tonal_signals)):
                plt.figure()
                plt.plot(l_time_data, l_np_output_tonal_signals[l_i], label=f"Channel {l_i}")
                plt.xlabel(f"Time ({l_time_unit})")
                plt.ylabel(f"Amplitude ({l_unit})")
                plt.title(f"Tonal signal - channel {l_i}")

            for l_i in range(len(l_np_output_non_tonal_signals)):
                plt.figure()
                plt.plot(l_time_data, l_np_output_non_tonal_signals[l_i], label=f"Channel {l_i}")
                plt.xlabel(f"Time ({l_time_unit})")
                plt.ylabel(f"Amplitude ({l_unit})")
                plt.title(f"Non tonal signal - channel {l_i}")

        ################
        # Delete intermediate variables
        del field, l_np_output_tonal_signals, l_np_output_non_tonal_signals
        del l_time_data, l_time_unit, l_unit

        # Show all figures created
        plt.show()
