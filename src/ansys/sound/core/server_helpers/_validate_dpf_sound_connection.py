"""Test if DPF Sound is available."""

import os

from ansys.dpf.core import Operator, connect_to_server, load_library

DEFAULT_PORT: int = int(os.environ.get("ANSRV_DPF_SOUND_PORT", 6780))


def validate_dpf_sound_connection(port=None) -> None:
    """Validate that DPF Sound is available."""
    port = port if port is not None else DEFAULT_PORT
    connect_to_server(port=port)
    load_library("dpf_sound.dll", "dpf_sound")
    Operator("load_wav_sas")
    print("DPF Sound is available and running.")
