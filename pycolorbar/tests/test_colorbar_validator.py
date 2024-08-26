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
from contextlib import contextmanager

import pytest
from pydantic import ValidationError

from pycolorbar.settings.colorbar_registry import ColorbarRegistry
from pycolorbar.settings.colorbar_validator import (
    ColorbarSettings,
    ColormapSettings,
    check_norm_settings,
    validate_cbar_dict,
)
from pycolorbar.settings.colormap_registry import ColormapRegistry
from pycolorbar.utils.yaml import write_yaml

TEST_CBAR_NAME = "pycolorbar_test_colorbar"
TEST_CMAP_NAME = "pycolorbar_test_colormap"

TEST_CBAR_DICT = {
    "cmap": {"name": "viridis"},
    "norm": {"name": "Norm", "vmin": 0, "vmax": 1},
    "cbar": {"extend": "neither"},
}

TEST_CMAP_DICT = {
    "colormap_type": "ListedColormap",
    "color_palette": ["#ff0000", "#00ff00", "#0000ff"],
    "color_space": "hex",
}


@pytest.fixture()
def setup_colormap_registry(tmp_path):
    """Fixture that register a colormap for testing purpose."""
    # Initialize pycolorbar.colormap registry
    registry = ColormapRegistry.get_instance()
    registry.reset()

    cmap_filepath = os.path.join(tmp_path, f"{TEST_CMAP_NAME}.yaml")
    write_yaml(TEST_CMAP_DICT, cmap_filepath)

    registry.register(cmap_filepath)

    yield TEST_CMAP_NAME  # Provide the colormap name to the test

    # Cleanup: Reset the registry after the test to ensure isolation
    registry.reset()
    os.remove(cmap_filepath)


@pytest.fixture()
def setup_colorbar_registry(tmp_path):
    """Fixture that register a colormap for testing purpose."""
    TEST_COLORBAR_DICT = {TEST_CBAR_NAME: TEST_CBAR_DICT}

    # Initialize pycolorbar.colorbar registry
    registry = ColorbarRegistry.get_instance()
    registry.reset()

    cbar_filepath = os.path.join(tmp_path, "test_colorbar_settings.yaml")
    write_yaml(TEST_COLORBAR_DICT, cbar_filepath)

    registry.register(cbar_filepath)

    yield TEST_CBAR_NAME  # Provide the colormap name to the test

    # Cleanup: Reset the registry after the test to ensure isolation
    registry.reset()
    os.remove(cbar_filepath)


@contextmanager
def register_temporary_colorbars(input_dict, name=None, multiple=False):
    """A context manager to register one or multiple dictionaries.

    It resets the registry on exit.
    """
    registry = ColorbarRegistry.get_instance()
    registry.reset()
    if multiple:
        _ = [registry.add_cbar_dict(cbar_dict=cbar_dict, name=name) for name, cbar_dict in input_dict.items()]
    else:
        registry.add_cbar_dict(cbar_dict=input_dict, name=name)
    try:
        yield registry

    finally:
        registry.reset()


