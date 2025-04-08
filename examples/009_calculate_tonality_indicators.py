# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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

"""
.. _calculate_tonality_indicators:

Calculate Tonality Indicators (ISO1996-2, DIN45681, ECMA418-2, ISO/TS 20065, Aurès)
-----------------------------------------------------------------------------------

This example shows how to calculate tonality indicators.
The list of indicators covered in this example includes:
- ISO1996-2
- DIN45681
- ECMA418-2
- ISO/TS 20065
- Aurès

All these indicators are calculated from a same acoustic signal,
and the different results are commented, compared or discussed.
"""

# %%
# Set up analysis
# ~~~~~~~~~~~~~~~
# Setting up the analysis consists of loading Ansys libraries, connecting to the
# DPF server, and retrieving the example files.

# Load required libraries.
from ansys.sound.core.examples_helpers import download_aircraft10kHz_wav
from ansys.sound.core.psychoacoustics import (
    TonalityAures,
    TonalityDIN45681,
    TonalityECMA418_2,
    TonalityISO1996_2,
    TonalityISO1996_2_OverTime,
    TonalityISOTS20065,
)
from ansys.sound.core.server_helpers import connect_to_or_start_server
from ansys.sound.core.signal_utilities import LoadWav
from ansys.sound.core.spectrogram_processing.stft import Stft

# Connect to a remote server or start a local server.
my_server = connect_to_or_start_server(use_license_context=True)

# Load example data file: it is the passby noise of an aircraft.
path_aircraft_wav = download_aircraft10kHz_wav(server=my_server)
wav_loader = LoadWav(path_aircraft_wav)
wav_loader.process()
signal_aircraft = wav_loader.get_output()[0]


# %%
# The signal used in this example is the passby noise of an aircraft.
# From the spectrogram, you can see that the signal contains some tonal components,
# especially the two tones starting around 800Hz and decreasing all along the
# duraction of the signal, due to the Doppler effect.
#
# The signal is sampled at 10 kHz, and the duration is about 26 seconds.

# Calculate and display the spectrogram of the signal used in this example
stft = Stft(signal_aircraft, fft_size=1024, window_overlap=0.8)
stft.process()
stft.plot()

# %%
# ISO 1996-2
# ~~~~~~~~~~
# In this section, we calculate tonal audibility according to standard ISO 1996-2
# using the class :class:`~ansys.sound.core.psychoacoustics.TonalityISO1996_2`.
tonality_ISO1996_2 = TonalityISO1996_2(signal=signal_aircraft)
tonality_ISO1996_2.process()

# %%
# As you can notice, the tonal audibility over the whole signal is not relevant, as it equals zero
# even if strong tonal components are heard in this signal.

# Display values in the console
print(
    f"ISO 1996-2 tonality: \n"
    f"- tonal audibility: {tonality_ISO1996_2.get_tonal_audibility():.1f} dB\n"
    f"- tonal adjustment: {tonality_ISO1996_2.get_tonal_adjustment():.1f} dB\n"
    f"- computation details: {tonality_ISO1996_2.get_computation_details()}"
)

# %%
# Let us now calculate the tonal audibility over time, based on the standard ISO 1996-2.
# this is done usingthe class :class:`~ansys.sound.core.psychoacoustics.TonalityISO1996_2_OverTime`.
tonality_ISO1996_2_over_time = TonalityISO1996_2_OverTime(signal=signal_aircraft)
tonality_ISO1996_2_over_time.process()


# %%
# In this figure, you can notice that the tonal audibility and tonal adjustment indicates
# strong tonal components at the beginning and the end of the signal.
# Some tones are also present in the middle of the signal, but they are not
# perceived as strong as the ones at the beginning and the end.

# Display curves in a figure
tonality_ISO1996_2_over_time.plot()


# %%
# DIN 45681
# ~~~~~~~~~
# Let us now use the tonality standard DIN 45681 to analyze the same signal.
# This is done using the class :class:`~ansys.sound.core.psychoacoustics.TonalityDIN45681`.
tonality_DIN45681 = TonalityDIN45681(signal=signal_aircraft)
tonality_DIN45681.process()

# %%
# The DIN 45681 tonality returns similar results to the ISO 1996-2 tonality.
# Additionally, this standard provides the frequency of the most prominent tone at each time.
# This is done using the method
# :meth:`~ansys.sound.core.psychoacoustics.TonalityDIN45681.get_tone_frequency`.
# However, DIN 45681 overall tonal audibility seems more relevant than ISO 1996-2 one.

