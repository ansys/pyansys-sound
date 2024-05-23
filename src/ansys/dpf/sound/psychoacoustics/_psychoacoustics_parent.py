"""Psychoacoustics functions."""
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
            if not (0.0 <= bark_band_indexes[ibark] <= 24.0):
                raise PyDpfSoundException(
                    "Specified Bark band indexes must be between 0.0 and 24.0 Bark."
                )

            if bark_band_indexes[ibark] < 2:
                bark_band_indexes[ibark] = (bark_band_indexes[ibark] - 0.3) / 0.85
            elif bark_band_indexes[ibark] > 20.1:
                bark_band_indexes[ibark] = (bark_band_indexes[ibark] + 4.422) / 1.22

        return 1920 * (bark_band_indexes + 0.53) / (26.28 - bark_band_indexes)
