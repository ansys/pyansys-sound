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

"""Xtract denoiser parameters."""

from ansys.dpf.core import Field, GenericDataContainer, Operator

from . import XtractParent
from .._pyansys_sound import PyAnsysSoundException

ID_DENOISER_PARAMETERS_CLASS = "Xtract_denoiser_parameters"
ID_NOISE_PSD = "noise_levels"


class XtractDenoiserParameters(XtractParent):
    """Store denoiser parameters for Xtract signal denoising.

    .. seealso::
        :class:`Xtract`, :class:`XtractDenoiser`

    Examples
    --------
    Create a set of Xtract denoiser parameters from a PSD.

    >>> from ansys.sound.core.xtract import XtractDenoiserParameters
    >>> denoiser_parameters = XtractDenoiserParameters(noise_psd=my_noise_psd)

    Create a set of Xtract denoiser parameters from a white noise level.

    >>> from ansys.sound.core.xtract import XtractDenoiserParameters
    >>> denoiser_parameters = XtractDenoiserParameters()
    >>> noise_psd = denoiser_parameters.create_noise_psd_from_white_noise_level(
    ...     white_noise_level=30.0,
    ...     sampling_frequency=48000.0,
    ...     window_length=50,
    ... )
    >>> denoiser_parameters.noise_psd = noise_psd

    Create a set of Xtract denoiser parameters from noise samples.

    >>> from ansys.sound.core.xtract import XtractDenoiserParameters
    >>> denoiser_parameters = XtractDenoiserParameters()
    >>> noise_psd = denoiser_parameters.create_noise_psd_from_noise_samples(
    ...     signal=my_noise_signal,
    ...     sampling_frequency=48000.0,
    ...     window_length=50,
    ... )
    >>> denoiser_parameters.noise_psd = noise_psd

    .. seealso::
        :ref:`xtract_feature_example`
            Example demonstrating how to use Xtract to extract the various components of a signal.
    """

    def __init__(self, noise_psd: Field = None):
        """Class instantiation takes the following parameters.

        Parameters
        ----------
        noise_psd : Field, optional
            Power spectral density of the noise in unit^2/Hz (Pa^2/Hz for example).
            This parameter can be produced using one of the following methods:

            - ``XtractDenoiserParameters.create_noise_psd_from_white_noise_level()``
            - ``XtractDenoiserParameters.create_noise_psd_from_noise_samples()``
            - ``XtractDenoiserParameters.create_noise_psd_from_automatic_estimation()``
        """
        self.__generic_data_container = GenericDataContainer()
        self.__generic_data_container.set_property("class_name", ID_DENOISER_PARAMETERS_CLASS)

        if noise_psd is None:
            noise_psd = Field()

        self.noise_psd = noise_psd

    @property
    def noise_psd(self) -> Field:
        """Power spectral density (PSD) of the noise in unit^2/Hz (Pa^2/Hz for example)."""
        return self.__generic_data_container.get_property(ID_NOISE_PSD)

    @noise_psd.setter
    def noise_psd(self, noise_psd: Field):
        """Set the noise PSD."""
        if noise_psd is None:
            raise PyAnsysSoundException("Noise PSD must be a non-empty field.")

        self.__generic_data_container.set_property(ID_NOISE_PSD, noise_psd)

    def get_parameters_as_generic_data_container(self) -> GenericDataContainer:
        """Get the parameters as a generic data container.

        Returns
        -------
        GenericDataContainer
            Parameter structure in a generic data container.
        """
        return self.__generic_data_container

    def create_noise_psd_from_white_noise_level(
        self, white_noise_level: float, sampling_frequency: float, window_length: int = 50
    ) -> Field:
        """Create a power spectral density (PSD) of noise from the white noise level.

        Parameters
        ----------
        white_noise_level : float
            Power of the white noise  in dB SPL.
        sampling_frequency : float, optional
            Sampling frequency in Hz of the signal to denoise,
            which can be different from the signal used for creating the noise profile.
            The default is the sampling frequency of the noise signal.
        window_length : int, default: 50
            Window length for the noise level estimation in milliseconds (ms).

        Returns
        -------
        Field
            PSD of noise in unit^2/Hz (Pa^2/Hz for example).
        """
        op = Operator("create_noise_profile_from_white_noise_power")
        op.connect(0, white_noise_level)
        op.connect(1, sampling_frequency)
        op.connect(2, int(window_length))
        op.run()

        f = op.get_output(0, "field")
        return f

    def create_noise_psd_from_noise_samples(
        self, signal: Field, sampling_frequency: float, window_length: int = 50
    ) -> Field:
        """Create a power spectral density (PSD) of noise from specific noise samples.

        Parameters
        ----------
        signal : Field
            Noise signal.
        sampling_frequency : float, optional
            Sampling frequency in Hz of the signal to denoise,
            which can be different from the signal used for creating the noise profile.
            The default is the sampling frequency of the noise signal.
        window_length : int, default: 50
            Window length for the noise level estimation in milliseconds (ms).

        Returns
        -------
        Field
            PSD of noise in unit^2/Hz (Pa^2/Hz for example).
        """
        op = Operator("create_noise_profile_from_noise_samples")
        op.connect(0, signal)
        op.connect(1, sampling_frequency)
        op.connect(2, window_length)
        op.run()

        f = op.get_output(0, "field")
        return f

    def create_noise_psd_from_automatic_estimation(
        self, signal: Field, window_length: int = 50
    ) -> Field:
        """Create a power spectral density (PSD) of noise using an automatic estimation.

        Parameters
        ----------
        signal : Field
            Signal to estimate the noise profile from.
        window_length : int, default: 50
            Window length for the noise level estimation in milliseconds (ms).

        Returns
        -------
        Field
            PSD of noise in unit^2/Hz (Pa^2/Hz for example).
        """
        op = Operator("create_noise_profile_from_automatic_estimation")
        op.connect(0, signal)
        op.connect(1, window_length)
        op.run()

        f = op.get_output(0, "field")
        return f
