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

"""Computes ISO 1996-2 tonality."""

import warnings

from ansys.dpf.core import DataTree, Field, Operator, types
import numpy as np

from . import PsychoacousticsParent
from .._pyansys_sound import PyAnsysSoundException, PyAnsysSoundWarning

# Name of the DPF Sound operator used in this module.
ID_COMPUTE_TONALITY_ISO1996_2 = "compute_tonality_iso1996_2"

# Keys identifying computation details.
KEY_DATA_TREE_CB_LOWER_LIMITS = "Lower critical band limit (Hz)"
KEY_DATA_TREE_CB_UPPER_LIMITS = "Higher critical band limit (Hz)"
KEY_DATA_TREE_TOTAL_NOISE_LEVEL = "Total noise level (dBA)"
KEY_DATA_TREE_TOTAL_TONAL_LEVEL = "Total tonal level (dBA)"


class TonalityISO1996_2(PsychoacousticsParent):
    """Computes the tonality according to the standard ISO 1996-2:2007, annex C.

    This class is used to compute the tonal audibility and tonal adjustment of a signal according
    to the annex C of the ISO 1996-2:2007 standard.

    .. seealso::
        :class:`TonalityISO1996_2_OverTime`, :class:`TonalityDIN45681`, :class:`TonalityISOTS20065`,
        :class:`TonalityECMA418_2`, :class:`TonalityAures`

    Examples
    --------
    Compute the tonality of a signal according to the 2007 version of the ISO 1996-2 standard,
    annex C.

    >>> from ansys.sound.core.psychoacoustics import TonalityISO1996_2
    >>> tonality = TonalityISO1996_2(signal=my_signal)
    >>> tonality.process()
    >>> tonal_audibility = tonality.get_tonal_audibility()

    .. seealso::
        :ref:`calculate_tonality_indicators`
            Example demonstrating how to compute various tonality indicators.
    """

    def __init__(
        self,
        signal: Field = None,
        noise_pause_threshold: float = 1.0,
        effective_analysis_bandwidth: float = 5.0,
        noise_bandwidth_ratio: float = 0.75,
    ):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        signal: Field, default: None
            Signal in Pa on which to calculate the tonality.
        noise_pause_threshold: float, default: 1.0
            Noise pause detection threshold ("level excess") in dB.
        effective_analysis_bandwidth: float, default: 5.0
            Effective analysis bandwidth in Hz.
        noise_bandwidth_ratio: float, default: 0.75
            Noise bandwidth, in proportion to the critical bandwidth, that is taken into account
            for the calculation of the masking noise level (the default value `0.75` means that the
            masking noise level is estimated in a band delimited by 75 % of the critical bandwidth
            on each side of the tone). Value must be between `0.75` and `2`.

        For more information about the parameters, please refer to the Ansys Sound SAS user guide.
        """
        super().__init__()
        self.signal = signal
        self.noise_pause_threshold = noise_pause_threshold
        self.effective_analysis_bandwidth = effective_analysis_bandwidth
        self.noise_bandwidth_ratio = noise_bandwidth_ratio
        self.__operator = Operator(ID_COMPUTE_TONALITY_ISO1996_2)

    def __str__(self):
        """Return the string representation of the object."""
        if self.get_output() is None:
            str_tonality = "Not processed\n"
            str_adjustement = "Not processed\n"
        else:
            str_tonality = f"{self.get_tonal_audibility():.1f} dB\n"
            str_adjustement = f"{self.get_tonal_adjustment():.1f} dB\n"

        return (
            f"{__class__.__name__} object.\n"
            "Data\n"
            f'Signal name: "{self.signal.name}"\n'
            f"Noise pause detection threshold: {self.noise_pause_threshold} dB\n"
            f"Effective analysis bandwidth: {self.effective_analysis_bandwidth} Hz\n"
            f"Noise bandwidth in proportion to CBW: {self.noise_bandwidth_ratio}\n"
            f"Tonal audibility: {str_tonality}"
            f"Tonal adjustment Kt: {str_adjustement}"
        )

    @property
    def signal(self) -> Field:
        """Input signal in Pa."""
        return self.__signal

    @signal.setter
    def signal(self, signal: Field):
        """Set the signal."""
        if not (isinstance(signal, Field) or signal is None):
            raise PyAnsysSoundException("Signal must be specified as a DPF field.")
        self.__signal = signal

    @property
    def noise_pause_threshold(self) -> float:
        """Noise pause detection threshold (level excess) in dB."""
        return self.__noise_pause_threshold

    @noise_pause_threshold.setter
    def noise_pause_threshold(self, noise_pause_threshold: float):
        """Set the noise pause detection threshold."""
        if not isinstance(noise_pause_threshold, float):
            if isinstance(noise_pause_threshold, int):
                noise_pause_threshold = float(noise_pause_threshold)
            else:
                raise PyAnsysSoundException(
                    "Noise pause threshold must be provided as a float value."
                )
        self.__noise_pause_threshold = noise_pause_threshold

    @property
    def effective_analysis_bandwidth(self) -> float:
        """Effective analysis bandwidth in Hz."""
        return self.__effective_analysis_bandwidth

    @effective_analysis_bandwidth.setter
    def effective_analysis_bandwidth(self, effective_analysis_bandwidth: float):
        """Set the effective analysis bandwidth."""
        if not (0.0 < effective_analysis_bandwidth <= 5.0):
            raise PyAnsysSoundException(
                "Effective analysis bandwidth must be in the range [0.0; 5.0] Hz."
            )
        self.__effective_analysis_bandwidth = effective_analysis_bandwidth

    @property
    def noise_bandwidth_ratio(self) -> float:
        """Noise bandwidth in proportion to the critical bandwidth.

        Noise bandwidth, in proportion to the critical bandwidth, that is taken into account for
        the calculation of the masking noise level (the default value `0.75` means that the masking
        noise level is estimated in a band delimited by 75 % of the critical bandwidth on each side
        of the tone). Value must be between `0.75` and `2`.
        """
        return self.__noise_bandwidth_ratio

    @noise_bandwidth_ratio.setter
    def noise_bandwidth_ratio(self, ratio: float):
        """Set the noise bandwidth in proportion to the critical bandwidth."""
        if not (0.75 <= ratio < 2.0) or not isinstance(ratio, float):
            raise PyAnsysSoundException(
                "Noise critical bandwidth ratio must be provided as a float value,"
                "in the range [0.75; 2.0]."
            )
        self.__noise_bandwidth_ratio = ratio

    def process(self):
        """Compute the ISO 1996-2 tonality.

        This method calls the appropriate DPF Sound operator.
        """
        if self.signal == None:
            raise PyAnsysSoundException(
                f"No input signal defined. Use ``{__class__.__name__}.signal``."
            )

        # Connect the operator input(s).
        self.__operator.connect(0, self.signal)
        self.__operator.connect(1, self.noise_pause_threshold)
        self.__operator.connect(2, self.effective_analysis_bandwidth)
        self.__operator.connect(3, self.noise_bandwidth_ratio)

        # Run the operator.
        self.__operator.run()

        # Store the operator outputs in a tuple.
        self._output = (
            self.__operator.get_output(0, types.double),
            self.__operator.get_output(1, types.double),
            self.__operator.get_output(2, types.data_tree),
        )

    def get_output(self) -> tuple[float, float, DataTree]:
        """Get the ISO 1996-2 tonality data, in a tuple containing data of various types.

        Returns
        -------
        tuple
            -   First element (float): tonal audibility, in dB.

            -   Second element (float): tonal adjustment, in dB.

            -   Third element (DataTree): computation details, that is, the main tone's critical
                band boundary frequencies, and the total tone and noise levels in dBA.
        """
        if self._output == None:
            warnings.warn(
                PyAnsysSoundWarning(
                    f"Output is not processed yet. "
                    f"Use the ``{__class__.__name__}.process()`` method."
                )
            )

        return self._output

    def get_output_as_nparray(self) -> tuple[np.ndarray]:
        """Get the ISO 1996-2 tonality data, in a tuple of NumPy arrays.

        Returns
        -------
        tuple
            -   First element: tonal audibility, in dB.

            -   Second element: tonal adjustment, in dB.

            -   Third element: computation details, that is, the main tone's critical band boundary
                frequencies, and the total tone and noise levels in dBA.
        """
        output = self.get_output()

        if output == None:
            return (
                np.nan,
                np.nan,
                np.array([]),
            )

        # Extracting data from the data tree
        data_tree = output[2]

        details_array = np.array(
            [
                data_tree.get_as(KEY_DATA_TREE_CB_LOWER_LIMITS, types.double),
                data_tree.get_as(KEY_DATA_TREE_CB_UPPER_LIMITS, types.double),
                data_tree.get_as(KEY_DATA_TREE_TOTAL_NOISE_LEVEL, types.double),
                data_tree.get_as(KEY_DATA_TREE_TOTAL_TONAL_LEVEL, types.double),
            ]
        )

        return (np.array(output[0]), np.array(output[1]), details_array)

    def get_tonal_audibility(self) -> float:
        """Get the ISO 1996-2 tonal audibility, in dB.

        Returns
        -------
        float
            ISO 1996-2 tonal audibility, in dB.
        """
        return float(self.get_output_as_nparray()[0])

    def get_tonal_adjustment(self) -> float:
        """Get the ISO 1996-2 tonal adjustment, in dB.

        Returns
        -------
        float
            ISO 1996-2 tonal adjustment, in dB.
        """
        return float(self.get_output_as_nparray()[1])

    def get_computation_details(self) -> dict[str, float]:
        """Get the ISO 1996-2 computation details.

        Returns
        -------
        dict[str, float]
            Dictionary containing the ISO 1996-2 tonality details, namely:

            -   Main tone's critical band lower frequency in Hz
                (`"Lower critical band limit (Hz)"`),

            -   Main tone's critical band higher frequency in Hz
                (`"Higher critical band limit (Hz)"`),

            -   Total tone level in dBA (`"Total tonal level (dBA)"`),

            -   Total noise level in dBA (`"Total noise level (dBA)"`).
        """
        if self.get_output() is None:
            return {}

        details_array = self.get_output_as_nparray()[2]
        return {
            KEY_DATA_TREE_CB_LOWER_LIMITS: details_array[0],
            KEY_DATA_TREE_CB_UPPER_LIMITS: details_array[1],
            KEY_DATA_TREE_TOTAL_NOISE_LEVEL: details_array[2],
            KEY_DATA_TREE_TOTAL_TONAL_LEVEL: details_array[3],
        }
