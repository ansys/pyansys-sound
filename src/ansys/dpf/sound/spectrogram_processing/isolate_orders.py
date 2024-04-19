"""Isolate orders of a signal."""

import warnings

from ansys.dpf.core import Field, FieldsContainer, Operator
import matplotlib.pyplot as plt
from numpy import typing as npt

from . import SpectrogramProcessingParent
from ..pydpf_sound import PyDpfSoundException, PyDpfSoundWarning


class IsolateOrders(SpectrogramProcessingParent):
    """Isolate orders of a signal.

    This class isolates the order of a given signal that has an RPM profile associated with.
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
        """Create an Istft class.

        Parameters
        ----------
        signal:
            The input signal(s) as a fields container or a field on which to isolate orders.
        rpm_profile:
            The RPM signal associated with the time signals, as a field.
            It is assumed that the signal's unit is 'rpm': if this is not the case,
            inaccurate behavior might occur during the conversion from RPM to frequency.
        orders
            List of the order numbers you want to isolate. Must contain at least one value.
        fft_size
            Size (as an integer) of the FFT used to compute the STFT. Default is 1024.
        window_type
            The window used for the FFT computation, as a string.
            Allowed input strings are :
            'HANNING', 'BLACKMANHARRIS', 'HANN','BLACKMAN', 'HAMMING', 'KAISER', 'BARTLETT' and
            'RECTANGULAR'.
            If no parameter is specified, the default value is 'HANNING'.
        window_overlap:
            The overlap value between two successive FFT computations (value between 0 and 1).
            0 means no overlap, 0.5 means 50 % overlap.
            If no parameter is specified, default value is 0.5.
        width_selection
            The width, in Hz, of the area used to select each individual order.
            Note that its precision depends on the FFT size. Default value is 10 Hz.
        """
        super().__init__()
        self.signal = signal
        self.rpm_profile = rpm_profile
        self.orders = orders
        self.fft_size = fft_size
        self.window_type = window_type
        self.window_overlap = window_overlap
        self.width_selection = width_selection
        self.operator = Operator("isolate_orders")

    @property
    def signal(self):
        """Signal property."""
        return self.__signal  # pragma: no cover

    @signal.setter
    def signal(self, signal: Field | FieldsContainer):
        """Set the signal."""
        self.__signal = signal

    @signal.getter
    def signal(self) -> Field | FieldsContainer:
        """Get the signal.

        Returns
        -------
        Field
                The signal as a Field or a FieldsContainer.
        """
        return self.__signal

    @property
    def rpm_profile(self):
        """RPM Profile property."""
        return self.__rpm_profile  # pragma: no cover

    @rpm_profile.getter
    def rpm_profile(self) -> Field:
        """Get the RPM profile.

        Returns
        -------
        Field
                The RPM profile.
        """
        return self.__rpm_profile

    @rpm_profile.setter
    def rpm_profile(self, rpm_profile: Field):
        """Set the RPM Profile."""
        self.__rpm_profile = rpm_profile

    @property
    def orders(self):
        """Orders property."""
        return self.__orders  # pragma: no cover

    @orders.getter
    def orders(self) -> Field:
        """Get the orders.

        Returns
        -------
        list
                The orders.
        """
        return self.__orders

    @orders.setter
    def orders(self, orders: Field | list):
        """Set the orders."""
        if type(orders) == list:
            f = Field()
            f.data = orders
            self.__orders = f
        elif type(orders):
            self.__orders = orders

    @property
    def fft_size(self):
        """Fft size property."""
        return self.__fft_size  # pragma: no cover

    @fft_size.setter
    def fft_size(self, fft_size):
        """Set the fft size."""
        if fft_size < 0:
            raise PyDpfSoundException("Fft size must be greater than 0.0.")
        self.__fft_size = fft_size

    @fft_size.getter
    def fft_size(self) -> float:
        """Get the fft size.

        Returns
        -------
        float
                The fft size.
        """
        return self.__fft_size

    @property
    def window_type(self):
        """Window type property."""
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
            and window_type != "RECTANGULAR"
        ):
            raise PyDpfSoundException(
                "Invalid window type, accepted values are 'HANNING', 'BLACKMANHARRIS', 'HANN', \
                    'BLACKMAN','HAMMING', 'KAISER', 'BARTLETT', 'RECTANGULAR'."
            )

        self.__window_type = window_type

    @window_type.getter
    def window_type(self) -> str:
        """Get the window type.

        Returns
        -------
        str
                The window type.
        """
        return self.__window_type

    @property
    def window_overlap(self):
        """Window overlap property."""
        return self.__window_overlap  # pragma: no cover

    @window_overlap.setter
    def window_overlap(self, window_overlap):
        """Set the window overlap."""
        if window_overlap < 0.0 or window_overlap > 1.0:
            raise PyDpfSoundException("Window overlap must be between 0.0 and 1.0.")

        self.__window_overlap = window_overlap

    @window_overlap.getter
    def window_overlap(self) -> float:
        """Get the fft size.

        Returns
        -------
        float
                The window overlap.
        """
        return self.__window_overlap

    @property
    def width_selection(self):
        """Width selection property."""
        return self.__width_selection  # pragma: no cover

    @width_selection.setter
    def width_selection(self, widt_selection):
        """Set the width selection."""
        if widt_selection < 0:
            raise PyDpfSoundException("Width selection must be greater than 0.0.")
        self.__width_selection = widt_selection

    @width_selection.getter
    def width_selection(self) -> int:
        """Get the width selection.

        Returns
        -------
        int
                The width selection.
        """
        return self.__width_selection

    def process(self):
        """Isolate the orders.

        Calls the appropriate DPF Sound operator to isolate the orders of the signal.
        """
        if self.signal == None:
            raise PyDpfSoundException("No signal for order isolation. Use IsolateOrder.signal.")

        if self.rpm_profile == None:
            raise PyDpfSoundException(
                "No RPM profile for order isolation. \
                                      Use IsolateOrder.rpm_profile."
            )

        if self.orders == None:
            raise PyDpfSoundException("No orders for order isolation. Use IsolateOrder.orders.")

        self.operator.connect(0, self.signal)
        self.operator.connect(1, self.rpm_profile)
        self.operator.connect(2, self.orders)
        self.operator.connect(3, self.fft_size)
        self.operator.connect(4, self.window_type)
        self.operator.connect(5, self.window_overlap)
        self.operator.connect(6, self.width_selection)

        # Runs the operator
        self.operator.run()

        # Stores output in the variable
        if type(self.signal) == FieldsContainer:
            self._output = self.operator.get_output(0, "fields_container")
        elif type(self.signal) == Field:
            self._output = self.operator.get_output(0, "field")

    def get_output(self) -> Field | FieldsContainer:
        """Return the temporal signal of the isolated orders as a Field or Fields Container.

        Returns
        -------
        Field | FieldsContainer
                The signal resulting from the order isolation as a DPF Field or FieldsContainer.
        """
        if self._output == None:
            # Computing output if needed
            warnings.warn(
                PyDpfSoundWarning("Output has not been yet processed, use IsolateOrders.process().")
            )

        return self._output

    def get_output_as_nparray(self) -> npt.ArrayLike:
        """Return the temporal signal of the isolated orders as a numpy array.

        Returns
        -------
        np.array
                The resulting from the order isolation as a numpy array.
        """
        output = self.get_output()

        if type(output) == Field:
            return output.data

        return self.convert_fields_container_to_np_array(output)

    def plot(self):
        """Plot signals.

        Plots the signal after order isolation.
        """
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

        plt.title(field.name)
        plt.legend()
        plt.xlabel(time_unit)
        plt.ylabel(unit)
        plt.grid(True)
        plt.show()
