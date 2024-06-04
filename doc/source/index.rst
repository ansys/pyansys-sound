PyAnsys Sound
=============

.. toctree::
   :hidden:
   :maxdepth: 3

   self
   getting_started
   api/index
   examples/index
   contribute


PyAnsys Sound
-------------

PyAnsys Sound enables the use of the main features of `Ansys Sound`_ to perform
post-processing and analysis of sounds and vibrations in Python. This library is based on
`Ansys DPF`_ and the DPF Sound plugin. It is a Python wrapper which implements classes on top
of DPF Sound operators.

For information demonstrating the behavior and usage of PyDPF Sound,
see the :doc:`examples/index` section, or navigate through the cards below.

.. grid:: 1 1 2 2
    :gutter: 2

    .. grid-item-card:: :octicon:`rocket` Getting started
        :link: getting_started
        :link-type: doc

        Contains installation instructions.

    .. grid-item-card:: :octicon:`play` Examples
        :link: examples/index
        :link-type: doc

        Demonstrates the use of PyAnsys Sound for various workflows.

    .. grid-item-card:: :octicon:`file-code` API reference
        :link: api/index
        :link-type: doc

        Describes the public Python classes, methods, and functions.

    .. grid-item-card:: :octicon:`code` Contribute
        :link: contribute
        :link-type: doc

        Provides developer installation and usage information.


Key features
''''''''''''

Here are some key features of PyAnsys Sounds:

* :doc:`api/signal_utilities` : tools to read/write wav files in Ansys Sound SAS format, and do basic editing of audio signals.
* :doc:`api/spectrogram_processing` : Time-Frequency <-> Time representations tools, and Time-Frequency edition tools.
* :doc:`api/psychoacoustics` : Psychoacoustics indicators computation, to measure perceived sound quality.
* :doc:`api/xtract` : Separation of a signal in several components: tonal, transient and noise parts.

Not all the features of Ansys Sound SAS are available in PyANsys Sound. Features are regularly added in new versions.

.. _limitations:

.. Limitations
.. '''''''''''
.. -  ???

.. _Ansys DPF: https://dpf.docs.pyansys.com/version/stable/
.. _Ansys Sound: https://www.ansys.com/sound