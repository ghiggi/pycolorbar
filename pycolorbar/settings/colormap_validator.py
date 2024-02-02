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
"""Implementation of pydantic validator for univariate colormap YAML files."""
import re
from typing import List, Optional

import numpy as np
from pydantic import BaseModel, field_validator

from pycolorbar.colors.colors_io import check_valid_internal_data_range
from pycolorbar.utils.mpl import get_mpl_named_colors


def check_color_space(color_space):
    valid_names = [
        "hex",
        "name",
        "rgb",
        "rgba",
        "hcl",
        "lch",
        "hsv",
        "cieluv",
        "cielab",
        "ciexyz",
        "cmyk",
    ]
    if color_space not in valid_names:
        raise ValueError(f"Invalid color_space '{color_space}'. The supported color spaces are {valid_names}.")


class ColorMapValidator(BaseModel):
    """
    A validator for colormap configurations using Pydantic.

    Validates the fields of a colormap configuration, including the type of colormap,
    the color space, the colors themselves, and the alpha transparency settings.

    Attributes
    ----------
    type : str
        The type of the colormap (e.g., "ListedColormap", "LinearSegmentedColormap").
    color_space : str
        The color space of the colormap (e.g., "rgb", "hsv").
    colors : np.ndarray
        The array of colors defined for the colormap.

    Methods
    -------
    validate_type(cls, v):
        Validates the type field.
    validate_color_space(cls, v):
        Validates the color_space field.
    validate_colors(cls, v, values, **kwargs):
        Validates the colors field.
    """

    type: str
    color_space: str  # colors_type ?
    colors: np.ndarray
    n: Optional[float] = None
    # LinearSegmentedColormap options
    segmentdata: Optional[List[float]] = None
    # gamma: Optional[float] = None

    # TODO:
    # - interpolation_space? 'rgb', ...

    class Config:
        arbitrary_types_allowed = True

    @field_validator("type")
    def validate_type(cls, v):
        valid_types = [
            "ListedColormap",
            "LinearSegmentedColormap",
        ]
        assert isinstance(v, str), "Colormap 'type' must be a string."
        assert v in valid_types, f"Colormap 'type' must be one of {valid_types}"
        return v

    @field_validator("color_space")
    def validate_color_space(cls, v):
        check_color_space(color_space=v)
        return v

    @field_validator("colors")
    def validate_colors(cls, v, values, **kwargs):
        v = np.asanyarray(v)
        color_space = values.data.get("color_space", "")
        validate_colors_values(v, color_space=color_space)
        return v

    @field_validator("segmentdata")
    def validate_segmentdata(cls, v, values):
        if v is not None:
            assert (
                values.data.get("type") == "LinearSegmentedColormap"
            ), "'segmentdata' requires the 'type' 'LinearSegmentedColormap'"
            assert isinstance(v, list), "'segmentdata' must be a list."
            assert all(isinstance(level, (int, float)) for level in v), "'segmentdata' must be a list of numbers."
            assert all(x < y for x, y in zip(v, v[1:])), "'segmentdata' must be monotonically increasing."
        return v


def validate_cmap_dict(cmap_dict: dict):
    # Validate dictionary
    ColorMapValidator(**cmap_dict)
    # Return dictionary
    return cmap_dict


####-------------------------------------------------------------------------------------------------------------------.


def _check_ndim(colors: np.ndarray, expected_ndim: int):
    """
    Checks if the colors array has the expected number of dimensions.

    Parameters
    ----------
    colors : np.ndarray
        The array of colors to validate.
    expected_ndim : int
        The expected number of dimensions for the colors array.

    Raises
    ------
    ValueError
        If the colors array does not have the expected number of dimensions.
    """
    if colors.ndim != expected_ndim:
        raise ValueError(f"Colors array must be {expected_ndim}-D.")


def _check_type(colors: np.ndarray, expected_type: type):
    """
    Checks if the color values in the colors array are of the expected type.

    Parameters
    ----------
    colors : np.ndarray
        The array of colors to validate.
    expected_type : type
        The expected data type(s) of the color values.

    Raises
    ------
    ValueError
        If the color values are not of the expected type.
    """
    if not issubclass(colors.dtype.type, expected_type):
        str_type = str(expected_type)
        raise ValueError(f"Color values must be of type {str_type}.")


def validate_hex_colors(colors: np.ndarray) -> bool:
    """
    Validates the array of HEX colors.

    Parameters
    ----------
    colors : np.ndarray
        The array of colors to validate.

    Raises
    ------
    ValueError
        If the colors array is not 1-D or if any color is not a valid hex string.
    """

    _check_ndim(colors, 1)
    _check_type(colors, np.str_)
    hex_color_pattern = re.compile(r"^#(?:[0-9a-fA-F]{3}){1,2}$")
    if not all(hex_color_pattern.match(color) for color in colors):
        raise ValueError(
            "Invalid color format for 'hex'. "
            "Colors should be strings starting with '#' and followed by 3 or 6 hex digits."
        )


def validate_name_colors(colors: np.ndarray) -> bool:
    """
    Validates the array of named colors.

    For more info on named colors, see https://matplotlib.org/stable/gallery/color/named_colors.html

    Parameters
    ----------
    colors : np.ndarray
        The array of colors to validate.

    Raises
    ------
    ValueError
        If the colors array is not 1-D, if color values are not strings,
        or if any color name is not a valid named color.
    """
    _check_ndim(colors, 1)
    _check_type(colors, np.str_)
    valid_named_colors = get_mpl_named_colors()
    invalid_colors = colors[~np.isin(colors, valid_named_colors)]
    if len(invalid_colors) > 0:
        raise ValueError(f"Invalid named colors: {invalid_colors}.")


def validate_colors_values(colors, color_space):
    """
    Validates the colors array based on the specified color space.

    Parameters
    ----------
    colors : np.ndarray
        The array of colors to validate.
    color_space : str
        The color space of the colors array (e.g., "hex", "rgb", "rgba", etc.).

    Raises
    ------
    ValueError
        If the color_space is not supported or if the colors array fails
        validation checks for the specified color space.
    """
    # Check valid color space
    check_color_space(color_space)
    # Check valid color values
    if color_space == "name":
        validate_name_colors(colors)
    elif color_space == "hex":
        validate_hex_colors(colors)
    else:
        check_valid_internal_data_range(colors, color_space=color_space.upper())


####-------------------------------------------------------------------------------------------------------------------.
