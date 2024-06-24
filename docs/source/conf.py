# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

# FOR AUTODOC:
    # sphinx-apidoc -o source/docstrings -e  ../cognixcore
    # ./make clear html
    # ./make html

# FOR AUTOAPI:
    # sphinx-build -b html . _build
    
import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

from cognixcore import *
from setup_cython_untested import *
from importlib.metadata import metadata

# -- Project information -----------------------------------------------------

project = 'cognixcore'
copyright = '2024, CogniX'
author = 'CogniX'

# The full version, including alpha/beta/rc tags
release = f"v{ metadata('cognixcore')['version'] }"
version = release

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.

# Either include 'sphinx.ext.autodoc' or 'autoapi.extension' depending
# on what you want to use
extensions = [
    # 'sphinx.ext.autodoc',
    'sphinx.ext.inheritance_diagram',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.doctest',
    'autoapi.extension',
]

# might test this later
autoapi_dirs = ['../../cognixcore'] # sphinx-build -b html . _build
autoapi_type = "python"
# og list ['members', 'undoc-members', 'private-members', 'show-inheritance', 'show-module-summary', 'special-members', 'imported-members',]
# we won't be including the imported members here
autoapi_options = ['members', 'undoc-members', 'show-inheritance', 'show-module-summary', 'special-members', 'imported-members']
autoapi_add_toctree_entry = False # do not add to toctree, we need to add additonaly files

add_module_names = False

# autodoc options
autodoc_member_order = 'bysource'

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.

html_theme = 'furo'
# 'furo'
# 'karma_sphinx_theme'
# 'insegel'
# 'pydata_sphinx_theme'
# 'furo'
# 'sphinx_rtd_theme'
# 'groundwork' 
# 'alabaster'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

html_css_files = [
    'custom.css',
]
