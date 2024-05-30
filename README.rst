****************
PyAnsys Sound
****************

|pyansys| |python| |GH-CI| |codecov| |MIT| |black|

.. |pyansys| image:: https://img.shields.io/badge/Py-Ansys-ffc107.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAABDklEQVQ4jWNgoDfg5mD8vE7q/3bpVyskbW0sMRUwofHD7Dh5OBkZGBgW7/3W2tZpa2tLQEOyOzeEsfumlK2tbVpaGj4N6jIs1lpsDAwMJ278sveMY2BgCA0NFRISwqkhyQ1q/Nyd3zg4OBgYGNjZ2ePi4rB5loGBhZnhxTLJ/9ulv26Q4uVk1NXV/f///////69du4Zdg78lx//t0v+3S88rFISInD59GqIH2esIJ8G9O2/XVwhjzpw5EAam1xkkBJn/bJX+v1365hxxuCAfH9+3b9/+////48cPuNehNsS7cDEzMTAwMMzb+Q2u4dOnT2vWrMHu9ZtzxP9vl/69RVpCkBlZ3N7enoDXBwEAAA+YYitOilMVAAAAAElFTkSuQmCC
   :target: https://docs.pyansys.com/
   :alt: PyAnsys

.. |python| image:: https://img.shields.io/badge/Python-%3E%3D3.9-blue
   :target: https://pypi.org/project/ansys-dpf-composites/
   :alt: Python

.. |codecov| image:: https://codecov.io/gh/ansys-internal/pydpf-sound/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/ansys-internal/pydpf-sound/
   :alt: Codecov

.. |GH-CI| image:: https://github.com/ansys-internal/pydpf-sound/actions/workflows/ci_cd.yml/badge.svg
   :target: https://github.com/ansys-internal/pydpf-sound/actions/workflows/ci_cd.yml
   :alt: GH-CI

.. |MIT| image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: MIT

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg?style=flat
   :target: https://github.com/psf/black
   :alt: Black


.. index_start

PyAnsys Sound enables the post-processing and analysis of sounds based on
`Ansys DPF`_ and the DPF Sound plugin. It is a Python wrapper which
implements classes on top of DPF Sound operators. For
information demonstrating the behavior and usage of PyAnsys Sound,
see Examples in the DPF Sound documentation.

.. START_MARKER_FOR_SPHINX_DOCS

----------
Contribute
----------


A Python wrapper for Ansys DPF Sound library.


How to install
--------------

Two installation modes are provided: user and developer.

For users
^^^^^^^^^

User installation can be performed by running:

.. code:: bash

    python -m pip install ansys-sound-core

For developers
^^^^^^^^^^^^^^

Installing the Pydpf-sound Library in developer mode allows
you to modify the source and enhance it.

Before contributing to the project, please refer to the `PyAnsys Developer's guide`_. You will
need to follow these steps:

#. Start by cloning this repository:

   .. code:: bash

      git clone https://github.com/ansys/pydpf-sound

#. Create a fresh-clean Python environment and activate it. Refer to the
   official `venv`_ documentation if you require further information:

   .. code:: bash

      # Create a virtual environment
      python -m venv .venv

      # Activate it in a POSIX system
      source .venv/bin/activate

      # Activate it in Windows CMD environment
      .venv\Scripts\activate.bat

      # Activate it in Windows Powershell
      .venv\Scripts\Activate.ps1

#. Make sure you have the latest version of `pip`_:

   .. code:: bash

      python -m pip install -U pip

#. Install the project in editable mode:

   .. code:: bash

      python -m pip install --editable ansys-sound-core

#. Install additional requirements (if needed):

   .. code:: bash

      python -m pip install -r requirements/requirements_build.txt
      python -m pip install -r requirements/requirements_doc.txt
      python -m pip install -r requirements/requirements_tests.txt

#. Finally, verify your development installation by running:

   .. code:: bash

      python -m pip install -r requirements/requirements_tests.txt
      pytest tests -v


Style and Testing
-----------------

If required, you can always call the style (`black`_, `isort`_,
`flake8`_...) or unit testing (`pytest`_) commands from the command line. However,
this does not guarantee that your project is being tested in an isolated
environment, which is another reason to consider using `tox`_.


Documentation
-------------

For building documentation, you can run the usual rules provided in the
`Sphinx`_ makefile, such as:

.. code:: bash

    python -m pip install -r requirements/requirements_doc.txt
    make -C doc/ html

    # subsequently open the documentation with (under Linux):
    your_browser_name doc/html/index.html

Distributing
------------

If you would like to create either source or wheel files, start by installing
the building requirements:

.. code:: bash

    python -m pip install -r requirements/requirements_build.txt

Then, you can execute:

.. code:: bash

    python -m build
    python -m twine check dist/*


.. LINKS AND REFERENCES
.. _black: https://github.com/psf/black
.. _flake8: https://flake8.pycqa.org/en/latest/
.. _isort: https://github.com/PyCQA/isort
.. _PyAnsys Developer's guide: https://dev.docs.pyansys.com/
.. _pre-commit: https://pre-commit.com/
.. _pytest: https://docs.pytest.org/en/stable/
.. _Sphinx: https://www.sphinx-doc.org/en/master/
.. _pip: https://pypi.org/project/pip/
.. _tox: https://tox.wiki/
.. _venv: https://docs.python.org/3/library/venv.html
.. _Ansys DPF: https://dpf.docs.pyansys.com/version/stable/
