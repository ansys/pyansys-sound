Getting started
---------------

PyAnsys Sound supports Ansys version 2024 R2 and later. Make sure you have a licensed copy of Ansys installed. See
:ref:`Compatibility` to understand which ``ansys-sound-core`` version corresponds to which Ansys version.

Installation
^^^^^^^^^^^^

This sections explains how to install properly PyAnsys Sound and its prerequisites.

Install Ansys DPF server and Ansys Sound
""""""""""""""""""""""""""""""""""""""""

PyAnsys Sound relies on Ansys products:
- Ansys DPF.
- DPF Sound, which is a plugin for DPF.

You can use two methods to install these prerequisites:

- from the Ansys installer: install Ansys and Ansys Sound SAS from the Download Center on `Ansys Customer Portal`_, then `Install PyDPF Core`_
- from DPF pre-release: download and install DPF Server and DPF Sound from the `DPF pre-release installation guidelines`_

Note: you can also use `DPF Server as a docker image`_.

Install PyAnsys Sound
"""""""""""""""""""""
Install the ``ansys-sound-core`` package with ``pip``:

.. code::

    pip install ansys-sound-core

Specific versions can be installed by specifying the version in the pip command. For example, Ansys 2024 R2 requires ansys-sound-core version 0.1.0:

.. code::

    pip install ansys-sound-core==0.1.0

You should use a `virtual environment <https://docs.python.org/3/library/venv.html>`_,
because it keeps Python packages isolated from your Python system.


.. _Compatibility:

Compatibility
^^^^^^^^^^^^^

The following table shows which ``ansys-sound-core`` version is compatible with which DPF server
version (Ansys version).

By default, the DPF server is started from the latest installed Ansys.

.. list-table::
   :widths: 20 20
   :header-rows: 1

   * - Server version
     - ansys.sound.core Python module version
   * - 8.0 (Ansys 2024 R2 pre0)
     - 0.1.0 and later


Examples
^^^^^^^^

The :doc:`examples/index` section provides several basic examples of use of PyAnsys Sound.

At the end of each example, there is a button for downloading the example's Python source code.


.. _DPF Server as a docker image:

Getting the DPF server Docker image
"""""""""""""""""""""""""""""""""""

Follow the steps described in the DPF documentation in the `Run DPF Server in a docker container
<https://dpf.docs.pyansys.com/version/stable/getting_started/dpf_server.html#run-dpf-server-in-a-docker-container>`_ section.
Make sure you also download the composites plugin (e.g ``ansys_dpf_sound_win_v2024.1.pre0.zip``).
After following the preceding steps, you should have a running DPF Docker container that listens to port 6780.



.. _Ansys DPF: https://dpf.docs.pyansys.com/version/stable/
.. _Ansys Sound: https://www.ansys.com/sound
.. _Ansys Customer Portal: https://innovationspace.ansys.com/customer-center/
.. _Install PyDPF Core: https://dpf.docs.pyansys.com/version/stable/getting_started/index.html#install-pydpf-core
.. _DPF pre-release installation guidelines: https://dpf.docs.pyansys.com/version/stable/getting_started/dpf_server.html#install-dpf-server