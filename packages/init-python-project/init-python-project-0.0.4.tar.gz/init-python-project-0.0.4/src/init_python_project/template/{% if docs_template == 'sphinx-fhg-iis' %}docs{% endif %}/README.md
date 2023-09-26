# Template for Technical Documentation

## DEMO
- See the [generated HTML output](https://sch.git01.iis.fhg.de/sphinx_template/) of this repository
- See the [generated PDF output](https://sch.git01.iis.fhg.de/sphinx_template/main.pdf) of this repository

## Overview
This project hosts a template for technical documentation that generates HTML pages or PDF documents that follow Fraunhofer IIS' corporate identity requirements based on markup text files using [Sphinx](https://www.sphinx-doc.org/).

Sphinx uses the [reStructuredText](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html) markup language by default, and can read [MyST Markdown](https://myst-parser.readthedocs.io/en/latest/syntax/optional.html) via third-party extensions. Both of these are powerful and straightforward to use, and have functionality for complex documentation and publishing workflows.

Here are some of Sphinx’s major features:

- **Output formats**: HTML (including Windows HTML Help), LaTeX (for printable PDF versions), ePub, Texinfo, manual pages, plain text
- **Extensive cross-references**: semantic markup and automatic links for functions, classes, citations, glossary terms and similar pieces of information
- **Hierarchical structure**: easy definition of a document tree, with automatic links to siblings, parents and children
- **Automatic indices**: general index as well as a language-specific module indices
- **Code handling**: automatic highlighting using the [Pygments highlighter](https://pygments.org/)
- **Extensions**: automatic testing of code snippets, inclusion of docstrings from Python modules (API docs) via [built-in extensions](https://www.sphinx-doc.org/en/master/usage/extensions/index.html#builtin-extensions), and much more functionality via [third-party extensions](https://www.sphinx-doc.org/en/master/usage/extensions/index.html#third-party-extensions).

## Installation
Refer to [requirements.in](requirements.in) to learn about the Python dependencies and inspect [requirements.txt](requirements.txt) to see all transitive dependencies [conf.py](source/conf.py). Use

```
pip3 install -r requirements.txt
```

to install all dependencies. To upgrade all modules use `pip-compile requirements.in` first which overrides `requirements.txt`.

## Usage
Sphinx generates [HTML](docs/html/index/html) pages and a [PDF](docs/latex/main.pdf) document that is based on the most recent LaTeX template using either

```
cd source; doxygen Doxyfile; cd ..
sphinx-build -b html source/ docs/html
```
or

```
cd source; doxygen Doxyfile; cd ..
sphinx-build -b latex source/ docs/latex
make latexpdf  # build the pdf from generated latex files
```

Please refer to [.gitlab-ci.yml](.gitlab-ci.yml) for further details and a GitLab automation including hosting on GitLab pages.

## Configuration
Sphinx is configured by [conf.py](source/conf.py). Please refer to the [Sphinx documentation](https://www.sphinx-doc.org/en/master/) for further details.
