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

"""Sound Composer's source."""

import warnings

from .._pyansys_sound import PyAnsysSoundWarning
from ._sound_composer_parent import SoundComposerParent


class SourceParent(SoundComposerParent):
    """
    Provides the abstract base class for the Sound Composer's sources.

    This is the base class of all Sound Composer's source classes and should not be used as is.
    """

    def is_source_control_valid(self) -> bool:
        """Check if the source control is valid."""
        return False

    def plot_control(self):
        """Plot the source control(s) in a figure."""
        pass

    def set_from_generic_data_containers(self, source_data, source_control_data):
        """Set the source and source control data from generic data containers."""
        warnings.warn(
            PyAnsysSoundWarning(
                "Cannot set from generic data containers because there is nothing to set here."
            )
        )

    def get_as_generic_data_containers(self) -> tuple:
        """Get the object data as generic data containers."""
        warnings.warn(
            PyAnsysSoundWarning("Cannot create generic data containers because there is no data.")
        )
        return (None, None)
