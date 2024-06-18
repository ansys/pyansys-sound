# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Xtract transient parameters."""

from ansys.dpf.core import GenericDataContainer

from . import XtractParent
from .._pyansys_sound import PyAnsysSoundException

ID_TRANSIENT_PARAMETERS_CLASS = "Xtract_transient_parameters"
ID_LOWER_THRESHOLD = "lower_threshold"
ID_UPPER_THRESHOLD = "upper_threshold"


class XtractTransientParameters(XtractParent):
    """Contains transient parameters for use in Xtract processing or signal denoising."""

    def __init__(self, lower_threshold: float = 0.0, upper_threshold: float = 100.0):
        """Init.

        Parameters
        ----------
        lower_threshold: float, default: 0.0
            Minimum threshold, which is related to the minimum energy of transient components.
            Values are between 0 and 100. You should set this parameter as high as possible
            provided that no transient element remains in the remainder (non-transient signal).
        upper_threshold: float, default: 100.0
            Maximum threshold in dB, which is related to the maximum energy of transient components.
            Values are between 0 and 100. You should set this parameter as low as possible provided
            that no transient element remains in the remainder (non-transient signal).
        """
        self.__generic_data_container = GenericDataContainer()
        self.__generic_data_container.set_property("class_name", ID_TRANSIENT_PARAMETERS_CLASS)
        self.lower_threshold = lower_threshold
        self.upper_threshold = upper_threshold

    @property
    def lower_threshold(self):
        """Lower threshold."""
        return self.__generic_data_container.get_property(ID_LOWER_THRESHOLD)  # pragma: no cover

    @lower_threshold.setter
    def lower_threshold(self, lower_threshold: float):
        """Set the lower threshold."""
        if lower_threshold < 0.0 or lower_threshold > 100.0:
            raise PyAnsysSoundException("Lower threshold must be between 0.0 and 100.0 dB.")

        self.__generic_data_container.set_property(ID_LOWER_THRESHOLD, lower_threshold)

    @lower_threshold.getter
    def lower_threshold(self) -> float:
        """Lower threshold in decibels (dB).

        Returns
        -------
        float
            Lower threshold in decibels.
        """
        return self.__generic_data_container.get_property(ID_LOWER_THRESHOLD)

    @property
    def upper_threshold(self):
        """Upper threshold in decibels (dB)."""
        return self.__generic_data_container.get_property(ID_UPPER_THRESHOLD)  # pragma: no cover

    @upper_threshold.setter
    def upper_threshold(self, upper_threshold: float):
        """Set the upper threshold."""
        if upper_threshold < 0.0 or upper_threshold > 100.0:
            raise PyAnsysSoundException("Upper threshold must be between 0.0 and 100.0 dB.")

        self.__generic_data_container.set_property(ID_UPPER_THRESHOLD, upper_threshold)

    @upper_threshold.getter
    def upper_threshold(self) -> float:
        """Upper threshold in decibels (dB).

        Returns
        -------
        float
            Upper threshold in decibels.
        """
        return self.__generic_data_container.get_property(ID_UPPER_THRESHOLD)

    def get_parameters_as_generic_data_container(self) -> GenericDataContainer:
        """Get the parameters as a generic data container.

        Returns
        -------
        GenericDataContainer
            Parameter structure in a generic data container.
        """
        return self.__generic_data_container
