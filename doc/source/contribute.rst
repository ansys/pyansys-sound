.. _ref_contribute:

==========
Contribute
==========
Overall guidance on contributing to a PyAnsys library appears in the
`Contributing <https://dev.docs.pyansys.com/how-to/contributing.html>`_ topic
in the `PyAnsys developer's guide`_. Ensure that you are thoroughly familiar
with this guide before attempting to contribute to PyAnsys Sound.

The following contribution information is specific to PyAnsys Sound.

.. _dev_install:

Install in development mode
---------------------------

Installing PyAnsys Sound in development mode allows you to modify and enhance
the source codebase and documentation.

.. note::
   For information on prerequisites, see :ref:`prerequisites`.

Follow these steps to install PyAnsys Sound in development mode:

#. Clone the repository:

   .. code:: bash

       git clone https://github.com/ansys/pyansys-sound
       cd pyansys-sound

#. Create a fresh-clean Python `virtual environment <https://docs.python.org/3/library/venv.html>`_
   and activate it.

   .. code:: bash

      # Create a virtual environment.
      python -m venv .venv

      # Activate it in a POSIX system.
      source .venv/bin/activate

      # Activate it in Windows CMD environment.
      .venv/Scripts/activate.bat

      # Activate it in Windows Powershell.
      .venv/Scripts/Activate.ps1

#. Install with minimum requirements, to cover core capability:

   .. code:: bash

        pip install -e .

#. Alternatively, install the full requirements, allowing access to all available features:

   .. code:: bash

        pip install -e.[full]

#. If needed, install additional requirements for testing and documentation-building:

   .. code:: bash

        pip install -e.[doc,tests]

.. _code_style:

Adhere to code style
--------------------

PyAnsys Sound follows the PEP8 standard as outlined in
`PEP 8 <https://dev.docs.pyansys.com/coding-style/pep8.html>`_ in
the `PyAnsys Developer's Guide`_
and implements style checking using `pre-commit <https://pre-commit.com/>`_.

To ensure your code meets minimum code styling standards, run these commands::

  pip install pre-commit
  pre-commit run --all-files

You can also install this as a pre-commit hook by running this command::

  pre-commit install

This flags style check issues whenever attempting to commit changes::

  $ pre-commit install
  $ git commit -am "added my cool feature"
    black....................................................................Passed
    isort....................................................................Passed
    flake8...................................................................Passed
    codespell................................................................Passed
    pydocstyle...............................................................Passed
    check for merge conflicts................................................Passed
    trim trailing whitespace.................................................Passed
    Add License Headers......................................................Passed
    Validate GitHub Workflows................................................Passed

Add examples
------------

Follow these steps to create new examples to demonstrate PyAnsys Sound workflows:

#. Create a new branch of the PyAnsys Sound repository.
#. Create a new Python script in the ``examples/`` folder.
#. Follow the structure of existing examples in the ``examples/`` folder.
   Ensure that your example includes descriptive comments to explain the workflow and that it is
   properly formatted to follow the adopted code style. See :ref:`code_style` and
   :doc:`examples/index` for reference.
#. If your example requires specific input files, use local paths while developing the example.
   These local paths shall be replaced at a later step, once the example is complete.
#. Make sure your example runs properly and produces the expected results.
#. Build documentation locally to verify that your example is correctly integrated into the
   documentation. See :ref:`build_documentation`. As long as the example file is in the
   ``examples/`` folder, it is automatically included in the documentation.
#. Once the example is complete, upload the input files to the PyAnsys Sound example data
   repository by submitting a `pull request
   <https://github.com/ansys/example-data/upload/main/pyansys-sound>`_:

   - Drag-and-drop the files in the dedicated field.
   - Add a title for the file upload, and, optionally, a description.
   - Click *Propose changes* to submit the pull request.
   - Wait for the approval of the pull request.

#. Define a new download function in module ``src/ansys/sound/core/example_helpers/download.py``
   to fetch the necessary files from the PyAnsys Sound example data repository. Refer to existing
   download functions in this module for guidance.

   .. note::
        If your input data files require a licensed DPF operator to load (typically WAV files, for
        example), they need to be made available to the server (which might be remote). In such case,
        use the function :func:`_download_example_file_to_server_tmp_folder`. Otherwise, when the files
        are loaded with Python built-in libraries or third-party libraries (text files, CSV files, for
        example), use the function :func:`_download_file_in_local_tmp_folder`.

#. Add your new download function to the ``src/ansys/sound/core/example_helpers`` package's
   initialization file ``__init__.py``.
#. Create a test function for your new download function in ``tests/test_example_helpers.py``, run
   this test module, and make sure the tests pass (see :ref:`run_tests`).
#. In your example script, replace the local input file paths with the new download function.
#. If your example uses libraries that are not already included in the project's dependencies in
   ``pyproject.toml`` at the root of cloned repository, make sure to add them in the *full* and
   *doc* dependency groups
#. Submit your changes in a `pull request` to the PyAnsys Sound repository and wait for review.

.. _build_documentation:

Build documentation
-------------------

.. vale off
.. locally deactivating vale because "dev" in the note below triggers an error in doc style check.

.. note::
    To view the current development documentation, go to
    `PyAnsys Sound Documentation <https://sound.docs.pyansys.com>`_. By default, the displayed
    documentation is that of the latest stable release. To switch to the current development
    version, select *dev* from the dropdown menu in the upper right corner of the documentation
    page.

.. vale on

.. note::
    Building the documentation requires access to a DPF Server with the DPF Sound plugin. See
    :ref:`prerequisites`. It also requires the installation of the documentation-building dependencies.
    See :ref:`dev_install`.

On Windows, build the documentation with this command:

.. code:: powershell

    .\doc\make.bat html

The documentation is built in the cloned repository, under ``docs/_build/html``.

You can clean the documentation build with this command:

.. code:: powershell

    .\doc\make.bat clean

.. _run_tests:

Run tests
---------

.. note::
    Running the tests requires access to a DPF Server with the DPF Sound plugin. See
    :ref:`prerequisites`. It also requires the installation of the testing dependencies. See
    :ref:`dev_install`.

To run all tests locally, use this command:

.. code:: bash

    pytest .

To run tests for all modules of a specific package, use the following command:

.. code:: bash

    pytest ./tests/tests_package_name/

To run tests for a specific module only, use the following command:

.. code:: bash

    pytest ./tests/tests_package_name/test_module_name.py

Post issues
-----------

Use the `PyAnsys Sound Issues <https://github.com/ansys/pyansys-sound/issues>`_
page to submit questions, report bugs, and request new features. When possible, you
should use these issue templates:

* Bug, problem, error: For filing a bug report
* Documentation error: For requesting modifications to the documentation
* Adding an example: For proposing a new example
* New feature: For requesting enhancements to the code

If your issue does not fit into one of these template categories, select Blank issue.

To reach out to the PyAnsys project support team, email `pyansys.core@ansys.com <pyansys.core@ansys.com>`_.


.. LINKS AND REFERENCES
.. _PyAnsys Developer's guide: https://dev.docs.pyansys.com/
.. _pre-commit: https://pre-commit.com/
.. _virtual environment: https://docs.python.org/3/library/venv.html
