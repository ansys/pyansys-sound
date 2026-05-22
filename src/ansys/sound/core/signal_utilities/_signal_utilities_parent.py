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

"""Signal utilities."""

from ansys.dpf.core import Field
import matplotlib.pyplot as plt

from .._pyansys_sound import PyAnsysSound, PyAnsysSoundException


class SignalUtilitiesParent(PyAnsysSound):
    """
    Provides the abstract base class for signal utilities.

    This is the base class of all signal utilities classes and should not be used as is.
    """

    def plot(self):
        """Plot the resulting signals in a single figure."""
        if self._output is None:
            raise PyAnsysSoundException(
                "Output is not processed yet. "
                f"Use the `{self.__class__.__name__}.process()` method."
            )
        output: Field | list[Field] = self.get_output()

        if isinstance(output, Field):
            output = [output]

        num_channels = len(output)

        time_data = output[0].time_freq_support.time_frequencies.data
        time_unit = output[0].time_freq_support.time_frequencies.unit
        unit = output[0].unit if isinstance(output[0].unit, str) else output[0].unit[1]
        unit_str = f" ({unit})" if len(unit) > 0 else ""

        for i in range(num_channels):
            plt.plot(time_data, output[i].data, label=f"Channel {i}")

        plt.title(output[0].name)
        plt.legend()
        plt.xlabel(f"Time ({time_unit})")
        plt.ylabel(f"Amplitude{unit_str}")
        plt.grid(True)
        plt.show()
