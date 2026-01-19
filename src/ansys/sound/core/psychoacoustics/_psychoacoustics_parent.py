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

"""Psychoacoustics functions."""

import numpy as np

from .._pyansys_sound import PyAnsysSound, PyAnsysSoundException

# Sound field types.
FIELD_FREE = "Free"
FIELD_DIFFUSE = "Diffuse"


class PsychoacousticsParent(PyAnsysSound):
    """
    Abstract base class for psychoacoustics calculations.

    This is the base class for all pychoacoustics indicators classes and should not be used as is.
    """

    def _convert_bark_to_hertz(self, bark_band_indexes: np.ndarray) -> np.ndarray:
        """Convert Bark band indexes into frequencies.

        Converts input Bark band indexes (in Bark) into corresponding frequencies (in Hz)
        according to this article: Traunmüller, Hartmut. "Analytical Expressions for the
        Tonotopic Sensory Scale." Journal of the Acoustical Society of America. Vol. 88,
        Issue 1, 1990, pp. 97–100.

        Parameters
        ----------
        bark_band_indexes : numpy.ndarray
            Array of Bark band indexes to convert in Bark.

        Returns
        -------
        numpy.ndarray
            Array of corresponding frequencies in Hz.
        """
        for ibark in range(len(bark_band_indexes)):
            if not (0 <= bark_band_indexes[ibark] <= 24 + 1e-6):
                # A slight margin (1e-6) is used for the upper limit, because the last index from
                # the DPF operator is precisely 24.00000036.
                raise PyAnsysSoundException(
                    "Specified Bark band indexes must be between 0.0 and 24.0 Bark."
                )

            if bark_band_indexes[ibark] < 2:
                bark_band_indexes[ibark] = (bark_band_indexes[ibark] - 0.3) / 0.85
            elif bark_band_indexes[ibark] > 20.1:
                bark_band_indexes[ibark] = (bark_band_indexes[ibark] + 4.422) / 1.22

        return 1920 * (bark_band_indexes + 0.53) / (26.28 - bark_band_indexes)
