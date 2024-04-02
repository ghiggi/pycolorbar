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
"""Test ColorbarRegistry."""
import os

import matplotlib.pyplot as plt  # noqa
import pytest
from deepdiff import DeepDiff
from matplotlib.colors import Colormap, Normalize
from pytest_mock import mocker  # noqa

import pycolorbar
from pycolorbar.settings.colorbar_registry import ColorbarRegistry
from pycolorbar.utils.yaml import write_yaml


@pytest.fixture()
def colorbar_registry():
    """Fixture to initialize and reset the colorbar registry."""
    registry = ColorbarRegistry.get_instance()
    registry.reset()

    yield registry

    registry.reset()


@pytest.fixture()
def mock_matplotlib_show(mocker):  # noqa
    mock = mocker.patch("matplotlib.pyplot.show")
    return mock  # noqa


@pytest.fixture()
def colorbar_test_filepath(tmp_path):
    """Fixture to create a temporary colorbar YAML file."""
    filepath = tmp_path / "temp_colorbar.yaml"
    cbar_dict1 = {"cmap": {"name": "viridis"}}
    cbar_dict2 = {"cmap": {"name": "viridis"}, "auxiliary": {"category": "TEST"}}
    cbar_dicts = {"TEST_CBAR_1": cbar_dict1, "TEST_CBAR_2": cbar_dict2}
    write_yaml(cbar_dicts, filepath)
    return filepath


@pytest.fixture()
def invalid_colorbar_test_filepath(tmp_path):
    """Fixture to create a temporary colorbar YAML file."""
    filepath = tmp_path / "invalid_colorbar.yaml"
    cbar_dicts = {"INVALID_TEST_CBAR": {}}
    write_yaml(cbar_dicts, filepath)
    return filepath


