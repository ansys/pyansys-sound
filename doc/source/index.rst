PyAnsys Sound
=============

.. toctree::
   :hidden:
   :maxdepth: 3

   getting_started
   user_guide
   api/index
   examples/index
   contribute


PyAnsys Sound let you use the main features of `Ansys Sound`_ to perform
the postprocessing and analysis of sounds and vibrations in Python. This library is based on
`Ansys DPF`_ and the DPF Sound plugin. It is a Python wrapper that implements classes on top
of DPF Sound operators.

These documentation sections provide information on installing and using PyAnsys Sound:

.. grid:: 1 1 2 2
    :gutter: 2

    .. grid-item-card:: Getting started :material-regular:`directions_run`
        :link: getting_started
        :link-type: doc

        Learn how to install PyAnsys Sound and its prerequisites in user mode.

    .. grid-item-card:: User guide :material-regular:`menu_book`
        :link: user_guide/index
        :link-type: doc

        Understand how to start a DPF server, load a WAV signal, and perform operations
        on the signal.

    .. grid-item-card:: API reference :material-regular:`bookmark`
        :link: api/index
        :link-type: doc

        Understand how to use Python to interact programmatically with PyAnsys Sound.

    .. grid-item-card:: Examples :material-regular:`play_arrow`
        :link: examples/index
        :link-type: doc

        Explore examples that show how to use PyAnsys Sound for various workflows.


    .. grid-item-card:: Contribute :material-regular:`group`
        :link: contribute
        :link-type: doc

        Learn how to contribute to the PyAnsys Sound codebase or documentation.


Key features
------------

These API reference pages describe some key features of PyAnsys Sound:

* :doc:`api/signal_utilities`: Tools to read/write WAV files in Ansys Sound SAS format and do basic editing of audio signals.
* :doc:`api/spectrogram_processing`: Time-frequency and time-representation conversion tools and time-frequency editing tools.
* :doc:`api/psychoacoustics`: Psychoacoustic indicators computation to measure perceived sound quality.
* :doc:`api/xtract`: Separation of a signal in several components, such as tonal, transient, and noise parts.

Not all features of Ansys Sound SAS are available in PyAnsys Sound. Features are regularly added in new versions.

.. _limitations:

.. Limitations
.. '''''''''''
.. -  ???

.. _Ansys DPF: https://dpf.docs.pyansys.com/version/stable/
.. _Ansys Sound: https://www.ansys.com/sound