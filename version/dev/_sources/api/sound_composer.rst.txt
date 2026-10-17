Sound composer
--------------

Sound Composer is a feature allowing you to generate complex sounds by mixing several tracks.

Each track contains a source, which can be an audio recording, or a set of spectral data
(from a CAE simulation for example), possibly associated to specific control values. The track may also
contain control profiles, an RPM profile for example, that are used to generate the sound, to
replicate a realistic situation.

Each track contains an optional transfer function (filter) to simulate the transfer
between a source and a receiver.

The Sound composer sub-package allows you to create projects including several tracks. It therefore eases the process of
mixing different source types: harmonics (1 or 2 control parameters), broadband noise (1 or 2 control parameters),
audio, and spectrum.

.. module:: ansys.sound.core.sound_composer

.. autosummary::
    :toctree: _autosummary

    SoundComposer
    Track
    SourceSpectrum
    SourceBroadbandNoise
    SourceBroadbandNoiseTwoParameters
    SourceHarmonics
    SourceHarmonicsTwoParameters
    SourceAudio
    SourceControlSpectrum
    SourceControlTime
    SpectrumSynthesisMethods