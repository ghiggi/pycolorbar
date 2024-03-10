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
"""Test Colorbar YAML files IO."""
import os

import pytest
from deepdiff import DeepDiff

from pycolorbar.settings.colorbar_io import (
    is_single_colorbar_settings,
    read_cbar_dict,
    read_cbar_dicts,
    write_cbar_dict,
    write_cbar_dicts,
)


def check_validated_dictionary_superset(validated_dict, original_dict):
    """Check the validated_dict is a superset of the original_dict."""
    for cbar_name, cbar_dict in original_dict.items():
        for key, values in cbar_dict.items():
            assert validated_dict[cbar_name][key] == values


class TestColorbarIO:
    @pytest.fixture
    def test_cbar_dict(self):
        """Return test cbar_dict."""
        cbar_dict = {"cmap": {"name": "viridis"}, "norm": {"name": "Norm"}, "cbar": {"extend": "both"}}
        return cbar_dict

    @pytest.fixture
    def test_cbar_dicts(self):
        """Return test cbar_dicts."""
        cbar_dicts = {
            "cbar1": {"cmap": {"name": "viridis"}, "norm": {"name": "Norm"}, "cbar": {"extend": "both"}},
            "cbar2": {"cmap": {"name": "plasma"}, "norm": {"name": "LogNorm"}, "cbar": {"extend": "neither"}},
        }
        return cbar_dicts

    def test_is_single_colorbar_settings(self, test_cbar_dict):
        # Assert cbar_dict
        assert is_single_colorbar_settings(test_cbar_dict)

        # Assert cbar_dicts case

    def test_is_single_colorbar_settings_false(self):
        assert not is_single_colorbar_settings({"not_cbar_setting": "value"})

    def test_read_write_cbar_dict(self, tmp_path, test_cbar_dict):
        """Test write_cbar_dict and read_cbar_dict."""
        # Setup
        filepath = os.path.join(tmp_path, "new_name.yaml")

        # Write to disk (without validation)
        write_cbar_dict(test_cbar_dict, "original_name", filepath, validate=False)
        assert os.path.exists(filepath)

        # Verify dictionary equality
        cbar_dict = read_cbar_dict(filepath)
        diff = DeepDiff(cbar_dict, test_cbar_dict)
        assert diff == {}, f"Dictionaries are not equal: {diff}"

        # Verify dictionary inequality if validate=True (because of set defaults)
        cbar_dict = read_cbar_dict(filepath, validate=True)
        diff = DeepDiff(cbar_dict, test_cbar_dict)
        assert diff != {}, f"Dictionaries are not equal: {diff}"

        # Now write to disk (with validation)
        write_cbar_dict(test_cbar_dict, "original_name", filepath, force=True)  # validate=True by default
        assert os.path.exists(filepath)

        # Assert that when read with read_cbar_dicts, the first dictionary level is the colorbar name !
        validated_cbar_dicts = read_cbar_dicts(filepath)
        assert list(validated_cbar_dicts) == ["new_name"]

    def test_read_write_cbar_dicts(self, tmp_path, test_cbar_dicts):
        """Test write_cbar_dicts and read_cbar_dicts."""
        # Setup multiple colorbar settings
        filepath = os.path.join(tmp_path, "whatever_name.yaml")

        # Write cbar_dicts
        write_cbar_dicts(test_cbar_dicts, filepath, validate=False)
        assert os.path.exists(filepath)

        # Verify dictionary equality
        cbar_dicts = read_cbar_dicts(filepath)
        diff = DeepDiff(cbar_dicts, test_cbar_dicts)
        assert diff == {}, f"Dictionaries are not equal: {diff}"

        # Now write to disk (with validation)
        write_cbar_dicts(test_cbar_dicts, filepath, force=True)  # validate=True by default
        assert os.path.exists(filepath)

        # Read validated cbar_dicts
        validated_cbar_dicts = read_cbar_dicts(filepath)
        assert isinstance(validated_cbar_dicts, dict)
        assert set(validated_cbar_dicts.keys()) == set(test_cbar_dicts.keys())
        assert "whatever_name" not in validated_cbar_dicts

        # Assert the read validated colorbar dictionary contains the key-value of the written one
        check_validated_dictionary_superset(validated_dict=validated_cbar_dicts, original_dict=test_cbar_dicts)
