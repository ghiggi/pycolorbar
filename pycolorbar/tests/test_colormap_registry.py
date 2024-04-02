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
"""Test ColormapRegistry."""

import os

import matplotlib.pyplot as plt  # noqa
import pytest
from matplotlib.colors import Colormap, ListedColormap
from pytest_mock import mocker  # noqa

import pycolorbar
from pycolorbar.settings.colormap_registry import ColormapRegistry
from pycolorbar.utils.yaml import write_yaml


@pytest.fixture
def colormap_registry():
    registry = ColormapRegistry.get_instance()
    registry.reset()

    yield registry

    registry.reset()


@pytest.fixture
def mock_matplotlib_show(mocker):  # noqa
    mock = mocker.patch("matplotlib.pyplot.show")
    yield mock


TEST_CMAP_DICT = {
    "colormap_type": "ListedColormap",
    "color_palette": ["#ff0000", "#00ff00", "#0000ff"],
    "color_space": "hex",
}

INVALID_CMAP_DICT = {
    "colormap_type": "BAD_TYPE",
    "color_palette": ["#ff0000", "#00ff00", "#0000ff"],
    "color_space": "hex",
}


# colormap_registry =ColormapRegistry.get_instance()
# colormap_registry.reset()
# tmp_path = "/tmp"


class TestColormapRegistry:
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

    def test_register_inexisting_file(self, colormap_registry):
        """Test registering an inexisting colormap YAML file raise an informative error."""
        filepath = "inexisting_path"
        with pytest.raises(ValueError) as excinfo:
            colormap_registry.register(filepath=filepath)
        assert f"The colormap configuration YAML file {filepath} does not exist." in str(excinfo.value)

    def test_register_overwriting(self, colormap_registry, tmp_path, capsys):
        """Test registering an already existing colormap."""
        # Create a temporary colormap YAML file
        cmap_name = "test_cmap"
        cmap_filepath = os.path.join(tmp_path, f"{cmap_name}.yaml")
        write_yaml(TEST_CMAP_DICT, cmap_filepath)

        # Register a colormap
        colormap_registry.register(filepath=cmap_filepath, verbose=False)

        # Test overwriting is allowed with force=True (default)
        colormap_registry.register(filepath=cmap_filepath, verbose=True)

        # Test it captured the overwriting warning
        captured = capsys.readouterr()
        assert "Warning: Overwriting existing colormap" in captured.out

        # Test overwriting is not allowed with force=False
        with pytest.raises(ValueError):
            colormap_registry.register(filepath=cmap_filepath, force=False)

    def test_unregister_inexisting_cmap(self, colormap_registry):
        """Test unregister an inexisting colormap."""
        name = "inexisting_cmap"
        with pytest.raises(ValueError) as excinfo:
            colormap_registry.unregister(name=name)
        assert f"The colormap {name} is not registered in pycolorbar." in str(excinfo.value)

    def test_add_cmap_dict(self, colormap_registry, capsys):
        """Test add_cmap_dict method."""
        # Test adding the colormap dictionary
        cmap_name = "test_cmap_dict"
        colormap_registry.add_cmap_dict(cmap_dict=TEST_CMAP_DICT, name=cmap_name, verbose=False)

        # Verify the colormap is added
        assert cmap_name in colormap_registry.names

        # Test retrieving the colormap
        cmap = colormap_registry.get_cmap(cmap_name)
        assert isinstance(cmap, ListedColormap)

        # Test overwriting the cmap (force=True)
        colormap_registry.add_cmap_dict(cmap_dict=TEST_CMAP_DICT, name=cmap_name, verbose=True, force=True)
        captured = capsys.readouterr()
        assert "Warning: Overwriting existing colormap" in captured.out

        # Test overwriting the cmap
        with pytest.raises(ValueError):
            colormap_registry.add_cmap_dict(cmap_dict=TEST_CMAP_DICT, name=cmap_name, force=False)

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
        """Test available colormaps."""
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

        Do not check for equality because of the default values set by the Colormap validator.
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

        # Assert overwriting an existing YAML raise an error (by default)
        with pytest.raises(ValueError):
            colormap_registry.to_yaml(name=cmap_name, filepath=dst_filepath)

        # Assert overwriting an existing YAML is allowed with force=True
        colormap_registry.to_yaml(name=cmap_name, filepath=dst_filepath, force=True)
        assert os.path.exists(dst_filepath)

        # Reset registry
        colormap_registry.reset()
        assert cmap_name not in colormap_registry

        # Register YAML
        colormap_registry.register(dst_filepath)
        assert new_cmap_name in colormap_registry

        # Assert same cmap
        assert colormap_registry.get_cmap(new_cmap_name) == cmap

        # Remove file
        os.remove(dst_filepath)

    def test_show_colormap(self, colormap_registry, mock_matplotlib_show):
        """Test show_colormap method."""
        # Register cmap
        cmap_name = "test_cmap"
        colormap_registry.add_cmap_dict(cmap_dict=TEST_CMAP_DICT, name=cmap_name, verbose=False)
        # Test it runs
        _ = colormap_registry.show_colormap(cmap_name)
        # Assert matplotlib show() is called
        mock_matplotlib_show.assert_called_once()

    def test_show_colormaps(self, colormap_registry, mock_matplotlib_show):
        """Test show_colormaps method."""
        # Test raise error if no colormap registered
        with pytest.raises(ValueError) as excinfo:
            _ = colormap_registry.show_colormaps()
        assert "No colormaps are yet registered in the pycolorbar ColormapRegistry." in str(excinfo.value)

        # Register cmap
        cmap_name = "test_cmap"
        colormap_registry.add_cmap_dict(cmap_dict=TEST_CMAP_DICT, name=cmap_name, verbose=False)

        # Test it works also with 1 colormap
        _ = colormap_registry.show_colormaps()
        mock_matplotlib_show.assert_called_once()

        # Register another cmap
        cmap_name = "test_cmap1"
        colormap_registry.add_cmap_dict(cmap_dict=TEST_CMAP_DICT, name=cmap_name, verbose=False)

        # Test it works also with more than 1 colormap
        _ = colormap_registry.show_colormaps()
        assert mock_matplotlib_show.call_count == 2


