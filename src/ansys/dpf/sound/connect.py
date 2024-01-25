"""Test if DPF Sound is available."""

from ansys.dpf.core import Operator, connect_to_server, load_library
import os
from ansys.dpf.sound.connect import validate_dpf_sound


DEFAULT_PORT: int = int(os.environ.get("ANSRV_DPF_SOUND_PORT", 678))


def validate_dpf_sound(port=None) -> None:
    """Validate that DPF Sound is available."""
    port = port if port is not None else DEFAULT_PORT
    server = connect_to_server(port=port)
    load_library("Acoustics\\SAS\\ads\\dpf_sound.dll", server=server)
    Operator("load_wav_sas", server=server)
    print("DPF Sound is available and running.")