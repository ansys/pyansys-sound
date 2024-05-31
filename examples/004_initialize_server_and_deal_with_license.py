"""
.. _initialize_server_and_deal_with_license:

Initialize PyAnsys Sound and ensure the check out of the license
-----------------------------------------------------------------

This example shows how to initialize DPF core and load DPF Sound, and how to check out the
required Ansys license increment avrxp_snd_level1 only once.
It also shows how to connect to the DPF server, verify where it is located and get other useful
information.

This example demonstrates the use of the LicenseContextManager, a mechanism that allows to check
out the license only once for the duration of the session
and greatly improves performance. It shows and compares the execution time of a simple DPF Sound
operator when using a LicenseContextManager
and when not using it.

Prerequisite: ensure that you have installed DPF core and DPF Sound, following the instructions
here:
- if you have installed latest Ansys release:
https://dpf.docs.pyansys.com/version/stable/getting_started/install.html#installation
- if you use DPF standalone:
https://dpf.docs.pyansys.com/version/stable/getting_started/install.html

"""

# %%
# Initial set up
# ~~~~~~~~~~~~~~~
# Here are the required python imports for this example

import datetime

import ansys.dpf.core as dpf

from ansys.dpf.sound.examples_helpers import get_absolute_path_for_flute_wav
from ansys.dpf.sound.server_helpers import connect_to_or_start_server
from ansys.dpf.sound.signal_utilities import LoadWav

# sphinx_gallery_thumbnail_path = '_image/example004_thumbnail.png'

# %%
# Use a DPF server without a LicenseContextManager
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Initialize DPF server without using a LicenseContextManager
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
# Display the information about the server you are currently using
print(f"Server information: {my_server.info}")

# %%
# Execute a same simple PyDPF Sound operator (LoadWav) several times in a row,
# and measure the execution time

path_flute_wav = get_absolute_path_for_flute_wav()

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
# Disconnect/shutdown the server and release the license increment
print("Disconnecting from the server and releasing the license increment")
my_server = None

# %%
# Use a DPF server with a LicenseContextManager
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# New connection to a remote server or start of a local server,
# now using the LicenseContextManager.
#
# Note: the LicenseContextManager is a mechanism that checks out a license increment when entering
# the context and releases it when exiting the context.

# Connect to a remote server or start a local server, using a LicenseContextManager
print("Connecting to the server using a LicenseContextManager")
my_server = connect_to_or_start_server(use_license_context=True)

# Execute the same piece of code as prviously, and measure the new execution time
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
# This is because - when not using a LicenseContactManage - the license is checked out
# each time you use a DPF Sound operator
