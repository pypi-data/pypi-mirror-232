# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))
import datetime
from pathlib import Path

year = str(datetime.date.today().year)
base = Path(__file__).resolve().parents[1]

# -- Project information -----------------------------------------------------
project = 'Product Name'
project_short = 'ShortName'
copyright = year + ', by Fraunhofer IIS'
author = 'Fraunhofer Institute for Integrated Circuits IIS'

# The full version, including alpha/beta/rc tags
release = '0.1'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
    "sphinx_tabs.tabs",
    'sphinx.ext.mathjax',
    "sphinxcontrib.bibtex",
    # "sphinx_charts.charts", ## uses plotly and shouldn't be used
    "breathe",
    "sphinx_design",
    "myst_parser",   # for Markdown support
]

myst_enable_extensions = ["colon_fence"]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
source_suffix = ['.rst', '.md']

# The master toctree document.
master_doc = 'index'

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

numfig = True

breathe_projects = {"myproject": "xml"}
breathe_default_project = "myproject"
breathe_projects_source = {
    "myproject" : ( "./include/", ["MathHelper.h"] )
}

bibtex_bibfiles = ['refs.bib']

# -- Options for HTML output -------------------------------------------------
html_logo = "_static/iis.svg"
html_title = project
html_copy_source = True
html_show_sourcelink = False
html_sourcelink_suffix = ""
html_favicon = "_static/iis.ico"
html_last_updated_fmt = '%Y-%m-%d'

html_theme = "pydata_sphinx_theme"
html_theme_options = {

    # Announcements bar on top
    "announcement": "This is a demo announcement that needs to be removed from conf.py",

    # Versioned documentation
    # Refer to https://pydata-sphinx-theme.readthedocs.io/en/stable/user_guide/version-dropdown.html when enabling
    #"switcher": {
    #    "json_url": "https://mysite.org/en/latest/_static/switcher.json",
    #}

    # Navigation bar configuration
    "header_links_before_dropdown": 4,

    # Nav Navigation configuration (left-hand menu)
    "show_nav_level": 2,
    "navigation_depth": 2,
    "collapse_navigation": True,

    # Table of content configuration (right-hand menu)
    "show_toc_level": 2,

    "use_edit_page_button" : False,

    # removes Sphinx version and Template version
    "footer_start": ["copyright", "confidential"],
    "footer_end": [],

    # removes the switcher for light/dark theme and therefore fixes theme to default_mode
    "navbar_end": [],
}

# defaults to light theme
html_context = {
    "default_mode": "light"
}

html_static_path = ["_static/html"]
html_css_files = ["custom.css"]


# -- Options for PDF output -------------------------------------------------
latex_engine = 'pdflatex'
latex_toplevel_sectioning = 'section'
latex_elements = {
    'papersize': 'a4paper',
    'releasename': project_short,
    "maketitle": open(base / "source" / "_static" / "texmf" / "title.tex").read(),
    "preamble": open(base / "source" / "_static" / "texmf" / "preamble.tex").read(),
    'fncychap' : '\\usepackage[Bjornstrup]{fncychap}',
    "fontpkg": r"\usepackage{charter}",
    'figure_align':'htbp',
    'pointsize': '12pt',

    "sphinxsetup": ",".join(
        (
            "verbatimwithframe=false",
            "VerbatimColor={HTML}{f0f2f4}",
            "InnerLinkColor={HTML}{2980b9}",
            "OuterLinkColor={HTML}{2980b9}",
            "warningBgColor={HTML}{e9a499}",
            "warningborder=0pt",
            r"HeaderFamily=\rmfamily\bfseries",
        )
    ),
}

latex_documents = [
    (master_doc, 'main.tex', project,
     author, 'fhgtechdoku', True)
]

# list any files in subdirectories of the texmf directory to include in the latex build
doc_root = Path(__file__).parent
fp_texmf = doc_root / "_static" / "texmf"
latex_additional_files = sorted(
    str(f.relative_to(doc_root)) for f in fp_texmf.glob("*/**/*") if f.is_file()
)
