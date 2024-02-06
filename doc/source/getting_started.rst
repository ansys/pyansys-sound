Getting started
---------------

Installation
^^^^^^^^^^^^

PyDPF Sound supports Ansys version 2024 R1 and later. Make sure you have a licensed copy of Ansys installed. See
:ref:`Compatibility` to understand which ``ansys-dpf-sound`` version corresponds to which Ansys version.

Install the ``ansys-dpf-sound`` package with ``pip``:

.. code::

    pip install ansys-dpf-sound

Specific versions can be installed by specifying the version in the pip command. For example: ansys 2024 R1 requires ansys-dpf-sound version 0.1.0:

.. code::

    pip install ansys-dpf-sound==0.1.0


You should use a `virtual environment <https://docs.python.org/3/library/venv.html>`_,
because it keeps Python packages isolated from your system Python.


Examples
^^^^^^^^

The :doc:`examples/index` section provides these basic examples for getting started:

* :ref:`sphx_glr_examples_gallery_examples_001_load_write_wav_files.py`

At the end of each example, there is a button for downloading the example's Python source code.
Input files, such as the input wav files and composite definition, are downloaded from a Git
repository when running the example.


.. _Compatibility:

Compatibility
"""""""""""""

The following table shows which ``ansys-dpf-sound`` version is compatible with which server version (Ansys version). See :ref:`Get DPF Sound Prerelease` to get the pre-releases.
By default the DPF server is started from the latest Ansys installer.

.. list-table::
   :widths: 20 20
   :header-rows: 1

   * - Server version
     - ansys.dpf.sound Python module version
   * - 8.0 (Ansys 2024 R2 pre0)
     - 0.1.0 and later


.. _Get DPF Sound Prerelease :

Getting the DPF server docker image
"""""""""""""""""""""""""""""""""""
Follow the steps described in the DPF documentation in the section `Run DPF Server in A Docker Container <https://dpf.docs.pyansys.com/version/stable/user_guide/getting_started_with_dpf_server.html#run-dpf-server-in-a-docker-container>`_.
Make sure you also download the composites plugin (e.g ``ansys_dpf_sound_win_v2024.1.pre0.zip``).
After following the preceding steps, you should have a running DPF docker container that listens to port 50052.
