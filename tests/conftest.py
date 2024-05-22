import os

from ansys.dpf.core import (
    AvailableServerContexts,
    LicenseContextManager,
    connect_to_server,
    load_library,
)
import pytest

CONTAINER_SERVER_PORT = 6780
STR_DPF_SOUND = "dpf_sound.dll"
STR_DPF_SOUND_DLL = "dpf_sound.dll"


def pytest_configure():
    pytest.data_path_flute_in_container = "C:\\data\\flute.wav"
    pytest.data_path_white_noise_in_container = "C:\\data\\white_noise.wav"
    pytest.data_path_accel_with_rpm_in_container = "C:\\data\\accel_with_rpm.wav"


@pytest.fixture(scope="session")
def dpf_sound_test_server():
    port_in_env = os.environ.get("ANSRV_DPF_SOUND_PORT")
    if port_in_env is not None:
        port = int(port_in_env)
    else:
        port = CONTAINER_SERVER_PORT

    # Connecting to server
    server = connect_to_server(port=port, context=AvailableServerContexts.premium)

    # Initializing licence context manager, will make tests faster by avoiding licenses checkouts
    licence_context_manager = LicenseContextManager(increment_name="avrxp_snd_level1")

    # Loading DPF Sound
    load_library(STR_DPF_SOUND_DLL, STR_DPF_SOUND)
    yield server
