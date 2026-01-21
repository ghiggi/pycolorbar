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
"""Test circular colorbar functionalities."""
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pytest

import pycolorbar
from pycolorbar.univariate import add_circular_colorbar_legend, get_discrete_cyclic_cmap, plot_circular_colorbar


def test_plot_circular_colorbar_polar():
    """Test circular colorbar plot using polar projection."""
    # Define cmap
    n = 24
    cmap = pycolorbar.get_cmap("twilight")
    cmap = get_discrete_cyclic_cmap(cmap, n)

    # Define custom ticks
    ticklabels = np.arange(0, n)
    ticks = np.linspace(0, 2 * np.pi - (2 * np.pi / len(ticklabels)), len(ticklabels))  # in radians

    # Plot colorbar on a new axis
    p = plot_circular_colorbar(cmap, use_wedges=False, ticks=ticks, ticklabels=ticklabels)
    assert isinstance(p, mpl.collections.QuadMesh)
    plt.close()

    # Plot colorbar on an specific axis
    fig, cax = plt.subplots(subplot_kw={"projection": "polar"})
    p = plot_circular_colorbar(cmap, cax=cax, use_wedges=False, ticks=ticks, ticklabels=ticklabels)
    assert isinstance(p, mpl.collections.QuadMesh)
    plt.close()

    # Plot colorbar to the sides on an existing axis
    fig, ax = plt.subplots()  # noqa: RUF059
    ax.scatter([0, 1, 2], [0, 1, 2])
    p = plot_circular_colorbar(cmap, ax=ax, use_wedges=False, ticks=ticks, ticklabels=ticklabels)
    assert isinstance(p, mpl.collections.QuadMesh)
    plt.close()


def test_plot_circular_colorbar_wedges():
    """Test circular colorbar plot using wedges."""
    # Define cmap
    n = 24
    cmap = pycolorbar.get_cmap("twilight")
    cmap = get_discrete_cyclic_cmap(cmap, n)

    # Define custom ticks
    ticklabels = np.arange(0, n)
    ticks = np.linspace(0, 2 * np.pi - (2 * np.pi / len(ticklabels)), len(ticklabels))  # in radians

    # Plot colorbar on a new axis
    p = plot_circular_colorbar(cmap, use_wedges=True, ticks=ticks, ticklabels=ticklabels)
    assert isinstance(p, mpl.collections.PatchCollection)
    plt.close()

    # Plot colorbar on an specific axis
    fig, cax = plt.subplots()
    p = plot_circular_colorbar(cmap, cax=cax, use_wedges=True, ticks=ticks, ticklabels=ticklabels)
    assert isinstance(p, mpl.collections.PatchCollection)
    plt.close()

    # Plot colorbar to the sides on an existing axis
    fig, ax = plt.subplots()  # noqa: RUF059
    ax.scatter([0, 1, 2], [0, 1, 2])
    p = plot_circular_colorbar(cmap, ax=ax, use_wedges=True, ticks=ticks, ticklabels=ticklabels)
    assert isinstance(p, mpl.collections.PatchCollection)
    plt.close()


@pytest.mark.parametrize("use_wedges", [True, False])
def test_add_circular_colorbar_legend(use_wedges):
    """Test adding a circular colorbar legend to a plot."""
    # Define cmap
    n = 24
    cmap = pycolorbar.get_cmap("twilight")
    cmap = get_discrete_cyclic_cmap(cmap, n)
    # Create plot
    fig, ax = plt.subplots()  # noqa: RUF059
    ax.scatter([0, 1, 2], [0, 1, 2])
    # Add legend
    p = add_circular_colorbar_legend(
        cmap=cmap,
        ax=ax,
        # Inset options
        box_aspect=1,
        height=0.2,
        pad=0.005,
        loc="upper right",
        inside_figure=True,
        optimize_layout=True,
        # Fancybox options
        fancybox=False,
        fancybox_pad=0,
        fancybox_fc="white",
        fancybox_ec="none",
        fancybox_lw=0.5,
        fancybox_alpha=0.4,
        fancybox_shape="square",
        # Colorbar options
        use_wedges=use_wedges,
        add_contour=True,
    )
    if use_wedges:
        assert isinstance(p, mpl.collections.PatchCollection)
    else:
        assert isinstance(p, mpl.collections.QuadMesh)
    plt.close()
