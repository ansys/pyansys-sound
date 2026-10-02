# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

"""Helpers to manage file upload and download to/from a remote DPF server."""

from contextlib import contextmanager
import os

from ansys.dpf.core import download_file, make_tmp_dir_server
from ansys.dpf.core import server as server_module
from ansys.dpf.core import upload_file_in_tmp_folder


@contextmanager
def server_upload(client_path, server=None):
    """Manage file upload to server in case of a remote server.

    In case of a remote server, this context manager uploads the file to the server and yields the
    upload path on entering the context. No server-side cleanup is performed on exiting the context,
    this is managed by the server itself on shutdown. In case of a local server, no upload is
    performed, and the context manager simply yields the client path.

    Parameters
    ----------
    client_path : str
        Source path on the client host where the file to upload is located.
    server : GrpcServer | InProcessServer | None, default: None
        Server to which the file is uploaded. If None, the global server is used.

    Examples
    --------
    >>> from ansys.sound.core.server_helpers._server_io import server_upload
    >>> from ansys.sound.core.signal_utilities import LoadWav
    >>> with server_upload(local_wav_path, server=my_server) as server_path:
    >>>     loader = LoadWav(path_to_wav=server_path)
    >>>     loader.process()
    >>>     my_signal = loader.get_output()
    """
    if server is None:
        server = server_module.get_or_create_server(None)

    if server.local_server:
        # Local server, no upload needed.
        yield client_path

    else:
        # Remote server, the file needs to be uploaded to the server for the DPF operator to use it.
        yield upload_file_in_tmp_folder(file_path=client_path, server=server)

        # No server-side cleanup done on context manager exit. The uploaded files are automatically
        # cleaned up on server shutdown.


@contextmanager
def server_download(client_path, server=None):
    """Manage file download from server in case of a remote server.

    In case of a remote server, this context manager yields the server path in the server temporary
    directory where the file shall be created. On context exit, the file is downloaded back to the
    client host. No server-side cleanup is performed, as it is managed by the server itself on
    shutdown. In case of a local server, the context manager simply yields the client path, and no
    download is performed on context exit.

    Parameters
    ----------
    client_path : str
        Target path on the client host where the file is downloaded from the server after saving.
    server : GrpcServer | InProcessServer | None, default: None
        Server from which the file is downloaded after saving. If None, the global server is used.

    Examples
    --------
    >>> from ansys.sound.core.server_helpers._server_io import server_download
    >>> from ansys.sound.core.signal_utilities import WriteWav
    >>> with server_download(local_wav_path, server=my_server) as server_path:
    >>>     writer = WriteWav(signal=my_signal, path_to_write=server_path)
    >>>     writer.process()
    """
    if server is None:
        server = server_module.get_or_create_server(None)

    if server.local_server:
        # Local server, we use the client path directly.
        yield client_path

    else:
        # Remote server, yield the server path in the server temporary directory where the file
        # shall be created before being downloaded back to the client host.
        server_path = os.path.join(make_tmp_dir_server(server), os.path.basename(client_path))
        yield server_path

        # On manager exit, download the file back to the client host.
        client_dir = os.path.dirname(os.path.abspath(client_path))
        os.makedirs(client_dir, exist_ok=True)
        download_file(server_path, client_path, server)

        # No server-side file cleanup done on context manager exit. The saved files are
        # automatically cleaned up on server shutdown.
