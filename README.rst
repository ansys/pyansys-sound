PyAnsys Sound
=============

|pyansys| |python| |pypi| |GH-CI| |codecov| |MIT| |black|

.. |pyansys| image:: https://img.shields.io/badge/Py-Ansys-ffc107.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAABDklEQVQ4jWNgoDfg5mD8vE7q/3bpVyskbW0sMRUwofHD7Dh5OBkZGBgW7/3W2tZpa2tLQEOyOzeEsfumlK2tbVpaGj4N6jIs1lpsDAwMJ278sveMY2BgCA0NFRISwqkhyQ1q/Nyd3zg4OBgYGNjZ2ePi4rB5loGBhZnhxTLJ/9ulv26Q4uVk1NXV/f///////69du4Zdg78lx//t0v+3S88rFISInD59GqIH2esIJ8G9O2/XVwhjzpw5EAam1xkkBJn/bJX+v1365hxxuCAfH9+3b9/+////48cPuNehNsS7cDEzMTAwMMzb+Q2u4dOnT2vWrMHu9ZtzxP9vl/69RVpCkBlZ3N7enoDXBwEAAA+YYitOilMVAAAAAElFTkSuQmCC
   :target: https://docs.pyansys.com/
   :alt: PyAnsys

.. |python| image:: https://img.shields.io/badge/Python-%3E%3D3.9-blue
   :target: https://pypi.org/project/ansys-dpf-sound/
   :alt: Python

.. |pypi| image:: https://img.shields.io/pypi/v/ansys-sound-core.svg?logo=python&logoColor=white
   :target: https://pypi.org/project/ansys-sound-core
   :alt: PyPI

.. |codecov| image:: https://codecov.io/gh/ansys/pyansys-sound/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/ansys/pyansys-sound/
   :alt: Codecov

.. |GH-CI| image:: https://github.com/ansys/pyansys-sound/actions/workflows/ci_cd.yml/badge.svg
   :target: https://github.com/ansys/pyansys-sound/actions/workflows/ci_cd.yml
   :alt: GH-CI

.. |MIT| image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: MIT

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg?style=flat
   :target: https://github.com/psf/black
   :alt: Black


.. index_start

PyAnsys Sound enables the postprocessing and analysis of sounds based on
`Ansys DPF`_ and the DPF Sound plugin. It is a Python wrapper that
implements classes on top of DPF Sound operators. For
information demonstrating the behavior and usage of PyAnsys Sound,
see the `Examples`_ section.

.. START_MARKER_FOR_SPHINX_DOCS

Contribute
----------


Install in development mode
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Installing PyAnsys Sound in development mode allows
you to modify the source and enhance it.

Before attempting to contribute to PyAnsys Sound, ensure that you are thoroughly
familiar with the `PyAnsys Developer's Guide`_.

#.  Clone the repository:

    .. code:: bash

        git clone https://github.com/ansys/pyansys-sound
        cd pyansys-sound

#.  Create a fresh-clean Python environment and activate it. Refer to the official `venv`_ documentation if you require further information:

    .. code:: bash

        # Create a virtual environment
        python -m venv .venv

#.  Install dependencies:

    .. code:: bash

        pip install -e .

#.  Install additional requirements for tests and documentation (if needed):

    .. code:: bash

        pip install -e.[doc,tests]


Test
^^^^

There are different ways to run the PyAnsys Sound tests, depending on how the DPF
server is started.

#.  Run tests with a Docker container:

    Follow the steps in `Getting the DPF server Docker image`_ to get
    and run the DPF docker image. Run the tests with the following command

    .. code:: bash

        pytest .

#.  Run tests with a Docker container from Github:

    .. code:: bash

        docker pull ghcr.io/ansys/ansys-sound:latest
        pytest .


Build documentation
===================

Follow the description in `Getting the DPF server Docker image`_ image to get
and run the dpf docker image.

On Windows, build the documentation with:

.. code:: powershell

    .\doc\make.bat html

You can use the latest container from Github to build it with the following command:

.. code:: powershell

    docker pull ghcr.io/ansys/ansys-dpf-sound:latest
    docker run -d -p 6780:50052 -e ANSYSLMD_LICENSE_FILE=1055@mylicserver -e ANSYS_DPF_ACCEPT_LA=Y ghcr.io/ansys/ansys-sound:latest
    docker run -d -e "ANSYS_DPF_ACCEPT_LA=Y" -e "ANSYSLMD_LICENSE_FILE=1055@mylicserver" -v $env:LOCALAPPDATA\Ansys\ansys_sound_core\examples:C:\data  -p 6780:50052 ghcr.io/ansys/ansys-dpf-sound:latest
    .\doc\make.bat html



Run style checks
================

The style checks use `pre-commit`_ and can be run from a powershell terminal:

.. code:: bash

    pre-commit run --all-files


The style checks can also be configured to run automatically before each ``git commit``:

.. code:: bash

    pre-commit install

View documentation
-------------------
Documentation for the latest stable release of PyAnsys Sound is hosted at
`PyAnsys Sound Documentation <https://sound.docs.pyansys.com/version/stable/>`_.

In the upper right corner of the documentation title bar, there is an option
for switching from viewing the documentation for the latest stable release
to viewing the documentation for the development version or previously
released versions.

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
.. _Getting the DPF server Docker image: https://sound.docs.pyansys.com/version/stable/getting_started.html#getting-the-dpf-server-docker-image
.. _Examples: https://sound.docs.pyansys.com/version/stable/examples/index.html
.. _Ansys DPF: https://dpf.docs.pyansys.com/version/stable/
