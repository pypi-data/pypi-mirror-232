# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys

project = 'contamxpy'
copyright = '2023, W. Stuart Dols, Brian J. Polidoro'
author = 'W. Stuart Dols, Brian J. Polidoro'
release = '0.0.8'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.todo',
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx_autodoc_typehints',
    'sphinx.ext.coverage'
]

templates_path = ['_templates']
exclude_patterns = []
todo_include_todos = True
todo_emit_warnings = True


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
#html_theme = 'bizstyle'
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['_static']

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
#
html_show_copyright = False

html_title = 'contamxpy - ContamX Python Bindings'
html_show_sourcelink = False
html_use_index = False
html_static_path = ['_static']

# -- Path setup -------------------------------------------------
# relative to conf.py file
sys.path.insert(0, os.path.relpath('../../contamxpy'))

# -- Options for rst2pdf output

# Grouping the document tree into PDF files. List of tuples
# (source start file, target name, title, author, options).
pdf_documents = [
    ('index', 'contamxpy', 'contamxpy documentation', author),
]

# pdf_stylesheets = ['twocolumn']

# -- Options for LaTeX output ---------------------------------------------

latex_engine = 'xelatex'
# latex_engine = 'pdflatex'

# show page numbers with reference links
latex_show_pagerefs = True

latex_elements = {
    # Set color of note border and warning background 
    # Reduce blank pages
    'sphinxsetup': 'noteBorderColor={RGB}{0,0,255},warningBgColor={RGB}{255,204,204}',
    'classoptions' : ',openany,oneside'
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).

# The master toctree document.

master_doc = 'index'
latex_documents = [
    (master_doc, 'contamxpy.tex', 'contamxpy Documentation',
     author, 'howto', True)
]