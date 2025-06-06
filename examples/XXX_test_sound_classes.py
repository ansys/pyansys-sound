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

from ansys.sound.core.psychoacoustics.loudness_iso_532_1_stationary import (
    LoudnessISO532_1_Stationary,
)
from ansys.sound.core.server_helpers._connect_to_or_start_server import connect_to_or_start_server
from ansys.sound.core.signal_utilities import CropSignal, LoadWav

server = connect_to_or_start_server(use_license_context=True)

loader = LoadWav("C:/ANSYSDev/PyDev/pyansys-sound/tests/data/Acceleration_stereo_84dBSPL.wav")
loader.process()
sound = loader.get_output()
print(sound)
loader = LoadWav("C:/ANSYSDev/PyDev/pyansys-sound/tests/data/flute.wav")
loader.process()
sound = loader.get_output()
print(sound)
cropper = CropSignal(sound, start_time=0.0, end_time=1.0)
cropper.process()
cropped = cropper.get_output()
loudness = LoudnessISO532_1_Stationary(signal=cropped)
loudness.process()
print(f"Loudness: {loudness.get_loudness_sone()}")
loader = LoadWav("C:/ANSYSDev/PyDev/pyansys-sound/tests/data/Acceleration_stereo_84dBSPL.wav")
loader.process()
sound = loader.get_output()
print(sound)
channels = sound.split_channels()
print(channels)
