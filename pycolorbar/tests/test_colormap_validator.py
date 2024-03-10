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
"""Test the ColormapValidator."""

import numpy as np
import pytest
from pydantic import ValidationError

from pycolorbar.settings.colormap_validator import validate_cmap_dict


class TestColormapColorPalette:
    """
    Tests for validating color map configurations related to colors.
    """

    def test_valid_hex_colors(self):
        """Validate a colormap dictionary with valid hex colors."""
        cmap_dict = {
            "colormap_type": "ListedColormap",
            "color_space": "hex",
            "color_palette": np.array(["#000000", "#FFFFFF"]),
        }
        validated_dict = validate_cmap_dict(cmap_dict)
        assert isinstance(validated_dict, dict)

    def test_valid_named_colors(self):
        """Validate a colormap dictionary with valid named colors."""
        cmap_dict = {
            "colormap_type": "ListedColormap",
            "color_space": "name",
            "color_palette": np.array(["red", "blue"]),
        }
        validated_dict = validate_cmap_dict(cmap_dict)
        assert isinstance(validated_dict, dict)

    @pytest.mark.parametrize(
        "color_space,colors",
        [
            ("hex", np.array(["#GGGGGG", "invalid1"])),  # Invalid hex code
            ("name", np.array(["not_a_color", "not_a_color1"])),  # Invalid color name
            ("name", np.array([["red", "blue"]])),  # Not 1D
            ("name", np.array([1, 2])),  # Unexpected type
            ("hex", np.array([1, 2])),  # Unexpected type
        ],
    )
    def test_invalid_colors(self, color_space, colors):
        """Validate colormap dictionaries with invalid color specifications."""
        cmap_dict = {"colormap_type": "ListedColormap", "color_space": color_space, "color_palette": colors}
        with pytest.raises(ValidationError):
            validate_cmap_dict(cmap_dict)

    def test_colors_list(self):
        """Validate a colormap dictionary with colors not provided as np.ndarray."""
        cmap_dict = {"colormap_type": "ListedColormap", "color_space": "hex", "color_palette": ["#000000", "#FFFFFF"]}
        cmap_dict = validate_cmap_dict(cmap_dict)
        assert isinstance(cmap_dict["color_palette"], np.ndarray)

    def test_colors_is_empty(self):
        """Validate a colormap dictionary with colors not provided as np.ndarray."""
        cmap_dict = {
            "colormap_type": "ListedColormap",
            "color_space": "hex",
            "color_palette": None,
        }
        with pytest.raises(ValidationError):
            validate_cmap_dict(cmap_dict)

    def test_colors_empty_array(self):
        """Validate handling of an empty colors array."""
        cmap_dict = {"colormap_type": "ListedColormap", "color_space": "name", "color_palette": np.array([])}
        with pytest.raises(ValidationError) as excinfo:
            validate_cmap_dict(cmap_dict)
        assert "The 'color_palette' array must not be empty" in str(
            excinfo.value
        ), "Empty colors array should raise ValueError."

    def test_colors_at_least_2(self):
        """Validate handling of a colors array with only 1 color."""
        cmap_dict = {"colormap_type": "ListedColormap", "color_space": "name", "color_palette": np.array(["red"])}
        with pytest.raises(ValidationError) as excinfo:
            validate_cmap_dict(cmap_dict)
        assert "The 'color_palette' array must have at least 2 colors." in str(
            excinfo.value
        ), "Array with only 1 color should raise ValueError."

    def test_rgba_colors_with_valid_alpha(self):
        """Validate a colormap dictionary with valid RGB colors and an alpha channel."""
        cmap_dict = {
            "colormap_type": "ListedColormap",
            "color_space": "rgba",
            "color_palette": np.array([[0, 0, 0, 100], [255, 255, 255, 0]]),  # RGBA values (alpha max is 100)
        }
        validated_dict = validate_cmap_dict(cmap_dict, decoded_colors=False)
        assert np.array_equal(
            validated_dict["color_palette"], cmap_dict["color_palette"]
        ), "Valid RGBA colors should pass validation."

    def test_rgba_colors_with_invalid_alpha(self):
        """Validate a colormap dictionary with valid RGB colors and an invalid alpha channel."""
        cmap_dict = {
            "colormap_type": "ListedColormap",
            "color_space": "rgba",
            "color_palette": np.array([[0, 0, 0, 255], [255, 255, 255, -1]]),  # Invalid alpha values
        }
        with pytest.raises(ValidationError) as excinfo:
            validate_cmap_dict(cmap_dict, decoded_colors=False)
        assert "Channel 'A' values are not within the external data range. Expected range (0, 100)" in str(
            excinfo.value
        ), "Invalid alpha values should raise ValueError."


class TestColormapColorSpace:
    """Tests for validating color map configurations related to color_space."""

    def test_invalid_color_space(self):
        """
        Test color map validation with an invalid color space.
        """
        cmap_dict = {
            "colormap_type": "ListedColormap",
            "color_space": "invalid_color_space",
            "color_palette": np.array(["#000000", "#FFFFFF"]),
        }
        with pytest.raises(ValidationError) as excinfo:
            validate_cmap_dict(cmap_dict)
        assert "Invalid color_space" in str(excinfo.value), "Invalid color space should raise ValueError."


