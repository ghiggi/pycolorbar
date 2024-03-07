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

import matplotlib.pyplot as plt  # noqa
import pytest
from deepdiff import DeepDiff
from pytest_mock import mocker  # noqa
from pycolorbar.settings.colorbar_registry import (
    ColorbarRegistry,
)
from pycolorbar.utils.yaml import write_yaml


@pytest.fixture
def colorbar_registry():
    """Fixture to initialize and reset the colorbar registry."""
    registry = ColorbarRegistry.get_instance()
    registry.reset()

    yield registry

    registry.reset()


@pytest.fixture
def mock_matplotlib_show(mocker):  # noqa
    mock = mocker.patch("matplotlib.pyplot.show")
    yield mock


@pytest.fixture
def colorbar_test_filepath(tmp_path):
    """Fixture to create a temporary colorbar YAML file."""
    filepath = tmp_path / "temp_colorbar.yaml"
    cbar_dict1 = {"cmap": {"name": "viridis"}}
    cbar_dict2 = {"cmap": {"name": "viridis"}, "auxiliary": {"category": "TEST"}}
    cbar_dicts = {"TEST_CBAR_1": cbar_dict1, "TEST_CBAR_2": cbar_dict2}
    write_yaml(cbar_dicts, filepath)
    return filepath


@pytest.fixture
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

    def test_validate_registered_colorbars(self, colorbar_registry, colorbar_test_filepath):
        """Test validation of registered colorbars."""
        colorbar_registry.register(colorbar_test_filepath)
        colorbar_registry.validate()

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

    def test_available_colorbars(self, colorbar_registry, colorbar_test_filepath):
        """Test listing available colorbars."""
        colorbar_registry.register(colorbar_test_filepath)
        names = colorbar_registry.available()
        assert names == ["TEST_CBAR_1", "TEST_CBAR_2"], "Should list available colorbars."

    def test_category_filtering(self, colorbar_registry, colorbar_test_filepath):
        """Test filtering colorbars by category."""
        colorbar_registry.register(colorbar_test_filepath)
        names = colorbar_registry.available(category="TEST")
        assert names == ["TEST_CBAR_2"]
