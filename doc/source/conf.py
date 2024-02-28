"""Sphinx documentation configuration file."""
from datetime import datetime
import os

from ansys_sphinx_theme import get_version_match
from ansys_sphinx_theme import pyansys_logo_black as logo
import numpy as np
import pyvista
from pyvista.plotting.utilities.sphinx_gallery import DynamicScraper
from sphinx_gallery.sorting import FileNameSortKey

from ansys.dpf.sound import __version__

# Manage errors
pyvista.set_error_output_file("errors.txt")

# Ensure that offscreen rendering is used for docs generation
pyvista.OFF_SCREEN = True

# necessary when building the sphinx gallery
pyvista.BUILDING_GALLERY = True

pyvista.global_theme.window_size = np.array([1024, 768]) * 2

# Project information
project = "ansys-dpf-sound"
copyright = f"(c) {datetime.now().year} ANSYS, Inc. All rights reserved"
author = "ANSYS, Inc."
release = version = __version__
cname = os.getenv("DOCUMENTATION_CNAME", "docs.pyansys.com")

# Select desired logo, theme, and declare the html title
html_logo = logo
html_theme = "ansys_sphinx_theme"
html_short_title = html_title = "PyDPF Sound"

# specify the location of your github repo
html_theme_options = {
    "github_url": "https://github.com/ansys/pydpf-sound",
    "show_prev_next": False,
    "show_breadcrumbs": True,
    "additional_breadcrumbs": [
        ("PyAnsys", "https://docs.pyansys.com/"),
    ],
    "switcher": {
        "json_url": f"https://{cname}/versions.json",
        "version_match": get_version_match(__version__),
    },
    "check_switcher": False,
}

# Sphinx extensions
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "numpydoc",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    "sphinx_gallery.gen_gallery",
    "sphinx_design",
    "pyvista.ext.viewer_directive",
]

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/dev", None),
    "ansys-dpf-core": ("https://dpf.docs.pyansys.com/version/stable", None),
    "numpy": ("https://numpy.org/doc/stable", None),
    "matplotlib": ("https://matplotlib.org/stable", None),
    # kept here as an example
    # "scipy": ("https://docs.scipy.org/doc/scipy/reference", None),
    # "numpy": ("https://numpy.org/devdocs", None),
    # "matplotlib": ("https://matplotlib.org/stable", None),
    # "pandas": ("https://pandas.pydata.org/pandas-docs/stable", None),
    # "pyvista": ("https://docs.pyvista.org/", None),
    # "grpc": ("https://grpc.github.io/grpc/python/", None),
}

# numpydoc configuration
numpydoc_show_class_members = False
numpydoc_xref_param_type = True

# Consider enabling numpydoc validation. See:
# https://numpydoc.readthedocs.io/en/latest/validation.html#
numpydoc_validate = True
numpydoc_validation_checks = {
    "GL06",  # Found unknown section
    "GL07",  # Sections are in the wrong order.
    "GL08",  # The object does not have a docstring
    "GL09",  # Deprecation warning should precede extended summary
    "GL10",  # reST directives {directives} must be followed by two colons
    "SS01",  # No summary found
    "SS02",  # Summary does not start with a capital letter
    # "SS03", # Summary does not end with a period
    "SS04",  # Summary contains heading whitespaces
    # "SS05", # Summary must start with infinitive verb, not third person
    "RT02",  # The first line of the Returns section should contain only the
    # type, unless multiple values are being returned"
}

# sphinx gallery options
sphinx_gallery_conf = {
    # convert rst to md for ipynb
    "pypandoc": True,
    # path to your examples scripts
    "examples_dirs": ["../../examples"],
    # path where to save gallery generated examples
    "gallery_dirs": ["examples/gallery_examples"],
    # Pattern to search for example files
    "filename_pattern": r"\.py",
    # Remove the "Download all examples" button from the top level gallery
    "download_all_examples": False,
    # Sort gallery example by file name instead of number of lines (default)
    "within_subsection_order": FileNameSortKey,
    # directory where function granular galleries are stored
    "backreferences_dir": None,
    # Modules for which function level galleries are created.  In
    "doc_module": "ansys-pydpf-sound",
    "image_scrapers": (DynamicScraper(), "matplotlib"),
    "ignore_pattern": r"__init__\.py",
    "thumbnail_size": (350, 350),
}

exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    # because we include this in examples/index.rst
    "examples/gallery_examples/index.rst",
]


# static path
html_static_path = ["_static"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# -- Options for LaTeX output ------------------------------------------------
latex_elements = {}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (
        master_doc,
        f"{project}-Documentation-{__version__}.tex",
        f"{project} Documentation",
        author,
        "manual",
    ),
]

# Fix to resolve hyperlink warnings when building PDF
# ( https://stackoverflow.com/questions/67485567/sphinx-cross-reference-in-latex)
latex_elements = {
    "preamble": r"""
\renewcommand{\hyperref}[2][]{#2}
"""
}
