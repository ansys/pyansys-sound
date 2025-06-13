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

"""
.. _initialize_server_and_deal_with_license:

Initialize PyAnsys Sound and check out the license
--------------------------------------------------

This example shows how to initialize PyDPF-Core, load DPF Sound, and check out the
required Ansys license (``increment avrxp_snd_level1``) only once. It also shows
how to connect to the DPF server, verify where it is located, and get other useful
information.

This example also demonstrates the use of the LicenseContextManager, a mechanism that lets you
check out the license only once for the duration of the session, which greatly improves performance.
It shows the execution time of a simple DPF Sound operator when you do not use the
LicenseContextManager versus when you do use it.

**Prerequisites**

Ensure that you have installed PyDPF-Core and DPF Sound according to procedures in
the PyDPF-Core documentation:

- If you have installed the latest Ansys release, see `Install using pip
  <https://dpf.docs.pyansys.com/version/stable/getting_started/install.html#installation>`_.
- If you want to use the DPF standalone version, see `Install DPF Server
  <https://dpf.docs.pyansys.com/version/stable/getting_started/dpf_server.html#dpf-server>`_.


"""

# %%
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Perform the required imports:

# Load Ansys and other libraries.
import datetime

from ansys.sound.core.examples_helpers import download_flute_wav
from ansys.sound.core.server_helpers import connect_to_or_start_server
from ansys.sound.core.signal_utilities import LoadWav

# sphinx_gallery_start_ignore
# sphinx_gallery_thumbnail_path = '_static/_image/example001_thumbnail.png'
# sphinx_gallery_end_ignore

# %%
# Use a DPF server without a LicenseContextManager
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Initialize a DPF server without using a LicenseContextManager.
#
# **Note**: When ``use_license_context=False``, the license is checked out each time
# you use a DPF Sound operator.


# Connect to a remote server or start a local server without using a LicenseContextManager
print("Connecting to the server without using a LicenseContextManager")
my_server, my_license_context = connect_to_or_start_server(use_license_context=False)

# Check if you are using a local or remote server
is_server_local = not my_server.has_client()
print(f"Local server: {is_server_local}")

# If using a local server, display the path to the server
if is_server_local == True:
    print(f"Local server path (server variable): {my_server.ansys_path}")

# %%
# Display information about the server that you are using.
print(f"Server information: {my_server.info}")

# %%
# Execute the PyAnsys Sound ``LoadWav`` operator several times in a row
# and measure the execution time.

path_flute_wav = download_flute_wav(server=my_server)

for i in range(5):
    now = datetime.datetime.now()
    wav_loader = LoadWav(path_flute_wav)
    wav_loader.process()
    fc_signal = wav_loader.get_output()
    later = datetime.datetime.now()
    execution_time = later - now
    print(
        f"Elapsed time (loop {i+1}): "
        f"{execution_time.seconds + execution_time.microseconds/1e6}"
        f" seconds"
    )

# %%
# Disconnect (shut down) the server.
print("Disconnecting from the server.")
my_server = None

# %%
# Use a DPF server with a LicenseContextManager
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Initialize a DPF server using a LicenseContextManager and execute the same code as run previously.
#
# **Note**: The LicenseContextManager is a mechanism that checks out a license increment
# when entering the context and releases it when exiting the context.

# Connect to a remote server or start a local server using a LicenseContextManager
print("Connecting to the server using a LicenseContextManager")
my_server, my_license_context = connect_to_or_start_server(use_license_context=True)

# Execute the same and measure the execution time
path_flute_wav = download_flute_wav(server=my_server)

for i in range(5):
    now = datetime.datetime.now()
    wav_loader = LoadWav(path_flute_wav)
    wav_loader.process()
    fc_signal = wav_loader.get_output()
    later = datetime.datetime.now()
    execution_time = later - now
    print(
        f"Elapsed time (loop {i+1}): "
        f"{execution_time.seconds + execution_time.microseconds / 1e6}"
        f" seconds"
    )

# %%
# You can see that the execution time is much faster when you use a LicenseContextManager.
# This is because when a LicenseContactManager is not used, the license is checked out
# each time you use a DPF Sound operator.

# %%
# You can release the license increment by deleting the LicenseContextManager object.
print("Releasing the license increment by deleting the LicenseContextManager object.")
my_license_context = None

# %%
# Now the LicenseContextManager has been deleted, any call to a PyAnsys Sound function will
# again take the time to check out the license increment. Let us call the same function as before:
now = datetime.datetime.now()
wav_loader = LoadWav(path_flute_wav)
wav_loader.process()
fc_signal = wav_loader.get_output()
later = datetime.datetime.now()
execution_time = later - now
print(
    f"Elapsed time: " f"{execution_time.seconds + execution_time.microseconds / 1e6}" f" seconds",
)

# %%
# Disconnect (shut down) the server and release the license increment.
print("Disconnecting from the server and releasing the license increment.")
my_server = None
