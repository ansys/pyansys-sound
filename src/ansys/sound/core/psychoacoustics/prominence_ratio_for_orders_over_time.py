# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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

"""Computes the ECMA 418-1/ISO 7779 prominence ratio (PR) for specific orders."""

import warnings

from ansys.dpf.core import Field, Operator, types
import matplotlib.pyplot as plt
import numpy as np

from . import PsychoacousticsParent
from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning

# Name of the DPF Sound operator used in this module.
ID_COMPUTE_PR_FOR_ORDERS_OVER_TIME = "compute_prominence_ratio_for_orders_over_time"


class ProminenceRatioForOrdersOverTime(PsychoacousticsParent):
    """Computes the ECMA 418-1/ISO 7779 prominence ratio (PR) for specific orders over time.

    This class computes the PR, as defined in ECMA 418-1 and ISO 7779 standards, following
    specific orders over time in a given time-domain signal.

    .. seealso::
        :class:`ProminenceRatio`, :class:`ToneToNoiseRatioForOrdersOverTime`

    Examples
    --------
    Compute and display the prominence ratio over time of a signal, for orders 2 and 4.

    >>> from ansys.sound.core.psychoacoustics import ProminenceRatioForOrdersOverTime
    >>> prominence_ratio = ProminenceRatioForOrdersOverTime(
    ...     signal=my_signal,
    ...     profile=my_rpm_profile,
    ...     order_list=[2, 4],
    ... )
    >>> prominence_ratio.process()
    >>> pr_value_over_time_order_2 = prominence_ratio.get_order_prominence_ratio_over_time(0)
    >>> pr_value_over_time_order_4 = prominence_ratio.get_order_prominence_ratio_over_time(1)
    >>> time_scale = prominence_ratio.get_time_scale()
    >>> prominence_ratio.plot()

    .. seealso::
        :ref:`calculate_PR_and_TNR`
            Example demonstrating how to compute tone-to-noise ratio and prominence ratio.
    """

    def __init__(self, signal: Field = None, profile: Field = None, order_list: list = None):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        signal : Field, default: None
            Signal on which to compute prominence ratio.
        profile : Field, default: None
            Associated RPM profile to the input signal.
        order_list : list, default: None
            List of the order numbers, as floats, on which to compute the prominence ratio.
        """
        super().__init__()
        self.signal = signal
        self.profile = profile
        self.order_list = order_list
        self.__operator = Operator(ID_COMPUTE_PR_FOR_ORDERS_OVER_TIME)

    def __str__(self):
        """Return the string representation of the object."""
        return (
            f"{__class__.__name__} object.\n"
            "Data\n"
            f'Signal name: "{self.signal.name}"\n'
            f'RPM profile signal name: "{self.profile.name}"\n'
            f"Order list: {self.order_list}\n"
        )

    @property
    def signal(self) -> Field:
        """Input signal."""
        return self.__signal

    @signal.setter
    def signal(self, signal: Field):
        """Set the signal."""
        if not (isinstance(signal, Field) or signal is None):
            raise PyAnsysSoundException("Signal must be provided as a DPF field.")
        self.__signal = signal

    @property
    def profile(self) -> Field:
        """RPM over time related to the input signal."""
        return self.__profile

    @profile.setter
    def profile(self, profile: Field):
        """Set the RPM profile."""
        if not (isinstance(profile, Field) or profile is None):
            raise PyAnsysSoundException("Profile must be provided as a DPF field.")
        self.__profile = profile

    @property
    def order_list(self) -> list[float]:
        """Orders list as floats.

        List of the order numbers on which to compute the prominence ratio, as floats.
        """
        return self.__order_list

    @order_list.setter
    def order_list(self, order_list: list):
        """Set the order list."""
        if order_list is not None:
            if len(order_list) == 0:
                raise PyAnsysSoundException("Order list must contain at least one order.")

            if min(order_list) <= 0:
                raise PyAnsysSoundException("Order list must contain strictly positive numbers.")

        self.__order_list = order_list

    def process(self):
        """Compute the prominence ratio for orders.

        This method calls the appropriate DPF Sound operator to compute the prominence ratio
        on the selected orders of the input signal.
        """
        if self.signal == None:
            raise PyAnsysSoundException(
                "No signal found for prominence ratio computation. "
                "Use 'ProminenceRatioForOrdersOverTime.signal'."
            )

        if self.profile == None:
            raise PyAnsysSoundException(
                "No profile found for prominence ratio computation. "
                "Use 'ProminenceRatioForOrdersOverTime.profile'."
            )

        if self.order_list is None:
            raise PyAnsysSoundException(
                "No order list found for prominence ratio computation. "
                "Use 'ProminenceRatioForOrdersOverTime.order_list'."
            )

        self.__operator.connect(0, self.signal)
        self.__operator.connect(1, self.profile)
        self.__operator.connect(2, self.order_list)

        # Run the operator
        self.__operator.run()

        # Store outputs in the tuple variable
        orders_pr = [field for field in self.__operator.get_output(0, types.fields_container)]
        rpm = self.__operator.get_output(1, types.field)
        self._output = orders_pr, rpm

    def get_output(self) -> tuple[list[Field], Field]:
        """Get PR data over time and its associated RPM profile.

        Returns
        -------
        list[Field]
            Prominence ratio data over time for the requested orders. Each field contains the PR
            over time, in dB, for each requested order in :attr:`order_list`.
        Field
            RPM over time with the same time scale as the PR data.
        """
        if self._output == None:
            warnings.warn(
                PyAnsysSoundWarning(
                    "Output is not processed yet. "
                    "Use the 'ProminenceRatioForOrdersOverTime.process()' method."
                )
            )

        return self._output

    def get_output_as_nparray(self) -> tuple[np.ndarray]:
        """Get PR data in a tuple of NumPy arrays.

        Returns
        -------
        numpy.ndarray
            Prominence ratio data over time for the requested orders. Each column contains the PR
            over time, in dB, for each requested order in :attr:`order_list`.
        numpy.ndarray
            Time scale associated with the PR data.
        numpy.ndarray
            RPM over time profile with the same time scale as the PR data.
        """
        output = self.get_output()
        if output is None:
            return (np.array([]), np.array([]), np.array([]))

        return (
            np.vstack([np.array(field.data) for field in output[0]]),
            np.array(output[0][0].time_freq_support.time_frequencies.data),
            np.array(output[1].data),
        )

    def get_order_prominence_ratio_over_time(self, order_index: int) -> np.ndarray:
        """Get the prominence ratio (PR) over time for a specific order.

        Parameters
        ----------
        order_index : int
            Index of the order for which to get the prominence ratio over time.
            The index refers to the list of orders stored in :attr:`order_list`.

        Returns
        -------
        numpy.ndarray
            Prominence ratio over time, in dB, for the specified order.
        """
        if self.order_list is not None:
            if order_index >= len(self.order_list) or order_index < 0:
                raise PyAnsysSoundException(
                    f"Order index {order_index} is out of range. "
                    f"Order list has {len(self.order_list)} elements."
                )

        pr_data, _, _ = self.get_output_as_nparray()

        if len(pr_data) == 0:
            # Handling the case where the output is not processed yet
            return np.array([])

        return pr_data[order_index]

    def get_time_scale(self) -> np.ndarray | None:
        """Get the time scale corresponding to the PR array over time.

        Returns
        -------
        numpy.ndarray
            Time scale of the PR calculation, in s.
        """
        return self.get_output_as_nparray()[1]

    def get_rpm_scale(self) -> np.ndarray:
        """Get the RPM scale corresponding to the PR array over time.

        Returns
        -------
        numpy.ndarray
            Array of the RPM values at the time steps of the PR calculation.
        """
        return self.get_output_as_nparray()[2]

    def plot(self, use_rpm_scale: bool = False):
        """Plot all orders’ PR over time or RPM.

        Parameters
        ----------
        use_rpm_scale : bool
            Indicates whether to plot the PR as a function of time or RPM.
        """
        output = self.get_output()
        if output is None:
            raise PyAnsysSoundException(
                f"Output is not processed yet. Use the ``{__class__.__name__}.process()`` method."
            )

        pr_unit = output[0][0].unit
        time = output[0][0].time_freq_support.time_frequencies
        rpm = output[1]

        if use_rpm_scale:
            x_scale_label = f"RPM ({rpm.unit})"
            x_scale_data = rpm.data
            title = "Orders’ prominence ratio over RPM"
        else:
            x_scale_label = f"Time ({time.unit})"
            x_scale_data = time.data
            title = "Orders’ prominence ratio over time"

        fig, ax = plt.subplots()
        fig.suptitle(title)
        ax.set_xlabel(x_scale_label)

        ax.set_ylabel(f"Prominence ratio ({pr_unit})")

        for order_idx, order_value in enumerate(self.order_list):
            order_data = self.get_order_prominence_ratio_over_time(order_idx)
            ax.plot(x_scale_data, order_data, label=f"Order {order_value}")

        ax.legend()
        plt.show()
