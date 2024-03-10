# -----------------------------------------------------------------------------.
# MIT License

# Copyright (c) 2024 pycolorbar developers
#
# This file is part of pycolorbar.

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# -----------------------------------------------------------------------------.
"""Define functions to visualize univariate colormaps."""
import math

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np


def plot_colormap(cmap, dpi=200):
    fig, ax = plt.subplots(figsize=(4, 0.4), dpi=dpi)
    mpl.colorbar.ColorbarBase(ax, cmap=cmap, orientation="horizontal")
    ax.set_title(cmap.name, fontsize=10, weight="bold")
    plt.show()


def plot_colormaps(cmaps, cols=None, subplot_size=None, dpi=200):
    # Define subplot_size
    if subplot_size is None:
        subplot_size = (2, 0.5)

    # Define number of subplots
    n = len(cmaps)

    # Define a layout most similar to a square
    if cols is None:
        cols = math.ceil(math.sqrt(n))
        cols = min(cols, 6)

    # Define number of rows required
    rows = int(np.ceil(n / cols))

    # Define figure width and height
    fig_width = cols * subplot_size[0]
    fig_height = rows * subplot_size[1]

    # Create dummy image for colormap
    im = np.outer(np.ones(10), np.arange(100))

    # Initialize figure
    fig, axes = plt.subplots(rows, cols, figsize=(fig_width, fig_height), dpi=dpi)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1, hspace=0.1, wspace=0.1)

    # Flatten axes for easy iteration
    axes = axes.ravel()

    # Loop through colormaps and axes
    for cmap, ax in zip(cmaps, axes):
        ax.set_title(cmap.name, fontsize=10, weight="bold")
        ax.imshow(im, cmap=cmap)
        ax.axis("off")  # Set axis off

    # Turn off any remaining axes
    for ax in axes[n:]:
        ax.axis("off")

    plt.show()


def show_colormap(cmap):
    from pycolorbar import get_cmap

    cmap = get_cmap(cmap)
    plot_colormap(cmap)


def show_colormaps(category=None, include_reversed=False, cols=None, subplot_size=None):
    import pycolorbar

    # Retrieve list of colormaps names
    if category is not None and category == "pycolorbar":
        names = pycolorbar.colormaps.available(include_reversed=include_reversed)
    else:  # include also matplotlib
        names = pycolorbar.available_colormaps(category=category, include_reversed=include_reversed)

    # Retrieve colormaps to display
    cmaps = [pycolorbar.get_cmap(name) for name in sorted(names)]

    # Display colormaps
    if len(cmaps) > 0:
        plot_colormaps(cmaps, cols=cols, subplot_size=subplot_size)
    else:
        print(f"No colormaps are available within the category '{category}'.")
