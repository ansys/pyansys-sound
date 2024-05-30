"""Psychoacoustics functions."""
from ansys.dpf.core import Field
from numpy import typing as npt

from ..pydpf_sound import PyDpfSound, PyDpfSoundException


class PsychoacousticsParent(PyDpfSound):
    """
    Abstract mother class for psychoacoustics calculations.

    This is the mother class of all pychoacoustics indicators classes, should not be used as is.
    """

    def __init__(self):
        """Init.

        Init the class.
        """
        super().__init__()

    def _convert_bark_to_hertz(self, bark_band_indexes: npt.ArrayLike) -> npt.ArrayLike:
        """Convert Bark band indexes into frequencies.

        Converts input Bark band indexes (in Bark) into corresponding frequencies (in Hz),
        according to: Traunmüller, Hartmut. "Analytical Expressions for the Tonotopic Sensory
        Scale." Journal of the Acoustical Society of America. Vol. 88, Issue 1, 1990, pp. 97–100.

        Parameters
        ----------
        bark_band_indexes: numpy array
            Array of Bark band indexes to convert, in Bark.

        Returns
        -------
        numpy array
            Array of corresponding frequencies, in Hz.
        """
        for ibark in range(len(bark_band_indexes)):
            if not (0 <= bark_band_indexes[ibark] <= 24 + 1e-6):
                # A slight margin (1e-6) is used for the upper limit, because the last index from
                # the DPF operator is precisely 24.00000036.
                raise PyDpfSoundException(
                    "Specified Bark band indexes must be between 0.0 and 24.0 Bark."
                )

            if bark_band_indexes[ibark] < 2:
                bark_band_indexes[ibark] = (bark_band_indexes[ibark] - 0.3) / 0.85
            elif bark_band_indexes[ibark] > 20.1:
                bark_band_indexes[ibark] = (bark_band_indexes[ibark] + 4.422) / 1.22

        return 1920 * (bark_band_indexes + 0.53) / (26.28 - bark_band_indexes)

    def _check_channel_index(self, channel_index: int) -> bool:
        """Check whether a specified signal channel index is available or not.

        Parameters
        -------
        channel_index: int
            Index of the signal channel to check.

        Returns
        -------
        bool
            True if channel index is available, False if not.
        """
        output = self.get_output()
        if output == None:
            return False

        if type(output[0]) == Field:
            if channel_index != 0:
                raise PyDpfSoundException(
                    f"Specified channel index ({channel_index}) does not exist."
                )

        else:
            if channel_index < 0 or channel_index > self.get_output_as_nparray()[0].ndim - 1:
                raise PyDpfSoundException(
                    f"Specified channel index ({channel_index}) does not exist."
                )

        return True
