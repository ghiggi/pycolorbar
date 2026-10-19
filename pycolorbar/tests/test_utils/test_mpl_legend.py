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
"""Test matplotlib legend utilities."""

import matplotlib as mpl
import matplotlib.pyplot as plt
import pytest
from matplotlib.transforms import Bbox

from pycolorbar.utils.mpl_legend import (
    add_colorbar_inset,
    add_fancybox,
    get_inset_bounds,
    get_location_origin,
    get_locations_acronyms,
    get_tightbbox_position,
    optimize_inset_position,
)


def test_get_locations_acronyms():
    """Test that get_locations_acronyms returns a list of valid acronyms."""
    locations = get_locations_acronyms()
    assert isinstance(locations, list)
    assert "upper right" in locations
    assert "lower left" in locations


class TestGetLocationOrigin:
    def test_valid(self):
        """Test get_location_origin returns correct origin for a known loc."""
        x0, y0 = get_location_origin("upper right", 0.2, 0.1, 0.01, 0.02)
        assert x0 == 0.79
        assert y0 == 0.88

    def test_invalid(self):
        """Test get_location_origin raises ValueError for invalid loc."""
        with pytest.raises(ValueError):
            get_location_origin("invalid", 0.2, 0.1, 0.01, 0.02)


class TestGetInsetBounds:

    @pytest.mark.parametrize("inside_figure", [True, False])
    def test_by_position(self, inside_figure):
        """Test get_inset_bounds returns expected bounds."""
        fig, ax = plt.subplots()  # noqa: RUF059
        bounds = get_inset_bounds(
            ax=ax,
            loc="upper right",
            inset_height=0.1,
            inside_figure=inside_figure,
            aspect_ratio=1,
            border_pad=0.01,
        )
        assert len(bounds) == 4

    def test_by_location(self):
        """Test get_inset_bounds returns expected bounds."""
        x0 = 0.5
        y0 = 0.4
        loc = (x0, y0)
        fig, ax = plt.subplots()  # noqa: RUF059
        bounds = get_inset_bounds(
            ax=ax,
            loc=(0.5, 0.4),
            inset_height=0.1,
            aspect_ratio=1,
            border_pad=0,
        )
        assert tuple(bounds[0:2]) == loc


def test_tightbbox_position():
    """Test get_tightbbox_position returns bbox in figure coords."""
    fig, ax = plt.subplots()  # noqa: RUF059
    bbox = get_tightbbox_position(ax)
    assert bbox.width >= 0
    assert bbox.height >= 0


def test_optimize_inset_position():
    """Test optimize_inset_position modifies cax position."""
    fig, ax = plt.subplots()  # noqa: RUF059
    cax = ax.inset_axes([0.7, 0.7, 0.2, 0.2])
    new_pos = optimize_inset_position(ax, cax, pad=0.01)
    assert new_pos.width == cax.get_position().width


def test_add_fancybox():
    """Test add_fancybox returns a FancyBboxPatch."""
    fig, ax = plt.subplots()  # noqa: RUF059
    bbox = Bbox.from_extents(0.5, 0.5, 0.6, 0.6)
    patch = add_fancybox(ax, bbox)
    assert isinstance(patch, mpl.patches.FancyBboxPatch)


def test_add_colorbar_inset():
    """Test add_colorbar_inset returns the created colorbar artist."""
    fig, ax = plt.subplots()  # noqa: RUF059

    def dummy_func(cax, **kwargs):
        return cax.imshow([[1, 2], [3, 4]])

    p_cbar = add_colorbar_inset(ax=ax, colorbar_func=dummy_func, colorbar_func_kwargs={}, height=0.3, fancybox=True)
    assert p_cbar is not None
