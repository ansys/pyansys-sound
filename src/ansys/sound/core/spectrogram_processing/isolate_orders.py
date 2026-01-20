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

"""Isolates the orders of a signal."""

import warnings

from ansys.dpf.core import Field, FieldsContainer, Operator
import matplotlib.pyplot as plt
import numpy as np

from . import SpectrogramProcessingParent
from .._pyansys_sound import (
    PyAnsysSoundException,
    PyAnsysSoundWarning,
    convert_fields_container_to_np_array,
)


class IsolateOrders(SpectrogramProcessingParent):
    """Isolate the orders of a signal.

    This class isolates the order of a signal that has an associated RPM profile.

    Examples
    --------
    Isolate orders 2 and 4 from a signal, and display the resulting signal.

    >>> from ansys.sound.core.spectrogram_processing import IsolateOrders
    >>> isolate_orders = IsolateOrders(signal=signal, rpm_profile=rpm_profile, orders=[2, 4])
    >>> isolate_orders.process()
    >>> isolated_orders_signal = isolate_orders.get_output()
    >>> isolate_orders.plot()

    .. seealso::
        :ref:`isolate_orders_example`
            Example demonstrating how to isolate orders.
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
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        signal : FieldsContainer | Field, default: None
            One or more input signals on which to isolate orders.
        rpm_profile : Field, default: None
            RPM signal associated with the time-domain signals.
            It is assumed that the signal's unit is ``rpm``. If this is not the case,
            inaccurate behavior might occur during the conversion from RPM to frequency.
        orders : list, default: None
            List of the order numbers to isolate. The list must contain at least one value.
        fft_size : int, default: 1024
            Size of the FFT used to compute the STFT.
        window_type : str, default: 'HANN'
            Window type used for the FFT computation. Options are ``'TRIANGULAR'``, ``'BLACKMAN'``,
            ``'BLACKMANHARRIS'``, ``'HAMMING'``, ``'HANN'``, ``'GAUSS'``, ``'FLATTOP'``,
            and ``'RECTANGULAR'``.
        window_overlap : float, default: 0.5
            Overlap value between two successive FFT computations. Values can range from 0 to 1.
            For example, ``0`` means no overlap, and ``0.5`` means 50% overlap.
        width_selection : int, default: 10
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
    def signal(self) -> Field | FieldsContainer:
        """Input signal."""
        return self.__signal

    @signal.setter
    def signal(self, signal: Field | FieldsContainer):
        """Set the signal."""
        self.__signal = signal

    @property
    def rpm_profile(self) -> Field:
        """RPM profile."""
        return self.__rpm_profile

    @rpm_profile.setter
    def rpm_profile(self, rpm_profile: Field):
        """Set the RPM profile."""
        self.__rpm_profile = rpm_profile

    @property
    def orders(self) -> Field:
        """List of the order numbers to isolate.

        Can be provided as a list or a DPF field, but will be stored as DPF field regardless.
        """
        return self.__orders

    @orders.setter
    def orders(self, orders: Field | list):
        """Set the orders."""
        if type(orders) == list:
            f = Field()
            f.append(orders, 1)
            self.__orders = f
        else:
            self.__orders = orders

    @property
    def fft_size(self) -> int:
        """Number of FFT points."""
        return self.__fft_size

    @fft_size.setter
    def fft_size(self, fft_size: int):
        """Set the FFT size."""
        if fft_size < 0:
            raise PyAnsysSoundException("FFT size must be greater than 0.0.")
        self.__fft_size = fft_size

    @property
    def window_type(self) -> str:
        """Window type.

        Supported options are ``'TRIANGULAR'``, ``'BLACKMAN'``, ``'BLACKMANHARRIS'``, ``'HAMMING'``,
        ``'HANN'``, ``'GAUSS'``, ``'FLATTOP'``, and ``'RECTANGULAR'``.
        """
        return self.__window_type

    @window_type.setter
    def window_type(self, window_type: str):
        """Set the window type."""
        if window_type not in (
            "BLACKMANHARRIS",
            "HANN",
            "HAMMING",
            "GAUSS",
            "FLATTOP",
            "TRIANGULAR",
            "BLACKMAN",
            "RECTANGULAR",
        ):
            raise PyAnsysSoundException(
                "Invalid window type, accepted values are 'BLACKMANHARRIS', 'HANN', "
                "'BLACKMAN', 'HAMMING', 'GAUSS', 'FLATTOP', 'TRIANGULAR' and 'RECTANGULAR'."
            )

        self.__window_type = window_type

    @property
    def window_overlap(self) -> float:
        """Window overlap in %."""
        return self.__window_overlap

    @window_overlap.setter
    def window_overlap(self, window_overlap: float):
        """Set the window overlap."""
        if window_overlap < 0.0 or window_overlap > 1.0:
            raise PyAnsysSoundException("Window overlap must be between 0.0 and 1.0.")

        self.__window_overlap = window_overlap

    @property
    def width_selection(self) -> int:
        """Width in Hz of each individual order selection.

        Results may vary depending on ``fft_size`` value.
        """
        return self.__width_selection

    @width_selection.setter
    def width_selection(self, widt_selection: int):
        """Set the width selection."""
        if widt_selection < 0:
            raise PyAnsysSoundException("Width selection must be greater than 0.0.")
        self.__width_selection = widt_selection

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

        if self.orders is None:
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
            warnings.warn(PyAnsysSoundWarning("Output is not processed yet. \
                        Use the 'IsolateOrders.process()' method."))

        return self._output

    def get_output_as_nparray(self) -> np.ndarray:
        """Get the temporal signal of the isolated orders as a NumPy array.

        Returns
        -------
        numpy.ndarray
            Temporal signal of the isolated orders in a NumPy array.
        """
        output = self.get_output()

        if type(output) == Field:
            return output.data

        return convert_fields_container_to_np_array(output)

    def plot(self):
        """Plot the signal after order isolation."""
        if self._output is None:
            raise PyAnsysSoundException(
                f"Output is not processed yet. Use the `{__class__.__name__}.process()` method."
            )
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
            plt.plot(time_data, output[i].data, label=f"Channel {i}")
        else:
            plt.plot(time_data, field.data, label="Channel 0")

        plt.title(field.name)
        plt.legend()
        plt.xlabel(f"Time ({time_unit})")
        plt.ylabel(f"Amplitude ({unit})")
        plt.grid(True)
        plt.show()
