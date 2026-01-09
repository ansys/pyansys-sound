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

"""Test if a DPF server with DPF Sound plugin is available."""

from ansys.dpf.core import Operator

from ansys.sound.core.server_helpers import connect_to_or_start_server


def validate_dpf_sound_connection(port=None) -> None:
    """Validate DPF server and DPF Sound plugin availability.

    Parameters
    ----------
    port : int, default: None
        Port on which the DPF server is listening.

    Examples
    --------
    Validate that a global DPF server (whether local or remote) is available and has the DPF Sound
    plugin.

    >>> from ansys.sound.core.server_helpers import validate_dpf_sound_connection
    >>> validate_dpf_sound_connection()

    Validate that a remote DPF server on a specific port is available and has the DPF Sound plugin.

    >>> from ansys.sound.core.server_helpers import validate_dpf_sound_connection
    >>> validate_dpf_sound_connection(port=6780)
    """
    connect_to_or_start_server(port=port)
    Operator("load_wav_sas")
    print("DPF Server with DPF Sound plugin is available and running.")