class TestColormapSettings:
    @pytest.mark.parametrize(
        "cmap_name",
        [
            "viridis",  # valid single matplotlib name
            ["viridis", "plasma"],  # valid list of names
            "pycolorbar_test_colormap",  # valid single pycolorbar colormap name
        ],
    )
    def test_valid_cmap_name(self, cmap_name, setup_colormap_registry):
        """Test valid colormap names."""
        cmap_settings = {"name": cmap_name, "n": 256}
        if isinstance(cmap_name, list):
            cmap_settings["n"] = [256, 256]
        validated = ColormapSettings(**cmap_settings)
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
            _ = ColormapSettings(**cmap_settings)

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
        validated = ColormapSettings(**cmap_settings)
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
            _ = ColormapSettings(**cmap_settings)

    @pytest.mark.parametrize(
        "color",
        [
            "#ff0000",  # valid hex
            (1, 0, 0),  # valid RGB tuple
            [1, 0, 0],  # valid RGB list
            (1, 0, 0, 1),  # valid RGBA tuple (if bad/over/under alpha provided ... RGB alpha will be overwritten !)
            "red",  # valid named color
            "none",
        ],
    )
    def test_valid_colors(self, color):
        """Test valid colors for 'bad_color', 'over_color', 'under_color'."""
        cmap_settings = {"name": "viridis", "bad_color": color, "over_color": color, "under_color": color}
        validated = ColormapSettings(**cmap_settings)
        if isinstance(color, list):
            color = tuple(color)
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
            _ = ColormapSettings(**cmap_settings)

    @pytest.mark.parametrize("alpha", [0, 0.5, 1, None])
    def test_valid_alpha(self, alpha):
        """Test valid alpha for 'bad_alpha', 'over_alpha', 'under_alpha'."""
        cmap_settings = {"name": "viridis", "bad_alpha": alpha, "over_alpha": alpha, "under_alpha": alpha}
        validated = ColormapSettings(**cmap_settings)
        assert validated.bad_alpha == alpha
        assert validated.over_alpha == alpha
        assert validated.under_alpha == alpha

    @pytest.mark.parametrize("alpha", [-0.1, 2, 100, "none"])
    def test_invalid_alpha(self, alpha):
        """Test invalid alpha for 'bad_alpha', 'over_alpha', 'under_alpha'."""
        cmap_settings = {"name": "viridis", "bad_alpha": alpha, "over_alpha": alpha, "under_alpha": alpha}
        with pytest.raises(ValidationError):
            ColormapSettings(**cmap_settings)


