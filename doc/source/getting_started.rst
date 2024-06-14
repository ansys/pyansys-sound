Getting started
---------------

PyAnsys Sound supports Ansys 2024 R2 and later. Make sure you have a licensed copy of Ansys installed.
To see which ``ansys-sound-core`` version corresponds to which Ansys version, see :ref:`Compatibility`.

Installation
^^^^^^^^^^^^

This sections explains how to install PyAnsys Sound and its prerequisites correctly.

Install Ansys DPF Server and DPF Sound
""""""""""""""""""""""""""""""""""""""

PyAnsys Sound relies on these Ansys products:

- Ansys DPF
- DPF Sound, which is a plugin for DPF

To install these prerequisites, you can choose from two methods:

- From the Ansys installer, install Ansys and Ansys Sound SAS from the Download Center on the `Ansys Customer Center`_.
  Then, perform the steps in `Install PyDPF Core`_ in the PyDPF-Core documentation.
- From the DPF pre-release, download and install DPF Server and DPF Sound as described in the pre-release guidelines in
  `Install DPF Server`_ in the PyDPF-Core documentation.

.. note::
  You can also use `DPF Server as a Docker image`_.

Install PyAnsys Sound
"""""""""""""""""""""

To install ``ansys-sound-core`` package with ``pip``, run this command:

.. code::

    pip install ansys-sound-core

To install a specific package version, specify the version in the ``pip`` command. For example, Ansys 2024 R2
requires version 0.1.0 of the ``ansys-sound-core`` package. To install version 0.1.0, you would run this command:

.. code::

    pip install ansys-sound-core==0.1.0

You should use a `virtual environment <https://docs.python.org/3/library/venv.html>`_,
because it keeps Python packages isolated from your Python system.


.. _Compatibility:

Compatibility
^^^^^^^^^^^^^

The following table shows which ``ansys-sound-core`` version is compatible with which DPF Server
version (Ansys version).

By default, DPF Server is started from the latest installed Ansys version.

.. list-table::
   :widths: 20 20
   :header-rows: 1

   * - DPF Server version
     - ansys.sound.core version
   * - 8.0 (Ansys 2024 R2 pre0)
     - 0.1.0 and later


Examples
^^^^^^^^

Several basic examples for using PyAnsys Sound are available in :doc:`examples/index`.
At the end of each example, there is a button for downloading the example's Python source code.


.. _DPF Server as a docker image:

DPF Server Docker image
"""""""""""""""""""""""

To use a DPF Server Docker image, follow the steps in `Run DPF Server in a Docker container
<https://dpf.docs.pyansys.com/version/stable/getting_started/dpf_server.html#run-dpf-server-in-a-docker-container>`_
in the DPF documentation. Make sure that you also download the Sound plugin for the corresponding release, such as
``ansys_dpf_sound_win_v2024.1.pre0.zip``. After following these steps, you should have a running DPF Docker container
that listens on port 6780.

.. _Ansys DPF: https://dpf.docs.pyansys.com/version/stable/
.. _Ansys Sound: https://www.ansys.com/sound
.. _Ansys Customer Center: https://innovationspace.ansys.com/customer-center/
.. _Install PyDPF Core: https://dpf.docs.pyansys.com/version/stable/getting_started/index.html#install-pydpf-core
.. _Install DPF Server: https://dpf.docs.pyansys.com/version/stable/getting_started/dpf_server.html#install-dpf-server