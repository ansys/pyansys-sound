"""Xtract denoiser parameters."""

from ansys.dpf.core import Field, GenericDataContainer, Operator

from . import XtractParent
from ..pydpf_sound import PyDpfSoundException

ID_DENOISER_PARAMETERS_CLASS = "Xtract_denoiser_parameters"
ID_NOISE_LEVELS = "noise_levels"


class XtractDenoiserParameters(XtractParent):
    """Data class for denoiser parameters that can be used in Xtract and XtractDenoiser."""

    def __init__(self, noise_levels: Field = None):
        """Init.

        Parameters
        ----------
        noise_levels:
            Noise levels are expected as a Field, the data corresponds
            to the amplitudes of the spectrum noise.
        """
        self.__generic_data_container = GenericDataContainer()
        self.__generic_data_container.set_property("class_name", ID_DENOISER_PARAMETERS_CLASS)

        if noise_levels is None:
            noise_levels = Field()

        self.noise_levels = noise_levels

    @property
    def noise_levels(self):
        """Noise levels property."""
        return self.__generic_data_container.get_property(ID_NOISE_LEVELS)  # pragma: no cover

    @noise_levels.setter
    def noise_levels(self, noise_levels: Field):
        """Set the noise levels."""
        if noise_levels is None:
            raise PyDpfSoundException("Noise levels must be a non-empty Field.")

        self.__generic_data_container.set_property(ID_NOISE_LEVELS, noise_levels)

    @noise_levels.getter
    def noise_levels(self) -> Field:
        """Get the noise levels.

        Returns
        -------
        Field
            The noise levels as a Field.
        """
        return self.__generic_data_container.get_property(ID_NOISE_LEVELS)

    def get_parameters_as_generic_data_container(self) -> GenericDataContainer:
        """Get the parameters as generic data container.

        Returns
        -------
        GenericDataContainer
            The parameter structure as a GenericDataContainer
        """
        return self.__generic_data_container

    def create_noise_levels_from_white_noise_power(
        self, white_noise_power: float, sampling_frequency: float, window_length: int = 50
    ) -> Field:
        """Create noise levels from white noise power.

        Parameters
        ----------
        white_noise_power:
            Power of the white noise (dB SPL).
        sampling_frequency:
            Sampling frequency of the signal to denoise
            (which can be different from the signal used for creating the noise profile).
        window_length:
            (Optional) Window length for the noise level estimation in ms.
            Default is 50 ms.
        """
        op = Operator("create_noise_profile_from_white_noise_power")
        op.connect(0, white_noise_power)
        op.connect(1, sampling_frequency)
        op.connect(2, int(window_length))
        op.run()

        f = op.get_output(0, "field")
        return f

    def create_noise_levels_from_noise_samples(
        self, signal: Field, sampling_frequency: float, window_length: int = 50
    ) -> Field:
        """Create noise levels from white noise power.

        Parameters
        ----------
        white_noise_power:
            Signal (field) of noise.
        sampling_frequency:
            (Optional) Sampling frequency of the signal to denoise
            (which can be different from the signal used for creating the noise profile).
            Default is the sampling frequency of the noise signal").
        window_length:
            (Optional) Window length for the noise level estimation in ms.
            Default is 50 ms.
        """
        op = Operator("create_noise_profile_from_noise_samples")
        op.connect(0, signal)
        op.connect(1, sampling_frequency)
        op.connect(2, window_length)
        op.run()

        f = op.get_output(0, "field")
        return f

    def create_noise_levels_from_automatic_estimation(
        self, signal: Field, window_length: int = 50
    ) -> Field:
        """Create noise levels from white noise power.

        Parameters
        ----------
        white_noise_power:
            Signal (filed) from which to estimate the noise profile.
        window_length:
            (Optional) Window length for the noise level estimation in ms.
            Default is 50 ms.
        """
        op = Operator("create_noise_profile_from_automatic_estimation")
        op.connect(0, signal)
        op.connect(1, window_length)
        op.run()

        f = op.get_output(0, "field")
        return f
