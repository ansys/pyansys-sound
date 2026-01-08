Xtract
------

This package provides access to Xtract. Xtract is a feature designed for denoising and extracting
components from time-domain signals.

Based on 3 extraction algorithms, Xtract lets you split a time-domain signal into 4 components:
noise, tones, transients, and the remaining part (that is, everything that is not detected as
either of the other 3 components).

The algorithm parameters can be set automatically or manually.

.. module:: ansys.sound.core.xtract

.. autosummary::
    :toctree: _autosummary

    Xtract
    XtractDenoiser
    XtractDenoiserParameters
    XtractTonal
    XtractTonalParameters
    XtractTransient
    XtractTransientParameters
