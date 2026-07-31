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

"""Computes order levels from a signal and RPM profile."""

import warnings

from ansys.dpf.core import Field, FieldsContainer, Operator, types
import matplotlib.pyplot as plt
import numpy as np

from . import OrderAnalysisParent
from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from .compute_rpm_order_representation import ComputeRPMOrderRepresentation


class OrderLevels(OrderAnalysisParent, min_sound_version="2027.1.0"):
    """Compute order levels from a signal and RPM profile.

    This class computes the order levels of a signal by first computing the RPM order
    representation, and then extracting order levels at the specified orders.

    Parameters
    ----------
    signal : Field, default: None
        Input signal.
    rpm_profile : Field, default: None
        RPM profile associated with the input signal.
    orders : list[float], default: None
        List of orders at which to extract levels.
    resolution : float, default: 2.0
        Order resolution in percent for the RPM order representation computation.
    width : float, default: 10.0
        Width in percent for the order level extraction.
    order_max : int, default: 100
        Maximum order for the RPM order representation computation.
    """

    def __init__(
        self,
        signal: Field = None,
        rpm_profile: Field = None,
        orders: list[float] = None,
        resolution: float = 2.0,
        width: float = 10.0,
        order_max: int = 100,
    ):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        signal : Field, default: None
            Input signal.
        rpm_profile : Field, default: None
            RPM profile associated with the input signal.
        orders : list[float], default: None
            List of orders at which to extract levels.
        resolution : float, default: 2.0
            Order resolution in percent for the RPM order representation computation.
        width : float, default: 10.0
            Width in percent for the order level extraction.
        order_max : int, default: 100
            Maximum order for the RPM order representation computation.
        """
        super().__init__()
        self.signal = signal
        self.rpm_profile = rpm_profile
        self.orders = orders
        self.resolution = resolution
        self.width = width
        self.order_max = order_max
        self.__rpm_order_representation = None
        self.__operator = Operator("extract_order_levels")

    def __str__(self):
        """Return the string representation of the object."""
        str_signal = f'"{self.signal.name}"' if self.signal is not None else "Not set"
        str_rpm = f'"{self.rpm_profile.name}"' if self.rpm_profile is not None else "Not set"

        if self.orders is not None:
            # Format each order: display as integer if possible, otherwise as float.
            formatted_orders = [str(int(o)) if o == int(o) else str(o) for o in self.orders]
            str_orders = f"{len(self.orders)} orders: [{', '.join(formatted_orders)}]"
        else:
            str_orders = "Not set"

        str_resolution = f"{self.resolution} %" if self.resolution is not None else "Not set"
        str_width = f"{self.width} %" if self.width is not None else "Not set"

        return (
            f"{__class__.__name__} object\n"
            "Data\n"
            f"\tSignal name: {str_signal}\n"
            f"\tRPM profile name: {str_rpm}\n"
            f"\t{str_orders}\n"
            f"\tOrder analysis resolution: {str_resolution}\n"
            f"\tOrder analysis width: {str_width}"
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
    def orders(self) -> list[float]:
        """List of orders at which to extract levels."""
        return self.__orders

    @orders.setter
    def orders(self, orders: list[float]):
        """Set the orders."""
        self.__orders = orders

    @property
    def resolution(self) -> float:
        """Order resolution in percent."""
        return self.__resolution

    @resolution.setter
    def resolution(self, resolution: float):
        """Set the order resolution."""
        if resolution <= 0.0:
            raise PyAnsysSoundException("Order resolution must be greater than 0.0.")
        if resolution >= 100.0:
            raise PyAnsysSoundException("Order resolution must be less than 100.0.")
        self.__resolution = resolution

    @property
    def width(self) -> float:
        """Width in percent for order level extraction."""
        return self.__width

    @width.setter
    def width(self, width: float):
        """Set the width."""
        if width <= 0.0:
            raise PyAnsysSoundException("Width must be greater than 0.0.")
        if width > 100.0:
            raise PyAnsysSoundException("Width must be less than or equal to 100.0.")
        self.__width = width

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

    def process(self):
        """Run the order analysis.

        This method first computes the RPM order representation, then extracts order levels
        at the specified orders.

        Raises
        ------
        PyAnsysSoundException
            If ``signal``, ``rpm_profile``, or ``orders`` is None.
        """
        if self.signal is None:
            raise PyAnsysSoundException(
                "No signal found for order level computation. Use `OrderLevels.signal`."
            )

        if self.rpm_profile is None:
            raise PyAnsysSoundException(
                "No RPM profile found for order level computation. Use `OrderLevels.rpm_profile`."
            )

        if self.orders is None:
            raise PyAnsysSoundException(
                "No orders found for order level computation. Use `OrderLevels.orders`."
            )

        # Step 1: Compute RPM order representation.
        rpm_order_repr = ComputeRPMOrderRepresentation(
            signal=self.signal,
            rpm_profile=self.rpm_profile,
            order_max=self.order_max,
            order_resolution=self.resolution,
        )
        rpm_order_repr.process()
        self.__rpm_order_representation = rpm_order_repr.get_output()

        # Step 2: Extract order levels.
        self.__operator.connect(0, self.__rpm_order_representation)
        self.__operator.connect(1, self.orders)  # doubleVector, not Field
        self.__operator.connect(2, self.width)

        # Runs the operator
        self.__operator.run()

        # Stores output in the variable
        self._output = self.__operator.get_output(0, types.fields_container)

    def get_rpm_order_representation(self) -> FieldsContainer:
        """Return the intermediate RPM-order representation.

        Returns
        -------
        FieldsContainer
            Intermediate RPM-order representation as a DPF fields container.
        """
        if self.__rpm_order_representation is None:
            warnings.warn(
                PyAnsysSoundWarning(
                    "Output is not processed yet. Use the `OrderLevels.process()` method."
                )
            )

        return self.__rpm_order_representation

    def get_output(self) -> list[Field]:
        """Get the order levels as a list of DPF fields.

        Returns
        -------
        list[Field]
            List of DPF fields, one per order.
        """
        if self._output is None:
            warnings.warn(
                PyAnsysSoundWarning(
                    "Output is not processed yet. Use the `OrderLevels.process()` method."
                )
            )
            return None

        return [self._output[i] for i in range(len(self._output))]

    def get_output_as_nparray(self) -> list[np.ndarray]:
        """Get the order levels as a list of NumPy arrays.

        Returns
        -------
        list[numpy.ndarray]
            List of NumPy arrays, one per order.
        """
        output = self.get_output()

        if output is None:
            return []

        return [np.array(field.data) for field in output]

    def get_order_levels_in_linear_unit(self) -> list[np.ndarray]:
        """Get the order levels in linear unit.

        Returns
        -------
        list[numpy.ndarray]
            Order levels in linear unit, one array per order.
        """
        # Raw output is in squared unit; take the square root to get linear unit.
        return [np.sqrt(level) for level in self.get_output_as_nparray()]

    def get_order_levels_in_squared_linear_unit(self) -> list[np.ndarray]:
        """Get the order levels in squared linear unit.

        Returns
        -------
        list[numpy.ndarray]
            Order levels squared (element-wise), one array per order.
        """
        # Raw output is already in squared unit.
        return self.get_output_as_nparray()

    def get_order_levels_in_dB(self, reference_value: float = 1.0) -> list[np.ndarray]:
        """Get the order levels in dB.

        Parameters
        ----------
        reference_value : float, default: 1.0
            Reference value for the dB computation. Must be greater than 0.

        Returns
        -------
        list[numpy.ndarray]
            Order levels in dB (10*log10(level / reference_value**2)), one array per order.

        Raises
        ------
        PyAnsysSoundException
            If ``reference_value`` is less than or equal to 0.
        """
        if reference_value <= 0:
            raise PyAnsysSoundException("Reference value must be greater than 0.")

        # Raw output is in squared unit: use 10*log10(level/ref²) = 20*log10(sqrt(level)/ref).
        return [
            10.0 * np.log10(level / reference_value**2) for level in self.get_output_as_nparray()
        ]

    def get_order_level(self, order: float) -> np.ndarray:
        """Get the level array for a single order.

        Parameters
        ----------
        order : float
            Order value for which to get the level.

        Returns
        -------
        numpy.ndarray
            Level array for the specified order.

        Raises
        ------
        PyAnsysSoundException
            If the specified order is not in the orders list.
        """
        if self.orders is None or order not in self.orders:
            raise PyAnsysSoundException(
                f"Order {order} is not in the list of orders. "
                "Use `OrderLevels.orders` to check or set the orders list."
            )

        index = self.orders.index(order)
        return self.get_output_as_nparray()[index]

    def get_associated_rpm(self) -> np.ndarray:
        """Get the RPM support of the output order levels.

        Returns
        -------
        numpy.ndarray
            RPM values associated with the order levels.
        """
        output = self.get_output()

        if output is None:
            return np.array([])

        return np.array(output[0].time_freq_support.time_frequencies.data)

    def plot(self, display_in_dB: bool = False, reference_value: float = 1.0):
        """Plot the order levels vs RPM.

        Parameters
        ----------
        display_in_dB : bool, default: False
            Whether to display levels in dB.
        reference_value : float, default: 1.0
            Reference value for the dB computation. Only used if ``display_in_dB`` is True.

        Raises
        ------
        PyAnsysSoundException
            If the output is not processed yet.
        """
        if self._output is None:
            raise PyAnsysSoundException(
                f"Output is not processed yet. Use the `{__class__.__name__}.process()` method."
            )

        orders_to_plot = self.orders
        if len(orders_to_plot) > 10:
            warnings.warn(
                PyAnsysSoundWarning(
                    "More than 10 order values were listed. "
                    "Only the first 10 order curves are displayed."
                )
            )
            orders_to_plot = orders_to_plot[:10]

        rpm = self.get_associated_rpm()

        if display_in_dB:
            levels = self.get_order_levels_in_dB(reference_value=reference_value)
        else:
            levels = self.get_order_levels_in_linear_unit()

        for i, order in enumerate(orders_to_plot):
            # Format order label: display as integer if possible.
            order_label = str(int(order)) if order == int(order) else str(order)
            plt.plot(rpm, levels[i], label=f"Order {order_label}")

        plt.title(f"Order Analysis: {self.signal.name}")
        plt.xlabel("RPM")

        if display_in_dB:
            plt.ylabel(f"Level (dB re {reference_value} {self.signal.unit})")
        else:
            plt.ylabel(f"Level ({self.signal.unit})")

        plt.legend()
        plt.grid(True)
        plt.show()

    def save_as_AnsysSound_Orders(self, path: str) -> None:
        """Save results to an AnsysSound_Orders file.

        Parameters
        ----------
        path : str
            Path to the output file.
        """
        raise NotImplementedError("save_as_AnsysSound_Orders() is not yet implemented.")
