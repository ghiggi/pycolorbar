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
"""Define functions to read and write colorbar YAML files."""
import os

import numpy as np

from pycolorbar.settings.colorbar_validator import validate_cbar_dict
from pycolorbar.utils.yaml import read_yaml, write_yaml


def remove_if_exists(filepath, force=False):
    if os.path.exists(filepath):
        if force:
            os.remove(filepath)
        else:
            raise ValueError(f"The {filepath} already exists !")


def read_cbar_dict(filepath):
    cbar_dict = read_yaml(filepath)
    # CONFIG FILE. pycolorbar.validate_at_registration
    # CONFIG FILE. pycolorbar.validate_at_selection
    cbar_dict = validate_cbar_dict(cbar_dict)
    return cbar_dict


def read_cbar_dicts(filepath):
    cbar_dicts = read_yaml(filepath)
    # TODO: Check is nested dictionary (names does not correspond to keywords ... )
    return cbar_dicts


def write_cbar_dict(cbar_dict, filepath, force=False):
    # Check if file exist
    remove_if_exists(filepath, force=force)
    # Validate fields
    cbar_dict = validate_cbar_dict(cbar_dict=cbar_dict)
    # Write file
    write_yaml(cbar_dict, filepath, sort_keys=False)


def tmp_conv_to_new_format(cbar_dict):
    # cmap
    cmap_keys = [
        "cmap",
        "cmap_n",
        "bad_alpha",
        "bad_color",
        "over_color",
        "under_color",
    ]

    cmap_keys_map = {
        "cmap": "name",
        "cmap_n": "n",
    }

    norm_keys = [
        "norm",
        "vmin",
        "vmax",
        "linthresh",
        "linscale",
        "base",
        "levels",
        "labels",
    ]

    norm_keys_map = {
        "norm": "name",
        "levels": "boundaries",
    }

    cbar_keys = [
        "extend",
        "extendfrac",
        "extendrect",
        "label",
    ]

    new_cbar_dict = {}

    # Reference
    if "reference" in cbar_dict:
        new_cbar_dict["reference"] = cbar_dict["reference"]
        return new_cbar_dict

    # Cmap
    if np.any(np.isin(cmap_keys, list(cbar_dict))):
        new_cbar_dict["cmap"] = {}
        for key in cmap_keys:
            if key in cbar_dict:
                value = cbar_dict[key]
                if key in cmap_keys_map:
                    new_key = cmap_keys_map[key]
                else:
                    new_key = key
                new_cbar_dict["cmap"][new_key] = value

    # Norm
    if np.any(np.isin(norm_keys, list(cbar_dict))):
        new_cbar_dict["norm"] = {}
        if "norm" not in cbar_dict:
            if "labels" in cbar_dict:
                new_cbar_dict["norm"]["name"] = "CategoryNorm"
            elif "levels" in cbar_dict:
                new_cbar_dict["norm"]["name"] = "BoundaryNorm"
            else:
                new_cbar_dict["norm"]["name"] = "Norm"

        for key in norm_keys:
            if key in cbar_dict:
                value = cbar_dict[key]
                if key in norm_keys_map:
                    new_key = norm_keys_map[key]
                else:
                    new_key = key
                new_cbar_dict["norm"][new_key] = value

    # Cbar
    if np.any(np.isin(cbar_keys, list(cbar_dict))):
        new_cbar_dict["cbar"] = {}
        for key in cbar_keys:
            if key in cbar_dict:
                value = cbar_dict[key]
                new_cbar_dict["cbar"][key] = value
    # Auxiliary
    aux_keys = ["citation", "citation_url", "author", "author_url", "comment", "category"]
    if np.any(np.isin(aux_keys, list(cbar_dict))):
        new_cbar_dict["auxiliary"] = {}
        for key in aux_keys:
            if key in cbar_dict:
                value = cbar_dict[key]
                new_cbar_dict["auxiliary"][key] = value

    return new_cbar_dict


def write_cbar_dicts(cbar_dicts, filepath, names=None, force=False, sort_keys=False):
    if isinstance(names, str):
        names = [names]

    # Check if file exist
    remove_if_exists(filepath, force=force)

    # Select colorbars
    if names is not None:
        cbar_dicts = {name: cbar_dicts[name] for name in names}

    # Conversion colorbars
    cbar_dicts = {name: tmp_conv_to_new_format(cbar_dict=cbar_dict) for name, cbar_dict in cbar_dicts.items()}

    # Validate colorbars
    cbar_dicts = {name: validate_cbar_dict(cbar_dict=cbar_dict) for name, cbar_dict in cbar_dicts.items()}

    # Write file
    write_yaml(cbar_dicts, filepath, sort_keys=sort_keys)
