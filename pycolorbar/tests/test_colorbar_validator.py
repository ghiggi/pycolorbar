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
"""Test ColorbarValidator."""
import os

import pytest
from pydantic import ValidationError

from pycolorbar.settings.colorbar_validator import (
    UnivariateCmapSettings,
    check_norm_settings,
)
from pycolorbar.settings.colormap_registry import ColorMapRegistry
from pycolorbar.utils.yaml import write_yaml


@pytest.fixture
def setup_pycolorbar_colormap(tmp_path):
    """Fixture that register a colormap for testing purpose."""
    PYCOLORBAR_CMAP_NAME = "pycolorbar_test_colormap"
    TEST_CMAP_DICT = {"type": "ListedColormap", "colors": ["#ff0000", "#00ff00", "#0000ff"], "color_space": "hex"}

    # Initialize pycolorbar.colormap registry
    registry = ColorMapRegistry.get_instance()
    registry.reset()

    cmap_filepath = os.path.join(tmp_path, f"{PYCOLORBAR_CMAP_NAME}.yaml")
    write_yaml(TEST_CMAP_DICT, cmap_filepath)

    registry.register(cmap_filepath)

    yield PYCOLORBAR_CMAP_NAME  # Provide the colormap name to the test

    # Cleanup: Reset the registry after the test to ensure isolation
    registry.reset()
    os.remove(cmap_filepath)


class TestCmapSettings:
    @pytest.mark.parametrize(
        "cmap_name",
        [
            "viridis",  # valid single matplotlib name
            ["viridis", "plasma"],  # valid list of names
            "pycolorbar_test_colormap",  # valid single pycolorbar colormap name
        ],
    )
    def test_valid_cmap_name(self, cmap_name, setup_pycolorbar_colormap):
        """Test valid colormap names."""
        cmap_settings = {"name": cmap_name, "n": 256}
        if isinstance(cmap_name, list):
            cmap_settings["n"] = [256, 256]
        validated = UnivariateCmapSettings(**cmap_settings)
        assert validated.name == cmap_name

    @pytest.mark.parametrize(
        "cmap_name",
        [
            "not_a_colormap",  # invalid single name
            ["viridis", "not_a_colormap"],  # list with an invalid name
        ],
    )
    def test_invalid_cmap_name(self, cmap_name):
        """Test invalid colormap names."""
        cmap_settings = {"name": cmap_name}
        with pytest.raises(ValidationError):
            _ = UnivariateCmapSettings(**cmap_settings)

    @pytest.mark.parametrize(
        "n",
        [
            256,  # valid single integer
            [256, 128],  # valid list of integers
        ],
    )
    def test_valid_n(self, n):
        """Test valid 'n' values."""
        cmap_settings = {"name": "viridis" if isinstance(n, int) else ["viridis", "plasma"], "n": n}
        validated = UnivariateCmapSettings(**cmap_settings)
        assert validated.n == n

    @pytest.mark.parametrize(
        "n",
        [
            0,  # invalid single integer
            [256, -1],  # invalid list of integers
        ],
    )
    def test_invalid_n(self, n):
        """Test invalid 'n' values."""
        cmap_settings = {"name": "viridis" if isinstance(n, int) else ["viridis", "plasma"], "n": n}
        with pytest.raises(ValidationError):
            _ = UnivariateCmapSettings(**cmap_settings)

    @pytest.mark.parametrize(
        "color",
        [
            "#ff0000",  # valid hex
            (1, 0, 0),  # valid RGB tuple
            [1, 0, 0],  # valid RGB tuple
            (1, 0, 0, 1),  # valid RGBA tuple (if bad/over/under alpha provided ... RGB alpha will be overwritten !)
            "red",  # valid named color
        ],
    )
    def test_valid_colors(self, color):
        """Test valid colors for 'bad_color', 'over_color', 'under_color'."""
        cmap_settings = {"name": "viridis", "bad_color": color, "over_color": color, "under_color": color}
        validated = UnivariateCmapSettings(**cmap_settings)
        if isinstance(color, tuple):
            color = list(color)
        assert validated.bad_color == color
        assert validated.over_color == color
        assert validated.under_color == color

    @pytest.mark.parametrize(
        "color",
        [
            "not_a_color",  # invalid named color
            "#ZZZZZZ",  # invalid hex
            (256, 256, 256),  # invalid RGB tuple
            (0, 1),  # invalid format
        ],
    )
    def test_invalid_colors(self, color):
        """Test invalid colors for 'bad_color', 'over_color', 'under_color'."""
        cmap_settings = {"name": "viridis", "bad_color": color, "over_color": color, "under_color": color}
        with pytest.raises(ValidationError):
            _ = UnivariateCmapSettings(**cmap_settings)