class TestColormapSegmentData:
    """Tests for validating color map configurations related to segmentdata."""

    def test_valid_segmentdata(self):
        """
        Validate a colormap dictionary with valid segmentdata for a LinearSegmentedColormap.
        """
        segment_data = {
            "red": [(0.0, 0.0, 0.0), (0.5, 1.0, 1.0), (1.0, 1.0, 1.0)],
            "green": [(0.0, 0.0, 0.0), (0.25, 0.0, 0.0), (0.75, 1.0, 1.0), (1.0, 1.0, 1.0)],
            "blue": [(0.0, 0.0, 0.0), (0.5, 0.0, 0.0), (1.0, 1.0, 1.0)],
        }

        cmap_dict = {
            "colormap_type": "LinearSegmentedColormap",
            "color_space": "rgb",
            "segmentdata": segment_data,
        }
        validated_dict = validate_cmap_dict(cmap_dict)
        assert isinstance(validated_dict, dict)

    def test_invalid_segmentdata(self):
        """Test segmentdata validation with non-monotonically increasing values."""
        # Monotonically increasing x (first tuple value)
        segment_data = {
            "red": [(0.0, 0.0, 0.0), (0.5, 1.0, 1.0), (1.0, 1.0, 1.0)],
            "green": [(0.0, 0.0, 0.0), (0.25, 0.0, 0.0), (0.75, 1.0, 1.0), (1.0, 1.0, 1.0)],
            "blue": [(1.0, 0.0, 0.0), (0.5, 0.0, 0.0), (1.0, 1.0, 1.0)],  # not monotonically increasing
        }
        cmap_dict = {
            "colormap_type": "LinearSegmentedColormap",
            "color_space": "rgb",
            "segmentdata": segment_data,
        }
        with pytest.raises(ValidationError) as excinfo:
            validate_cmap_dict(cmap_dict)
        assert "must be monotonically increasing" in str(excinfo.value)

        # Tuple of size 3
        segment_data = {
            "red": [(0.0, 0.0, 0.0, 1.0), (0.5, 1.0, 1.0), (1.0, 1.0, 1.0)],
            "green": [(0.0, 0.0, 0.0), (0.25, 0.0, 0.0), (0.75, 1.0, 1.0), (1.0, 1.0, 1.0)],
            "blue": [(0.0, 0.0, 0.0), (0.5, 0.0, 0.0), (1.0, 1.0, 1.0)],
        }
        cmap_dict = {
            "colormap_type": "LinearSegmentedColormap",
            "color_space": "rgb",
            "segmentdata": segment_data,
        }
        with pytest.raises(ValidationError) as excinfo:
            validate_cmap_dict(cmap_dict)
        assert "a tuple of three floats" in str(excinfo.value)


class TestColormapType:
    """Tests for validating color map configurations related to colormap type."""

    @pytest.mark.parametrize("cmap_type", ["ListedColormap", "LinearSegmentedColormap"])
    def test_valid_type_listed_colormap(self, cmap_type):
        """Validate a colormap dictionary with a valid type of ListedColormap."""
        cmap_dict = {"colormap_type": cmap_type, "color_space": "name", "color_palette": np.array(["red", "blue"])}
        validated_dict = validate_cmap_dict(cmap_dict)
        assert isinstance(validated_dict, dict)

    def test_invalid_type(self):
        """Test type validation with an unsupported colormap type."""
        cmap_dict = {
            "colormap_type": "UnsupportedColormap",
            "color_space": "rgb",
            "color_palette": np.array([[0, 0, 0], [1, 1, 1]]),
        }
        with pytest.raises(ValidationError) as excinfo:
            validate_cmap_dict(cmap_dict)
        assert "'colormap_type' must be one of" in str(excinfo.value)


class TestColormapN:
    """Tests for validating color map configurations related to N."""

    @pytest.mark.parametrize("n_value", [10, None])  # Testing both specified and default values
    def test_optional_n_field(self, n_value):
        """Validate handling of the optional 'n' field in colormap configurations."""
        cmap_dict = {
            "colormap_type": "ListedColormap",
            "color_space": "rgb",
            "color_palette": np.array([[0, 0, 0], [1, 1, 1]]),
            "n": n_value,
        }
        validated_dict = validate_cmap_dict(cmap_dict)
        assert validated_dict["n"] == n_value, "'n' field should match the specified value or default."


def test_colormap_strict_arguments():
    """Test that no extra keys are allowed in the colormap configuration."""
    cmap_dict = {
        "name": "SHOULD_NOT_BE_ACCEPTED",
        "colormap_type": "ListedColormap",
        "color_space": "rgb",
        "color_palette": np.array([[0, 0, 0], [1, 1, 1]]),
    }
    with pytest.raises(ValidationError):
        validate_cmap_dict(cmap_dict)
