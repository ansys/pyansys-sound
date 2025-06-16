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

"""PyAnsys Sound class to store sound data."""
from typing import Optional

from ansys.dpf.core import FieldsContainer
import numpy as np

from .._pyansys_sound import PyAnsysSoundException


class _SourceBase(FieldsContainer):
    """PyAnsys Sound class to store sound data."""

    # def __init__(self, source_type: str = "", control_count: int = 1):
    #     super().__init__()
    #     self.type = source_type
    #     self.control_count = control_count

    @classmethod
    def create(cls, object: FieldsContainer) -> "BroadbandNoiseSource | HarmonicsSource":
        """TODO."""
        object.__class__ = cls
        object.check()
        object.update()
        return object

    def __str__(self):
        """Return the string representation of the object."""
        if self.channel_count > 0:
            properties_str = (
                f":\n\tsampling frequency: {self.fs:.1f} Hz" f"\n\tDuration: {self.duration:.2f} s"
            )
        else:
            properties_str = ""
        return f"Sound object with {self.channel_count} channels{properties_str}"

    # @property
    # def shape(self) -> tuple[int]:
    #     data_count = len(self._main_support)
    #     return (data_count, len(self.control_points[0]))
    #     # THIS IS NOT WORKING BECAUSE SOME I-J COMBINATIONS MIGHT BE MISSING
    #     # control_count = len(self.control_names)
    #     # if control_count == 1:
    #     #     return (data_count, len(self.control_points[0]))
    #     # return (data_count, len(self.control_points[0]), len(self.control_points[1]))

    @property
    def control_names(self) -> list[str]:
        return self.__control_names

    @property
    def control_units(self) -> list[str]:
        return self.__control_units

    @property
    def control_mins(self) -> list[float]:
        return self.__control_mins

    @property
    def control_maxs(self) -> list[float]:
        return self.__control_maxs

    @property
    def control_points(self) -> list[np.ndarray]:
        return self.__control_points

    def update(self) -> None:
        """Update the sound data."""
        if (
            len(self) < 1
            or len(self[0].data) < 1
            or len(self[0].time_freq_support.time_frequencies.data) < 1
        ):
            # NOTE: error message should be adjusted for each source type. Possibly use class
            # attributes containing the messages
            raise PyAnsysSoundException(
                "Specified harmonics source with two parameters must contain at least one "
                "order level (the provided DPF fields container must contain at least one "
                "field with at least one data point)."
            )

        self._main_support = np.array(self[0].time_freq_support.time_frequencies.data)

        for field in self:
            if len(field.data) != len(self._main_support):
                raise PyAnsysSoundException(
                    "Each set of order levels in the specified harmonics source with two "
                    "parameters must contain as many level values as the number of orders (in "
                    "the provided DPF fields container, each field must contain the same "
                    "number of data points and support values)."
                )

            if len(field.data) != len(self[0].data):
                raise PyAnsysSoundException(
                    "Each set of order levels in the specified harmonics source with two "
                    "parameters must contain the same number of level values (in the provided "
                    "DPF fields container, each field must contain the same number of data "
                    "points)."
                )

        name, unit, min, max, data = self.__get_control_info(1)
        self.__control_names = [name]
        self.__control_units = [unit]
        self.__control_mins = [min]
        self.__control_maxs = [max]
        self.__control_points = [data]
        # self.__control_points = [np.unique(data)]

        if len(self.labels) == 2:
            name, unit, min, max, data = self.__get_control_info(2)
            self.__control_names.append(name)
            self.__control_units.append(unit)
            self.__control_mins.append(min)
            self.__control_maxs.append(max)
            if len(data) != len(self.__control_points[0]):
                raise PyAnsysSoundException(
                    f"Control parameter 2 has {len(data)} points, "
                    f"but control parameter 1 has {len(self.__control_points[0])} points."
                )
            self.__control_points.append(data)
            # self.__control_points.append(np.unique(data))

        # test against 2nd control parameter (if relevant) is covered by the above check within the
        # if statement (technically, by the combination of it and this one)
        if self.__control_points[0] != len(self):
            raise PyAnsysSoundException(
                "Specified harmonics source with two parameters must contain as many sets of "
                "order levels as the number of values in both associated control parameters "
                "(in the provided DPF fields container, the number of fields should be the "
                "same as the number of values in both fields container supports)."
            )

    def get_as_nparray(self, i: int, j: Optional[int] = None) -> np.ndarray:
        """Get the sound data as a NumPy array."""
        # start by update to do required checks?
        self.update()

        # # THIS IS NOT WORKING BECAUSE SOME I-J COMBINATIONS MIGHT BE MISSING

        # if i < 0 or i >= self.shape[1]:
        #     raise PyAnsysSoundException(
        #         f"Control index i ({i}) is out of range. "
        #         f"This source control has {self.shape[1]} points."
        #     )

        # if j is not None:
        #     if len(self.shape) < 3:
        #         raise PyAnsysSoundException(
        #             f"Source data has 1 control only. Only one index must be provided."
        #         )

        #     if j < 0 or j >= self.shape[2]:
        #         raise PyAnsysSoundException(
        #             f"Control index j ({j}) is out of range. "
        #             f"This source control has {self.shape[2]} points."
        #         )

        #     return np.array(self.get_field({self.labels[0]: i, self.labels[1]: j}).data)

        # return np.array(self.get_field({self.labels[0]: i}).data)

    def __get_control_info(self, index) -> tuple[str, str, float, float, np.ndarray]:
        if index > len(self.labels) or index < 1:
            raise PyAnsysSoundException(
                f"Control index ({index}) is out of range. "
                f"This source has {len(self.labels)} controls."
            )

        match index:
            case 1:
                control_data = self.get_support("control_parameter_1")
            case 2:
                control_data = self.get_support("control_parameter_2")

        unit = control_data.available_field_supported_properties()[0]
        support = control_data.field_support_by_property(unit)
        data = support.data
        return support.name, unit, float(data.min()), float(data.max()), np.array(data)


class BroadbandNoiseSource(_SourceBase):
    """PyAnsys Sound class to store broadband noise data."""

    @property
    def spectrum_type(self) -> str:
        """Get the spectrum type of the sound data."""
        return self[0].time_freq_support.time_frequencies.field_definition.quantity_types[0]

    @property
    def delta_f(self) -> float:
        """Get the frequency resolution of the sound data."""
        frequencies = self[0].time_freq_support.time_frequencies.data
        if len(frequencies) > 1:
            return frequencies[1] - frequencies[0]
        else:
            return 0.0

    @property
    def frequencies(self) -> np.ndarray:
        """Get the frequencies of the sound data."""
        return self._main_support


class HarmonicsSource(_SourceBase):
    """PyAnsys Sound class to store harmonics data."""

    @property
    def orders(self) -> np.ndarray:
        """Get the frequencies of the sound data."""
        return self._main_support
