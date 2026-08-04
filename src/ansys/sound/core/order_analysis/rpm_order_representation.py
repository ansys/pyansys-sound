# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

"""Compute RPM order representation."""

import warnings

from ansys.dpf.core import Field, FieldsContainer, Operator, types
import numpy as np

from . import OrderAnalysisParent
from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning

ID_COMPUTE_RPM_ORDER_REPRESENTATION = "compute_rpm_order_representation"


class RpmOrderRepresentation(OrderAnalysisParent, min_sound_version="2027.1.0"):
    """Compute the RPM order representation of a signal.

    This class computes an RPM-order representation of a signal, given an associated RPM profile. An
    RPM-order describes how the signal level varies depending on order value and RPM. The output
    takes the form of a matrix, where each row corresponds to a specific order value and each column
    corresponds to a specific RPM or time value. This class is used for extracting order levels over
    RPM or time, with the class :class:`ExtractOrderLevels`.

    .. seealso::
        :class:`ExtractOrderLevels`

    Examples
    --------
    Compute the RPM order representation of a signal.

    >>> from ansys.sound.core.order_analysis import RpmOrderRepresentation
    >>> rpm_order_representation = RpmOrderRepresentation(
    ...     signal=my_signal,
    ...     rpm_profile=my_rpm_profile,
    ...     max_order=160,
    ...     order_resolution=2.0
    ... )
    >>> rpm_order_representation.process()
    >>> output = rpm_order_representation.get_output()
    """

    def __init__(
        self,
        signal: Field = None,
        rpm_profile: Field = None,
        max_order: int = 160,
        order_resolution: float = 2.0,
    ):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        signal : Field, default: None
            Input signal.
        rpm_profile : Field, default: None
            RPM profile associated with the input signal.
        max_order : int, default: 160
            Maximum order to consider. This is the maximum order value included in the output
            RPM-order representation. Signal content beyond this order value is ignored.
        order_resolution : float, default: 2.0
            Order resolution, in percent of order. This corresponds to the order step between
            each row of the output RPM-order representation.
        """
        super().__init__()
        self.signal = signal
        self.rpm_profile = rpm_profile
        self.max_order = max_order
        self.order_resolution = order_resolution
        self.__operator = Operator(ID_COMPUTE_RPM_ORDER_REPRESENTATION)

    def __str__(self):
        """Return the string representation of the object."""
        str_signal = f'"{self.signal.name}"' if self.signal is not None else "Not set"
        str_rpm = f'"{self.rpm_profile.name}"' if self.rpm_profile is not None else "Not set"

        return (
            f"{__class__.__name__} object\n"
            "Data:\n"
            f"\tSignal name: {str_signal}\n"
            f"\tRPM profile name: {str_rpm}\n"
            f"\tMaximum order: {self.max_order}\n"
            f"\tOrder resolution: {self.order_resolution} %"
        )

    @property
    def signal(self) -> Field:
        """Input signal."""
        return self.__signal

    @signal.setter
    def signal(self, signal: Field):
        """Set the signal."""
        if not (signal is None or isinstance(signal, Field)):
            raise PyAnsysSoundException("Signal must be specified as a DPF field.")
        self.__signal = signal

    @property
    def rpm_profile(self) -> Field:
        """RPM profile associated with :attr:`signal`."""
        return self.__rpm_profile

    @rpm_profile.setter
    def rpm_profile(self, rpm_profile: Field):
        """Set the RPM profile."""
        if not (rpm_profile is None or isinstance(rpm_profile, Field)):
            raise PyAnsysSoundException("RPM profile must be specified as a DPF field.")
        self.__rpm_profile = rpm_profile

    @property
    def max_order(self) -> int:
        """Maximum order to consider in the RPM-order representation.
        
        Signal content beyond this order value is ignored, and is not included in the output
        RPM-order representation.
        """
        return self.__max_order

    @max_order.setter
    def max_order(self, max_order: int):
        """Set the maximum order."""
        if max_order <= 0:
            raise PyAnsysSoundException("Maximum order must be greater than 0.")
        self.__max_order = max_order

    @property
    def order_resolution(self) -> float:
        """Order resolution, in percent of order.
        
        This is the order step between each order value included in the RPM-order representation.
        """
        return self.__order_resolution

    @order_resolution.setter
    def order_resolution(self, order_resolution: float):
        """Set the order resolution."""
        if order_resolution <= 0.0:
            raise PyAnsysSoundException("Order resolution must be greater than 0.0.")
        self.__order_resolution = order_resolution

    def process(self):
        """Compute the RPM order representation.

        This method calls the appropriate DPF Sound operator to compute the RPM order
        representation of the signal.
        """
        if self.signal is None:
            raise PyAnsysSoundException(
                "No signal found for RPM order representation computation. "
                f"Use `{__class__.__name__}.signal`."
            )

        if self.rpm_profile is None:
            raise PyAnsysSoundException(
                "No RPM profile found for RPM order representation computation. "
                f"Use `{__class__.__name__}.rpm_profile`."
            )

        self.__operator.connect(0, self.signal)
        self.__operator.connect(1, self.rpm_profile)
        self.__operator.connect(2, self.max_order)
        self.__operator.connect(3, self.order_resolution)

        # Runs the operator
        self.__operator.run()

        # Stores output in the variable
        self._output = self.__operator.get_output(0, types.fields_container)

    def get_output(self) -> FieldsContainer:
        """Get the RPM order representation.

        Returns
        -------
        FieldsContainer
            RPM-order representation. Each field contains the real or imaginary part of a specific
            order value's level over RPM or time, in the input signal's unit. The fields container
            is indexed with labels "time" and "complex". The "complex" index (0 or 1) identifies
            whether the field contains the real or imaginary part. The "time" indexes correspond to
            both the time and RPM values stored in the fields container's supports labelled "time"
            and "RPM", respectively.
        """
        if self._output is None:
            warnings.warn(
                PyAnsysSoundWarning(
                    "Output is not processed yet. "
                    f"Use the `{__class__.__name__}.process()` method."
                )
            )

        return self._output

    def get_output_as_nparray(self) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Get the RPM order representation as a NumPy array.

        Returns
        -------
        numpy.ndarray
            RPM order representation as a 2-D NumPy array. Each stored value corresponds to a
            specific order value's complex level, in the input signal's unit, over RPM or time.
        numpy.ndarray
            Order values corresponding to the rows of the output array.
        numpy.ndarray
            RPM values corresponding to the columns of the output array.
        numpy.ndarray
            Time values, in second, corresponding to the columns of the output array.
        """
        output: FieldsContainer = self.get_output()
        
        time_indexes = output.get_available_ids_for_label("time")
        Ntime = len(time_indexes)
        Nfft = len(output.get_field({"complex": 0, "time": 0}).data)

        # Pre-allocate memory for the output array.
        out_as_np_array = np.empty((Ntime, Nfft), dtype=np.complex128)

        for i in time_indexes:
            f1 = output.get_field({"complex": 0, "time": i})
            f2 = output.get_field({"complex": 1, "time": i})
            out_as_np_array[i] = f1.data + 1j * f2.data

        order_values = np.array(output[0].time_freq_support.time_frequencies.data)
        rpm_values = np.array(output.get_support("RPM").time_frequencies.data)
        time_values = np.array(output.time_freq_support.time_frequencies.data)

        return out_as_np_array, order_values, rpm_values, time_values

    def get_rpm_order_representation(self) -> np.ndarray:
        """Get the RPM order representation.

        Returns
        -------
        numpy.ndarray
            RPM order representation as a 2-D NumPy array. Each stored value corresponds to a
            specific order value's complex level, in the input signal's unit, over RPM or time.
        """
        return self.get_output_as_nparray()[0]

    def get_orders(self) -> np.ndarray:
        """Get the order values.

        Returns
        -------
        numpy.ndarray
            Order values corresponding to the rows of the RPM-order representation.
        """
        return self.get_output_as_nparray()[1]

    def get_associated_rpm(self) -> np.ndarray:
        """Get the associated RPM values.

        Returns
        -------
        numpy.ndarray
            RPM values corresponding to the columns of the RPM-order representation.
        """
        return self.get_output_as_nparray()[2]
    
    def get_associated_times(self) -> np.ndarray:
        """Get the associated time values.

        Returns
        -------
        numpy.ndarray
            Time values, in second, corresponding to the columns of the RPM-order representation.
        """
        return self.get_output_as_nparray()[3]