class TestNormSettings:
    @pytest.mark.parametrize(
        "norm_settings",
        [
            # Testing Normalize settings
            {"name": "Norm"},
            {"name": "Norm", "vmin": 0, "vmax": 1, "clip": False},
            # Testing NoNorm settings
            {"name": "NoNorm"},
            {"name": "NoNorm", "vmin": None, "vmax": None, "clip": True},
            # Testing BoundaryNorm settings with valid boundaries and extend options
            {"name": "BoundaryNorm", "boundaries": [0, 0.5, 1]},
            {"name": "BoundaryNorm", "boundaries": [0, 0.5, 1], "ncolors": 2, "clip": False, "extend": "neither"},
            {"name": "BoundaryNorm", "boundaries": [0, 0.5, 1], "ncolors": 4, "clip": False, "extend": "both"},
            {"name": "BoundaryNorm", "boundaries": [0, 0.5, 1], "ncolors": 3, "clip": False, "extend": "min"},
            {"name": "BoundaryNorm", "boundaries": [0, 0.5, 1], "ncolors": 3, "clip": False, "extend": "max"},
            # Testing TwoSlopeNorm settings
            {"name": "TwoSlopeNorm", "vcenter": 0.5},
            {"name": "TwoSlopeNorm", "vcenter": 0.5, "vmin": 0, "vmax": 1},
            # Testing CenteredNorm settings
            {"name": "CenteredNorm"},
            {"name": "CenteredNorm", "vcenter": 0, "halfrange": 1, "clip": False},
            # Testing LogNorm settings
            {"name": "LogNorm"},
            {"name": "LogNorm", "vmin": 1, "vmax": 100, "clip": False},
            # Testing SymLogNorm settings
            {"name": "SymLogNorm", "linthresh": 0.1},
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
            {"name": "PowerNorm", "gamma": 0.5},
            {"name": "PowerNorm", "gamma": 0.5, "vmin": 0, "vmax": 1, "clip": False},
            # Testing AsinhNorm settings
            {"name": "AsinhNorm"},
            {"name": "AsinhNorm", "linear_width": 1, "vmin": -10, "vmax": 10, "clip": False},
            # Testing CategoryNorm settings
            {"name": "CategoryNorm", "categories": {0: "low", 1: "medium", 2: "high"}},
            # Testing CategorizeNorm settings
            {"name": "CategorizeNorm", "boundaries": [0, 0.5, 1], "labels": ["low", "medium"]},
        ],
    )
    def test_valid_norm_settings(self, norm_settings):
        """Test that valid normalization settings are accepted without raising errors."""
        # Check that do not raise error
        check_norm_settings(norm_settings)

    @pytest.mark.parametrize(
        ("norm_settings", "expected_error_msg"),
        [
            # Invalid Normalize settings due to incorrect vmin and vmax
            ({"name": "Norm", "vmin": 1, "vmax": 0}, "vmin must be less than vmax"),
            # Invalid BoundaryNorm settings due to non-monotonically increasing boundaries
            (
                {"name": "BoundaryNorm", "boundaries": [1, 0.5, 0], "ncolors": 2},
                "'boundaries' must be monotonically increasing",
            ),
            # Invalid BoundaryNorm boundaries size (< 3)
            ({"name": "BoundaryNorm", "boundaries": [0, 1]}, "Expecting 'boundaries' of at least size 3"),
            # Invalid BoundaryNorm boundaries value type
            ({"name": "BoundaryNorm", "boundaries": ["invalid", "values", "dtype"]}, ""),  # captured by pydantic
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
            # Invalid CategorizeNorm
            # - labels size is not len(boundaries)-1
            (
                {"name": "CategorizeNorm", "boundaries": [0, 1, 2], "labels": ["a"]},
                "'labels' size must be 2 given the size of 'boundaries'",
            ),
            # - boundaries size < 3
            (
                {"name": "CategorizeNorm", "boundaries": [0, 1], "labels": ["one"]},
                "Expecting 'boundaries' of at least size 3",
            ),
            # - boundaries value type
            ({"name": "CategorizeNorm", "boundaries": ["invalid", "values", "dtype"], "labels": ["one", "two"]}, ""),
            # Invalid CategoryNorm
            # - Keys are not integers
            (
                {"name": "CategoryNorm", "categories": {0.0: "a", 1.0: "b", 2.0: "c"}},
                "All 'categories' dictionary keys must be integers.",
            ),
            # - Values are not strings
            (
                {"name": "CategoryNorm", "categories": {0: -9, 1: -9, 2: -9}},
                "All 'categories' dictionary values be strings",
            ),
            # - Only 1 category
            (
                {"name": "CategoryNorm", "categories": {0: "a"}},
                "Expecting a 'categories' dictionary with at least 2 keys.",
            ),
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
        ("norm_name", "extra_param"),
        [
            ("Norm", {"unexpected": 123}),
            ("BoundaryNorm", {"boundaries": [0, 1], "extra": "not valid"}),
            ("CategoryNorm", {"categories": {0: "a", 1: "b"}, "extra": "not valid"}),
            ("CategorizeNorm", {"boundaries": [0, 1, 2], "labels": ["a", "b"], "extra": "not valid"}),
            ("TwoSlopeNorm", {"vcenter": 0.5, "clip": True}),
            ("CenteredNorm", {"vmin": 0, "vmax": 1}),
        ],
    )
    def test_invalid_arguments(self, norm_name, extra_param):
        norm_settings = {"name": norm_name, **extra_param}
        with pytest.raises(ValueError):
            check_norm_settings(norm_settings)

    @pytest.mark.parametrize(
        ("norm_name", "missing_param"),
        [
            ("BoundaryNorm", {}),
            ("CategoryNorm", {}),
            ("CategorizeNorm", {}),
            ("TwoSlopeNorm", {"vmin": 0}),
        ],
    )
    def test_missing_parameters(self, norm_name, missing_param):
        norm_settings = {"name": norm_name, **missing_param}
        with pytest.raises(ValueError):
            check_norm_settings(norm_settings)

    def test_set_default_boundary_norm_ncolors(self):
        """Test that the default values are set correctly."""
        norm_settings = {"name": "BoundaryNorm", "boundaries": [0, 0.5, 1]}
        norm_settings = check_norm_settings(norm_settings)
        assert norm_settings["ncolors"] == 2


class TestColorbarSettings:
    @pytest.mark.parametrize("extend", ["neither", "both", "min", "max", None])
    def test_valid_extend(self, extend):
        """Test valid extend options."""
        cbar_settings = ColorbarSettings(extend=extend)
        assert cbar_settings.extend == extend

    @pytest.mark.parametrize("extend", ["invalid_option", 123, []])
    def test_invalid_extend(self, extend):
        """Test invalid extend options."""
        with pytest.raises(ValidationError):
            ColorbarSettings(extend=extend)

    @pytest.mark.parametrize("extendfrac", [0.5, [0.1, 0.2], "auto", None])
    def test_valid_extendfrac(self, extendfrac):
        """Test valid extendfrac options."""
        cbar_settings = ColorbarSettings(extendfrac=extendfrac)
        assert cbar_settings.extendfrac == extendfrac

    @pytest.mark.parametrize("extendfrac", [[-0.1], 1.1, [1, 2], "not_a_number"])
    def test_invalid_extendfrac(self, extendfrac):
        """Test invalid extendfrac options."""
        with pytest.raises(ValidationError):
            ColorbarSettings(extendfrac=extendfrac)

    @pytest.mark.parametrize("extendrect", [True, False, None])
    def test_valid_extendrect(self, extendrect):
        """Test valid extendrect options."""
        cbar_settings = ColorbarSettings(extendrect=extendrect)
        assert cbar_settings.extendrect == extendrect

    @pytest.mark.parametrize("extendrect", [123, []])
    def test_invalid_extendrect(self, extendrect):
        """Test invalid extendrect options."""
        with pytest.raises(ValidationError):
            ColorbarSettings(extendrect=extendrect)

    @pytest.mark.parametrize("label", ["Valid label", "", None])
    def test_valid_label(self, label):
        """Test valid label options."""
        cbar_settings = ColorbarSettings(label=label)
        assert cbar_settings.label == label

    @pytest.mark.parametrize("label", [123, False, []])
    def test_invalid_label(self, label):
        """Test invalid label options."""
        with pytest.raises(ValidationError):
            ColorbarSettings(label=label)


def assert_is_superset_dict(cbar_dict, validated_dict):
    """Test that the validated dictionary contains all key-values of the original dictionary."""
    for setting, sub_dict in cbar_dict.items():
        for field, value in sub_dict.items():
            assert field in validated_dict[setting]
            assert value == validated_dict[setting][field]


class TestValidateCbarDict:
    def test_valid_cbar_dict(self, setup_colormap_registry):
        """Test validate_cbar_dict with a valid colorbar dictionary."""
        cbar_dict = {
            "cmap": {"name": "viridis"},
            "norm": {"name": "Norm", "vmin": 0, "vmax": 1},
            "cbar": {"extend": "neither"},
        }
        assert_is_superset_dict(cbar_dict=cbar_dict, validated_dict=validate_cbar_dict(cbar_dict, name="dummy"))

    def test_valid_reference(self, setup_colormap_registry, setup_colorbar_registry):
        """Test validate_cbar_dict with a valid reference to another colorbar."""
        # setup_colorbar_registry set up a registry with the pycolorbar_test_colorbar reference
        cbar_dict = {"reference": "pycolorbar_test_colorbar"}
        validated_dict = validate_cbar_dict(cbar_dict, name="dummy")
        assert validated_dict == cbar_dict, "Valid reference should pass validation."

    def test_inexisting_reference(self):
        """Test validate_cbar_dict with an invalid reference."""
        cbar_dict = {"reference": "invalid_reference"}
        with pytest.raises(ValueError) as excinfo:
            validate_cbar_dict(cbar_dict, name="dummy")
        assert "Invalid reference" in str(excinfo.value), "Invalid reference should raise ValueError."

    def test_reference_dict_keys(self):
        """Test validate_cbar_dict with excess key."""
        # Register valid colorbar
        valid_cbar_dict = {"cmap": {"name": "viridis"}}
        valid_reference = "original_colorbar"
        with register_temporary_colorbars(valid_cbar_dict, name=valid_reference):
            # Now validate valid reference colorbar dictionary
            reference_cbar_dict = {"reference": valid_reference, "auxiliary": {"whatever_key": "value"}}
            validate_cbar_dict(reference_cbar_dict, name="dummy")
            # Now test that if whatever other 'key' is specified, it raise error
            reference_cbar_dict = {
                "reference": valid_reference,
                "auxiliary": {"whatever_key": "value"},
                "cmap": {"whatever_key": "value"},
            }
            with pytest.raises(ValueError):
                validate_cbar_dict(reference_cbar_dict, name="dummy")

    def test_valid_recursive_reference(self):
        """Test validate_cbar_dict with a recursive reference."""
        valid_cbar_dict = {"cmap": {"name": "viridis"}}
        cbar_dicts = {}
        cbar_dicts["original_colorbar"] = valid_cbar_dict
        cbar_dicts["first_reference"] = {"reference": "original_colorbar"}
        cbar_dicts["second_reference"] = {"reference": "first_reference"}
        cbar_dicts["third_reference"] = {"reference": "second_reference"}
        with register_temporary_colorbars(cbar_dicts, multiple=True):
            cbar_dict = {"reference": "third_reference"}
            validate_cbar_dict(cbar_dict, name="dummy")

    def test_circular_recursive_reference(self):
        """Test validate_cbar_dict with a recursive reference."""
        valid_cbar_dict = {"cmap": {"name": "viridis"}}
        cbar_dicts = {}
        cbar_dicts["original_colorbar"] = valid_cbar_dict
        cbar_dicts["first_reference"] = {"reference": "original_colorbar"}
        cbar_dicts["second_reference"] = {"reference": "first_reference"}
        cbar_dicts["third_reference"] = {"reference": "second_reference"}
        with register_temporary_colorbars(cbar_dicts, multiple=True):
            cbar_dict = {"reference": "third_reference"}
            with pytest.raises(ValueError) as excinfo:
                validate_cbar_dict(cbar_dict, name="first_reference")
        assert "Circular reference detected with" in str(excinfo.value), "Circular reference should raise ValueError."

    def test_invalid_cbar_dict(self):
        """Test validate_cbar_dict with an invalid colorbar dictionary."""
        cbar_dict = {
            "cmap": {"name": "nonexistent_cmap"},
            "norm": {"name": "InvalidNorm"},
            "cbar": {"extend": "invalid_option"},
        }
        with pytest.raises(ValueError) as excinfo:
            validate_cbar_dict(cbar_dict, name="dummy")
        assert "Invalid configuration" in str(excinfo.value), "Invalid colorbar dictionary should raise ValueError."

    def test_simple_cbar_dict(self):
        """Test validate_cbar_dict with the simplest allowed colorbar dictionary."""
        cbar_dict = {
            "cmap": {"name": "viridis"},
        }
        validated_dict = validate_cbar_dict(cbar_dict, name="dummy")
        assert_is_superset_dict(cbar_dict=cbar_dict, validated_dict=validated_dict)

        # Another option
        cbar_dict = {"cmap": {"name": "viridis"}, "norm": {}, "cbar": {}}
        validated_dict = validate_cbar_dict(cbar_dict, name="dummy")
        assert_is_superset_dict(cbar_dict=cbar_dict, validated_dict=validated_dict)

        # 'None' as cmap name is not allowed
        cbar_dict = {
            "cmap": {"name": None},
        }
        with pytest.raises(ValueError):
            validated_dict = validate_cbar_dict(cbar_dict, name="dummy")

        # Empty dictionary is not allowed
        with pytest.raises(ValueError) as excinfo:
            validate_cbar_dict(cbar_dict={}, name="dummy")
        assert "The colorbar dictionary can not be empty." in str(excinfo.value)

        # None is not allowed
        with pytest.raises(TypeError) as excinfo:
            validate_cbar_dict(cbar_dict=None, name="dummy")
        assert "The colorbar dictionary must be a dictionary" in str(excinfo.value)

    def test_categorize_norm_consistency_checks(self):
        """Test consistency checks for CategorizeNorm."""
        # Check valid combinations
        cbar_dict = {
            "cmap": {"name": "viridis", "n": 3},
            "norm": {"name": "CategorizeNorm", "boundaries": [0, 1, 2, 3], "labels": ["A", "B", "C"]},
            "cbar": {"extend": "neither"},
        }
        validate_cbar_dict(cbar_dict, name="dummy")

        cbar_dict = {
            "cmap": {"name": "viridis"},  # n not specified
            "norm": {"name": "CategorizeNorm", "boundaries": [0, 1, 2, 3], "labels": ["A", "B", "C"]},
            "cbar": {"extend": "neither"},
        }
        validate_cbar_dict(cbar_dict, name="dummy")

        cbar_dict = {
            "cmap": {"name": ["viridis", "Spectral"], "n": [2, 2]},
            "norm": {"name": "CategorizeNorm", "boundaries": [0, 1, 2, 3, 4], "labels": ["A", "B", "C", "D"]},
            "cbar": {"extend": "neither"},
        }
        validate_cbar_dict(cbar_dict, name="dummy")

        # Check invalid combinations
        cbar_dict = {
            "cmap": {"name": "viridis", "n": 4},
            "norm": {"name": "CategorizeNorm", "boundaries": [0, 1, 2, 3], "labels": ["A", "B", "C"]},
            "cbar": {"extend": "neither"},
        }
        with pytest.raises(ValueError):
            validate_cbar_dict(cbar_dict, name="dummy")

    def test_category_norm_consistency_checks(self):
        """Test consistency checks for CategoryNorm."""
        # Check valid combinations
        cbar_dict = {
            "cmap": {"name": "viridis", "n": 3},
            "norm": {"name": "CategoryNorm", "categories": {0: "A", 1: "B", 2: "C"}},
            "cbar": {"extend": "neither"},
        }
        validate_cbar_dict(cbar_dict, name="dummy")

        cbar_dict = {
            "cmap": {"name": "viridis"},  # n not specified
            "norm": {"name": "CategoryNorm", "categories": {0: "A", 1: "B", 2: "C"}},
            "cbar": {"extend": "neither"},
        }
        validate_cbar_dict(cbar_dict, name="dummy")

        cbar_dict = {
            "cmap": {"name": ["viridis", "Spectral"], "n": [2, 2]},
            "norm": {"name": "CategoryNorm", "categories": {0: "A", 1: "B", 2: "C", 3: "D"}},
            "cbar": {"extend": "neither"},
        }
        validate_cbar_dict(cbar_dict, name="dummy")

        # Check invalid combinations
        cbar_dict = {
            "cmap": {"name": "viridis", "n": 4},
            "norm": {"name": "CategoryNorm", "categories": {0: "A", 1: "B", 2: "C"}},
            "cbar": {"extend": "neither"},
        }
        with pytest.raises(ValueError):
            validate_cbar_dict(cbar_dict, name="dummy")

    def test_boundary_norm_consistency_checks(self):
        """Test consistency checks for CategoricalNorm and BoundaryNorm."""
        # Check valid combinations
        cbar_dict = {
            "cmap": {"name": "viridis", "n": 2},
            "norm": {"name": "BoundaryNorm", "boundaries": [0, 1, 2]},
            "cbar": {"extend": "neither"},
        }
        validate_cbar_dict(cbar_dict, name="dummy")

        cbar_dict = {
            "cmap": {"name": ["viridis", "Spectral"], "n": [2, 2]},
            "norm": {"name": "BoundaryNorm", "boundaries": [0, 1, 2, 3, 4]},
            "cbar": {"extend": "neither"},
        }
        validate_cbar_dict(cbar_dict, name="dummy")

        # Check invalid combinations
        cbar_dict = {
            "cmap": {"name": "viridis", "n": 4},
            "norm": {"name": "BoundaryNorm", "boundaries": [0, 1, 2]},
            "cbar": {"extend": "neither"},
        }
        with pytest.raises(ValueError):
            validate_cbar_dict(cbar_dict, name="dummy")
