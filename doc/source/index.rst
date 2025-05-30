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


PyAnsys Sound lets you use the main features of `Ansys Sound`_ to perform
the postprocessing and analysis of sounds and vibrations in Python. This library is based on
`PyDPF-Core`_ and the DPF Sound plugin. It is a Python wrapper that implements classes on top
of DPF Sound operators.

These documentation sections provide information on installing and using PyAnsys Sound:

.. grid:: 1 1 2 2
    :gutter: 2

    .. grid-item-card:: Getting started :material-regular:`directions_run`
        :link: getting_started
        :link-type: doc

        Learn how to install PyAnsys Sound and its prerequisites in user mode.

    .. grid-item-card:: User guide :material-regular:`menu_book`
        :link: user_guide
        :link-type: doc

        Learn how to start a DPF server, load a signal from a WAV files, and perform operations
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

The following API reference pages describe some key features of PyAnsys Sound:

* :doc:`api/signal_utilities`: Tools to read and write WAV files in the format used by Ansys Sound Analysis
  and Specification (SAS) and tools to perform basic editing of audio signals.
* :doc:`api/signal_processing`: Tools to perform time-domain signal processing, such as filtering.
* :doc:`api/spectral_processing`: Tools to perform frequency-domain signal processing, such as
  calculating a power spectral density (PSD).
* :doc:`api/spectrogram_processing`: Spectrogram calculation and editing tools.
* :doc:`api/psychoacoustics`: Psychoacoustic indicators computation to measure perceived sound quality.
* :doc:`api/xtract`: Separation of a signal into several components, such as tonal, transient, and noise parts.
* :doc:`api/sound_composer`: Generation of sounds from sources defined in the time domain or the frequency domain.
  Creation of complex sounds by mixing several tracks (each track contains a specific user-defined source).
* :doc:`api/standard_levels`: Calculation of standard levels for time-domain signals.
* :doc:`api/sound_power`: Calculation of sound power from time-domain signals.


Not all features of Ansys SAS are available in PyAnsys Sound. Features are regularly
added in new versions.

.. _limitations:

.. Limitations
.. '''''''''''
.. -  ???

.. LINKS AND REFERENCES
.. _Ansys Sound: https://www.ansys.com/sound
.. _PyDPF-Core: https://dpf.docs.pyansys.com/version/stable/