class TestNormSettings:
    @pytest.mark.parametrize(
        "norm_settings",
        [
            # Testing Normalize settings
            {"name": "Norm", "vmin": 0, "vmax": 1, "clip": False},
            # Testing NoNorm settings
            {"name": "NoNorm", "vmin": None, "vmax": None, "clip": True},
            # Testing BoundaryNorm settings with valid boundaries and extend options
            {"name": "BoundaryNorm", "boundaries": [0, 0.5, 1], "ncolors": 2, "clip": False, "extend": "neither"},
            {"name": "BoundaryNorm", "boundaries": [0, 0.5, 1], "ncolors": 4, "clip": False, "extend": "both"},
            {"name": "BoundaryNorm", "boundaries": [0, 0.5, 1], "ncolors": 3, "clip": False, "extend": "min"},
            {"name": "BoundaryNorm", "boundaries": [0, 0.5, 1], "ncolors": 3, "clip": False, "extend": "max"},
            # Testing TwoSlopeNorm settings
            {"name": "TwoSlopeNorm", "vcenter": 0.5, "vmin": 0, "vmax": 1},
            {"name": "TwoSlopeNorm", "vcenter": 0.5},
            # Testing CenteredNorm settings
            {"name": "CenteredNorm", "vcenter": 0, "halfrange": 1, "clip": False},
            # Testing LogNorm settings
            {"name": "LogNorm", "vmin": 1, "vmax": 100, "clip": False},
            # Testing SymLogNorm settings
            {
                "name": "SymLogNorm",
                "linthresh": 0.1,
                "linscale": 1,
                "base": 10,
                "vmin": 0.01,
                "vmax": 100,
                "clip": False,
            },
            # Testing PowerNorm settings
            {"name": "PowerNorm", "gamma": 0.5, "vmin": 0, "vmax": 1, "clip": False},
            # Testing AsinhNorm settings
            {"name": "AsinhNorm", "linear_width": 1, "vmin": -10, "vmax": 10, "clip": False},
            # Testing CategoryNorm settings with a valid list of labels
            {"name": "CategoryNorm", "labels": ["low", "medium", "high"], "first_value": 0},
        ],
    )
    def test_valid_norm_settings(self, norm_settings):
        """Test that valid normalization settings are accepted without raising errors."""
        # Check that do not raise error
        check_norm_settings(norm_settings)

    @pytest.mark.parametrize(
        "norm_settings, expected_error_msg",
        [
            # Invalid Normalize settings due to incorrect vmin and vmax
            ({"name": "Norm", "vmin": 1, "vmax": 0}, "vmin must be less than vmax"),
            # Invalid BoundaryNorm settings due to non-monotonically increasing boundaries
            (
                {"name": "BoundaryNorm", "boundaries": [1, 0.5, 0], "ncolors": 2},
                "'boundaries' must be monotonically increasing",
            ),
            # Invalid TwoSlopeNorm settings due to vcenter not being between vmin and vmax
            ({"name": "TwoSlopeNorm", "vcenter": 0.5, "vmin": 0.5, "vmax": 1}, "'vmin' must be less than 'vcenter'"),
            ({"name": "TwoSlopeNorm", "vcenter": 0.5, "vmin": 0, "vmax": 0.5}, "'vmax' must be larger than 'vcenter'"),
            # Invalid LogNorm settings due to vmin being non-positive
            ({"name": "LogNorm", "vmin": -1, "vmax": 100}, "LogNorm vmin should be a positive value."),
            # Invalid SymLogNorm settings due to negative linthresh
            (
                {"name": "SymLogNorm", "linthresh": -0.1, "linscale": 1, "vmin": 0.01, "vmax": 100},
                "'linthresh' must be positive for 'SymLogNorm'",
            ),
            # Invalid CategoryNorm settings due to empty labels list
            ({"name": "CategoryNorm", "labels": []}, "'labels' must have at least two strings"),
            ({"name": "CategoryNorm", "labels": ["one"]}, "'labels' must have at least two strings"),
            ({"name": "CategoryNorm", "labels": [1, 2]}, "Input should be a valid string"),
            # Example of an invalid normalization type
            ({"name": "InvalidNormName", "vmin": 0, "vmax": 1}, "Invalid norm 'InvalidNormName'. Valid options are "),
        ],
    )
    def test_invalid_norm_settings(self, norm_settings, expected_error_msg):
        """Test that invalid normalization settings raise appropriate exceptions with specific error messages."""
        with pytest.raises(ValueError) as exc_info:
            check_norm_settings(norm_settings)
        assert expected_error_msg in str(exc_info.value)

    @pytest.mark.parametrize(
        "norm_name, extra_param",
        [
            ("Norm", {"unexpected": 123}),
            ("BoundaryNorm", {"boundaries": [0, 1], "extra": "not valid"}),
            ("CategoryNorm", {"labels": ["a", "b"], "clip": True}),
            ("TwoSlopeNorm", {"vcenter": 0.5, "clip": True}),
            ("CenteredNorm", {"vmin": 0, "vmax": 1}),
        ],
    )
    def test_invalid_arguments(self, norm_name, extra_param):
        norm_settings = {"name": norm_name, **extra_param}
        with pytest.raises(ValueError):
            check_norm_settings(norm_settings)

    @pytest.mark.parametrize(
        "norm_name, missing_param",
        [
            ("BoundaryNorm", {}),
            ("TwoSlopeNorm", {"vmin": 0}),
        ],
    )
    def test_missing_parameters(self, norm_name, missing_param):
        norm_settings = {"name": norm_name, **missing_param}
        with pytest.raises(ValueError):
            check_norm_settings(norm_settings)


# @pytest.mark.parametrize("cmap_settings", [
#     ({"name": "viridis"}),  # valid single name
#     ({"name": ["viridis", "plasma"], "n": [256, 256]}),  # valid list
#     # Add more...
# ])
# def test_validate_cmap_settings(cmap_settings):
#     """Test cmap settings validation."""
#     # Assuming a simplified cbar_dict structure for illustration
#     cbar_dict = {"cmap": cmap_settings, "norm": {}, "cbar": {}}
#     assert validate_cbar_dict(cbar_dict) == cbar_dict  # Expects to pass without ValidationError

# # two cmaps --> twoslopenorm required ?


# @pytest.mark.parametrize("norm_settings", [
#     ({"name": "Normalize", "vmin": 0, "vmax": 1}),  # valid Normalize settings
#     # Add more for each norm type...
# ])
# def test_validate_norm_settings(norm_settings):
#     """Test norm settings validation."""
#     cbar_dict = {"cmap": {}, "norm": norm_settings, "cbar": {}}
#     assert validate_cbar_dict(cbar_dict) == cbar_dict
