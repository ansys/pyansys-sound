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

"""Computes RPM order representation."""

import warnings

from ansys.dpf.core import Field, FieldsContainer, Operator, types
import numpy as np

from . import OrderAnalysisParent
from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning


class ComputeRPMOrderRepresentation(OrderAnalysisParent):
    """Compute the RPM order representation of a signal.

    This class wraps the DPF Sound operator ``"compute_rpm_order_representation"`` to compute
    the RPM-order representation of a signal given an associated RPM profile.

    Parameters
    ----------
    signal : Field, default: None
        Input signal.
    rpm_profile : Field, default: None
        RPM profile associated with the input signal.
    order_max : int, default: 100
        Maximum order to compute.
    order_resolution : float, default: 2.0
        Order resolution in percent (e.g. ``2.0`` for 2%).
    """

    def __init__(
        self,
        signal: Field = None,
        rpm_profile: Field = None,
        order_max: int = 100,
        order_resolution: float = 2.0,
    ):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        signal : Field, default: None
            Input signal.
        rpm_profile : Field, default: None
            RPM profile associated with the input signal.
        order_max : int, default: 100
            Maximum order to compute.
        order_resolution : float, default: 2.0
            Order resolution in percent (e.g. ``2.0`` for 2%).
        """
        super().__init__()
        self.signal = signal
        self.rpm_profile = rpm_profile
        self.order_max = order_max
        self.order_resolution = order_resolution
        self.__operator = Operator("compute_rpm_order_representation")

    def __str__(self):
        """Return the string representation of the object."""
        str_signal = f'"{self.signal.name}"' if self.signal is not None else "Not set"
        str_rpm = f'"{self.rpm_profile.name}"' if self.rpm_profile is not None else "Not set"

        return (
            f"{__class__.__name__} object\n"
            "Data:\n"
            f"\tSignal name: {str_signal}\n"
            f"\tRPM profile name: {str_rpm}\n"
            f"\tMaximum order: {self.order_max}\n"
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
        """RPM profile."""
        return self.__rpm_profile

    @rpm_profile.setter
    def rpm_profile(self, rpm_profile: Field):
        """Set the RPM profile."""
        if not (rpm_profile is None or isinstance(rpm_profile, Field)):
            raise PyAnsysSoundException("RPM profile must be specified as a DPF field.")
        self.__rpm_profile = rpm_profile

    @property
    def order_max(self) -> int:
        """Maximum order."""
        return self.__order_max

    @order_max.setter
    def order_max(self, order_max: int):
        """Set the maximum order."""
        if order_max <= 0:
            raise PyAnsysSoundException("Maximum order must be greater than 0.")
        self.__order_max = order_max

    @property
    def order_resolution(self) -> float:
        """Order resolution in percent."""
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
                "Use `ComputeRPMOrderRepresentation.signal`."
            )

        if self.rpm_profile is None:
            raise PyAnsysSoundException(
                "No RPM profile found for RPM order representation computation. "
                "Use `ComputeRPMOrderRepresentation.rpm_profile`."
            )

        self.__operator.connect(0, self.signal)
        self.__operator.connect(1, self.rpm_profile)
        self.__operator.connect(2, self.order_max)
        self.__operator.connect(3, self.order_resolution)

        # Runs the operator
        self.__operator.run()

        # Stores output in the variable
        self._output = self.__operator.get_output(0, types.fields_container)

    def get_output(self) -> FieldsContainer:
        """Get the RPM order representation as a DPF fields container.

        Returns
        -------
        FieldsContainer
            RPM order representation as a DPF fields container.
        """
        if self._output is None:
            warnings.warn(
                PyAnsysSoundWarning(
                    "Output is not processed yet. "
                    "Use the `ComputeRPMOrderRepresentation.process()` method."
                )
            )

        return self._output

    def get_output_as_nparray(self) -> np.ndarray:
        """Get the RPM order representation as a NumPy array.

        Returns
        -------
        numpy.ndarray
            RPM order representation as a 2-D NumPy array.
        """
        output = self.get_output()

        if output is None:
            return np.array([])

        return np.stack([field.data for field in output])

    def plot(self):
        """Plot the output.

        Raises
        ------
        PyAnsysSoundException
            This method is not implemented for this class because the output is an intermediate
            result not meant for direct plotting.
        """
        raise PyAnsysSoundException(
            f"Plotting is not supported for class `{__class__.__name__}`. "
            "The output is an intermediate result not meant for direct plotting."
        )
