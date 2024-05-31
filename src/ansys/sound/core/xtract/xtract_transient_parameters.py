"""Xtract transient parameters."""

from ansys.dpf.core import GenericDataContainer

from . import XtractParent
from ..pyansys_sound import PyDpfSoundException

ID_TRANSIENT_PARAMETERS_CLASS = "Xtract_transient_parameters"
ID_LOWER_THRESHOLD = "lower_threshold"
ID_UPPER_THRESHOLD = "upper_threshold"


class XtractTransientParameters(XtractParent):
    """Data class for transient parameters that can be used in Xtract and XtractTransient."""

    def __init__(self, lower_threshold: float = 0.0, upper_threshold: float = 100.0):
        """Init.

        Parameters
        ----------
        lower_threshold:
            Minimum threshold is related to the minimum energy of transient components.
            We recommend setting this parameter as high as possible provided that no transient
            element remains in the remainder (non-transient signal).
            Values between 0 and 100. Default is 0.
        upper_threshold:
            Maximum threshold (in dB) is related to the maximum energy of transient components.
            We recommend setting this parameter as low as possible provided that no transient
            element remains in the remainder (non-transient signal).
            Values between 0 and 100. Default is 100.
        """
        self.__generic_data_container = GenericDataContainer()
        self.__generic_data_container.set_property("class_name", ID_TRANSIENT_PARAMETERS_CLASS)
        self.lower_threshold = lower_threshold
        self.upper_threshold = upper_threshold

    @property
    def lower_threshold(self):
        """Lower threshold property."""
        return self.__generic_data_container.get_property(ID_LOWER_THRESHOLD)  # pragma: no cover

    @lower_threshold.setter
    def lower_threshold(self, lower_threshold: float):
        """Set the lower threshold."""
        if lower_threshold < 0.0 or lower_threshold > 100.0:
            raise PyDpfSoundException("Lower threshold must be between 0.0 and 100.0 dB.")

        self.__generic_data_container.set_property(ID_LOWER_THRESHOLD, lower_threshold)

    @lower_threshold.getter
    def lower_threshold(self) -> float:
        """Get the lower threshold.

        Returns
        -------
        float
            The lower threshold in dB.
        """
        return self.__generic_data_container.get_property(ID_LOWER_THRESHOLD)

    @property
    def upper_threshold(self):
        """Upper threshold property."""
        return self.__generic_data_container.get_property(ID_UPPER_THRESHOLD)  # pragma: no cover

    @upper_threshold.setter
    def upper_threshold(self, upper_threshold: float):
        """Set the upper threshold."""
        if upper_threshold < 0.0 or upper_threshold > 100.0:
            raise PyDpfSoundException("Upper threshold must be between 0.0 and 100.0 dB.")

        self.__generic_data_container.set_property(ID_UPPER_THRESHOLD, upper_threshold)

    @upper_threshold.getter
    def upper_threshold(self) -> float:
        """Get the upper threshold.

        Returns
        -------
        float
            The upper threshold in dB.
        """
        return self.__generic_data_container.get_property(ID_UPPER_THRESHOLD)

    def get_parameters_as_generic_data_container(self) -> GenericDataContainer:
        """Get the parameters as generic data container.

        Returns
        -------
        GenericDataContainer
            The parameter structure as a GenericDataContainer
        """
        return self.__generic_data_container
