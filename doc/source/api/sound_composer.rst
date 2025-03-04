Sound composer
--------------

Sound Composer is a module allowing you to generate complex sounds through mixing several tracks.

Each track contains a source, which can be a sound coming from a recording, or the parameters to generate a sound
(from a CAE simulation for example). A control profile is used to generate this sound, an RPM profile for example,
to follow a realistic situation.

Each track contains an optional transfer function (filter) can be applied to each track to simulate the transfer
between a source and a receiver.

The Sound composer module allows you to create projects including several tracks, therefore it eases the process of
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