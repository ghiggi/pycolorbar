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
"""Test univariate colorbar functionalities."""

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pytest
from mpl_toolkits.axes_grid1 import make_axes_locatable

import pycolorbar
from pycolorbar.univariate.colorbar import (
    _get_orientation_location,
    add_colorbar_legend,
    plot_colorbar,
    set_colorbar_fully_transparent,
)


def test_plot_colorbar():
    """Test colorbar plot."""
    # Define cmap
    cmap = pycolorbar.get_cmap("Spectral")

    # Define custom ticks
    data = np.arange(0, 10)
    ticklabels = np.arange(0, 10)
    ticks = np.linspace(0, 10, len(ticklabels))  # in radians

    # Plot colorbar to the sides of the current axis
    p = plt.scatter(data, data, c=data, cmap=cmap)
    p_cbar = plot_colorbar(p, ticks=ticks, ticklabels=ticklabels)
    assert isinstance(p_cbar, mpl.colorbar.Colorbar)
    plt.close()

    # Plot colorbar on the specified axis
    fig, ax = plt.subplots()
    p = ax.scatter(data, data, c=data, cmap=cmap)
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="20%", pad=0.10, axes_class=plt.Axes)
    p.figure.add_axes(cax)
    p_cbar = plot_colorbar(p, ax=ax, cax=cax, ticks=ticks, ticklabels=ticklabels)
    assert isinstance(p_cbar, mpl.colorbar.Colorbar)
    plt.close()

    # Plot colorbar to the sides on an existing axis
    fig, ax = plt.subplots()
    p = plt.scatter(data, data, c=data, cmap=cmap)
    p_cbar = plot_colorbar(p, ax=ax, ticks=ticks, ticklabels=ticklabels)
    assert isinstance(p_cbar, mpl.colorbar.Colorbar)
    plt.close()

    fig, ax = plt.subplots()  # noqa: RUF059
    p = plt.scatter(data, data, c=data, cmap=cmap)
    p_cbar = plot_colorbar(p, ax=ax, ticklabels=ticklabels)  # without ticks !
    assert isinstance(p_cbar, mpl.colorbar.Colorbar)
    plt.close()


class TestGetOrientationLocation:
    """Test arguments for colorbar positioning."""

    def test_defaults(self):
        assert _get_orientation_location({}) == ("vertical", "right")

    def test_defaults_with_valid_orientation(self):
        assert _get_orientation_location({"orientation": "vertical"}) == ("vertical", "right")
        assert _get_orientation_location({"orientation": "horizontal"}) == ("horizontal", "bottom")

    def test_defaults_with_valid_location(self):
        assert _get_orientation_location({"location": "left"}) == ("vertical", "left")
        assert _get_orientation_location({"location": "bottom"}) == ("horizontal", "bottom")

    def test_valid_orientation_location_combinations(self):
        assert _get_orientation_location({"orientation": "horizontal", "location": "top"}) == ("horizontal", "top")
        assert _get_orientation_location({"orientation": "vertical", "location": "left"}) == ("vertical", "left")

    def test_invalid_orientation(self):
        with pytest.raises(ValueError):
            _get_orientation_location({"orientation": "invalid"})

    def test_invalid_location(self):
        with pytest.raises(ValueError):
            _get_orientation_location({"location": "invalid"})

    def test_invalid_orientation_location_combination(self):
        with pytest.raises(ValueError):
            _get_orientation_location({"orientation": "vertical", "location": "top"})

        with pytest.raises(ValueError):
            _get_orientation_location({"orientation": "horizontal", "location": "left"})


def test_plot_colorbar_orientation_and_location():
    # Define cmap
    cmap = pycolorbar.get_cmap("Spectral")

    # Define data
    data = np.arange(0, 10)

    # Check correct couple
    p = plt.scatter(data, data, c=data, cmap=cmap)
    plot_colorbar(p, ax=p.axes, orientation="horizontal", location="bottom")
    plt.close()

    # Raise error for invalid orientation
    p = plt.scatter(data, data, c=data, cmap=cmap)
    with pytest.raises(ValueError):
        plot_colorbar(p, ax=p.axes, orientation="bad")

    # Raise error for invalid location
    p = plt.scatter(data, data, c=data, cmap=cmap)
    with pytest.raises(ValueError):
        plot_colorbar(p, ax=p.axes, location="bad")

    # Raise error for invalid location, orientation options
    p = plt.scatter(data, data, c=data, cmap=cmap)
    with pytest.raises(ValueError):
        plot_colorbar(p, ax=p.axes, location="right", orientation="horizontal")

    p = plt.scatter(data, data, c=data, cmap=cmap)
    with pytest.raises(ValueError):
        plot_colorbar(p, ax=p.axes, location="top", orientation="vertical")

    # Use defaults location/orientation
    p = plt.scatter(data, data, c=data, cmap=cmap)
    plot_colorbar(p, ax=p.axes, orientation="horizontal")
    plt.close()

    p = plt.scatter(data, data, c=data, cmap=cmap)
    plot_colorbar(p, ax=p.axes, orientation="vertical")
    plt.close()

    p = plt.scatter(data, data, c=data, cmap=cmap)
    plot_colorbar(p, ax=p.axes, orientation="horizontal")
    plt.close()

    p = plt.scatter(data, data, c=data, cmap=cmap)
    plot_colorbar(p, ax=p.axes, location="left")
    plt.close()

    p = plt.scatter(data, data, c=data, cmap=cmap)
    plot_colorbar(p, ax=p.axes, location="top")
    plt.close()


def test_add_colorbar_legend():
    """Test adding a colorbar legend to a plot."""
    # Define cmap
    cmap = pycolorbar.get_cmap("Spectral")

    # Define data
    data = np.arange(0, 10)

    # Create plot
    p = plt.scatter(data, data, c=data, cmap=cmap)
    # Add legend
    p_cbar = add_colorbar_legend(
        mappable=p,
        ax=p.axes,
        # Inset options
        box_aspect=4,
        height=0.1,
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
        orientation="horizontal",
    )
    assert isinstance(p_cbar, mpl.colorbar.Colorbar)
    plt.close()


def test_set_colorbar_fully_transparent():
    """Test setting a colorbar fully transparent."""
    # Define cmap
    cmap = pycolorbar.get_cmap("Spectral")

    # Define data
    data = np.arange(0, 10)

    # Set colorbar fully transparent
    p = plt.scatter(data, data, c=data, cmap=cmap)
    _ = plot_colorbar(p, ax=p.axes)
    set_colorbar_fully_transparent(p=p)
    plt.close()
