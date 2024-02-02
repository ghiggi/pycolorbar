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
"""Define functions to read and write colormap YAML files."""
import os

import numpy as np

from pycolorbar.colors.colors_io import decode_colors as decode_colors_array
from pycolorbar.colors.colors_io import encode_colors as encode_colors_array
from pycolorbar.settings.colormap_validator import validate_cmap_dict
from pycolorbar.utils.yaml import read_yaml, write_yaml


def _get_colors_and_space(cmap_dict):
    if "colors" not in cmap_dict:
        raise KeyError("The colormap dictionary does not contain the 'colors' key.")
    if "color_space" not in cmap_dict:
        raise KeyError("The colormap dictionary does not contain the 'color_space' key.")
    colors = cmap_dict["colors"]
    color_space = cmap_dict["color_space"]
    return colors, color_space


def decode_colors(cmap_dict):
    colors, color_space = _get_colors_and_space(cmap_dict)
    # Convert colors to numpy array
    colors = np.asanyarray(colors)
    # Rescale colors to expected data range (i.e. rgb: 0-255 --> 0-1)
    colors = decode_colors_array(colors, color_space=color_space)
    # Return cmap_dict
    cmap_dict["colors"] = colors
    return cmap_dict


def encode_colors(cmap_dict):
    colors, color_space = _get_colors_and_space(cmap_dict)
    # Encode colors to expected YAML data range (i.e. rgb: 0-1 --> 0-255)
    colors = encode_colors_array(colors, color_space=color_space)
    # Reformat np.array to list of list
    if isinstance(colors, np.ndarray):
        if colors.ndim in [1, 2]:
            colors = colors.tolist()
            cmap_dict["colors"] = colors
        else:
            raise ValueError("Invalid 'colors' numpy array. Should be either 1D or 2D.")
    return cmap_dict


def read_cmap_dict(filepath):
    cmap_dict = read_yaml(filepath)
    cmap_dict = decode_colors(cmap_dict)
    cmap_dict = validate_cmap_dict(cmap_dict)
    return cmap_dict


def write_cmap_dict(cmap_dict, filepath, force=False):
    # Check if file exist
    if os.path.exists(filepath):
        if force:
            os.remove(filepath)
        else:
            raise ValueError(f"The {filepath} already exists !")
    # Validate fields
    cmap_dict = validate_cmap_dict(cmap_dict=cmap_dict)
    # Encode colors
    cmap_dict = encode_colors(cmap_dict)
    # Write file
    write_yaml(cmap_dict, filepath, sort_keys=False)