# Display values in the console
print(
    f"DIN 45681 tonality: \n"
    f"- mean audibility: {tonality_DIN45681.get_mean_difference():.1f} dB "
    f"(+/-{tonality_DIN45681.get_uncertainty():.1f} dB)\n"
    f"- tonal adjustment: {tonality_DIN45681.get_tonal_adjustment():.1f} dB\n"
)

# Display curves in a figure
tonality_DIN45681.plot()

# %%
# ISO/TS 20065
# ~~~~~~~~~~~~
# Let us now use the tonality standard ISO/TS 20065 to analyze the same signal.
# This is done using the class :class:`~ansys.sound.core.psychoacoustics.TonalityISOTS20065`.
tonality_ISOTS20065 = TonalityISOTS20065(signal=signal_aircraft)
tonality_ISOTS20065.process()

# %%
# As you can see from the results and the figures, ISO/TS 20065 is basically the same as DIN45681,
# but with some differences:
# - DIN 45681 outputs a Tonal adjustment Kt, meant to be used as a dBA penalty when the sound has
#   tonal components, whereas ISO/TS 20065 does not.
# - DIN 45681 can detect tones down to 90 Hz, whereas this limit was extended to 50 Hz in
#   ISO/TS 20065. This means that a very low frequency tone (that is, between 50 and 90 Hz)
#   can be detected by ISO/TS 20065, but will most likely be missed by DIN45681.
# - Minor differences in the calculation of the detected tones’ edge slopes.

# Display values in the console
print(
    f"ISO/TS 20065 tonality: \n"
    f"- mean audibility: {tonality_ISOTS20065.get_mean_audibility():.1f} dB "
    f"(+/-{tonality_ISOTS20065.get_uncertainty():.1f} dB)\n"
)

# Display curves in a figure
tonality_ISOTS20065.plot()


# %%
# Aurès
# ~~~~~
# Let us now calculate the tonality according to Aures, to analyze the same signal.
# This is done using the class :class:`~ansys.sound.core.psychoacoustics.TonalityAures`.
tonality_Aures = TonalityAures(signal=signal_aircraft)
tonality_Aures.process()

# %%
# As you can see from the calulation's output, Aurès tonality is really different from
# the tonality standards used previously. It is based on the notion of tonality unit (tu),
# defined on the fact that in this unit, a 1-kHz pure tone with a level of 60 dB SPL
# has a tonality of 1 tu.
#
# The figure represents, over time, the following quantities:
# - the Aurès tonality, which is the main value of interest,
# - the tonal component weighting, which is an intermediate value used to calculate the tonality,
# - the relative loudness weighting, another intermediate value used to calculate the tonality.

# Display values in the console
print(f"Aures tonality: \n" f"- average tonality : {tonality_Aures.get_tonality():.1f} tu\n")

# Display curves in a figure
tonality_Aures.plot()


# %%
# ECMA 418-2
# ~~~~~~~~~~
# Let us now use the tonality according to ECMA418-2 standard, to analyze the same signal.
# This is done using the class :class:`~ansys.sound.core.psychoacoustics.TonalityECMA418_2`.
tonality_ECMA418_2 = TonalityECMA418_2(signal=signal_aircraft)
tonality_ECMA418_2.process()

# %%
# As you can see from the results and the figures, ECMA418-2 tonality looks similar to
# Aurès tonality for the interpretation of the results.
#
# However, the tonality unit is different: ECMA-418-2 used the tuHMS (tonality unit –
# Hearing Model of Sottek). A value of 1 tuHMS corresponds to the tonality of a 1-kHz
# tone with a sound pressure of 40 dB SPL in quiet.
# For other signals, tonality values should vary between 0 tuHMS and a few tuHMS (sometimes
# even above 10 tuHMS) depending on the tonal contents of the signals.
# A value of 0 tuHMS indicates that no tonality could be detected (that is, no tonal content),
# while high values in tuHMS indicate prominent tonal contents.
#
# The figure shows the psychoacoustic tonality over time, as well as the frequency of
# the most prominent tone at each time.

# Display values in the console
print(
    f"Tonality ECMA 418-2: \n"
    f"- psychoacoustic tonality : {tonality_ECMA418_2.get_tonality():.1f} tuHMS\n"
)

# Display curves in a figure
tonality_ECMA418_2.plot()