def test_utility_methods(colormap_registry, tmp_path):
    """Tests register_colormap, get_cmap and get_cmap_dict utility."""
    # Create a temporary colormap YAML file
    cmap_name = "test_cmap"
    cmap_filepath = os.path.join(tmp_path, f"{cmap_name}.yaml")
    write_yaml(TEST_CMAP_DICT, cmap_filepath)

    # Test registering the colormap
    pycolorbar.register_colormap(filepath=cmap_filepath, verbose=False, force=True)

    # Verify the colormap is registered
    assert cmap_name in pycolorbar.colormaps.names
    assert cmap_name in pycolorbar.colormaps

    # Test retrieving the colormap with get_cmap
    cmap = pycolorbar.get_cmap(cmap_name)
    assert isinstance(cmap, (ListedColormap))

    # Test retrieving the colormap dictionary with get_cmap_dict
    cmap_dict = pycolorbar.get_cmap_dict(cmap_name)
    assert isinstance(cmap_dict, dict)


def test_register_colormaps(colormap_registry, tmp_path):
    """Tests register_colormaps in a directory."""
    # Define colormaps
    cmap_name = "test_cmap"
    cmap_filepath = os.path.join(tmp_path, f"{cmap_name}.yaml")
    write_yaml(TEST_CMAP_DICT, cmap_filepath)

    cmap_name1 = "test_cmap"
    cmap_filepath1 = os.path.join(tmp_path, f"{cmap_name1}.yaml")
    write_yaml(TEST_CMAP_DICT, cmap_filepath1)

    # Test registering all colormaps in a directory
    pycolorbar.register_colormaps(directory=tmp_path)
    assert cmap_name in pycolorbar.colormaps
    assert cmap_name1 in pycolorbar.colormaps

    # Clear the registry
    pycolorbar.colormaps.reset()
    assert cmap_name not in pycolorbar.colormaps

    # Test registering only a single colormaps in a directory
    pycolorbar.register_colormaps(directory=tmp_path, name=cmap_name)
    assert cmap_name in pycolorbar.colormaps


