"""Xtract denoiser parameters."""

from ansys.dpf.core import Field, GenericDataContainer, Operator

from . import XtractParent
from ..pyansys_sound import PyAnsysSoundException

ID_DENOISER_PARAMETERS_CLASS = "Xtract_denoiser_parameters"
ID_NOISE_PSD = "noise_levels"


class XtractDenoiserParameters(XtractParent):
    """Data class for denoiser parameters that can be used in Xtract and XtractDenoiser."""

    def __init__(self, noise_psd: Field = None):
        """Init.

        Parameters
        ----------
        noise_psd:
            Power spectral density of the noise in unit^2/Hz (Pa^2/Hz for example).
            Can be produced using either:
            - XtractDenoiserParameters.create_noise_psd_from_white_noise_level()
            - XtractDenoiserParameters.create_noise_psd_from_noise_samples()
            - XtractDenoiserParameters.create_noise_psd_from_automatic_estimation()
        """
        self.__generic_data_container = GenericDataContainer()
        self.__generic_data_container.set_property("class_name", ID_DENOISER_PARAMETERS_CLASS)

        if noise_psd is None:
            noise_psd = Field()

        self.noise_psd = noise_psd

    @property
    def noise_psd(self):
        """Noise PSD property."""
        return self.__generic_data_container.get_property(ID_NOISE_PSD)  # pragma: no cover

    @noise_psd.setter
    def noise_psd(self, noise_psd: Field):
        """Set the noise PSD."""
        if noise_psd is None:
            raise PyAnsysSoundException("Noise PSD must be a non-empty Field.")

        self.__generic_data_container.set_property(ID_NOISE_PSD, noise_psd)

    @noise_psd.getter
    def noise_psd(self) -> Field:
        """Get the noise PSD.

        Returns
        -------
        Field
            The noise PSD as a Field.
        """
        return self.__generic_data_container.get_property(ID_NOISE_PSD)

    def get_parameters_as_generic_data_container(self) -> GenericDataContainer:
        """Get the parameters as generic data container.

        Returns
        -------
        GenericDataContainer
            The parameter structure as a GenericDataContainer
        """
        return self.__generic_data_container

    def create_noise_psd_from_white_noise_level(
        self, white_noise_level: float, sampling_frequency: float, window_length: int = 50
    ) -> Field:
        """Create a power spectral density of noise from white noise level.

        Parameters
        ----------
        white_noise_level:
            Power of the white noise (dB SPL).
        sampling_frequency:
            Sampling frequency in Hz of the signal to denoise
            (which can be different from the signal used for creating the noise profile).
        window_length:
            (Optional) Window length for the noise level estimation in ms.
            Default is 50 ms.

        Returns
        -------
        Field
            Power spectral density of noise in unit^2/Hz (Pa^2/Hz for example).
        """
        op = Operator("create_noise_profile_from_white_noise_power")
        op.connect(0, white_noise_level)
        op.connect(1, sampling_frequency)
        op.connect(2, int(window_length))
        op.run()

        f = op.get_output(0, "field")
        return f

    def create_noise_psd_from_noise_samples(
        self, signal: Field, sampling_frequency: float, window_length: int = 50
    ) -> Field:
        """Create a power spectral density of noise from specific noise samples.

        Parameters
        ----------
        signal:
            Noise signal (field).
        sampling_frequency:
            (Optional) Sampling frequency in Hz of the signal to denoise
            (which can be different from the signal used for creating the noise profile).
            Default is the sampling frequency of the noise signal.
        window_length:
            (Optional) Window length for the noise level estimation in ms.
            Default is 50 ms.

        Returns
        -------
        Field
            Power spectral density of noise in unit^2/Hz (Pa^2/Hz for example).
        """
        op = Operator("create_noise_profile_from_noise_samples")
        op.connect(0, signal)
        op.connect(1, sampling_frequency)
        op.connect(2, window_length)
        op.run()

        f = op.get_output(0, "field")
        return f

    def create_noise_psd_from_automatic_estimation(
        self, signal: Field, window_length: int = 50
    ) -> Field:
        """Create a power spectral density of noise using an automatic estimation.

        Parameters
        ----------
        signal:
            Signal (field) from which to estimate the noise profile.
        window_length:
            (Optional) Window length for the noise level estimation in ms.
            Default is 50 ms.

        Returns
        -------
        Field
            Power spectral density of noise in unit^2/Hz (Pa^2/Hz for example).
        """
        op = Operator("create_noise_profile_from_automatic_estimation")
        op.connect(0, signal)
        op.connect(1, window_length)
        op.run()

        f = op.get_output(0, "field")
        return f
