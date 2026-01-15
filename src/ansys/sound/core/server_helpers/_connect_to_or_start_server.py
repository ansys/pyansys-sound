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

"""Helpers to connect to or start a DPF server with the DPF Sound plugin."""

import os
from typing import Optional, Union

from ansys.dpf.core import (
    LicenseContextManager,
    connect_to_server,
    load_library,
    server_types,
    start_local_server,
)


def connect_to_or_start_server(
    port: Optional[int] = None,
    ip: Optional[str] = None,
    ansys_path: Optional[str] = None,
    use_license_context: Optional[bool] = False,
    license_increment_name: Optional[str] = "avrxp_snd_level1",
) -> tuple[server_types.InProcessServer | server_types.GrpcServer, LicenseContextManager]:
    """Connect to or start a DPF server with the DPF Sound plugin loaded.

    Parameters
    ----------
    port : int, default: None
        Port that the DPF server is listening to.
    ip : str, default: None
        IP address for the DPF server.
    ansys_path : str, default: None
        Root path for the Ansys installation. For example, `"C:/Program Files/ANSYS Inc/v242"`.
        This parameter is ignored if either the port or IP address is set.
    use_license_context : bool, default: False
        Whether to check out the DPF Sound license increment before using PyAnsys Sound (see
        parameter ``license_increment_name``). If set to :obj:`True`, the function returns a
        :class:`LicenseContextManager <ansys.dpf.core.server_context.LicenseContextManager>` object
        (:obj:`None` otherwise) in addition to the server object.

        This improves performance if you are doing multiple calls to DPF Sound operators, as it
        allows a single check out of the license increment, rather than requiring a check out for
        each operator call. The license is checked back in (that is, released) when the
        :class:`LicenseContextManager <ansys.dpf.core.server_context.LicenseContextManager>` object
        is deleted.

        This parameter can also be used to force check out before running a script when only few
        DPF Sound license increments are available.
    license_increment_name : str, default: "avrxp_snd_level1"
        Name of the license increment to check out. Only taken into account if
        ``use_license_context`` is :obj:`True`. The default value is `"avrxp_snd_level1"`, which
        corresponds to the license required by Ansys Sound Pro.

    Returns
    -------
    InProcessServer | GrpcServer
        Server object started or connected to.
    LicenseContextManager
        Licensing context object. Retains the licence increment until the object is deleted.
        :obj:`None` if ``use_license_context`` is set to :obj:`False`.

    Notes
    -----
    If a port or IP address is passed in arguments, or if the environment variable
    ``ANSRV_DPF_SOUND_PORT`` is defined with a port number, this function attempts to connect to a
    remote server at the specified port and/or IP address. Otherwise, the function attempts to
    start a local server, located at the path passed in ``ansys_path`` if specified, or at the path
    specified in the environment variable ``ANSYS_DPF_PATH`` if it is defined. Finally, if none of
    these arguments and environment variables is defined, the function attempts to start a local
    server from the latest Ansys installation folder. Note that, in any case, arguments are
    prioritized over environment variables.

    Examples
    --------
    Start a local DPF server with DPF Sound plugin from the latest Ansys installation folder.

    >>> from ansys.sound.core.server_helpers import connect_to_or_start_server
    >>> server, lic_context = connect_to_or_start_server(
    ...     ansys_path="C:/Program Files/ANSYS Inc/v261",
    ... )

    Connect to a remote DPF server with DPF Sound plugin, through a given communication port.

    >>> from ansys.sound.core.server_helpers import connect_to_or_start_server
    >>> server, lic_context = connect_to_or_start_server(port=6780)

    .. seealso::
        :ref:`initialize_server_and_deal_with_license`
            Example demonstrating how to connect to or start a DPF server with the DPF Sound plugin.
    """
    # Collect the port to connect to the server (if unspecified in arguments)
    if port is None:
        port_in_env = os.environ.get("ANSRV_DPF_SOUND_PORT")
        if port_in_env is not None:
            port = int(port_in_env)

    connect_kwargs: dict[str, Union[int, str]] = {}
    if port is not None:
        connect_kwargs["port"] = port
    if ip is not None:  # pragma: no cover
        connect_kwargs["ip"] = ip

    full_path_dll = ""
    if len(list(connect_kwargs.keys())) > 0:
        # Remote server => connect using gRPC
        server = connect_to_server(
            **connect_kwargs,
            as_global=True,
        )
    else:  # pragma: no cover
        # Local server => start a local server
        server = start_local_server(ansys_path=ansys_path, as_global=True)
        full_path_dll = os.path.join(server.ansys_path, "Acoustics\\SAS\\ads\\")

    required_version = "8.0"
    server.check_version(
        required_version,
        f"The DPF Sound plugin requires DPF Server version {required_version} "
        f"(Ansys 2024 R2) or later. Your version is currently {server.version}.",
    )

    load_library(full_path_dll + "dpf_sound.dll", "dpf_sound", server=server)

    # if required, check out the DPF Sound license once and for all for this session
    lic_context = None
    if use_license_context == True:
        lic_context = LicenseContextManager(license_increment_name, server=server)

    return server, lic_context