class TestGetCmap:
    def test_input_colormap(self):
        """Test providing a matplotlib colormap returns the object itself."""
        cmap = plt.get_cmap("Spectral")
        assert pycolorbar.get_cmap(cmap) == cmap

    def test_default_mpl_cmap(self):
        """Test that None returns the default matplotlib colormap."""
        cmap = pycolorbar.get_cmap(name=None)
        assert isinstance(cmap, Colormap)

    def test_invalid_name(self):
        """Test the retrieval of an undefined colormap."""
        with pytest.raises(ValueError):
            pycolorbar.get_cmap(name="inexisting_cmap_name")

    def test_mpl_cmap_name(self):
        """Test the retrieval of a matplotlib colormap."""
        cmap = pycolorbar.get_cmap(name="Spectral")
        assert isinstance(cmap, Colormap)

    def test_pycolorbar_cmap_name(self, colormap_registry, tmp_path):
        """Test the retrieval of a pycolorbar colormap."""
        # Define colormaps
        cmap_name = "test_cmap"
        cmap_filepath = os.path.join(tmp_path, f"{cmap_name}.yaml")
        write_yaml(TEST_CMAP_DICT, cmap_filepath)
        # Register the colormap
        pycolorbar.register_colormap(filepath=cmap_filepath, verbose=False, force=True)
        # Retrieve colormap
        cmap = pycolorbar.get_cmap(name=cmap_name)
        assert isinstance(cmap, Colormap)
        # Retrieve reversed colormap
        reversed_cmap = pycolorbar.get_cmap(name=f"{cmap_name}_r")
        assert isinstance(reversed_cmap, Colormap)
        # assert cmap.reversed()(0) == reversed_cmap(0)  # TODO BUG


def test_available_colormaps(colormap_registry, tmp_path):
    """Test available_colormaps returns matplotlib and pycolorbar colormaps."""
    # Assert that matplotlib colormaps are always returned
    names = pycolorbar.available_colormaps()
    assert len(names) > 1  # matplotlib colormaps

    # Now register a pycolorbar cmap and test is inside  the list
    cmap_name = "test_cmap"
    cmap_filepath = os.path.join(tmp_path, f"{cmap_name}.yaml")
    write_yaml(TEST_CMAP_DICT, cmap_filepath)
    pycolorbar.register_colormap(filepath=cmap_filepath)

    names = pycolorbar.available_colormaps()
    assert cmap_name in names

    # Test empty list for inexisting category
    names = pycolorbar.available_colormaps(category="inexistent")
    assert names == []


@pytest.mark.parametrize("category", ["qualitative", "diverging", "sequential", "perceptual", "cyclic"])
@pytest.mark.parametrize("include_reversed", [True, False])
def test_available_colormaps_by_category(category, include_reversed):
    """Test available_colormaps returns the colormaps names of the specified category."""
    names = pycolorbar.available_colormaps(category=category, include_reversed=include_reversed)
    assert len(names) > 1  # matplotlib colormaps


def test_show_colormap(colormap_registry, mock_matplotlib_show):
    """Test show_colormap function."""
    # Register cmap
    cmap_name = "test_cmap"
    colormap_registry.add_cmap_dict(cmap_dict=TEST_CMAP_DICT, name=cmap_name, verbose=False)
    # Test it runs
    pycolorbar.show_colormap(cmap_name)
    # Assert matplotlib show() is called
    mock_matplotlib_show.assert_called_once()


def test_show_colormaps(colormap_registry, mock_matplotlib_show):
    """Test show_colormaps function."""
    # Test raise error if no colormap registered
    with pytest.raises(ValueError) as excinfo:
        _ = colormap_registry.show_colormaps()
    assert "No colormaps are yet registered in the pycolorbar ColormapRegistry." in str(excinfo.value)

    # Register cmap
    cmap_name = "test_cmap"
    colormap_registry.add_cmap_dict(cmap_dict=TEST_CMAP_DICT, name=cmap_name, verbose=False)

    # Test it works also with 1 colormap
    pycolorbar.show_colormaps()
    mock_matplotlib_show.assert_called_once()

    # Register another cmap
    cmap_name = "test_cmap1"
    colormap_registry.add_cmap_dict(cmap_dict=TEST_CMAP_DICT, name=cmap_name, verbose=False)

    # Test it works also with more than 1 colormap
    pycolorbar.show_colormaps()
    assert mock_matplotlib_show.call_count == 2