class TestColorbarRegistry:
    def test_register_and_unregister_colorbar(self, colorbar_registry, colorbar_test_filepath):
        """Test registering and unregistering a colorbar configuration."""
        colorbar_registry.register(colorbar_test_filepath)
        assert len(colorbar_registry.names) > 0, "Colorbar should be registered."

        colorbar_name = list(colorbar_registry.registry.keys())[0]
        colorbar_registry.unregister(colorbar_name)
        assert colorbar_name not in colorbar_registry.names, "Colorbar should be unregistered."

    def test_register_inexisting_file(self, colorbar_registry):
        """Test registering an inexisting colormap YAML file raise an informative error."""
        filepath = "inexisting_path"
        with pytest.raises(ValueError) as excinfo:
            colorbar_registry.register(filepath=filepath)
        assert f"The colorbars configuration YAML file {filepath} does not exist." in str(excinfo.value)

    def test_register_overwriting(self, colorbar_registry, colorbar_test_filepath, capsys):
        """Test registering an already existing colorbar."""
        # Register a colorbar
        colorbar_registry.register(filepath=colorbar_test_filepath, verbose=False)

        # Test overwriting is allowed with force=True (default)
        colorbar_registry.register(filepath=colorbar_test_filepath, verbose=True)

        # Test it captured the overwriting warning
        captured = capsys.readouterr()
        assert "Warning: Overwriting existing colorbar" in captured.out

        # Test overwriting is not allowed with force=False
        with pytest.raises(ValueError):
            colorbar_registry.register(filepath=colorbar_test_filepath, force=False)

    def test_unregister_inexisting_cmap(self, colorbar_registry):
        """Test unregister an inexisting colormap."""
        name = "inexisting_colorbar"
        with pytest.raises(ValueError) as excinfo:
            colorbar_registry.unregister(name=name)
        assert f"The colorbar configuration for {name} is not registered in pycolorbar." in str(excinfo.value)

    def test_validate_registered_colorbars(self, colorbar_registry, colorbar_test_filepath):
        """Test validation of registered colorbars."""
        colorbar_registry.register(colorbar_test_filepath)
        colorbar_registry.validate()
        colorbar_registry.validate("TEST_CBAR_1")

    def test_invalid_colorbar_registration(self, colorbar_registry, invalid_colorbar_test_filepath):
        """Test handling of invalid colorbar registration."""
        # By default does not validate at registration
        colorbar_registry.register(invalid_colorbar_test_filepath)

        # Validate raise an error
        with pytest.raises(ValueError):
            colorbar_registry.validate()

        # Now check that if validate at registration, raise error with invalid colorbar settings
        colorbar_registry.reset()
        with pytest.raises(ValueError):
            colorbar_registry.register(invalid_colorbar_test_filepath, validate=True)

    def test_add_cbar_dict(self, colorbar_registry):
        """Test that add_cbar_dict register the provided colorbar dictionary."""
        test_colorbar_name = "test_colorbar"
        test_colorbar_dict = {"cmap": {"name": "viridis"}, "cbar": {"label": "Test Label"}}
        colorbar_registry.add_cbar_dict(cbar_dict=test_colorbar_dict, name=test_colorbar_name)

        assert test_colorbar_name in colorbar_registry.names
        retrieved_dict = colorbar_registry.get_cbar_dict(test_colorbar_name)
        assert retrieved_dict["cbar"]["label"] == "Test Label"

    def test_get_cbar_dict(self, colorbar_registry, colorbar_test_filepath):
        """Test get_cbar_dict retrieves the colorbar configuration."""
        colorbar_registry.register(colorbar_test_filepath)
        colorbar_name = list(colorbar_registry.registry.keys())[0]
        cbar_dict = colorbar_registry.get_cbar_dict(colorbar_name)
        assert isinstance(cbar_dict, dict), "Should return a colorbar configuration dictionary."

        # Test unregistered colorbar raise error
        with pytest.raises(ValueError):
            colorbar_registry.get_cbar_dict("inexistent")

    def test_get_cbar_dict_resolve_reference(self, colorbar_registry, colorbar_test_filepath):
        """Test get_cbar_dict resolves references."""
        colorbar_registry.register(colorbar_test_filepath)
        # Register a reference
        reference_cbar_dict = {"reference": "TEST_CBAR_1"}
        colorbar_registry.add_cbar_dict(reference_cbar_dict, name="TEST_REFERENCE_CBAR")
        # Assert that the reference is resolved
        resolved_dict = colorbar_registry.get_cbar_dict("TEST_REFERENCE_CBAR")
        expected_dict = colorbar_registry.get_cbar_dict("TEST_CBAR_1")
        diff = DeepDiff(resolved_dict, expected_dict)
        assert diff == {}, f"Dictionaries are not equal: {diff}"

    def test_get_cmap(self, colorbar_registry, colorbar_test_filepath):
        """Test the get_cmap method."""
        colorbar_registry.register(colorbar_test_filepath)
        cmap = colorbar_registry.get_cmap("TEST_CBAR_1")
        assert isinstance(cmap, Colormap)

    def test_get_plot_kwargs(self, colorbar_registry, colorbar_test_filepath):
        """Test the get_plot_kwargs method."""
        colorbar_registry.register(colorbar_test_filepath)

        # Test raise error with invalid type
        with pytest.raises(TypeError):
            colorbar_registry.get_plot_kwargs(name=1)
        with pytest.raises(TypeError):
            colorbar_registry.get_plot_kwargs(name=["a"])

        # Test with no custom kwargs
        plot_kwargs, cbar_kwargs = colorbar_registry.get_plot_kwargs(
            name="TEST_CBAR_1",
            user_plot_kwargs={},
            user_cbar_kwargs={},
        )
        assert isinstance(plot_kwargs["cmap"], Colormap)
        assert isinstance(plot_kwargs["norm"], Normalize)
        assert isinstance(cbar_kwargs, dict)

        # Test with custom kwargs
        plot_kwargs, cbar_kwargs = colorbar_registry.get_plot_kwargs(
            name="TEST_CBAR_1",
            user_plot_kwargs={"vmin": 10, "vmax": 20},
            user_cbar_kwargs={},
        )
        assert isinstance(plot_kwargs["cmap"], Colormap)
        assert isinstance(plot_kwargs["norm"], Normalize)
        assert plot_kwargs["norm"].vmin == 10.0
        assert plot_kwargs["norm"].vmax == 20.0

        # Test inexisting colorbar configuration with no custom kwargs
        plot_kwargs, cbar_kwargs = colorbar_registry.get_plot_kwargs(name="INEXISTING")
        assert plot_kwargs["cmap"] is None
        assert isinstance(plot_kwargs["norm"], Normalize)
        assert plot_kwargs["norm"].vmin is None
        assert plot_kwargs["norm"].vmin is None

        # Test inexisting colorbar configuration with no custom kwargs
        plot_kwargs, cbar_kwargs = colorbar_registry.get_plot_kwargs(
            name=None,
            user_plot_kwargs={"vmin": 10, "vmax": 20},
            user_cbar_kwargs={},
        )
        assert plot_kwargs["cmap"] is None
        assert isinstance(plot_kwargs["norm"], Normalize)
        assert plot_kwargs["norm"].vmin == 10.0
        assert plot_kwargs["norm"].vmax == 20.0

    def test_to_yaml(self, colorbar_registry, colorbar_test_filepath, tmp_path):
        """Test the to_yaml method."""
        # Register colorbars
        colorbar_registry.register(colorbar_test_filepath)
        # Write single and multiple colorbar YAML
        single_colorbar_filepath = os.path.join(tmp_path, "single_colorbar.yaml")
        multiple_colorbars_filepath = os.path.join(tmp_path, "multiple_colorbar.yaml")
        colorbar_registry.to_yaml(names="TEST_CBAR_1", filepath=single_colorbar_filepath)
        colorbar_registry.to_yaml(filepath=multiple_colorbars_filepath)

        assert os.path.exists(single_colorbar_filepath)
        assert os.path.exists(multiple_colorbars_filepath)

        # Reset and assert no colorbar is registered
        colorbar_registry.reset()
        assert colorbar_registry.names == []

        # Register single colorbar
        colorbar_registry.register(filepath=single_colorbar_filepath)
        assert colorbar_registry.names == ["TEST_CBAR_1"]

        # Reset and assert no colorbar is registered
        colorbar_registry.reset()
        assert colorbar_registry.names == []

        # Register multiple colorbar
        colorbar_registry.register(filepath=multiple_colorbars_filepath)
        assert colorbar_registry.names == ["TEST_CBAR_1", "TEST_CBAR_2"]

    def test_available_colorbars(self, colorbar_registry, colorbar_test_filepath):
        """Test listing available colorbars."""
        colorbar_registry.register(colorbar_test_filepath)
        names = colorbar_registry.available()
        assert names == ["TEST_CBAR_1", "TEST_CBAR_2"], "Should list available colorbars."

        # Test it include reference colorbars
        reference_cbar_dict = {"reference": "TEST_CBAR_1"}
        colorbar_registry.add_cbar_dict(reference_cbar_dict, name="TEST_REFERENCE_CBAR")
        names = colorbar_registry.available()
        assert names == ["TEST_CBAR_1", "TEST_CBAR_2", "TEST_REFERENCE_CBAR"]

        # Test standalone and referenced colorbars
        names = colorbar_registry.get_standalone_settings()
        assert names == ["TEST_CBAR_1", "TEST_CBAR_2"]

        names = colorbar_registry.get_referenced_settings()
        assert names == ["TEST_REFERENCE_CBAR"]

    def test_category_filtering(self, colorbar_registry, colorbar_test_filepath):
        """Test filtering colorbars by category."""
        # Test it filter by category
        colorbar_registry.register(colorbar_test_filepath)
        names = colorbar_registry.available(category="TEST")
        assert names == ["TEST_CBAR_2"]

        # Test it exclude reference colorbars
        names = colorbar_registry.available(exclude_referenced=True)
        assert names == ["TEST_CBAR_1", "TEST_CBAR_2"]

    def test_show_colorbar(self, colorbar_registry, colorbar_test_filepath, mock_matplotlib_show):
        """Test show_colorbar method."""
        # Register cbar
        colorbar_registry.register(colorbar_test_filepath)
        # Test it runs
        _ = colorbar_registry.show_colorbar("TEST_CBAR_1")
        # Assert matplotlib show() is called
        mock_matplotlib_show.assert_called_once()

    def test_show_colorbars(self, colorbar_registry, colorbar_test_filepath, mock_matplotlib_show):
        """Test show_colorbars method."""
        # Test raise error if no colorbar registered
        with pytest.raises(ValueError) as excinfo:
            _ = colorbar_registry.show_colorbars()
        assert "No colorbars are yet registered in the pycolorbar ColorbarRegistry." in str(excinfo.value)

        # Register cbar
        colorbar_registry.register(colorbar_test_filepath)
        colorbar_registry.unregister("TEST_CBAR_2")

        # Test it works also with 1 colorbar
        _ = colorbar_registry.show_colorbars()
        mock_matplotlib_show.assert_called_once()

        # Register more than 1 colorbar
        colorbar_registry.register(colorbar_test_filepath)

        # Test it works also with more than 1 colorbar
        _ = colorbar_registry.show_colorbars()
        assert mock_matplotlib_show.call_count == 2


