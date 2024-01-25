"""Test if DPF Sound is available."""

import ansys.dpf.core as dpf
from ansys.dpf.core import Operator


def validate_dpf_sound() -> None:
    """Validate that DPF Sound is available."""
    dpf.start_local_server(ansys_path="C:\\ansys\\dpf\\server_2024_2_pre0\\")
    dpf.load_library("C:\\ansys\\dpf\\server_2024_2_pre0\\Acoustics\\SAS\\ads\\dpf_sound.dll")
    Operator("load_wav_sas")
    print("DPF Sound is available and running.")
