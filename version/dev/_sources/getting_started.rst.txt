===============
Getting started
===============

This section explains how to install PyAnsys Sound (``ansys-sound-core``) if you only wish to use
it. If you are also interested in contributing to PyAnsys Sound, see :ref:`ref_contribute` for
information on installing in development mode.

.. _prerequisites:

Prerequisites
-------------

Prerequisites for using PyAnsys Sound are:

- Python 3.10 or later (see Python documentation for installation instructions).
- Ansys DPF Server with DPF Sound plugin (version 2024 R2 or later), with a valid license.

The DPF Server and DPF Sound plugin can be found in major Ansys releases, or in DPF pre-releases:

- For major Ansys releases: Go to the `Current Releases Download Center`_ on the Ansys Customer
  Portal, select the appropriate release, and click the **Ansys Automated Installer** button. Use
  the downloaded installer to install *Ansys Sound Analysis and Specification (SAS)*, which
  includes the DPF Server and DPF Sound plugin.
- For DPF pre-releases: Go to the `DPF Pre-Release Download Center`_, download and install DPF
  Server and DPF Sound as described in the pre-release guidelines in `Install DPF Server`_ from the
  `PyDPF-Core`_ documentation. Note: The DPF Sound plugin is contained in the zip file named
  ``ansys_dpf_sound_win_v<version>.zip``

.. note::
  To see which ``ansys-sound-core`` version corresponds to which Ansys Sound release, see
  :ref:`Compatibility`.

.. note::
  DPF Server and DPF Sound plugin containerization is also possible using Docker. For more
  information, see :ref:`DPF Docker containerization`.

Installation
------------

To install the latest ``ansys-sound-core`` package with ``pip``, run this command:

.. code::

    pip install ansys-sound-core

To install a specific package version, specify the version in the ``pip`` command. For example, Ansys 2024 R2
requires version 0.1.0 of the ``ansys-sound-core`` package. To install version 0.1.0, you would run this command:

.. code::

    pip install ansys-sound-core==0.1.0

You should use a `virtual environment <https://docs.python.org/3/library/venv.html>`_
because it keeps Python packages isolated from your Python system.


.. _Compatibility:

Compatibility
-------------

The following table shows which ``ansys-sound-core`` version is compatible with which DPF Server
version (Ansys version).

By default, a DPF server is started from the latest installed Ansys version.

.. list-table::
   :widths: 20 20
   :header-rows: 1

   * - DPF Server version
     - ansys.sound.core version
   * - 8.0 (Ansys 2024 R2 pre0)
     - 0.1.0 and later
   * - 10.0 (Ansys 2025 R2 pre0)
     - 0.2.0 and later
   * - 11.0 (Ansys 2026 R1 pre0)
     - 0.3.0 and later


Starting PyAnsys Sound
----------------------

To start using PyAnsys Sound, you first need to connect to or start a DPF Server in Python.

.. code::

    from ansys.sound.core.server_helpers import connect_to_or_start_server

    server, license_context = connect_to_or_start_server()

You can now verify that PyAnsys Sound is running.

.. code::

    from ansys.sound.core.server_helpers import validate_dpf_sound_connection

    validate_dpf_sound_connection()

If no error is raised, you are ready to use PyAnsys Sound. See :doc:`user_guide` for more
information on using PyAnsys Sound.

You can also find relevant PyAnsys Sound workflow examples in :doc:`examples/index`.
At the end of each example, a button allows you to download the example's Python source code.

.. LINKS AND REFERENCES
.. _PyDPF-Core: https://dpf.docs.pyansys.com/version/stable/
.. _DPF Server: https://dpf.docs.pyansys.com/version/stable/getting_started/dpf_server.html#dpf-server
.. _Current Releases Download Center: https://download.ansys.com/Current%20Release
.. _DPF Pre-Release Download Center: https://download.ansys.com/Others/DPF%20Pre-Release
.. _Install DPF Server: https://dpf.docs.pyansys.com/version/stable/getting_started/dpf_server.html#install-dpf-server
.. _Build DPF Docker images: https://github.com/ansys/pyansys-sound/tree/main/docker
.. _DPF Server secure mode: https://dpf.docs.pyansys.com/version/stable/getting_started/dpf_server.html#run-dpf-server-in-secure-mode-with-mtls

.. toctree::
   :maxdepth: 2
   :hidden:

   docker_containerization