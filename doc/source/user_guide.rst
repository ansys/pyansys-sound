==========
User guide
==========

PyAnsys Sound lets you use the main features of `Ansys Sound`_ to perform
postprocessing and analysis of sounds and vibrations in Python. This library is based on
`Ansys DPF`_ and the DPF Sound plugin. It is a Python wrapper that implements classes on top
of DPF Sound operators.

Start a DPF server
------------------

You use the :func:`connect_to_or_start_server() <ansys.sound.core.server_helpers._connect_to_or_start_server.connect_to_or_start_server>`
method to start either a remote or local DPF server that is required to run PyAnsys Sound.

You can start the server with this code:

.. code:: python

    from ansys.sound.core.server_helpers import connect_to_or_start_server

    my_server = connect_to_or_start_server()

If the ``ANSRV_DPF_SOUND_PORT`` environment variable is set, PyAnsys Sound
attempts to connect to a server located in a Docker container. The default port is ``6780``.

If this environment variable is not specified, PyAnsys Sound tries to start a local server.

For more information on local and remote DPF servers, see `Install DPF Server`_ in the DPF-Core documentation.

Load a WAV signal
-----------------

Most of the processing done by PyAnsys Sound relies on temporal sound signals that are often saved as WAV files.

.. vale off

To load a WAV file , you must use the :class:`LoadWav <ansys.sound.core.signal_utilities.LoadWav>` class.
Once your signal is loaded, you can use all other PyAnsys Sound classes can be used and applied to this signal.

.. vale on
.. code:: python

    from ansys.sound.core.signal_utilities import LoadWav

    # Load a WAV file and plot it
    wav_loader = LoadWav(r"C:\path\to\my\wav\file.wav)
    wav_loader.process()

    # Obtain the output as a DPF fields container
    fc_wav_signal = wav_loader.get_output()

    # Plot the signal
    wav_loader.plot()

For descriptions of all PyAnsys Sound classes and helpers, see :doc:`api/index`. These classes
have four methods in common:

- ``process()``: Performs the operation that the class was made for. This method must be called explicitly
  every time an input parameter is changed.
- ``plot()``: Plots the output of the class. Depending on the nature of the output, the plot might be different.
- ``get_output()``: Returns the outputs as a DPF object (either a ``Field`` or a ``FieldsContainer`` object).
- ``get_output_as_nparray()``: Returns the outputs as a NumPy array.

A class might also have some additional methods.

For examples on how to use PyAnsys Sound classes and helpers, see :doc:`examples/index`.

.. _Ansys DPF: https://dpf.docs.pyansys.com/version/stable/
.. _Ansys Sound: https://www.ansys.com/sound
.. _Install DPF Server: https://dpf.docs.pyansys.com/version/stable/getting_started/dpf_server.html#install-dpf-server