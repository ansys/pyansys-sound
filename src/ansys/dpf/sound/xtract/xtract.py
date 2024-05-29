"""Xtract class."""

from typing import Tuple
import warnings

from ansys.dpf.core import Field, FieldsContainer, Operator
import matplotlib.pyplot as plt
import numpy as np
from numpy import typing as npt

from . import (
    XtractDenoiserParameters,
    XtractParent,
    XtractTonalParameters,
    XtractTransientParameters,
)
from ..pydpf_sound import PyDpfSoundException, PyDpfSoundWarning


class Xtract(XtractParent):
    """Xtract class.

    XTRACT processing: in the same way as in Sound SAS, this operator chains a denoising step,
    followed by a tonal extraction step and then a transient extraction step.
    It returns the individual signals processed at each step, as well as the remainder.
    """

    def __init__(
        self,
        input_signal: FieldsContainer | Field = None,
        parameters_denoiser: XtractDenoiserParameters = None,
        parameters_tonal: XtractTonalParameters = None,
        parameters_transient: XtractTransientParameters = None,
    ):
        """Create a Xtract class.

        Parameters
        ----------
        input_signal:
            Signal(s) on which to apply the XTRACT processing, as a field or fields container.
        parameters_denoiser:
            Structure that contains the parameters of the denoising step:
            - Noise levels (Field): level vs frequency of the noise
            This structure is of type XtractDenoiserParameters (see this class for more details).
        parameters_tonal:
            Structure that contains the parameters of the tonal extraction step:
            - NFFT (int) number of points used for the FFT computation
            - Regularity setting (float) in percent
            - Maximum slope (float) in dB/Hz
            - Minimum duration (float) in seconds
            - Intertonal gap (float) in Hz
            - Local emergence (float) in dB
            This structure is of type XtractTonalParameters (see this class for more details).
        parameters_transient:
            Structure that contains the parameters of the transient extraction step:
            - Lower threshold (float), between 0 and 100 percent
            - Upper threshold (float), between 0 and 100 percent
        This structure is of type XtractTransientParameters (see this class for more details).
        """
        super().__init__()
        self.input_signal = input_signal
        self.parameters_denoiser = parameters_denoiser
        self.parameters_tonal = parameters_tonal
        self.parameters_transient = parameters_transient

        # Define output fields
        self.__output_noise_signal = None
        self.__output_tonal_signal = None
        self.__output_transient_signal = None
        self.__output_remainder_signal = None

        self._output = (
            self.__output_noise_signal,
            self.__output_tonal_signal,
            self.__output_transient_signal,
            self.__output_remainder_signal,
        )

        self.__operator = Operator("xtract")

    @property
    def input_signal(self) -> FieldsContainer | Field:
        """Get input signal.

        Returns
        -------
        FieldsContainer | Field
            Signal(s) on which to apply the XTRACT processing, as a field or fields container.
        """
        return self.__input_signal  # pragma: no cover

    @input_signal.setter
    def input_signal(self, value: FieldsContainer | Field):
        """Set input signal."""
        self.__input_signal = value

    @property
    def parameters_denoiser(self) -> XtractDenoiserParameters:
        """Get parameters of the denoiser step.

        Returns
        -------
        XtractDenoiserParameters
            Structure that contains the parameters of the denoising step:
                - Noise levels (Field): level vs frequency of the noise
        """
        return self.__parameters_denoiser

    @parameters_denoiser.setter
    def parameters_denoiser(self, value: XtractDenoiserParameters):
        """Set parameters of the denoiser step."""
        self.__parameters_denoiser = value

    @property
    def parameters_tonal(self) -> XtractTonalParameters:
        """Get parameters of the tonal extraction step.

        Returns
        -------
        GenericDataContainer
            Structure that contains the parameters of the tonal extraction step:
                - NFFT (int) number of points used for the FFT computation
                - Regularity setting (float) in percent
                - Maximum slope (float) in dB/Hz
                - Minimum duration (float) in seconds
                - Intertonal gap (float) in Hz
                - Local emergence (float) in dB
        """
        return self.__parameters_tonal  # pragma: no cover

    @parameters_tonal.setter
    def parameters_tonal(self, value: XtractTonalParameters):
        """Set parameters of the tonal extraction step."""
        self.__parameters_tonal = value

    @property
    def parameters_transient(self) -> XtractTransientParameters:
        """Get parameters of the transient extraction step.

        Returns
        -------
        XtractTransientParameters
            Structure that contains the parameters of the transient extraction step:
                - Lower threshold (float), between 0 and 100 percent
                - Upper threshold (float), between 0 and 100 percent
        """
        return self.__parameters_transient  # pragma: no cover

    @parameters_transient.setter
    def parameters_transient(self, value: XtractTransientParameters):
        """Set parameters of the transient extraction step."""
        self.__parameters_transient = value

    @property
    def output_noise_signal(self) -> Tuple[FieldsContainer, FieldsContainer] | Tuple[Field, Field]:
        """Get noise signal.

        Returns
        -------
        Tuple[FieldsContainer, FieldsContainer] | Tuple[Field, Field]
            Noise signal, as a field or fields container.
        """
        return self.__output_noise_signal  # pragma: no cover

    @property
    def output_tonal_signal(self) -> Tuple[FieldsContainer, FieldsContainer] | Tuple[Field, Field]:
        """Get tonal signal.

        Returns
        -------
        Tuple[FieldsContainer, FieldsContainer] | Tuple[Field, Field]
            Tonal signal, as a field or fields container.
        """
        return self.__output_tonal_signal  # pragma: no cover

    @property
    def output_transient_signal(
        self,
    ) -> Tuple[FieldsContainer, FieldsContainer] | Tuple[Field, Field]:
        """Get transient signal.

        Returns
        -------
        Tuple[FieldsContainer, FieldsContainer] | Tuple[Field, Field]
            Transient signal, as a field or fields container.
        """
        return self.__output_transient_signal  # pragma: no cover

    @property
    def output_remainder_signal(
        self,
    ) -> Tuple[FieldsContainer, FieldsContainer] | Tuple[Field, Field]:
        """Get remainder signal.

        Returns
        -------
        Tuple[FieldsContainer, FieldsContainer] | Tuple[Field, Field]
            Remainder signal, as a field or fields container.
        """
        return self.__output_remainder_signal  # pragma: no cover

    def process(self):
        """Process the XTRACT algorithm."""
        if self.input_signal is None:
            raise PyDpfSoundException("Input signal is not set.")

        if self.parameters_denoiser is None:
            raise PyDpfSoundException("Input parameters denoiser are not set.")

        if self.parameters_tonal is None:
            raise PyDpfSoundException("Input parameters tonal are not set.")

        if self.parameters_transient is None:
            raise PyDpfSoundException("Input parameters transient are not set.")

        # Wrapping
        self.__operator.connect(0, self.input_signal)
        self.__operator.connect(
            1, self.parameters_denoiser.get_parameters_as_generic_data_container()
        )
        self.__operator.connect(2, self.parameters_tonal.get_parameters_as_generic_data_container())
        self.__operator.connect(
            3, self.parameters_transient.get_parameters_as_generic_data_container()
        )

        # Runs the operator
        self.__operator.run()

        # Stores the output in the variables
        if type(self.input_signal) == Field:
            self.__output_noise_signal = self.__operator.get_output(0, "fields_container")[0]
            self.__output_tonal_signal = self.__operator.get_output(1, "fields_container")[0]
            self.__output_transient_signal = self.__operator.get_output(2, "fields_container")[0]
            self.__output_remainder_signal = self.__operator.get_output(3, "fields_container")[0]
        else:
            self.__output_noise_signal = self.__operator.get_output(0, "fields_container")
            self.__output_tonal_signal = self.__operator.get_output(1, "fields_container")
            self.__output_transient_signal = self.__operator.get_output(2, "fields_container")
            self.__output_remainder_signal = self.__operator.get_output(3, "fields_container")

        self._output = (
            self.__output_noise_signal,
            self.__output_tonal_signal,
            self.__output_transient_signal,
            self.__output_remainder_signal,
        )

    def get_output(
        self,
    ) -> (
        Tuple[FieldsContainer, FieldsContainer, FieldsContainer, FieldsContainer]
        | Tuple[Field, Field, Field, Field]
    ):
        """Get the output of the XTRACT algorithm.

        Returns
        -------
        Tuple[FieldsContainer, FieldsContainer, FieldsContainer, FieldsContainer] |
        Tuple[Field, Field, Field, Field]
            Noise signal, tonal signal, transient signal, and remainder signal,
            as fields or fields containers.
        """
        if (
            (self.__output_noise_signal is None)
            or (self.__output_tonal_signal is None)
            or (self.__output_transient_signal is None)
            or (self.__output_remainder_signal is None)
        ):
            warnings.warn(PyDpfSoundWarning("No output available."))

        return (
            self.__output_noise_signal,
            self.__output_tonal_signal,
            self.__output_transient_signal,
            self.__output_remainder_signal,
        )

    def get_output_as_nparray(
        self,
    ) -> Tuple[npt.ArrayLike, npt.ArrayLike, npt.ArrayLike, npt.ArrayLike]:
        """Get the output of the XTRACT algorithm as numpy arrays.

        Returns
        -------
        Tuple[numpy.array, numpy.array, numpy.array, numpy.array]
            Noise signal, tonal signal, transient signal, and remainder signal, as numpy arrays.
        """
        (
            l_output_noise_signal,
            l_output_tonal_signal,
            l_output_transient_signal,
            l_output_remainder_signal,
        ) = self.get_output()

        if type(l_output_noise_signal) == Field:
            return (
                np.array(l_output_noise_signal.data),
                np.array(l_output_tonal_signal.data),
                np.array(l_output_transient_signal.data),
                np.array(l_output_remainder_signal.data),
            )
        else:
            if (
                self.output_noise_signal is None
                or self.output_tonal_signal is None
                or self.output_transient_signal is None
                or self.output_remainder_signal is None
            ):
                return np.array([]), np.array([]), np.array([]), np.array([])
            else:
                return (
                    self.convert_fields_container_to_np_array(l_output_noise_signal),
                    self.convert_fields_container_to_np_array(l_output_tonal_signal),
                    self.convert_fields_container_to_np_array(l_output_transient_signal),
                    self.convert_fields_container_to_np_array(l_output_remainder_signal),
                )

    def plot(self):
        """Plot the XTRACT algorithm results."""
        l_output_noise_signal = self.get_output()[0]

        l_output_noise_signal_as_field = (
            l_output_noise_signal
            if type(l_output_noise_signal) == Field
            else l_output_noise_signal[0]
        )

        l_time_data = l_output_noise_signal_as_field.time_freq_support.time_frequencies.data
        l_time_unit = l_output_noise_signal_as_field.time_freq_support.time_frequencies.unit
        l_unit = l_output_noise_signal_as_field.unit

        (
            l_np_output_noise_signal,
            l_np_output_tonal_signal,
            l_np_output_transient_signal,
            l_np_output_remainder_signal,
        ) = self.get_output_as_nparray()

        if l_np_output_noise_signal.ndim == 1:
            ###########
            # Field type
            _, axs = plt.subplots(4, figsize=(10, 20))

            axs[0].plot(l_time_data, l_np_output_noise_signal)
            axs[0].set_ylabel(f"Amplitude ({l_unit})")
            axs[0].set_title("Noise signal")

            axs[1].plot(l_time_data, l_np_output_tonal_signal)
            axs[1].set_ylabel(f"Amplitude ({l_unit})")
            axs[1].set_title("Tonal signal")

            axs[2].plot(l_time_data, l_np_output_transient_signal)
            axs[2].set_ylabel(f"Amplitude ({l_unit})")
            axs[2].set_title("Transient signal")

            axs[3].plot(l_time_data, l_np_output_remainder_signal)
            axs[3].set_xlabel(f"Time ({l_time_unit})")
            axs[3].set_ylabel(f"Amplitude ({l_unit})")
            axs[3].set_title("Remainder signal")
        else:
            ###########
            # FieldsContainer type
            for l_i in range(len(l_np_output_noise_signal)):
                _, axs = plt.subplots(4, figsize=(10, 20))

                axs[0].plot(l_time_data, l_np_output_noise_signal[l_i])
                axs[0].set_ylabel(f"Amplitude ({l_unit})")
                axs[0].set_title(f"Noise signal - channel {l_i}")

                axs[1].plot(l_time_data, l_np_output_tonal_signal[l_i])
                axs[1].set_ylabel(f"Amplitude ({l_unit})")
                axs[1].set_title(f"Tonal signal - channel {l_i}")

                axs[2].plot(l_time_data, l_np_output_transient_signal[l_i])
                axs[2].set_ylabel(f"Amplitude ({l_unit})")
                axs[2].set_title(f"Transient signal - channel {l_i}")

                axs[3].plot(l_time_data, l_np_output_remainder_signal[l_i])
                axs[3].set_xlabel(f"Time ({l_time_unit})")
                axs[3].set_ylabel(f"Amplitude ({l_unit})")
                axs[3].set_title(f"Remainder signal - channel {l_i}")

        # Show all figures created
        plt.show()
