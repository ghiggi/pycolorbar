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
import os

import pytest

from pycolorbar.utils.directories import list_files, remove_file_if_exists


def test_list_files(tmp_path):
    """Test list_files functions."""
    # Set up test environment
    ext = "yaml"
    dir1 = tmp_path / "dir1"
    dir1.mkdir()

    dir1_dummy = tmp_path / "dir1_dummy"
    dir1_dummy.mkdir()

    dir2 = dir1 / "dir2"
    dir2.mkdir()

    dir2_dummy = dir1 / "dir2_dummy"
    dir2_dummy.mkdir()

    file1 = tmp_path / f"file1.{ext}"
    file2 = tmp_path / f"file2.{ext}"
    file3 = tmp_path / "file3.ANOTHER"

    file4 = dir1 / f"file4.{ext}"
    file5 = dir1 / "file5.ANOTHER"

    file6 = dir2 / f"file6.{ext}"

    file1.touch()
    file2.touch()
    file3.touch()
    file4.touch()
    file5.touch()
    file6.touch()

    glob_pattern = "*"
    expected_files = [file1, file2, file3]
    assert set(list_files(tmp_path, glob_pattern, recursive=False)) == set(map(str, expected_files))

    glob_pattern = os.path.join("*", "*")
    expected_files = [file4, file5]
    assert set(list_files(tmp_path, glob_pattern, recursive=False)) == set(map(str, expected_files))

    glob_pattern = f"*.{ext}"
    expected_files = [file1, file2]
    assert set(list_files(tmp_path, glob_pattern, recursive=False)) == set(map(str, expected_files))

    glob_pattern = os.path.join("*", f"*.{ext}")
    expected_files = [file4]
    assert set(list_files(tmp_path, glob_pattern, recursive=False)) == set(map(str, expected_files))

    glob_pattern = f"*.{ext}"
    expected_files = [file1, file2, file4, file6]
    assert set(list_files(tmp_path, glob_pattern, recursive=True)) == set(map(str, expected_files))

    glob_pattern = os.path.join("*", f"*.{ext}")
    expected_files = [file4, file6]
    assert set(list_files(tmp_path, glob_pattern, recursive=True)) == set(map(str, expected_files))


class Test_Remove_File_If_Exists:
    """Test remove_file_if_exists."""

    def test_filepath_is_directory(self, tmp_path):
        tmp_directory = tmp_path / "test_directory"
        tmp_directory.mkdir()

        # Check it raise an error if force=False
        with pytest.raises(ValueError):
            remove_file_if_exists(filepath=tmp_directory, force=False)

        # Check it raise an error if force=True
        with pytest.raises(ValueError):
            remove_file_if_exists(filepath=tmp_directory, force=False)

    def test_remove_file_if_exists_file(self, tmp_path):
        filepath = tmp_path / "test_pycolorbar.yaml"
        filepath.write_text("This is a test file.")

        # Check it raise an error if force=False
        with pytest.raises(ValueError):
            remove_file_if_exists(filepath, force=False)

        # Check it removes the directory
        remove_file_if_exists(filepath, force=True)

        # Test the removal
        assert not os.path.exists(filepath)
