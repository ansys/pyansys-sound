PyAnsys Sound
=============

|pyansys| |python| |pypi| |GH-CI| |codecov| |MIT| |black| |pre-commit.ci|

.. |pyansys| image:: https://img.shields.io/badge/Py-Ansys-ffc107.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAABDklEQVQ4jWNgoDfg5mD8vE7q/3bpVyskbW0sMRUwofHD7Dh5OBkZGBgW7/3W2tZpa2tLQEOyOzeEsfumlK2tbVpaGj4N6jIs1lpsDAwMJ278sveMY2BgCA0NFRISwqkhyQ1q/Nyd3zg4OBgYGNjZ2ePi4rB5loGBhZnhxTLJ/9ulv26Q4uVk1NXV/f///////69du4Zdg78lx//t0v+3S88rFISInD59GqIH2esIJ8G9O2/XVwhjzpw5EAam1xkkBJn/bJX+v1365hxxuCAfH9+3b9/+////48cPuNehNsS7cDEzMTAwMMzb+Q2u4dOnT2vWrMHu9ZtzxP9vl/69RVpCkBlZ3N7enoDXBwEAAA+YYitOilMVAAAAAElFTkSuQmCC
   :target: https://docs.pyansys.com/
   :alt: PyAnsys

.. |python| image:: https://img.shields.io/pypi/pyversions/ansys-sound-core?logo=pypi
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

.. |pre-commit.ci| image:: https://results.pre-commit.ci/badge/github/ansys/pyansys-sound/main.svg
   :target: https://results.pre-commit.ci/latest/github/ansys/pyansys-sound/main
   :alt: pre-commit.ci status

PyAnsys Sound lets you use the main features of `Ansys Sound`_ to perform
the postprocessing and analysis of sounds and vibrations in Python. This library is based on
`PyDPF-Core`_ and the DPF Sound plugin. It is a Python wrapper that implements classes on top
of DPF Sound operators

Documentation and issues
------------------------
Documentation for the latest stable release of PyAnsys Sound is hosted at
`PyAnsys Sound documentation <https://sound.docs.pyansys.com/version/stable/>`_.

The documentation has these sections:

- `Getting started <https://sound.docs.pyansys.com/version/stable/getting_started.html>`_: Learn
  how to install PyAnsys Sound in user mode.
- `User guide <https://sound.docs.pyansys.com/version/stable/user_guide.html>`_: Learn how to start
  a DPF server, load a signal from a WAV file, and perform operations on the signal.
- `API reference <https://sound.docs.pyansys.com/version/stable/api/index.html>`_: Understand how
  to use Python to interact programmatically with PyAnsys Sound.
- `Examples <https://sound.docs.pyansys.com/version/stable/examples/index.html>`_: Explore examples
  that show how to use PyAnsys Sound for various workflows.
- `Contribute <https://sound.docs.pyansys.com/version/stable/contribute.html>`_: Learn how to
  contribute to the PyAnsysSound codebase or documentation.

In the upper right corner of the documentation's title bar, there is an option
for switching from viewing the documentation for the latest stable release
to viewing the documentation for the development version or previously
released versions.

.. LINKS AND REFERENCES
.. _Ansys Sound: https://www.ansys.com/sound
.. _PyDPF-Core: https://dpf.docs.pyansys.com/version/stable/
