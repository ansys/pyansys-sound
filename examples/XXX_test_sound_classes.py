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
# from ansys.sound.core.psychoacoustics.loudness_iso_532_1_stationary import (
#     LoudnessISO532_1_Stationary,
# )
from ansys.sound.core.psychoacoustics.tone_to_noise_ratio import ToneToNoiseRatio
from ansys.sound.core.server_helpers._connect_to_or_start_server import connect_to_or_start_server

# from ansys.sound.core.signal_utilities import CropSignal
from ansys.sound.core.signal_utilities import LoadWav

# from ansys.sound.core.sound_composer.sound_composer import SoundComposer
from ansys.sound.core.spectral_processing.power_spectral_density import PowerSpectralDensity
from ansys.sound.core.spectrogram_processing.stft import Stft

server = connect_to_or_start_server(use_license_context=True)

loader = LoadWav(
    "C:/ANSYSDev/PyDev/pyansys-sound/tests/data/Acceleration_stereo_nonUnitaryCalib.wav"
)
loader.process()
sound = loader.get_output()
print(sound)


print(sound.fs)
print(sound.duration)
print(sound.time)
print(sound[0].unit)
channels = sound.split_channels()
print(channels)

# loader = LoadWav("C:/ANSYSDev/PyDev/pyansys-sound/tests/data/flute.wav")
# loader.process()
# sound = loader.get_output()
# print(sound)
# # sound.plot()
# cropper = CropSignal(sound, start_time=0.0, end_time=1.0)
# cropper.process()
# cropped = cropper.get_output()
# # cropped.plot()
# loudness = LoudnessISO532_1_Stationary(signal=cropped)
# loudness.process()
# print(f"Loudness: {loudness.get_loudness_sone()}")

psder = PowerSpectralDensity(input_signal=sound)
psder.process()
psd = psder.get_output()
print(psd.delta_f)
print(psd.f_max)
print(psd.frequencies)
print(psd)

tnrer = ToneToNoiseRatio(psd=psd)
tnrer.process()
# tnrer.plot()

stfter = Stft(signal=channels[0], fft_size=1024, window_type="HANN", window_overlap=0.5)
stfter.process()
stft = stfter.get_output()
print(stft.time)
print(stft.frequencies)


# scer = SoundComposer(
#     "C:/ANSYSDev/PyDev/pyansys-sound/tests/data/"
#     "20250130_SoundComposerProjectForDpfSoundTesting_valid.scn"
# )
# bbn: FieldsContainer = scer.tracks[0].source.source_bbn
# bbn_support = bbn.get_support("control_parameter_1")
# bbn_support_ppts = bbn_support.available_field_supported_properties()
# bbn_control = bbn_support.field_support_by_property("kph")
# bbn2 = scer.tracks[3].source.source_bbn_two_parameters
# bbn2_field = bbn2.get_field({"control_parameter_1": 0, "control_parameter_2": 0})
# bbn2_support1 = bbn2.get_support("control_parameter_1")
# bbn2_support1_ppts = bbn2_support1.available_field_supported_properties()
# bbn2_control1 = bbn2_support1.field_support_by_property("celsius")
# bbn2_support2 = bbn2.get_support("control_parameter_2")
# bbn2_support2_ppts = bbn2_support2.available_field_supported_properties()
# bbn2_control2 = bbn2_support2.field_support_by_property("%")
# h = scer.tracks[4].source.source_harmonics
# h_support = h.get_support("control_parameter_1")
# h_support_ppts = h_support.available_field_supported_properties()
# h_control = h_support.field_support_by_property("RPM")
# h2 = scer.tracks[5].source.source_harmonics_two_parameters
# h2_support1 = h2.get_support("control_parameter_1")
# h2_support1_ppts = h2_support1.available_field_supported_properties()
# h2_control1 = h2_support1.field_support_by_property("RPM")
# h2_support2 = h2.get_support("control_parameter_2")
# h2_support2_ppts = h2_support2.available_field_supported_properties()
# h2_control2 = h2_support2.field_support_by_property("%")

# h2_2 = scer.tracks[6].source.source_harmonics_two_parameters
# h2_2_support1 = h2_2.get_support("control_parameter_1")
# h2_2_support1_ppts = h2_2_support1.available_field_supported_properties()
# h2_2_control1 = h2_2_support1.field_support_by_property("RPM")
# h2_2_support2 = h2_2.get_support("control_parameter_2")
# h2_2_support2_ppts = h2_2_support2.available_field_supported_properties()
# h2_2_control2 = h2_2_support2.field_support_by_property("%")
