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

"""PyAnsys Sound signal fields container creation."""

import warnings

from ansys.dpf.core import Field, FieldsContainer
import numpy as np

from . import SignalUtilitiesParent
from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning

FIELDCONTAINER_LABELSPACE_ID = "channel"


class CreateSignalFieldsContainer(SignalUtilitiesParent):
    """Create a PyAnsys Sound fields container containing signals as DPF fields.

    This class creates a DPF fields container from a list, tuple, or array of signal fields. To
    create signal fields from signal data, use the class :class:`CreateSignalField`.

    .. seealso::
        :class:`CreateSignalField`

    Examples
    --------
    Create a fields container from a list of signal fields.

    >>> from ansys.sound.core.signal_utilities import CreateSignalFieldsContainer
    >>> create_fields_container = CreateSignalFieldsContainer(fields=my_signal_fields)
    >>> create_fields_container.process()
    >>> signals_in_a_fields_container = create_fields_container.get_output()
    """

    def __init__(
        self,
        fields: list[Field] | tuple[Field] | np.ndarray[Field] = None,
    ):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        fields : list[Field] | tuple[Field] | np.ndarray[Field], default: None
            Signal fields to include in the fields container.
        """
        super().__init__()
        self.fields = fields

    def __str__(self):
        """Return the string representation of the object."""
        if self._output is None:
            str_output = " None"
        else:
            str_output = f"\n{self._output}"

        return (
            f"{self.__class__.__name__} object with "
            f"{len(self.fields) if self.fields is not None else 0} field(s).\n"
            f"Output:{str_output}"
        )

    @property
    def fields(self) -> list[Field] | tuple[Field] | np.ndarray[Field]:
        """List, tuple, or NumPy array of signal fields to store."""
        return self.__fields

    @fields.setter
    def fields(self, fields: list[Field] | tuple[Field] | np.ndarray[Field]):
        """Set the signal fields."""
        if fields is not None:
            valid = True
            if not isinstance(fields, (list, tuple, np.ndarray)):
                valid = False
            else:
                for field in fields:
                    if not isinstance(field, Field):
                        valid = False
                        break

            if not valid:
                raise PyAnsysSoundException(
                    "Attribute `fields` must be provided as a list, tuple, or NumPy array of DPF "
                    "fields."
                )

        self.__fields = fields

    def process(self):
        """Create the signal fields container."""
        self._output = FieldsContainer()
        self._output.labels = [FIELDCONTAINER_LABELSPACE_ID]
        if self.fields is not None:
            for ifield, field in enumerate(self.fields):
                self._output.add_field({FIELDCONTAINER_LABELSPACE_ID: ifield + 1}, field)

    def get_output(self) -> FieldsContainer:
        """Get the signal fields container.

        Returns
        -------
        FieldsContainer
            Signal fields container.
        """
        if self._output is None:
            warnings.warn(
                PyAnsysSoundWarning(
                    f"Output is not processed yet. "
                    f"Use the `{self.__class__.__name__}.process()` method."
                )
            )

        return self._output
