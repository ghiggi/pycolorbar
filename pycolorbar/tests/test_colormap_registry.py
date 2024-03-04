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
"""Test ColorMapRegistry."""

import os

import pytest
from matplotlib.colors import ListedColormap

from pycolorbar.settings.colormap_registry import ColorMapRegistry
from pycolorbar.utils.yaml import write_yaml


@pytest.fixture
def colormap_registry():
    registry = ColorMapRegistry.get_instance()
    registry.reset()
    return registry


TEST_CMAP_DICT = {"type": "ListedColormap", "colors": ["#ff0000", "#00ff00", "#0000ff"], "color_space": "hex"}

INVALID_CMAP_DICT = {"type": "BAD_TYPE", "colors": ["#ff0000", "#00ff00", "#0000ff"], "color_space": "hex"}


# colormap_registry =ColorMapRegistry.get_instance()
# colormap_registry.reset()
# tmp_path = "/tmp"


def TestColorMapRegistry():
    def test_register_unregister_colormap(self, colormap_registry, tmp_path):
        """Tests for registering, get a colormap and unregistering the colormaps."""
        # Create a temporary colormap YAML file
        cmap_name = "test_cmap"
        cmap_filepath = os.path.join(tmp_path, f"{cmap_name}.yaml")
        write_yaml(TEST_CMAP_DICT, cmap_filepath)

        # Test registering the colormap
        colormap_registry.register(filepath=cmap_filepath, verbose=False, force=True)

        # Verify the colormap is registered
        assert cmap_name in colormap_registry.names
        assert cmap_name in colormap_registry

        # Test retrieving the colormap
        cmap = colormap_registry.get_cmap(cmap_name)
        assert isinstance(cmap, (ListedColormap))

        # Unregister the colormap and check name does not appear anymore
        colormap_registry.unregister(cmap_name)
        assert cmap_name not in colormap_registry.names

        # Remove file
        os.remove(cmap_filepath)

    def test_add_cmap_dict(self, colormap_registry):
        """Test add_cmap_dict method."""
        # Test adding the colormap dictionary
        cmap_name = "test_cmap_dict"
        colormap_registry.add_cmap_dict(cmap_dict=TEST_CMAP_DICT, name=cmap_name, verbose=False)

        # Verify the colormap is added
        assert cmap_name in colormap_registry.names

        # Test retrieving the colormap
        cmap = colormap_registry.get_cmap(cmap_name)
        assert isinstance(cmap, ListedColormap)

    def test_registration_invalid_colormap_yaml_file(self, colormap_registry, tmp_path):
        """Test registration of an invalid colormap YAML file."""
        # Creade a bad temporary colormap YAML file
        cmap_name = "invalid_cmap"
        cmap_filepath = os.path.join(tmp_path, f"{cmap_name}.yaml")
        write_yaml(INVALID_CMAP_DICT, cmap_filepath)

        # Test registering the invalid colormap (with YAML file) do not raise error
        colormap_registry.register(filepath=cmap_filepath, verbose=False, force=True)

        # Verify validation raises ValueError for invalid colormap
        with pytest.raises(ValueError):
            colormap_registry.validate(cmap_name)

        # Unregister the colormap
        colormap_registry.unregister(cmap_name)
        colormap_registry.validate()

        # Remove file
        os.remove(cmap_filepath)

    def test_registration_invalid_cmap_dict(self, colormap_registry):
        """Test registration of an invalid cmap_dict."""
        # Test registering the invalid colormap with add_cmap_dict
        cmap_name = "invalid_cmap"

        # Test validation raise error
        with pytest.raises(ValueError):
            colormap_registry.add_cmap_dict(cmap_dict=INVALID_CMAP_DICT, name=cmap_name)
        assert cmap_name not in colormap_registry

    def test_available(self, colormap_registry):
        """Test available colormaps"""
        # Register cmap
        cmap_name = "test_cmap_dict"
        colormap_registry.add_cmap_dict(cmap_dict=TEST_CMAP_DICT, name=cmap_name)

        # Test with no category and no reversed names
        assert colormap_registry.available() == [cmap_name]

        # Test with reversed colormaps too
        assert colormap_registry.available(include_reversed=True) == [cmap_name, cmap_name + "_r"]

        # Test with category
        my_category = "precip"
        category_cmap_name = "test_cmap_precip"
        category_cmap_dict = TEST_CMAP_DICT.copy()
        category_cmap_dict["auxiliary"] = {"category": my_category}
        colormap_registry.add_cmap_dict(cmap_dict=category_cmap_dict, name=category_cmap_name)
        assert colormap_registry.available(category=my_category) == [category_cmap_name]

    def test_get_cmap_filepath(self, colormap_registry, tmp_path):
        """Test get_cmap_filepath method."""
        cmap_name = "test_cmap"
        cmap_filepath = os.path.join(tmp_path, f"{cmap_name}.yaml")
        write_yaml(TEST_CMAP_DICT, cmap_filepath)

        # Test registering the colormap
        colormap_registry.register(filepath=cmap_filepath, verbose=False, force=True)

        # Retrieve filepath
        assert colormap_registry.get_cmap_filepath(cmap_name) == cmap_filepath
        assert colormap_registry.get_cmap_filepath(cmap_name + "_r") == cmap_filepath

        # Retrieve a missing colormap
        with pytest.raises(ValueError):
            colormap_registry.get_cmap_filepath("unregistered_cmap")

        # Remove file
        os.remove(cmap_filepath)

    def test_get_cmap_dict(self, colormap_registry):
        """Test get_cmap_dict method.

        Do not check for equality because of the default values set by the ColorMap validator.
        """
        cmap_name = "test_cmap_dict"
        colormap_registry.add_cmap_dict(cmap_dict=TEST_CMAP_DICT, name=cmap_name, verbose=False)
        assert isinstance(colormap_registry.get_cmap_dict(cmap_name), dict)

    def test_get_cmap(self, colormap_registry):
        """Test get_cmap method."""
        cmap_name = "test_cmap"
        colormap_registry.add_cmap_dict(cmap_dict=TEST_CMAP_DICT, name=cmap_name, verbose=False)
        cmap = colormap_registry.get_cmap(cmap_name)
        # Assert colormap is reverted
        assert cmap.reversed() == colormap_registry.get_cmap(cmap_name + "_r")

    def test_validate(self, colormap_registry):
        """Test validate method."""
        cmap_name = "test_cmap"
        colormap_registry.add_cmap_dict(cmap_dict=TEST_CMAP_DICT, name=cmap_name, verbose=False)
        # Validate all colormaps
        colormap_registry.validate()
        # Validate a existing cmap
        colormap_registry.validate(cmap_name)
        # Validate an unexisting cmap
        with pytest.raises(ValueError):
            colormap_registry.validate("inexisting_cmap")
        # Validate an invalid colormap
        invalid_cmap_name = "invalid_cmap_name"
        colormap_registry.registry[invalid_cmap_name] = INVALID_CMAP_DICT  # hack to register invalid colormap
        with pytest.raises(ValueError):
            colormap_registry.validate()
        with pytest.raises(ValueError):
            colormap_registry.validate(invalid_cmap_name)

    def test_to_yaml(self, colormap_registry, tmp_path):
        """Test to_yaml method."""
        # Register cmap
        cmap_name = "test_cmap"
        colormap_registry.add_cmap_dict(cmap_dict=TEST_CMAP_DICT, name=cmap_name, verbose=False)
        # Retrieve cmap
        cmap = colormap_registry.get_cmap(cmap_name)
        # Save colormap YAML
        new_cmap_name = "example_cmap"
        dst_filepath = os.path.join(tmp_path, f"{new_cmap_name}.yaml")
        colormap_registry.to_yaml(name=cmap_name, filepath=dst_filepath)
        assert os.path.exists(dst_filepath)
        colormap_registry.reset()
        assert cmap_name not in colormap_registry
        # Register YAML
        colormap_registry.register(dst_filepath)
        assert new_cmap_name in colormap_registry
        # Assert same cmap
        assert colormap_registry.get_cmap(new_cmap_name) == cmap

        # Remove file
        os.remove(dst_filepath)

    def test_show_colormap(self, colormap_registry):
        """Test show_colormap method."""
        # Register cmap
        cmap_name = "test_cmap"
        colormap_registry.add_cmap_dict(cmap_dict=TEST_CMAP_DICT, name=cmap_name, verbose=False)
        # Test it runs
        _ = colormap_registry.show_colormap(cmap_name)
