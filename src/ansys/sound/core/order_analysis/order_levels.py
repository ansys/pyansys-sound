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

"""Compute order levels from a signal and its RPM profile."""

import os
import warnings

from ansys.dpf.core import Field, FieldsContainer, Operator, types
import matplotlib.pyplot as plt
import numpy as np

from . import OrderAnalysisParent
from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning
from .rpm_order_representation import RpmOrderRepresentation

ID_EXTRACT_ORDER_LEVELS = "extract_order_levels"


class OrderLevels(OrderAnalysisParent, min_sound_version="2027.1.0"):
    """Compute order levels from a signal and its associated RPM profile.

    This class computes the order levels of a signal by first computing the RPM order
    representation, and then extracting order levels at the specified orders.
    """

    def __init__(
        self,
        signal: Field = None,
        rpm_profile: Field = None,
        orders: list[float] = None,
        order_width: float = 10.0,
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
        orders : list[float], default: None
            List of orders at which to extract levels.
        order_width : float, default: 10.0
            Width in percent of order for the order level extraction. It defines the range of order
            values around each specified order in :attr:`orders` where the energy is integrated to
            compute that order's level.
        max_order : int, default: 160
            Maximum order for the RPM-order representation computation. This is the maximum order
            value included in the computed RPM-order representation. Every order listed in
            :attr:`orders` must be less than or equal to this value.
        order_resolution : float, default: 2.0
            Order resolution in percent of order for the RPM order representation computation.
        """
        super().__init__()
        self.signal = signal
        self.rpm_profile = rpm_profile
        self.orders = orders
        self.order_resolution = order_resolution
        self.order_width = order_width
        self.max_order = max_order
        self.__rpm_order_representation = None
        self.__operator = Operator(ID_EXTRACT_ORDER_LEVELS)

    def __str__(self):
        """Return the string representation of the object."""
        str_signal = f'"{self.signal.name}"' if self.signal is not None else "Not set"
        str_rpm = f'"{self.rpm_profile.name}"' if self.rpm_profile is not None else "Not set"

        if self.orders is not None:
            str_orders = f"Orders ({len(self.orders)}): "
            if len(self.orders) > 10:
                str_orders += f"{str(self.orders[:5])[:-1]}, ... {str(self.orders[-5:])[1:]}"
            else:
                str_orders += f"{self.orders}"
        else:
            str_orders = "Orders: Not set"

        return (
            f"{__class__.__name__} object\n"
            "Data\n"
            f"\tSignal name: {str_signal}\n"
            f"\tRPM profile name: {str_rpm}\n"
            f"\t{str_orders}\n"
            f"\tOrder analysis width: {self.order_width} %\n"
            f"\tMaximum order: {self.max_order}\n"
            f"\tOrder analysis resolution: {self.order_resolution} %"
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
        if orders is not None:
            if not isinstance(orders, (list, tuple, np.ndarray)):
                raise PyAnsysSoundException(
                    "Orders must be specified as a list of positive floats."
                )
            
            for order in orders:
                if not isinstance(order, (int, float)) or order <= 0.0:
                    raise PyAnsysSoundException(
                        "Orders must be specified as a list of positive floats."
                    )

        self.__orders = orders

    @property
    def order_resolution(self) -> float:
        """Order resolution in percent."""
        return self.__resolution

    @order_resolution.setter
    def order_resolution(self, resolution: float):
        """Set the order resolution."""
        if resolution <= 0.0:
            raise PyAnsysSoundException(r"Order resolution must be greater than 0.0 %.")
        self.__resolution = resolution

    @property
    def order_width(self) -> float:
        """Width in percent for order level extraction."""
        return self.__width

    @order_width.setter
    def order_width(self, width: float):
        """Set the width."""
        if width <= 0.0:
            raise PyAnsysSoundException(
                r"Width must be greater than 0.0 %."
            )
        self.__width = width

    @property
    def max_order(self) -> int:
        """Maximum order."""
        return self.__max_order

    @max_order.setter
    def max_order(self, max_order: int):
        """Set the maximum order."""
        if max_order <= 0.0:
            raise PyAnsysSoundException("Maximum order must be greater than 0.")
        self.__max_order = max_order

    @property
    def rpm_order_representation(self) -> FieldsContainer:
        """RPM-order representation of the input signal.
        
        Requires that the :meth:`process()` method be called to be populated.
        """
        return self.__rpm_order_representation

    def process(self):
        """Run the order analysis.

        This method first computes the RPM order representation using the signal and rpm profile,
        and then extracts the levels of the specified orders.
        """
        if self.signal is None:
            raise PyAnsysSoundException(
                f"No input signal is set. Use `{__class__.__name__}.signal`."
            )

        if self.rpm_profile is None:
            raise PyAnsysSoundException(
                f"No input RPM profile is set. Use `{__class__.__name__}.rpm_profile`."
            )

        if self.orders is None:
            raise PyAnsysSoundException(
                f"No input order list is set. Use `{__class__.__name__}.orders`."
            )

        if max([order + self.order_width / 2 for order in self.orders]) > self.max_order:
            raise PyAnsysSoundException(
                f"Maximum order ({self.max_order}) must be greater than the highest value in the "
                "`orders` list."
            )

        if self.order_width < self.order_resolution:
            warnings.warn(
                PyAnsysSoundWarning(
                    f"Order width ({self.order_width} %) is smaller than the order resolution "
                    f"({self.order_resolution} %). Results may be inaccurate. Consider increasing the "
                    "order width or decreasing the order resolution."
                )
            )

        # Step 1: Compute RPM-order representation.
        rpm_order_repr = RpmOrderRepresentation(
            signal=self.signal,
            rpm_profile=self.rpm_profile,
            max_order=self.max_order,
            order_resolution=self.order_resolution,
        )
        rpm_order_repr.process()
        self.__rpm_order_representation = rpm_order_repr.get_output()

        # Step 2: Extract order levels.
        orders = map(float, self.orders)

        self.__operator.connect(0, self.__rpm_order_representation)
        self.__operator.connect(1, list(orders))
        self.__operator.connect(2, self.order_width)

        # Runs the operator
        self.__operator.run()

        # Stores output in the variable
        self._output = self.__operator.get_output(0, types.fields_container)

    def get_output(self) -> FieldsContainer:
        """Get the order levels.

        Returns
        -------
        FieldsContainer
            FieldsContainer of order levels. Each field corresponds to a requested order in :attr:`orders`,
            containing that order's level over RPM, in squared signal unit.
        """
        if self._output is None:
            warnings.warn(
                PyAnsysSoundWarning(
                    f"Output is not processed yet. Use the `{__class__.__name__}.process()` method."
                )
            )
            return None

        return self._output

    def get_output_as_nparray(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Get the order levels as NumPy arrays.

        Returns
        -------
        numpy.ndarray
            Order levels as a 2-D NumPy array. Each row corresponds to a specific order value, and
            each column corresponds to a specific RPM value. The values are in squared signal unit.
        numpy.ndarray
            Order values corresponding to the rows of the output array.
        numpy.ndarray
            RPM values corresponding to the columns of the output array.
        """
        output = self.get_output()

        if output is None:
            return np.array([]), np.array([]), np.array([])

        order_levels = np.vstack([np.array(field.data) for field in output])
        order_values = np.array(self.orders)
        rpm_values = np.array(output[0].time_freq_support.time_frequencies.data)

        return order_levels, order_values, rpm_values

    def get_order_levels_squared_linear(self) -> np.ndarray:
        """Get the order levels in squared signal unit.

        Returns
        -------
        numpy.ndarray
            Order levels as a 2-D NumPy array. Each row corresponds to a specific order value, and
            each column corresponds to a specific RPM value. The values are in squared signal unit.
        """
        return self.get_output_as_nparray()[0]

    def get_order_levels_dB(self, reference_value: float = 1.0) -> np.ndarray:
        """Get the order levels in dB.

        Parameters
        ----------
        reference_value : float, default: 1.0
            Reference value for dB conversion. If the input signal is in Pa, the reference value
            should be 2e-5 Pa to produce levels in dB SPL.

        Returns
        -------
        list[numpy.ndarray]
            Order levels in dB (actual unit depends on the reference value), as a 2-D NumPy array.
            Each row corresponds to a specific order value, and each column corresponds to a
            specific RPM value.
        """
        if reference_value <= 0:
            raise PyAnsysSoundException("Reference value must be greater than 0.")

        levels_squared = self.get_order_levels_squared_linear()
        return 10.0 * np.log10(levels_squared / reference_value**2 + 1e-12)

    def get_order_level_squared_linear(self, order: float) -> np.ndarray:
        """Get a single order's level over RPM or time, in squared linear unit.

        Parameters
        ----------
        order : float
            Order value of interest.

        Returns
        -------
        numpy.ndarray
            Level over RPM or time of the specified order, in squared linear unit.
        """
        if self.orders is None or order not in self.orders:
            raise PyAnsysSoundException(
                f"Order {order} is not in the `orders` list."
            )

        index = self.orders.index(order)
        levels = self.get_order_levels_squared_linear()

        if len(levels) == 0:
            return np.array([])
        
        return levels[index]

    def get_order_level_dB(self, order: float, reference_value: float = 1.0) -> np.ndarray:
        """Get a single order's level over RPM or time, in dB.

        Parameters
        ----------
        order : float
            Order value of interest.
        reference_value : float, default: 1.0
            Reference value for dB conversion. If the input signal is in Pa, the reference value
            should be 2e-5 Pa to produce levels in dB SPL.

        Returns
        -------
        numpy.ndarray
            Level over RPM or time of the specified order, in dB.
        """
        levels = self.get_order_level_squared_linear(order)
        return 10.0 * np.log10(levels / reference_value**2 + 1e-12)

    def get_rpm_scale(self) -> np.ndarray:
        """Get the RPM scale associated with the order levels.

        Returns
        -------
        numpy.ndarray
            RPM values where the order levels are defined.
        """
        return self.get_output_as_nparray()[2]

    def plot(self, display_in_dB: bool = False, reference_value: float = 1.0):
        """Plot the order levels over RPM.

        Parameters
        ----------
        display_in_dB : bool, default: False
            Whether to display levels in squared units (False), or in dB (True).
        reference_value : float, default: 1.0
            Reference value for dB conversion. Ignored if ``display_in_dB`` is False. If the input
            signal is in Pa, the reference value should be 2e-5 Pa to display levels in dB SPL.
        """
        if self._output is None:
            raise PyAnsysSoundException(
                f"Output is not processed yet. Use the `{__class__.__name__}.process()` method."
            )

        orders = self.orders
        if len(orders) > 10:
            warnings.warn(
                PyAnsysSoundWarning(
                    "There are more than 10 order values. Only the first 10 are displayed."
                )
            )
            orders = orders[:10]

        rpm = self.get_rpm_scale()

        if display_in_dB:
            levels = self.get_order_levels_dB(reference_value=reference_value)
        else:
            levels = self.get_order_levels_squared_linear()

        for i, order in enumerate(orders):
            plt.plot(rpm, levels[i], label=f"Order {order}")

        title = "Order Analysis"
        if len(self.signal.name) > 0:
            title += f": {self.signal.name}"
        plt.title(title)
        plt.xlabel("RPM")

        unit = self.signal.unit if isinstance(self.signal.unit, str) else self.signal.unit[1]

        if display_in_dB:
            str_unit = f"dB re {reference_value}"
            if len(unit) > 0:
                str_unit += f" {unit}"
        elif len(unit) > 0:
            if any(c in unit for c in [".", "/", "^"]):
                str_unit = f"({unit})^2"
            else:
                str_unit = f"{unit}^2"
        else:
            str_unit = "squared units"

        plt.ylabel(f"Level ({str_unit})")

        plt.legend()
        plt.grid()
        plt.tight_layout()
        plt.show()

    def save_as_AnsysSound_Orders(self, filepath: str) -> None:
        """Save computed order levels to a text file with AnsysSound_Orders header.

        Parameters
        ----------
        filepath : str
            Path to the saved file.
        """
        if self._output is None:
            raise PyAnsysSoundException(
                f"Output is not processed yet. Use the `{__class__.__name__}.process()` method."
            )

        if self.signal.unit != "Pa":
            warnings.warn(
                PyAnsysSoundWarning(
                    "The input signal is not in Pa, while the format only allows storing acoustic "
                    "pressure data (Pa, Pa^2, dB SPL, etc.). The data will be saved as if it were "
                    "acoustic pressure data, using Pa^2 as unit."
                )
            )

        levels, orders, rpm_scale = self.get_output_as_nparray()

        path, _ = os.path.split(filepath)
        if not os.path.exists(path):  # pragma: no cover
            os.makedirs(path)

        with open(filepath, "w") as f:
            # File header
            f.write("AnsysSound_Orders\t1\nPa2\n")

            # Table header (orders)
            f.write("RPM\t")
            f.write("\t".join(map(str, orders)))
            f.write("\n")

            # Table data (RPM value and corresponding order levels)
            for i, rpm in enumerate(rpm_scale):
                f.write(f"{rpm}\t")
                f.write("\t".join(map(str, levels[:, i])))
                f.write("\n")
