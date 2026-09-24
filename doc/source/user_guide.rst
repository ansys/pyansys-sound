.. _ref_user_guide:

==========
User guide
==========

This section explains the basics of how to use PyAnsys Sound. Specifically, it shows how to start
PyAnsys Sound, run a basic example consisting of loading a signal from a WAV file, and it explains
the common methods available in all PyAnsys Sound classes.

.. _start_pyansys_sound:

Start PyAnsys Sound
-------------------

Use the :func:`~.server_helpers._connect_to_or_start_server.connect_to_or_start_server()`
function to either connect to a remote DPF Server or start a local DPF Server, which is required to
run PyAnsys Sound.

.. code:: python

    from ansys.sound.core.server_helpers import connect_to_or_start_server

    my_server = connect_to_or_start_server()

If the ``ANSRV_DPF_SOUND_PORT`` environment variable is set, PyAnsys Sound
attempts to connect to a remote server (in a Docker container, for example). The default port is
``6780``. You can also explicitly specify the port by passing the port number to the
:func:`~.server_helpers._connect_to_or_start_server.connect_to_or_start_server()`
function.

.. code:: python

    from ansys.sound.core.server_helpers import connect_to_or_start_server

    my_server = connect_to_or_start_server(port=6780)

Otherwise, PyAnsys Sound attempts to locate and start a local server, following the priority order
specified in `Manage multiple DPF Server installations`_.

For more information on local and remote DPF servers, see `DPF Server`_ in the `PyDPF-Core`_
documentation.

Basic PyAnsys Sound usage example
---------------------------------

In this basic example, you can load and plot a signal contained in a WAV file. Time-domain signals
are the primary type of data used in PyAnsys Sound. These signals are typically stored in WAV files.
PyAnsys Sound provides WAV file loading capabilities through the
:class:`~.signal_utilities.LoadWav` class. Once the signal is loaded, you can use other PyAnsys
Sound features to analyze and/or transform it.

.. code:: python

    from ansys.sound.core.signal_utilities import LoadWav

    # Load a WAV file.
    wav_loader = LoadWav(r"C:\path\to\my\wav\file.wav)
    wav_loader.process()

    # Get the signal data.
    signal = wav_loader.get_output()

    # Plot the signal.
    wav_loader.plot()

For descriptions of all available PyAnsys Sound features, see :doc:`api/index`. Most features are
implemented as classes that all share these four basic methods:

- ``process()``: Performs the operation intended for this class. This method must be explicitly
  called every time an input parameter is changed.
- ``plot()``: Plots the output of the class. Depending on the nature of the output, the plot might
  be different.
- ``get_output()``: Gets the outputs as DPF objects (:class:`~ansys.dpf.core.field.Field` or
  :class:`~ansys.dpf.core.fields_container.FieldsContainer`, for example).
- ``get_output_as_nparray()``: Gets the output as `NumPy arrays`_.

Usually, PyAnsys Sound classes also have additional class-specific methods.

You can also find relevant PyAnsys Sound workflow examples in :doc:`examples/index`.

.. note::
    Files that are meant to be used as inputs to PyAnsys Sound (WAV files for example) need to be
    made available to the DPF Server with DPF Sound plugin (see :ref:`start_pyansys_sound`). If a
    `local` server is started with
    :func:`~.server_helpers._connect_to_or_start_server.connect_to_or_start_server()`, the files are
    already available to the server, since it runs on the same system as the Python process.
    However, if a _remote_ server is connected to, an extra step is required to make the files
    available to it. This step is automatically done when calling the download functions from module
    :mod:`ansys.sound.core.examples_helpers.download`. But if you wish to use your own files, you
    must upload them to the DPF Server with the dedicated `PyDPF Core upload function`_.

.. LINKS AND REFERENCES
.. _PyDPF-Core: https://dpf.docs.pyansys.com/version/stable/
.. _DPF Server: https://dpf.docs.pyansys.com/version/stable/getting_started/dpf_server.html#
.. _Manage multiple DPF Server installations: https://dpf.docs.pyansys.com/version/stable/getting_started/dpf_server.html#manage-multiple-dpf-server-installations
.. _NumPy arrays: https://numpy.org/doc/stable/reference/generated/numpy.array.html
.. _PyDPF Core upload function: https://dpf.docs.pyansys.com/version/stable/api/ansys/dpf/core/core/index.html#core.upload_file_in_tmp_folder