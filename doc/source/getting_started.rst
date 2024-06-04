Getting started
---------------

Installation
^^^^^^^^^^^^

PyDPF Sound supports Ansys version 2024 R2 and later. Make sure you have a licensed copy of Ansys installed. See
:ref:`Compatibility` to understand which ``ansys-sound-core`` version corresponds to which Ansys version.

Install PyAnsys-Sound
"""""""""""""""""""""
Install the ``ansys-sound-core`` package with ``pip``:

.. code::

    pip install ansys-sound-core

Specific versions can be installed by specifying the version in the pip command. For example, Ansys 2024 R2 requires ansys-sound-core version 0.1.0:

.. code::

    pip install ansys-sound-core==0.1.0


You should use a `virtual environment <https://docs.python.org/3/library/venv.html>`_,
because it keeps Python packages isolated from your Python system.


Install sound plugin
""""""""""""""""""""
Make sure you also download the sound plugin (e.g ``ansys_dpf_sound_win_v2024.2.pre0.zip``).
The sound plugin is available through:

* downloading here: **TODO: ADD LINK to ansys_dpf_sound_win_v2024.2.pre0.zip**

* installing SAS: **TODO: ADD LINK**


.. _Compatibility:

Compatibility
"""""""""""""

The following table shows which ``ansys-sound-core`` version is compatible with which server
version (Ansys version). See :ref:`Get DPF Sound Prerelease` to get the pre-releases.
By default, the DPF server is started from the latest installed Ansys.

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
After following the preceding steps, you should have a running DPF docker container that listens on port 50052.


Examples
^^^^^^^^

The :doc:`examples/index` section provides several basic examples of use of PyAnsys Sound.

At the end of each example, there is a button for downloading the example's Python source code.

**TODO: EXPLAIN WHERE/HOW TO GET INPUT FILES NEEDED TO RUN EXAMPLES. To be completed when clarified.**

