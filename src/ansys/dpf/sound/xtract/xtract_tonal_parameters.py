"""Xtract tonal parameters."""

from ansys.dpf.core import GenericDataContainer

from . import XtractParent
from ..pydpf_sound import PyDpfSoundException

ID_TONAL_PARAMETERS_CLASS = "Xtract_tonal_parameters"
ID_REGULARITY = "regularity"
ID_MAXIMUM_SLOPE = "maximum_slope"
ID_MINIMUM_DURATION = "minimum_duration"
ID_INTERTONAL_GAP = "intertonal_gap"
ID_LOCAL_EMERGENCE = "local_emergence"
ID_FFT_SIZE = "fft_size"


class XtractTonalParameters(XtractParent):
    """Data class for tonal parameters that can be used in Xtract and XtractTonal."""

    def __init__(
        self,
        regularity: float = 1.0,
        maximum_slope: float = 750.0,
        minimum_duration: float = 1.0,
        intertonal_gap: float = 20.0,
        local_emergence: float = 15.0,
        fft_size: int = 8192,
    ):
        """Init.

        Parameters
        ----------
        regularity:
            Regularity parameter, this parameter is designed to reject tonal components with a
            too high frequency variation.
            Lowering this parameter will discard tonal components whose frequency
            evolution is too erratic.
            Values between 0 and 1. Default is 1 (100%).
        maximum_slope:
            Maximum slope in Hz/s for each tonal component.
            A higher value enables finding tonal components with a greater
            frequency slope over time.
            Values between 0 and 15000 Hz/s. Default is 750 Hz/s.
        minimum_duration:
            Minimum duration in s for each tonal components.
            Values between 0 and 5 s. Default is 1 s.
        intertonal_gap:
            Minimum gap in Hz between two tonal components.
            Values between 10 and 200 Hz. Default is 20 Hz.
        local_emergence:
            Emergence of the tonal components compared to the background noise in dB.
            Values between 0 and 100 dB. Default is 15 dB.
        fft_size:
            Integer, number of samples for the FFT Computation.
            Must be greater than 0. Default is  8192.
        """
        self.__generic_data_container = GenericDataContainer()
        self.__generic_data_container.set_property("class_name", ID_TONAL_PARAMETERS_CLASS)
        self.regularity = regularity
        self.maximum_slope = maximum_slope
        self.minimum_duration = minimum_duration
        self.intertonal_gap = intertonal_gap
        self.local_emergence = local_emergence
        self.fft_size = fft_size
        super().__init__()

    @property
    def regularity(self):
        """Regularity property."""
        return self.__generic_data_container.get_property(ID_REGULARITY)  # pragma: no cover

    @regularity.setter
    def regularity(self, regularity: float):
        """Set the regularity."""
        if regularity < 0.0 or regularity > 1.0:
            raise PyDpfSoundException("Regularity must be between 0.0 and 1.0.")

        self.__generic_data_container.set_property(ID_REGULARITY, regularity)

    @regularity.getter
    def regularity(self) -> float:
        """Get the regularity.

        Returns
        -------
        float
            The regularity.
        """
        return self.__generic_data_container.get_property(ID_REGULARITY)

    @property
    def maximum_slope(self):
        """Maximum slope property."""
        return self.__generic_data_container.get_property(ID_MAXIMUM_SLOPE)  # pragma: no cover

    @maximum_slope.setter
    def maximum_slope(self, maximum_slope: float):
        """Set the maximum slope."""
        if maximum_slope < 0.0 or maximum_slope > 15000.0:
            raise PyDpfSoundException("Maximum slope must be between 0.0 and 15000.0 Hz/s.")

        self.__generic_data_container.set_property(ID_MAXIMUM_SLOPE, maximum_slope)

    @maximum_slope.getter
    def maximum_slope(self) -> float:
        """Get the maximum slope.

        Returns
        -------
        float
            The maximum slope.
        """
        return self.__generic_data_container.get_property(ID_MAXIMUM_SLOPE)

    @property
    def minimum_duration(self):
        """Minimum duration property."""
        return self.__generic_data_container.get_property(ID_MINIMUM_DURATION)  # pragma: no cover

    @minimum_duration.setter
    def minimum_duration(self, minimum_duration: float):
        """Set the minimum duration."""
        if minimum_duration < 0.0 or minimum_duration > 5.0:
            raise PyDpfSoundException("Minimum duration must be between 0.0 and 5.0 s.")

        self.__generic_data_container.set_property(ID_MINIMUM_DURATION, minimum_duration)

    @minimum_duration.getter
    def minimum_duration(self) -> float:
        """Get the minimum duration.

        Returns
        -------
        float
            The minimum duration.
        """
        return self.__generic_data_container.get_property(ID_MINIMUM_DURATION)

    @property
    def intertonal_gap(self):
        """Intertonal gap property."""
        return self.__generic_data_container.get_property(ID_INTERTONAL_GAP)  # pragma: no cover

    @intertonal_gap.setter
    def intertonal_gap(self, intertonal_gap: float):
        """Set the intertonal gap."""
        if intertonal_gap < 10.0 or intertonal_gap > 200.0:
            raise PyDpfSoundException("Intertonal gap must be between 10.0 and 200.0 Hz.")

        self.__generic_data_container.set_property(ID_INTERTONAL_GAP, intertonal_gap)

    @intertonal_gap.getter
    def intertonal_gap(self) -> float:
        """Get the intertonal gap.

        Returns
        -------
        float
            The intertonal gap.
        """
        return self.__generic_data_container.get_property(ID_INTERTONAL_GAP)

    @property
    def local_emergence(self):
        """Local emergence property."""
        return self.__generic_data_container.get_property(ID_LOCAL_EMERGENCE)  # pragma: no cover

    @local_emergence.setter
    def local_emergence(self, local_emergence: float):
        """Set the local emergence."""
        if local_emergence < 0.0 or local_emergence > 100.0:
            raise PyDpfSoundException("Local emergence must be between 0.0 and 100.0 dB.")

        self.__generic_data_container.set_property(ID_LOCAL_EMERGENCE, local_emergence)

    @local_emergence.getter
    def local_emergence(self) -> float:
        """Get the local emergence.

        Returns
        -------
        float
            The local emergence.
        """
        return self.__generic_data_container.get_property(ID_LOCAL_EMERGENCE)

    @property
    def fft_size(self):
        """Fft size property."""
        return self.__generic_data_container.get_property(ID_FFT_SIZE)  # pragma: no cover

    @fft_size.setter
    def fft_size(self, fft_size: int):
        """Set the fft size."""
        if fft_size < 0:
            raise PyDpfSoundException("Fft size must be between greater than 0.")

        self.__generic_data_container.set_property(ID_FFT_SIZE, fft_size)

    @fft_size.getter
    def fft_size(self) -> int:
        """Get the fft size.

        Returns
        -------
        int
            The local emergence.
        """
        return self.__generic_data_container.get_property(ID_FFT_SIZE)

    def get_parameters_as_generic_data_container(self) -> GenericDataContainer:
        """Get the parameters as generic data container.

        Returns
        -------
        GenericDataContainer
            The parameter structure as a GenericDataContainer
        """
        return self.__generic_data_container
