.. _ref_contribute:

Contribute
----------
Overall guidance on contributing to a PyAnsys library appears in the
`Contributing <https://dev.docs.pyansys.com/how-to/contributing.html>`_ topic
in the *PyAnsys developer's guide*. Ensure that you are thoroughly familiar
with this guide before attempting to contribute to PyAnsys Sound.

The following contribution information is specific to PyAnsys Sound.


Install in development mode
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Installing PyAnsys Sound in development mode allows you to modify and enhance
the source.

.. note::
  For information on prerequisites, see :ref:`prerequisistes`.

Perform these steps to install PyAnsys Sound in developer mode:

#. Clone the repository:

   .. code:: bash

       git clone https://github.com/ansys/pyansys-sound
       cd pyansys-sound

#. Create a fresh-clean Python `virtual environment <https://docs.python.org/3/library/venv.html>`_
   and activate it.

   .. code:: bash

       # Create a virtual environment
       python -m venv .venv

      # Activate it in a POSIX system
      source .venv/bin/activate

      # Activate it in Windows CMD environment
      .venv\Scripts\activate.bat

      # Activate it in Windows Powershell
      .venv\Scripts\Activate.ps1

#. Install with minimum requirements, to cover core capability:

   .. code:: bash

       pip install -e .

#. Alternatively, install the full requirements, allowing to access all available features:

    .. code:: bash

         pip install -e.[full]

#. If needed, install additional requirements for testing and documentation-building:

   .. code:: bash

       pip install -e.[doc,tests]

Test
----

There are different ways to run the PyAnsys Sound tests, depending on how the DPF
server is started.

- Run tests with an existing Docker container.

  For information on getting and running the DPF Server Docker image, see :ref:`DPF Server Docker image`.
  Run the tests with this command:

  .. code:: bash

      pytest .

- Run tests with the latest Docker container from GitHub with these commands:

  .. code:: bash

      docker pull ghcr.io/ansys/ansys-sound:latest
      pytest .


Run style checks
----------------

The style checks use `pre-commit`_, which can be run from a Powershell terminal:

.. code:: bash

    pre-commit run --all-files


You can also install this as a Git pre-commit hook by running this command:

.. code:: bash

    pre-commit install

Build documentation
-------------------

Before you can build the documentation, you must get and run the DPF Server Docker image.
For more information, see :ref:`DPF Server Docker image`.

On Windows, build the documentation with this command:

.. code:: powershell

    .\doc\make.bat html

You can use the latest container from GitHub to build it with the following command:

.. code:: powershell

    docker pull ghcr.io/ansys/ansys-dpf-sound:latest
    docker run -d -p 6780:50052 -e ANSYSLMD_LICENSE_FILE=1055@mylicserver -e ANSYS_DPF_ACCEPT_LA=Y ghcr.io/ansys/ansys-sound:latest
    docker run -d -e "ANSYS_DPF_ACCEPT_LA=Y" -e "ANSYSLMD_LICENSE_FILE=1055@mylicserver" -v $env:LOCALAPPDATA\Ansys\ansys_sound_core\examples:C:\data  -p 6780:50052 ghcr.io/ansys/ansys-dpf-sound:latest
    .\doc\make.bat html


.. LINKS AND REFERENCES
.. _black: https://github.com/psf/black
.. _flake8: https://flake8.pycqa.org/en/latest/
.. _isort: https://github.com/PyCQA/isort
.. _PyAnsys Developer's guide: https://dev.docs.pyansys.com/
.. _pre-commit: https://pre-commit.com/
.. _pytest: https://docs.pytest.org/en/stable/
.. _Sphinx: https://www.sphinx-doc.org/en/master/
.. _pip: https://pypi.org/project/pip/
.. _tox: https://tox.wiki/en/stable/
.. _venv: https://docs.python.org/3/library/venv.html
.. _Getting the DPF Server Docker image: https://sound.docs.pyansys.com/version/stable/getting_started.html#getting-the-dpf-server-docker-image
.. _Examples: https://sound.docs.pyansys.com/version/stable/examples/index.html
.. _Ansys DPF: https://dpf.docs.pyansys.com/version/stable/