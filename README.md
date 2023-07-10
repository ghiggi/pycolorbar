# Welcome to pycolorbar
[![DOI](https://zenodo.org/badge/664629093.svg)](https://zenodo.org/badge/latestdoi/664629093)
[![PyPI version](https://badge.fury.io/py/pycolorbar.svg)](https://badge.fury.io/py/pycolorbar)
[![Conda Version](https://img.shields.io/conda/vn/conda-forge/pycolorbar.svg)](https://anaconda.org/conda-forge/pycolorbar)
[![Tests](https://github.com/ghiggi/pycolorbar/actions/workflows/tests.yml/badge.svg)](https://github.com/ghiggi/pycolorbar/actions/workflows/tests.yml)
[![Coverage Status](https://coveralls.io/repos/github/ghiggi/pycolorbar/badge.svg?branch=main)](https://coveralls.io/github/ghiggi/pycolorbar?branch=main)
[![Documentation Status](https://readthedocs.org/projects/pycolorbar/badge/?version=latest)](https://pycolorbar.readthedocs.io/projects/pycolorbar/en/stable/?badge=stable)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![License](https://img.shields.io/github/license/ghiggi/pycolorbar)](https://github.com/ghiggi/pycolorbar/blob/master/LICENSE)

The pycolorbar is still in development. Feel free to try it out and to report issues or to suggest changes.

## Quick start

pycolorbar provides a way to define colormaps and colorbar settings for later use in matplotlib or xarray. 

Look at the [Tutorials][tutorial_link] to have an overview of the software !

## Installation

### pip

pycolorbar can be installed via [pip][pip_link] on Linux, Mac, and Windows.
On Windows you can install [WinPython][winpy_link] to get Python and pip
running.
Then, install the pycolorbar package by typing the following command in the command terminal:

    pip install pycolorbar

To install the latest development version via pip, see the
[documentation][doc_install_link].

### conda [NOT YET AVAILABLE]

pycolorbar can be installed via [conda][conda_link] on Linux, Mac, and Windows.
Install the package by typing the following command in a command terminal:

    conda install pycolorbar

In case conda forge is not set up for your system yet, see the easy to follow
instructions on [conda forge][conda_forge_link].


## Documentation for pycolorbar

You can find the documentation under [pycolorbar.readthedocs.io][doc_link]

### Tutorials and Examples

The documentation also includes some [tutorials][tutorial_link], showing the most important use cases of pycolorbar.
These tutorial are also available as Jupyter Notebooks and in Google Colab:

- 1. Introduction to colormaps definition [[Notebook][tut3_label_link]][[Colab][colab3_label_link]]
- 2. Introduction to colorbars definition [[Notebook][tut3_label_link]][[Colab][colab3_label_link]]
- 3. Introduction to bivariate colorbars  [[Notebook][tut3_label_link]][[Colab][colab3_label_link]]
- 4. Introduction to trivariate colorbars [[Notebook][tut3_label_link]][[Colab][colab3_label_link]]


## Citation

If you are using pycolorbar in your publication please cite our paper:

TODO: GMD

You can cite the Zenodo code publication of pycolorbar by:

> Ghiggi Gionata & XXXX . ghiggi/pycolorbar. Zenodo. https://doi.org/10.5281/zenodo.8131552

If you want to cite a specific version, have a look at the [Zenodo site](https://doi.org/10.5281/zenodo.7753488).

## Requirements:

- [numpy](https://numpy.org/)
- [matplotlib](https://matplotlib.org/)

## License

The content of this repository is released under the terms of the [MIT](LICENSE) license.


[pip_link]: https://pypi.org/project/gstools
[conda_link]: https://docs.conda.io/en/latest/miniconda.html
[conda_forge_link]: https://github.com/conda-forge/pycolorbar-feedstock#installing-pycolorbar
[conda_pip]: https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-pkgs.html#installing-non-conda-packages
[pipiflag]: https://pip-python3.readthedocs.io/en/latest/reference/pip_install.html?highlight=i#cmdoption-i
[winpy_link]: https://winpython.github.io/

[tutorial_link]: https://github.com/ghiggi/pycolorbar/tree/master#tutorials-and-examples

[tut3_label_link]: https://github.com/ghiggi/pycolorbar/tree/master/tutorials
[colab3_label_link]: https://github.com/ghiggi/pycolorbar/tree/master/tutorials

[tut3_patch_link]: https://github.com/ghiggi/pycolorbar/tree/master/tutorials
[colab3_patch_link]: https://github.com/ghiggi/pycolorbar/tree/master/tutorials
