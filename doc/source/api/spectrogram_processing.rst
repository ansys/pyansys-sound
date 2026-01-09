Spectrogram processing
----------------------

This subpackage provides functions to process signals in the time-frequency domain,
such as the calculation of the Short-Time Fourier Transform (STFT) and Inverse STFT (ISTFT).

In the case of rotating machines, given the RPM information,
it also allows you to isolate specific orders from a spectrogram.

.. module:: ansys.sound.core.spectrogram_processing

.. autosummary::
    :toctree: _autosummary

    Stft
    Istft
    IsolateOrders