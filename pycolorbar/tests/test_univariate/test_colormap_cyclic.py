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
import pytest

import pycolorbar
from pycolorbar.univariate import (
    get_discrete_cyclic_cmap,
    plot_circular_colormap,
)


def test_get_discrete_cyclic_cmap():
    """Test creation of cyclic colormap."""
    cmap = pycolorbar.get_cmap("twilight")
    n = 12
    cmap_discrete = get_discrete_cyclic_cmap(cmap, n)
    assert cmap_discrete.N == 12


@pytest.mark.parametrize("clockwise", [True, False])
def test_plot_circular_colormap(clockwise):
    """Test plotting of circular colormap."""
    cmap = pycolorbar.get_cmap("twilight")
    p = plot_circular_colormap(cmap, add_contour=True, add_title=True, clockwise=clockwise)
    assert isinstance(p, mpl.collections.QuadMesh)
    plt.close()


def test_plot_circular_colormap_with_axes():
    """Test plotting of circular colormap on a specific axis."""
    cmap = pycolorbar.get_cmap("twilight")
    # Assert raise error if provided axis is not polar projection
    fig, ax = plt.subplots()
    with pytest.raises(ValueError):
        plot_circular_colormap(cmap, ax=ax)

    # Assert works if axis is in polar projection
    fig, ax = plt.subplots(subplot_kw={"projection": "polar"})
    p = plot_circular_colormap(cmap, ax=ax)
    assert isinstance(p, mpl.collections.QuadMesh)
    plt.close()
