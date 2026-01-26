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
"""Test the Colormap utilities."""

import pytest
from matplotlib.colors import LinearSegmentedColormap, ListedColormap

from pycolorbar.settings.colormap_utility import create_cmap


@pytest.mark.parametrize(
    ("cmap_dict", "expected_type"),
    [
        (
            {
                "colormap_type": "ListedColormap",
                "color_palette": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
                "color_space": "RGB",
            },
            ListedColormap,
        ),
        (
            {
                "colormap_type": "LinearSegmentedColormap",
                "color_palette": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
                "color_space": "RGB",
            },
            LinearSegmentedColormap,
        ),
        (
            {
                "colormap_type": "LinearSegmentedColormap",
                "segmentdata": {
                    "red": [(0, 1, 1), (1, 0, 0)],
                    "green": [(0, 0, 0), (1, 1, 1)],
                    "blue": [(0, 0, 0), (1, 0, 0)],
                },
                "color_space": "RGB",
            },
            LinearSegmentedColormap,
        ),
    ],
)
def test_create_cmap(cmap_dict, expected_type):
    """Test the create_cmap function for different types of colormaps."""
    cmap_name = "test_cmap"
    cmap = create_cmap(cmap_dict, cmap_name)

    # Check if the created colormap is of the expected type
    assert isinstance(cmap, expected_type), f"Created colormap should be an instance of {expected_type.__name__}"

    # Check if the colormap has the correct name
    assert cmap.name == cmap_name, "Colormap name does not match the expected name"
