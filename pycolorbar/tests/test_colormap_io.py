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
"""Test the Colormap I/O."""

import os

import numpy as np
import pytest
from deepdiff import DeepDiff

from pycolorbar.settings.colormap_io import read_cmap_dict, write_cmap_dict


@pytest.fixture()
def test_cmap_dict():
    return {
        "colormap_type": "ListedColormap",
        "color_palette": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],  # RGB colors
        "color_space": "rgb",
    }


def test_default_write_read_cmap_dict(tmp_path, test_cmap_dict):
    """Test custom read/write cmap_dict with default colors representation."""
    # Define filepath
    filepath = os.path.join(tmp_path, "test_cmap.yaml")

    # Write cmap dict (encode=True is the default)
    write_cmap_dict(test_cmap_dict, filepath, force=True, encode=True, validate=True)

    # Read cmap dict (decode=True is the default)
    read_dict = read_cmap_dict(filepath, decode=True, validate=True)

    # Assert written and read colors
    assert np.array_equal(read_dict["color_palette"], test_cmap_dict["color_palette"])
    assert np.array_equal(read_dict["color_palette"][0], [1, 0, 0])

    # Assert defaults arguments are decode=True and validate=True
    diff = DeepDiff(read_dict, read_cmap_dict(filepath))
    assert diff == {}, f"Dictionaries are not equal: {diff}"

    # Assert colors with read_cmap_dict (decode=False)
    encoded_dict = read_cmap_dict(filepath, decode=False, validate=True)
    assert np.array_equal(encoded_dict["color_palette"][0], [255, 0, 0])


@pytest.mark.parametrize("validate", [True, False])
def test_custom_write_read_cmap_dict(tmp_path, test_cmap_dict, validate):
    """Test custom read/write cmap_dict with internal representation colors."""
    # Define filepath
    filepath = os.path.join(tmp_path, "test_cmap.yaml")

    # Write cmap dict with encode=False
    write_cmap_dict(test_cmap_dict, filepath, force=True, encode=False, validate=validate)

    # Read cmap dict with decode=False
    read_dict = read_cmap_dict(filepath, decode=False, validate=validate)

    # Assert colors
    assert np.array_equal(read_dict["color_palette"], test_cmap_dict["color_palette"])
    assert np.array_equal(read_dict["color_palette"][0], [1, 0, 0])

    # Assert defaults arguments are decode=True and validate=True
    diff = DeepDiff(read_dict, read_cmap_dict(filepath, decode=True))
    assert diff != {}, f"Dictionaries are not equal: {diff}"


def test_write_invalid_cmap_dict(tmp_path):
    """Test write_cmap_dict with missing keys or colors."""
    # Define filepath
    filepath = os.path.join(tmp_path, "test_cmap.yaml")

    # Test raise error if cmap_dict has no 'color_palette'.
    cmap_dict = {
        "colormap_type": "ListedColormap",
        "color_space": "rgb",
    }
    with pytest.raises(KeyError):
        write_cmap_dict(cmap_dict, filepath, force=True, validate=False)

    # Test raise error if cmap_dict has no 'color_space'.
    cmap_dict = {
        "colormap_type": "ListedColormap",
        "color_palette": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],  # RGB colors
    }
    with pytest.raises(KeyError):
        write_cmap_dict(cmap_dict, filepath, force=True, validate=False)

    # Test raise error if cmap_dict has invalid array dimension (i.e 3D).
    cmap_dict = {
        "colormap_type": "ListedColormap",
        "color_palette": [[[1, 0, 0], [0, 1, 0], [0, 0, 1]]],  # RGB colors
        "color_space": "rgb",
    }
    with pytest.raises(ValueError):
        write_cmap_dict(cmap_dict, filepath, force=True, validate=False)
