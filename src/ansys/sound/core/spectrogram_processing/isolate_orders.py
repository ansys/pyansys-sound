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

"""Isolates the orders of a signal."""

import warnings

from ansys.dpf.core import Field, FieldsContainer, Operator
import matplotlib.pyplot as plt
from numpy import typing as npt

from . import SpectrogramProcessingParent
from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning


class IsolateOrders(SpectrogramProcessingParent):
    """Isolates the orders of a signal.

    This class isolates the order of a signal that has an associated RPM profile.
    """

    def __init__(
        self,
        signal: FieldsContainer | Field = None,
        rpm_profile: Field = None,
        orders: list = None,
        fft_size: int = 1024,
        window_type: str = "HANN",
        window_overlap: float = 0.5,
        width_selection: int = 10,
    ):
        """Create an ``Istft`` instance.

        Parameters
        ----------
        signal: FieldsContainer | Field, default: None
            One or more input signals to isolate orders on as a DPF fields container or field.
        rpm_profile: Field, default: None
            RPM signal associated with the time signals as a DPF field.
            It is assumed that the signal's unit is ``rpm``. If this is not the case,
            inaccurate behavior might occur during the conversion from RPM to frequency.
        orders: list, default: None
            List of the order numbers to isolate. The list must contain at least one value.
        fft_size: int, default: 1024
            Size of the FFT used to compute the STFT.
        window_type: str, default: 'HANN'
            Window type used for the FFT computation. Options are ``'BARTLETT'``, ``'BLACKMAN'``,
            ``'BLACKMANHARRIS'``,``'HAMMING'``, ``'HANN'``, ``'HANNING'``, ``'KAISER'``, and
            ``'RECTANGULAR'``.
        window_overlap: float, default: 0.5
            Overlap value between two successive FFT computations. Values can range from 0 to 1.
            For example, ``0`` means no overlap, and ``0.5`` means 50% overlap.
        width_selection: int, default: 10
            Width in Hz of the area used to select each individual order.
            Note that its precision depends on the FFT size.
        """
        super().__init__()
        self.signal = signal
        self.rpm_profile = rpm_profile
        self.orders = orders
        self.fft_size = fft_size
        self.window_type = window_type
        self.window_overlap = window_overlap
        self.width_selection = width_selection
        self.__operator = Operator("isolate_orders")

    @property
    def signal(self):
        """Signal."""
        return self.__signal  # pragma: no cover

    @signal.setter
    def signal(self, signal: Field | FieldsContainer):
        """Set the signal."""
        self.__signal = signal

    @signal.getter
    def signal(self) -> Field | FieldsContainer:
        """Signal.

        Returns
        -------
        Field | FieldsContainer
            Signal as a DPF field or fields container.
        """
        return self.__signal

    @property
    def rpm_profile(self):
        """RPM profile."""
        return self.__rpm_profile  # pragma: no cover

    @rpm_profile.getter
    def rpm_profile(self) -> Field:
        """RPM profile.

        Returns
        -------
        Field
            RPM profile.
        """
        return self.__rpm_profile

    @rpm_profile.setter
    def rpm_profile(self, rpm_profile: Field):
        """Set the RPM profile."""
        self.__rpm_profile = rpm_profile

    @property
    def orders(self):
        """Orders."""
        return self.__orders  # pragma: no cover

    @orders.getter
    def orders(self) -> Field:
        """Orders.

        Returns
        -------
        list
            Orders.
        """
        return self.__orders

    @orders.setter
    def orders(self, orders: Field | list):
        """Set the orders."""
        if type(orders) == list:
            f = Field()
            f.append(orders, 1)
            self.__orders = f
        elif type(orders):
            self.__orders = orders

    @property
    def fft_size(self):
        """FFT size."""
        return self.__fft_size  # pragma: no cover

    @fft_size.setter
    def fft_size(self, fft_size):
        """Set the FFT size."""
        if fft_size < 0:
            raise PyAnsysSoundException("FFT size must be greater than 0.0.")
        self.__fft_size = fft_size

    @fft_size.getter
    def fft_size(self) -> float:
        """FFT size.

        Returns
        -------
        float
            FFT size.
        """
        return self.__fft_size

    @property
    def window_type(self):
        """Window type."""
        return self.__window_type  # pragma: no cover

    @window_type.setter
    def window_type(self, window_type):
        """Set the window type."""
        if (
            window_type != "BLACKMANHARRIS"
            and window_type != "HANN"
            and window_type != "HAMMING"
            and window_type != "HANNING"
            and window_type != "KAISER"
            and window_type != "BARTLETT"
            and window_type != "BLACKMAN"
            and window_type != "RECTANGULAR"
        ):
            raise PyAnsysSoundException(
                "Invalid window type, accepted values are 'HANNING', 'BLACKMANHARRIS', 'HANN', "
                "'BLACKMAN','HAMMING', 'KAISER', 'BARTLETT', 'RECTANGULAR'."
            )

        self.__window_type = window_type

    @window_type.getter
    def window_type(self) -> str:
        """Window type.

        Returns
        -------
        str
            Window type.
        """
        return self.__window_type

    @property
    def window_overlap(self):
        """Window overlap."""
        return self.__window_overlap  # pragma: no cover

    @window_overlap.setter
    def window_overlap(self, window_overlap):
        """Set the window overlap."""
        if window_overlap < 0.0 or window_overlap > 1.0:
            raise PyAnsysSoundException("Window overlap must be between 0.0 and 1.0.")

        self.__window_overlap = window_overlap

    @window_overlap.getter
    def window_overlap(self) -> float:
        """Window overlap.

        Returns
        -------
        float
            Window overlap.
        """
        return self.__window_overlap

    @property
    def width_selection(self):
        """Width selection."""
        return self.__width_selection  # pragma: no cover

    @width_selection.setter
    def width_selection(self, widt_selection):
        """Set the width selection."""
        if widt_selection < 0:
            raise PyAnsysSoundException("Width selection must be greater than 0.0.")
        self.__width_selection = widt_selection

    @width_selection.getter
    def width_selection(self) -> int:
        """Width selection.

        Returns
        -------
        int
            Width selection.
        """
        return self.__width_selection

    def process(self):
        """Isolate the orders of the signal.

        This method calls the appropriate DPF Sound operator to isolate the orders of the signal.
        """
        if self.signal == None:
            raise PyAnsysSoundException(
                "No signal found for order isolation. Use 'IsolateOrder.signal'."
            )

        if self.rpm_profile == None:
            raise PyAnsysSoundException(
                "No RPM profile found for order isolation. Use 'IsolateOrder.rpm_profile'."
            )

        if self.orders == None:
            raise PyAnsysSoundException(
                "No orders found for order isolation. Use 'IsolateOrder.orders'."
            )

        self.__operator.connect(0, self.signal)
        self.__operator.connect(1, self.rpm_profile)
        self.__operator.connect(2, self.orders)
        self.__operator.connect(3, self.fft_size)
        self.__operator.connect(4, self.window_type)
        self.__operator.connect(5, self.window_overlap)
        self.__operator.connect(6, self.width_selection)

        # Runs the operator
        self.__operator.run()

        # Stores output in the variable
        if type(self.signal) == FieldsContainer:
            self._output = self.__operator.get_output(0, "fields_container")
        elif type(self.signal) == Field:
            self._output = self.__operator.get_output(0, "field")

    def get_output(self) -> Field | FieldsContainer:
        """Get the temporal signal of the isolated orders as a DPF field or fields container.

        Returns
        -------
        Field | FieldsContainer
            Signal resulting from the order isolation as a DPF field or fields container.
        """
        if self._output == None:
            # Computing output if needed
            warnings.warn(
                PyAnsysSoundWarning(
                    "Output is not processed yet. \
                        Use the 'IsolateOrders.process()' method."
                )
            )

        return self._output

    def get_output_as_nparray(self) -> npt.ArrayLike:
        """Get the temporal signal of the isolated orders as a NumPy array.

        Returns
        -------
        np.array
            Temporal signal of the isolated orders in a NumPy array.
        """
        output = self.get_output()

        if type(output) == Field:
            return output.data

        return self.convert_fields_container_to_np_array(output)

    def plot(self):
        """Plot the signal after order isolation."""
        output = self.get_output()

        if type(output) == Field:
            num_channels = 0
            field = output
        else:
            num_channels = len(output)
            field = output[0]

        time_data = field.time_freq_support.time_frequencies.data
        time_unit = field.time_freq_support.time_frequencies.unit
        unit = field.unit

        for i in range(num_channels):
            plt.plot(time_data, output[i].data, label="Channel {}".format(i))
        else:
            plt.plot(time_data, field.data, label="Channel 0")

        plt.title(field.name)
        plt.legend()
        plt.xlabel(time_unit)
        plt.ylabel(unit)
        plt.grid(True)
        plt.show()
