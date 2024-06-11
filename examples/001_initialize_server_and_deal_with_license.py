# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
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

Initialize PyAnsys Sound and ensure the check out of the license
-----------------------------------------------------------------

This example shows how to initialize DPF core and load DPF Sound, and how to check out the
required Ansys license increment avrxp_snd_level1 only once.
It also shows how to connect to the DPF server, verify where it is located and get other useful
information.

This example demonstrates the use of the LicenseContextManager, a mechanism that allows you to
check out the license only once for the duration of the session and greatly improves performance.
It shows and compares the execution time of a simple DPF Sound operator when using a
LicenseContextManager or not.

Prerequisite: ensure that you have installed DPF core and DPF Sound, following the instructions
here:

- if you have installed the latest Ansys release: see `how to install PyDPF core \
<https://dpf.docs.pyansys.com/version/stable/getting_started/install.html#installation>`_
- if you want to use the DPF standalone version: see `how to install DPF server \
<https://dpf.docs.pyansys.com/version/stable/getting_started/dpf_server.html#dpf-server>`_

"""

# %%
# Initial set up
# ~~~~~~~~~~~~~~~
# Here are the required python imports for this example:

# Load Ansys & other libraries.
import datetime

import ansys.dpf.core as dpf

from ansys.sound.core.examples_helpers import download_flute_wav
from ansys.sound.core.server_helpers import connect_to_or_start_server
from ansys.sound.core.signal_utilities import LoadWav

# sphinx_gallery_start_ignore
# sphinx_gallery_thumbnail_path = '_static/_image/example004_thumbnail.png'
# sphinx_gallery_end_ignore

# %%
# Use a DPF server without a LicenseContextManager
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Initialize DPF server without using a LicenseContextManager.
#
# Note: when use_license_context=False, the license is checked out each time
# you use a DPF Sound operator.


# Connect to a remote server or start a local server, without using a LicenseContextManager
print("Connecting to the server without using a LicenseContextManager")
my_server = connect_to_or_start_server(use_license_context=False)

# check if you are using a local or remote server
has_local_server = dpf.server.has_local_server()
print(f"Local server: {has_local_server}")

# if using a local server, display the path to the server
if has_local_server == True:
    print(f"Local server path (server variable): {my_server.ansys_path}")

# %%
# Display the information about the server you are currently using.
print(f"Server information: {my_server.info}")

# %%
# Execute the same simple PyDPF Sound operator (LoadWav) several times in a row,
# and measure the execution time.

path_flute_wav = download_flute_wav()

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
# Disconnect/shutdown the server and release the license increment.
print("Disconnecting from the server and releasing the license increment")
my_server = None

# %%
# Use a DPF server with a LicenseContextManager
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# New connection to a remote server or start a local server,
# now using the LicenseContextManager.
#
# Note: the LicenseContextManager is a mechanism that checks out a license increment when entering
# the context and releases it when exiting the context.

# Connect to a remote server or start a local server, using a LicenseContextManager
print("Connecting to the server using a LicenseContextManager")
my_server = connect_to_or_start_server(use_license_context=True)

# Execute the same piece of code as previously, and measure the new execution time
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
# Conclusion
# ~~~~~~~~~~~
# You can notice that the execution time is much faster when you use a LicenseContextManager
# (second case), compared to not using it (first case).
# This is because, when not using a LicenseContactManager, the license is checked out
# each time you use a DPF Sound operator.
