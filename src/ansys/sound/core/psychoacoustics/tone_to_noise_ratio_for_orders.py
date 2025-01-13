# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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

"""Computes the ECMA 418-1/ISO 7779 tone-to-noise ratio (TNR) for specific orders."""
import warnings

from ansys.dpf.core import Field, FieldsContainer, Operator, types
import matplotlib.pyplot as plt
import numpy as np

from . import PsychoacousticsParent
from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning


class ToneToNoiseRatioForOrdersOverTime(PsychoacousticsParent):
    """Computes the ECMA 418-1/ISO 7779 tone-to-noise ratio (TNR) for specific orders over time.

    This class computes the TNR, as defined in ECMA 418-1 and ISO 7779 standards, following
    the specific orders over time in a given time-domain signal.
    """

    def __init__(self, signal: Field = None, profile: Field = None, order_list: list = None):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        signal : Field, default: None
            Signal on which to compute tone-to-noise ratio, as a DPF field.

        profile : Field, default: None
            Associated RPM profile to the input signal, as a DPF field.

        order_list : list, default: None
            List of the order numbers, as floats, on which to compute the tone-to-noise ratio.
        """
        super().__init__()
        self.signal = signal  # uses the setter
        self.profile = profile  # uses the setter
        self.order_list = order_list  # uses the setter
        self.__operator = Operator("compute_tone_to_noise_ratio_for_orders_over_time")

    @property
    def signal(self) -> Field:
        """Input signal as a DPF field."""
        return self.__signal

    @signal.setter
    def signal(self, signal: Field):
        """Set the signal."""
        if not (isinstance(signal, Field) or signal is None):
            raise PyAnsysSoundException("Signal must be provided as a DPF field.")
        self.__signal = signal

    @property
    def profile(self) -> Field:
        """Associated RPM profile to the input signal as a DPF field."""
        return self.__profile

    @profile.setter
    def profile(self, profile: Field):
        """Set the profile."""
        if not (isinstance(profile, Field) or profile is None):
            raise PyAnsysSoundException("Profile must be provided as a DPF field.")
        self.__profile = profile

    @property
    def order_list(self) -> list[float]:
        """Orders list as floats.

        List of the orders as floats on which to compute the tone-to-noise ratio.
        """
        return self.__order_list

    @order_list.setter
    def order_list(self, order_list: list):
        """Set the order list."""
        if len(order_list) == 0:
            raise PyAnsysSoundException("Order list must contain at least one order.")
        self.__order_list = order_list

    def process(self):
        """Compute the tone-to-noise ratio for orders.

        This method calls the appropriate DPF Sound operator to compute the tone-to-noise ratio
        on the orders of the input signal.
        """
        if self.signal == None:
            raise PyAnsysSoundException(
                "No signal found for tone-to-noise ratio computation. "
                "Use 'ToneToNoiseRatioForOrdersOverTime.signal'."
            )

        if self.profile == None:
            raise PyAnsysSoundException(
                "No profile found for tone-to-noise ratio computation. "
                "Use 'ToneToNoiseRatioForOrdersOverTime.profile'."
            )

        if self.order_list == None:
            raise PyAnsysSoundException(
                "No order list found for tone-to-noise ratio computation. "
                "Use 'ToneToNoiseRatioForOrdersOverTime.order_list'."
            )

        self.__operator.connect(0, self.signal)
        self.__operator.connect(1, self.profile)
        self.__operator.connect(2, self.order_list)

        # Runs the operator
        self.__operator.run()

        # Stores outputs in the tuple variable
        self._output = self.__operator.get_output(
            0, types.fields_container
        ), self.__operator.get_output(1, types.field)

    def get_output(self) -> tuple[FieldsContainer, Field]:
        """Get TNR data as a fields container and the associated resampled RPM profile as a Field.

        Returns
        -------
        tuple(FieldsContainer) | tuple(Field)
            First element is the tone-to-noise ratio data in a fields container.
            Each field of the fields container gives the TNR over time for one of the requested
            orders.

            Second element is the RPM profile resampled to match the TNR calculation time steps, as
            a Field.

        """
        if self._output == None:
            warnings.warn(
                PyAnsysSoundWarning(
                    "Output is not processed yet. "
                    "Use the 'ToneToNoiseRatioForOrdersOverTime.process()' method."
                )
            )

        return self._output

    def get_output_as_nparray(self) -> tuple[np.ndarray] | None:
        """Get TNR data in a tuple of NumPy arrays.

        Returns
        -------
        tuple
            First element is the tone-to-noise ratio data, in dB.

            Second element is the RPM profile resampled to match the TNR calculation time steps.
        """
        tnr_container = self.get_output()
        if tnr_container == None:
            return (np.array([]), np.array([]))

        return (self.convert_fields_container_to_np_array(tnr_container[0]), tnr_container[1].data)

    def get_order_tone_to_noise_ratio_over_time(self, order_index: int) -> np.ndarray | None:
        """Get the tone-to-noise ratio over time for a specific order.

        Parameters
        ----------
        order_index : int
            Index of the order for which to get the tone-to-noise ratio.

        Returns
        -------
        numpy.ndarray
            Tone-to-noise ratio over time, in dB, for the specified order.
        """
        if order_index >= len(self.order_list) or order_index < 0:
            raise PyAnsysSoundException(
                f"Order index {order_index} is out of range. "
                f"Order list has {len(self.order_list)} elements."
            )

        tnr_container = self.get_output_as_nparray()
        return tnr_container[0][order_index]

    def get_time_scale(self) -> np.ndarray | None:
        """Get the TNR calculation time scale.

        Returns
        -------
        numpy.ndarray
            Time scale of the TNR calculation, in s.
        """
        tnr_container = self.get_output()
        if tnr_container == None:
            return np.array([])

        return tnr_container[0][0].time_freq_support.time_frequencies.data

    def get_rpm_scale(self) -> np.ndarray | None:
        """Get the resampled RPM scale.

        Returns
        -------
        numpy.ndarray
            RPM scale, resampled to match the TNR calculation time steps.
        """
        tnr_container = self.get_output()
        if tnr_container == None:
            return np.array([])

        return tnr_container[1].data

    def __str__(self):
        """Return the string representation of the object."""
        return (
            f"{__class__.__name__} object.\n"
            "Data\n"
            f'Signal name: "{self.signal.name}"\n'
            f'RPM profile signal name: "{self.profile.name}"\n'
            f"Order list: {self.order_list}\n"
        )

    def plot(self, use_rpm_scale: bool = False):
        """Plot all orders’ TNR as functions of time or RPM.

        Parameters
        ----------
        use_rpm_scale : bool
            Indicate whether to plot the TNR as a function of time or RPM.
        """
        tnr_container = self.get_output()
        if tnr_container == None:
            raise PyAnsysSoundException(
                f"Output is not processed yet. Use the ``{__class__.__name__}.process()`` method."
            )

        if use_rpm_scale:
            x_scale_label = "RPM (rpm)"
            x_scale_data = self.get_rpm_scale()
            title = "Orders’ tone-to-noise ratio ratio over RPM"
        else:
            x_scale_label = "Time (s)"
            x_scale_data = self.get_time_scale()
            title = "Orders’ tone-to-noise ratio over time"

        fig, ax = plt.subplots()
        fig.suptitle(title)
        ax.set_xlabel(x_scale_label)

        ax.set_ylabel("Tone-to-noise ratio (dB)")

        for order_idx in range(len(self.order_list)):
            order_data = self.get_order_tone_to_noise_ratio_over_time(order_idx)
            order_value = self.order_list[order_idx]
            ax.plot(x_scale_data, order_data, label=f"Order {order_value}")

        ax.legend()
        plt.show()
