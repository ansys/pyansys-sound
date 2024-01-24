"""Test if DPF Sound is available."""

from ansys.dpf.core import Operator


def validate_dpf_sound() -> None:
    """Validate that DPF Sound is available."""
    Operator("load_wav_sas")
    print("DPF Sound is available and running.")