def test_utility_methods(colorbar_test_filepath):
    """Tests register_colorbar, get_cbar_dict and get_plot_kwargs utility."""
    cbar_name = "TEST_CBAR_1"
    assert cbar_name not in pycolorbar.colorbars

    # Test registering the colorbar
    pycolorbar.register_colorbar(filepath=colorbar_test_filepath, verbose=False, force=True)

    # Verify the colorbar is registered
    assert cbar_name in pycolorbar.colorbars.names
    assert cbar_name in pycolorbar.colorbars

    # Test retrieving the colorbar with get_cbar
    cbar = pycolorbar.get_cbar_dict(cbar_name)
    assert isinstance(cbar, dict)

    # Test retrieving the colorbar dictionary with get_plot_kwargs
    plot_kwargs, cbar_kwargs = pycolorbar.get_plot_kwargs(cbar_name)
    assert isinstance(plot_kwargs["cmap"], Colormap)
    assert isinstance(plot_kwargs["norm"], Normalize)
    assert isinstance(cbar_kwargs, dict)


def test_register_colorbars(colorbar_registry, tmp_path):
    """Tests register_colorbars in a directory."""
    # Define colorbars YAML files
    filepath1 = tmp_path / "temp_colorbar.yaml"
    filepath2 = tmp_path / "temp_colorbar1.yaml"
    cbar_dict1 = {"cmap": {"name": "viridis"}}
    cbar_dict2 = {"cmap": {"name": "viridis"}, "auxiliary": {"category": "TEST"}}
    cbar_dicts1 = {"TEST_CBAR_1": cbar_dict1, "TEST_CBAR_2": cbar_dict2}
    cbar_dicts2 = {"TEST_CBAR_3": {"cmap": {"name": "viridis"}}}
    write_yaml(cbar_dicts1, filepath1)
    write_yaml(cbar_dicts2, filepath2)

    # Assert empty colorbar register
    assert pycolorbar.colorbars.names == []

    # Test registering all colorbars in a directory
    pycolorbar.register_colorbars(directory=tmp_path)
    assert pycolorbar.colorbars.names == ["TEST_CBAR_1", "TEST_CBAR_2", "TEST_CBAR_3"]

    # Clear the registry
    pycolorbar.colorbars.reset()
    assert pycolorbar.colorbars.names == []


