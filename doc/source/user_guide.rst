==========
User Guide
==========

PyAnsys Sound enables the use of the main features of `Ansys Sound`_ to perform
post-processing and analysis of sounds and vibrations in Python. This library is based on
`Ansys DPF`_ and the DPF Sound plugin. It is a Python wrapper which implements classes on top
of DPF Sound operators.

For information demonstrating the behavior and usage of PyDPF Sound,
see the :doc:`examples/index` section.

Start a DPF Server
------------------

The :func:`connect_to_or_start_server() <ansys.sound.core.server_helpers._connect_to_or_start_server.connect_to_or_start_server>` method
can be used to start either a remote or local DPF server that is required to run the PyAnsys Sound library.

You can start the server with the following code:

.. code:: python

    from ansys.sound.core.server_helpers import connect_to_or_start_server

    my_server = connect_to_or_start_server()

If the environment variable ``ANSRV_DPF_SOUND_PORT`` is set (default value should be ``6780``), PyAnsys Sound
will attempt to connect to a server located in a Docker container.

If the environmeent variable is **not** specified, PyAnsys Sound will try to start a local server.

More information about local and remote DPF Servers: `Getting started with DPF servers`_.

Load a Wav signal
-----------------

Most of the processing done by PyAnsys Sound relies on temporal sound signals that are often saved as ``.wav`` files.

In order to load a ``.wav`` , one must use the :class:`LoadWav <ansys.sound.core.signal_utilities.LoadWav>`

.. code:: python

    from ansys.sound.core.signal_utilities import LoadWav

    # Loadind a wav file and plotting it.
    wav_loader = LoadWav(r"C:\path\to\my\wav\file.wav)
    wav_loader.process()

    # Obtaining the output as a DPF Fields Container
    fc_wav_signal = wav_loader.get_output()

    # Plotting the signal
    wav_loader.plot()

Once your signal is loaded, all other PyAnsys Sound classes can be used and applied to this signal.

PyAnsys Sound API
-----------------

All the different classes and helpers are documented in the :doc:`api/index`.

All classes have four methods in common:

#. ``process()`` performs the operation for which the class is made for. Must be called explicitly every time an input parameter is changed.
#. ``plot()`` plots the output of the class, depending on the nature of the output, the plot will be different.
#. ``get_output()`` returns the output(s) as a DPF object (either a ``Field`` or a ``FieldsContainer``).
#. ``get_output_as_nparray()`` returns the output(s) as a numpy array.

Some additional methods might be available for a given class.

We strongly encourage to check the :doc:`examples/index` in order to start using PyAnsys Sound.

.. _Ansys DPF: https://dpf.docs.pyansys.com/version/stable/
.. _Ansys Sound: https://www.ansys.com/sound
.. _Getting started with DPF servers: https://dpf.docs.pyansys.com/version/stable/getting_started/index.html#install-dpf-server