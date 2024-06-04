Getting started
---------------

Installation
^^^^^^^^^^^^

PyAnsys Sound supports Ansys version 2024 R1 and later. Make sure you have a licensed copy of Ansys installed. See
:ref:`Compatibility` to understand which ``ansys-sound-core`` version corresponds to which Ansys version.

Install the ``ansys-sound-core`` package with ``pip``:

.. code::

    pip install ansys-sound-core

Specific versions can be installed by specifying the version in the pip command. For example, Ansys 2024 R1 requires ansys-sound-core version 0.1.0:

.. code::

    pip install ansys-sound-core==0.1.0


You should use a `virtual environment <https://docs.python.org/3/library/venv.html>`_,
because it keeps Python packages isolated from your system Python.


Examples
^^^^^^^^

The :doc:`examples/index` section provides these basic examples for getting started:

* :ref:`load_resample_amplify_write_wav_files_example`
* :ref:`xtract_feature_example`

At the end of each example, there is a button for downloading the example's Python source code.
Input files, such as the input wav files, are downloaded from a Git
repository when running the example.


.. _Compatibility:

Compatibility
"""""""""""""

The following table shows which ``ansys-sound-core`` version is compatible with which server version
(Ansys version). See :ref:`Get DPF Sound Prerelease` to get the pre-releases.
By default, the DPF server is started from the latest Ansys installer.

.. list-table::
   :widths: 20 20
   :header-rows: 1

   * - Server version
     - ansys.sound.core Python module version
   * - 8.0 (Ansys 2024 R2 pre0)
     - 0.1.0 and later


.. _Get DPF Sound Prerelease :

Getting the DPF server docker image
"""""""""""""""""""""""""""""""""""
Follow the steps described in the DPF documentation in the `Run DPF Server in A Docker Container
<https://dpf.docs.pyansys.com/version/stable/getting_started/dpf_server.html#run-dpf-server-in-a-docker-container>`_ section.
Make sure you also download the composites plugin (e.g ``ansys_dpf_sound_win_v2024.1.pre0.zip``).
After following the preceding steps, you should have a running DPF docker container that listens on port 50052.