def test_available_colorbars(colorbar_registry, colorbar_test_filepath):
    """Test available_colorbars."""
    # Register colorbars
    colorbar_registry.register(filepath=colorbar_test_filepath, verbose=False, force=True)

    # Assert that the registered colorbars are returned
    names = pycolorbar.available_colorbars()
    assert names == ["TEST_CBAR_1", "TEST_CBAR_2"]

    # Test empty list for inexisting category
    names = pycolorbar.available_colorbars(category="inexistent")
    assert names == []

    # Test select specific category
    names = pycolorbar.available_colorbars(category="TEST")
    assert names == ["TEST_CBAR_2"]

    # Test include/exclude reference colorbars
    reference_cbar_dict = {"reference": "TEST_CBAR_1"}
    pycolorbar.colorbars.add_cbar_dict(reference_cbar_dict, name="TEST_REFERENCE_CBAR")

    names = pycolorbar.available_colorbars()
    assert "TEST_REFERENCE_CBAR" in names

    names = pycolorbar.available_colorbars(exclude_referenced=True)
    assert "TEST_REFERENCE_CBAR" not in names


def test_show_colorbar(colorbar_registry, colorbar_test_filepath, mock_matplotlib_show):
    """Test show_colorbar function."""
    # Register cbar
    colorbar_registry.register(colorbar_test_filepath)
    # Test it runs
    pycolorbar.show_colorbar("TEST_CBAR_1")
    # Assert matplotlib show() is called
    mock_matplotlib_show.assert_called_once()


def test_show_colorbars(colorbar_registry, colorbar_test_filepath, mock_matplotlib_show):
    """Test show_colorbars function."""
    # Test raise error if no colorbar registered
    with pytest.raises(ValueError) as excinfo:
        _ = colorbar_registry.show_colorbars()
    assert "No colorbars are yet registered in the pycolorbar ColorbarRegistry." in str(excinfo.value)

    # Register cbar
    colorbar_registry.register(colorbar_test_filepath)
    colorbar_registry.unregister("TEST_CBAR_2")

    # Test it works also with 1 colorbar
    pycolorbar.show_colorbars()
    mock_matplotlib_show.assert_called_once()

    # Register more than 1 colorbar
    colorbar_registry.register(colorbar_test_filepath)

    # Test it works also with more than 1 colorbar
    pycolorbar.show_colorbars()
    assert mock_matplotlib_show.call_count == 2
