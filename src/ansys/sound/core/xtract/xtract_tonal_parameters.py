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

"""Xtract tonal parameters."""

from ansys.dpf.core import GenericDataContainer

from . import XtractParent
from .._pyansys_sound import PyAnsysSoundException

ID_TONAL_PARAMETERS_CLASS = "Xtract_tonal_parameters"
ID_REGULARITY = "regularity"
ID_MAXIMUM_SLOPE = "maximum_slope"
ID_MINIMUM_DURATION = "minimum_duration"
ID_INTERTONAL_GAP = "intertonal_gap"
ID_LOCAL_EMERGENCE = "local_emergence"
ID_FFT_SIZE = "fft_size"


class XtractTonalParameters(XtractParent):
    """Contains tonal parameters for use in Xtract processing or signal denoising."""

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
        regularity: float, default: 1.0
            Regularity parameter. Values are between 0 and 1. This parameter is designed to
            reject tonal components with too much frequency variation. You should start with
            the default value (``1.0``) and then lower it to remove detected tonals whose
            frequency evolutions are too erratic.
        maximum_slope: float, default: 750.0
            Maximum slope in Hz/s for each tonal component. Values are between 0 and 15000 Hz/s.
            A higher value enables finding tonal components with a greater
            frequency slope over time.
        minimum_duration: float, default: 1.0
            Minimum duration in seconds for each tonal components.
            Values are between 0 and 5.
        intertonal_gap: float, default: 20.0
            Minimum gap in Hz between two tonal components.
            Values are between 10 and 200.
        local_emergence: float, default: 15.0
            Emergence of the tonal components compared to the background noise in dB.
            Values are between 0 and 100.
        fft_size: int, default: 8192
            Number of samples for the FFT computation. The value
            must be greater than 0.
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
        """Regularity."""
        return self.__generic_data_container.get_property(ID_REGULARITY)  # pragma: no cover

    @regularity.setter
    def regularity(self, regularity: float):
        """Set the regularity."""
        if regularity < 0.0 or regularity > 1.0:
            raise PyAnsysSoundException("Regularity must be between 0.0 and 1.0.")

        self.__generic_data_container.set_property(ID_REGULARITY, regularity)

    @regularity.getter
    def regularity(self) -> float:
        """Regularity.

        Returns
        -------
        float
            Regularity.
        """
        return self.__generic_data_container.get_property(ID_REGULARITY)

    @property
    def maximum_slope(self):
        """Maximum slope."""
        return self.__generic_data_container.get_property(ID_MAXIMUM_SLOPE)  # pragma: no cover

    @maximum_slope.setter
    def maximum_slope(self, maximum_slope: float):
        """Set the maximum slope."""
        if maximum_slope < 0.0 or maximum_slope > 15000.0:
            raise PyAnsysSoundException("Maximum slope must be between 0.0 and 15000.0 Hz/s.")

        self.__generic_data_container.set_property(ID_MAXIMUM_SLOPE, maximum_slope)

    @maximum_slope.getter
    def maximum_slope(self) -> float:
        """Maximum slope.

        Returns
        -------
        float
            Maximum slope.
        """
        return self.__generic_data_container.get_property(ID_MAXIMUM_SLOPE)

    @property
    def minimum_duration(self):
        """Minimum duration."""
        return self.__generic_data_container.get_property(ID_MINIMUM_DURATION)  # pragma: no cover

    @minimum_duration.setter
    def minimum_duration(self, minimum_duration: float):
        """Set the minimum duration."""
        if minimum_duration < 0.0 or minimum_duration > 5.0:
            raise PyAnsysSoundException("Minimum duration must be between 0.0 and 5.0 s.")

        self.__generic_data_container.set_property(ID_MINIMUM_DURATION, minimum_duration)

    @minimum_duration.getter
    def minimum_duration(self) -> float:
        """Minimum duration.

        Returns
        -------
        float
            Minimum duration.
        """
        return self.__generic_data_container.get_property(ID_MINIMUM_DURATION)

    @property
    def intertonal_gap(self):
        """Intertonal gap."""
        return self.__generic_data_container.get_property(ID_INTERTONAL_GAP)  # pragma: no cover

    @intertonal_gap.setter
    def intertonal_gap(self, intertonal_gap: float):
        """Set the intertonal gap."""
        if intertonal_gap < 10.0 or intertonal_gap > 200.0:
            raise PyAnsysSoundException("Intertonal gap must be between 10.0 and 200.0 Hz.")

        self.__generic_data_container.set_property(ID_INTERTONAL_GAP, intertonal_gap)

    @intertonal_gap.getter
    def intertonal_gap(self) -> float:
        """Intertonal gap.

        Returns
        -------
        float
            Intertonal gap.
        """
        return self.__generic_data_container.get_property(ID_INTERTONAL_GAP)

    @property
    def local_emergence(self):
        """Local emergence."""
        return self.__generic_data_container.get_property(ID_LOCAL_EMERGENCE)  # pragma: no cover

    @local_emergence.setter
    def local_emergence(self, local_emergence: float):
        """Set the local emergence."""
        if local_emergence < 0.0 or local_emergence > 100.0:
            raise PyAnsysSoundException("Local emergence must be between 0.0 and 100.0 dB.")

        self.__generic_data_container.set_property(ID_LOCAL_EMERGENCE, local_emergence)

    @local_emergence.getter
    def local_emergence(self) -> float:
        """Local emergence.

        Returns
        -------
        float
            Local emergence.
        """
        return self.__generic_data_container.get_property(ID_LOCAL_EMERGENCE)

    @property
    def fft_size(self):
        """FFT size."""
        return self.__generic_data_container.get_property(ID_FFT_SIZE)  # pragma: no cover

    @fft_size.setter
    def fft_size(self, fft_size: int):
        """Set the FFT size."""
        if fft_size < 0:
            raise PyAnsysSoundException("FFT size must be greater than 0.")

        self.__generic_data_container.set_property(ID_FFT_SIZE, fft_size)

    @fft_size.getter
    def fft_size(self) -> int:
        """FFT size.

        Returns
        -------
        int
            FFT size.
        """
        return self.__generic_data_container.get_property(ID_FFT_SIZE)

    def get_parameters_as_generic_data_container(self) -> GenericDataContainer:
        """Get the parameters as a generic data container.

        Returns
        -------
        GenericDataContainer
           Parameter structure in a generic data container.
        """
        return self.__generic_data_container
