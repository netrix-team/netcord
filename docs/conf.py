# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import sys
import os

sys.path.insert(0, os.path.abspath('../'))

from netcord import __version__
from datetime import date

project = 'Netcord'
copyright = f'{date.today().year}, netrix-team'
author = 'netrix-team'
release = __version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx_copybutton',
    'sphinx_autodoc_typehints',
    'myst_parser',
]

simplify_optional_unions = True
autodoc_member_order = 'bysource'

intersphinx_mapping = {
    'py': ('https://docs.python.org/3', None),
}

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
html_static_path = ['_static']

html_logo = '_static/logo.png'
html_favicon = '_static/favicon.ico'
html_title = f'<h6 align="center">Version: <b>{release}</b></h6>'
