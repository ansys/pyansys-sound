"""Helpers to connect to or start a DPF server with the DPF Sound plugin."""

import os
from typing import Any, Optional, Union

from ansys.dpf.core import connect_to_server, load_library, start_local_server


def connect_to_or_start_server(
    port: Optional[int] = None, ip: Optional[str] = None, ansys_path: Optional[str] = None
) -> Any:
    r"""Connect to or start a DPF server with the DPF Sound plugin loaded.

    .. note::

        If a port or IP address is set, this method tries to connect to the server specified
        and the ``ansys_path`` parameter is ignored. If no parameters are set, a local server
        from the latest available Ansys installation is started.

    Parameters
    ----------
    port :
        Port that the DPF server is listening on.
    ip :
        IP address for the DPF server.
    ansys_path :
        Root path for the Ansys installation. For example, ``C:\\Program Files\\ANSYS Inc\\v232``.
        This parameter is ignored if either the port or IP address is set.

    Returns
    -------
    :
        DPF server.
    """
    # Collect the port to connect to the server
    port_in_env = os.environ.get("ANSRV_DPF_SOUND_PORT")
    if port_in_env is not None:
        port = int(port_in_env)

    connect_kwargs: dict[str, Union[int, str]] = {}
    if port is not None:
        connect_kwargs["port"] = port
    if ip is not None:
        connect_kwargs["ip"] = ip

    # Decide whether we start a local server or a remote server
    full_path_dll = ""
    if len(list(connect_kwargs.keys())) > 0:
        server = connect_to_server(
            **connect_kwargs,
        )
    else:  # pragma: no cover
        server = start_local_server(
            ansys_path=ansys_path,
        )

        full_path_dll = os.path.join(ansys_path, "Acoustics\\SAS\\ads\\")

    required_version = "8.0"
    server.check_version(
        required_version,
        f"The DPF Sound plugin requires DPF Server version {required_version} "
        f"(Ansys 2024 R2) or later. Your version is currently {server.version}.",
    )

    load_library(full_path_dll + "dpf_sound.dll", "dpf_sound")
    return server
