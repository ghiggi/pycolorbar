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
"""Implementation of pydantic validator for univariate colorbar YAML files."""

import re
from typing import List, Optional, Union

import numpy as np
from pydantic import BaseModel, root_validator, validator

from pycolorbar.utils.mpl import get_mpl_colormaps, get_mpl_named_colors


class UnivariateCmapSettings(BaseModel):
    name: Union[str, List[str]]
    n: Optional[Union[int, List[int]]]
    bad_alpha: Optional[float]
    bad_color: Optional[str]
    over_color: Optional[str]
    under_color: Optional[str]

    class Config:
        arbitrary_types_allowed = True

    @validator("name")
    def validate_name(cls, v):
        """Check if cmap is a registered matplotlib colormap or name in pycolorbar.colormaps.registry."""
        import pycolorbar

        if isinstance(v, str):
            valid_names = get_mpl_colormaps() + pycolorbar.colormaps.names
            assert v in valid_names, f"'{v}' is not a recognized colormap name."
        elif isinstance(v, list):
            for name in v:
                valid_names = get_mpl_colormaps() + pycolorbar.colormaps.names
                assert name in valid_names, f"'{name}' is not a recognized colormap name."
        return v

    @validator("n")
    def validate_n(cls, v, values, **kwargs):
        if v is not None:
            # Single colormap
            if isinstance(values.get("name"), str):
                assert isinstance(v, int) and v > 0, "'n' must be a positive integer."
            # Multiple colormaps
            if isinstance(values.get("name"), list):
                assert len(values.get("name")) == len(v), "'n' must match the number of color maps in 'name'."
                for n in v:
                    assert isinstance(n, int) and n > 0, "'n' values must be positive integers."
        return v

    @validator("bad_color", "over_color", "under_color")
    def validate_colors(cls, v):
        if v is not None and v.lower() != "none":
            if isinstance(v, str):
                # Check if it's a named color
                if v in get_mpl_named_colors():
                    return v
                # Check if it's a hex color
                hex_color_pattern = re.compile(r"^#(?:[0-9a-fA-F]{3}){1,2}$")
                if not hex_color_pattern.match(v):
                    raise ValueError(
                        'Invalid color format. Expected hex string like "#RRGGBB" or "#RRGGBBAA", or a named color.'
                    )
            elif isinstance(v, (list, tuple)) and len(v) in [3, 4]:
                # Check if it's an RGB or RGBA tuple
                if not all(
                    isinstance(color_component, (int, float)) and 0 <= color_component <= 1 for color_component in v
                ):
                    raise ValueError("Invalid RGB/RGBA format. Expected tuple with values between 0 and 1.")
            else:
                raise ValueError("Invalid color format. Expected a named color, hex string, or RGB/RGBA tuple.")
        return v

    @validator("bad_alpha")
    def validate_bad_alpha(cls, v):
        if v is not None:
            assert 0 <= v <= 1, "bad_alpha must be between 0 and 1"
        return v


####-------------------------------------------------------------------------------------------------------------------.


def _check_norm_invalid_keys(norm_name, values, valid_args):
    invalid_keys = set(values.keys()) - set(valid_args)
    if invalid_keys:
        raise ValueError(f"Invalid parameters {invalid_keys} for normalization type '{norm_name}'.")


def _check_vmin_vcenter_vmax(vmin, vcenter, vmax, norm_name):
    if vmin is not None and vcenter is not None:
        assert vmin < vcenter, "'vmin' must be less than 'vcenter' for 'TwoSlopeNorm'."
    if vmax is not None and vcenter is not None:
        assert vcenter < vmax, "'vcenter' must be less than 'vmax' for 'TwoSlopeNorm'."


def _check_vmin_vmax(vmin, vmax):
    assert isinstance(vmin, (int, float, type(None))), "'vmin' must be an integer, float or None."
    assert isinstance(vmax, (int, float, type(None))), "'vmax' must be an integer, float or None."
    if vmin is not None and vmax is not None:
        assert vmin < vmax, "vmin must be less than vmax."


def _check_clip(clip):
    assert isinstance(clip, bool), "'clip' must be either True or False."


def _check_extend(extend):
    valid_extends = ["neither", "both", "min", "max"]
    assert extend in valid_extends, f"Invalid extend option '{extend}'. Valid options are {valid_extends}."


def _is_monotonically_increasing(x):
    x = np.asanyarray(x)
    return np.all(x[1:] > x[:-1])


def _get_boundary_norm_expected_ncolors(norm_settings):
    boundaries = norm_settings.get("boundaries", [])
    extend = norm_settings.get("extend", "neither")
    if extend == "neither":
        required_ncolors = len(boundaries) - 1
    elif extend in ["min", "max"]:
        required_ncolors = len(boundaries)
    else:  #  extend == 'both':
        required_ncolors = len(boundaries) + 1
    return required_ncolors


class NormalizeSettings(BaseModel):
    vmin: Optional[float]
    vmax: Optional[float]
    clip: Optional[bool] = False

    @validator("clip")
    def validate_clip(cls, v):
        """Validate `clip` option for Normalize."""
        _check_clip(v)
        return v

    @root_validator
    def check_vmin_vmax(cls, values):
        """Check `vmin` and `vmax` for Normalize."""
        vmin, vmax = values.get("vmin"), values.get("vmax")
        _check_vmin_vmax(vmin, vmax)
        return values

    @root_validator
    def check_valid_args(cls, values):
        """Check for no excess parameters in Normalize."""
        valid_args = {"vmin", "vmax", "clip"}
        _check_norm_invalid_keys(norm_name="Normalize", values=values, valid_args=valid_args)
        return values


class CategoryNormSettings(BaseModel):
    labels: List[str]
    first_value: Optional[int]

    @validator("labels")
    def validate_labels(cls, v, values):
        """Validate labels for CategoryNorm."""
        if v is not None:
            assert isinstance(v, list), "'labels' must be a list."
            assert len(v) >= 2, "'labels' must have at least two strings"
            assert all([isinstance(label, str) for label in v]), "'labels' must be a list of strings."
        return v

    @validator("first_value")
    def validate_first_value(cls, v, values):
        """Validate first_value for CategoryNorm."""
        if v is not None:
            assert isinstance(v, int), "'first_value' must be an integer."
        return v


class BoundaryNormSettings(BaseModel):
    # "ncolors" if not specified is taken from len(boundaries).

    boundaries: List[float]
    ncolors: Optional[int]
    clip: Optional[bool] = False
    extend: Optional[str] = "neither"

    @validator("boundaries")
    def validate_boundaries(cls, v):
        """Validate `boundaries` list for BoundaryNorm."""
        assert isinstance(v, list), "'boundaries' list is required for 'BoundaryNorm'."
        assert all(isinstance(b, (int, float)) for b in v), "'boundaries' must be a list of numbers."
        assert _is_monotonically_increasing(v), "'boundaries' must be monotonically increasing."
        return v

    @validator("clip")
    def validate_clip(cls, v):
        """Validate ` clip` option for BoundaryNorm."""
        _check_clip(v)
        return v

    @validator("extend")
    def validate_extend(cls, v):
        """Validate `extend` option for BoundaryNorm."""
        if v is not None:
            _check_extend(v)
        return v

    @validator("ncolors")
    def validate_ncolors(cls, v, values):
        """Validate `ncolors` for BoundaryNorm."""
        if v is not None:
            assert isinstance(v, int), "'ncolors' must be an integer for 'BoundaryNorm'."
            assert v >= 2, "'ncolors' must be equal or larger than 2."
            # - If extend is "neither" (default) there must be equal or larger than len(boundaries) - 1 colors.
            # - If extend is "min" or "max" ncolors must be equal or larger than len(boundaries)
            # - If extend is "both"  ncolors must be equal or larger than len(boundaries) + 1
            extend = values.get("extend", "neither")
            required_ncolors = _get_boundary_norm_expected_ncolors(norm_settings=values)
            if extend == "neither":
                assert (
                    v >= required_ncolors
                ), f"'ncolors' must be equal or larger than len('boundaries') - 1 ({required_ncolors})."
            elif extend in ["min", "max"]:
                assert (
                    v >= required_ncolors
                ), f"'ncolors' must be equal or larger than len('boundaries') ({required_ncolors})."
            elif extend == "both":
                assert (
                    v >= required_ncolors
                ), f"'ncolors' must be equal or larger than len('boundaries') + 1 ({required_ncolors})."
        return v

    @root_validator
    def check_valid_args(cls, values):
        """Check for no excess parameters in BoundaryNorm."""
        valid_args = {"boundaries", "ncolors", "clip", "extend"}
        _check_norm_invalid_keys(norm_name="BoundaryNorm", values=values, valid_args=valid_args)
        return values


class NoNormSettings(BaseModel):
    vmin: Optional[float]
    vmax: Optional[float]
    clip: Optional[bool] = False

    @validator("clip")
    def validate_clip(cls, v):
        """Validate `clip` option for NoNorm."""
        _check_clip(v)
        return v

    @root_validator
    def check_vmin_vmax(cls, values):
        """Check `vmin` and `vmax` for NoNorm."""
        vmin, vmax = values.get("vmin"), values.get("vmax")
        _check_vmin_vmax(vmin, vmax)
        return values

    @root_validator
    def check_valid_args(cls, values):
        """Check for no excess parameters in NoNorm."""
        valid_args = {"vmin", "vmax", "clip"}
        _check_norm_invalid_keys(norm_name="NoNorm", values=values, valid_args=valid_args)
        return values


class CenteredNormSettings(BaseModel):
    vcenter: Optional[Union[int, float]] = 0
    halfrange: Optional[Union[int, float]]
    clip: Optional[bool] = False

    @validator("clip")
    def validate_clip(cls, v):
        """Validate `clip` option for CenteredNorm."""
        _check_clip(v)
        return v

    @validator("vcenter")
    def validate_vcenter(cls, v):
        """Validate `vcenter` for CenteredNorm."""
        assert isinstance(v, (int, float)), "'vcenter' must be an integer or float."
        return v

    @validator("halfrange")
    def validate_halfrange(cls, v):
        """Validate `halfrange` for CenteredNorm."""
        if v is not None:
            assert isinstance(v, (int, float)), "'halfrange' must be an integer, float or None."
        return v

    @root_validator
    def check_valid_args(cls, values):
        """Check for no excess parameters in CenteredNorm."""
        valid_args = {"vcenter", "halfrange", "clip"}
        _check_norm_invalid_keys(norm_name="CenteredNorm", values=values, valid_args=valid_args)
        return values


class TwoSlopeNormSettings(BaseModel):
    vcenter: float
    vmin: Optional[float]
    vmax: Optional[float]

    @validator("vcenter")
    def validate_vcenter(cls, v):
        """Validate `vcenter` for TwoSlopeNorm."""
        assert isinstance(v, (int, float)), "'vcenter' must be an integer or float."
        return v

    @root_validator
    def check_vmin_vcenter_vmax(cls, values):
        """Check `vmin`, `vcenter`, and `vmax` for TwoSlopeNorm."""
        vmin, vcenter, vmax = values.get("vmin"), values.get("vcenter"), values.get("vmax")
        _check_vmin_vcenter_vmax(vmin=vmin, vcenter=vcenter, vmax=vmax, norm_name="TwoSlopeNorm")
        return values

    @root_validator
    def check_valid_args(cls, values):
        """Check for no excess parameters in TwoSlopeNorm."""
        valid_args = {"vcenter", "vmin", "vmax"}
        _check_norm_invalid_keys(norm_name="TwoSlopeNorm", values=values, valid_args=valid_args)
        return values


class LogNormSettings(BaseModel):
    vmin: Optional[float]
    vmax: Optional[float]
    clip: Optional[bool] = False

    @validator("clip")
    def validate_clip(cls, v):
        """Validate `clip` option for LogNorm."""
        _check_clip(v)
        return v

    @root_validator
    def check_vmin_vmax(cls, values):
        """Check `vmin` and `vmax` for LogNorm."""
        vmin, vmax = values.get("vmin"), values.get("vmax")
        _check_vmin_vmax(vmin, vmax)
        return values

    @root_validator
    def check_valid_args(cls, values):
        """Check for no excess parameters in LogNorm."""
        valid_args = {"vmin", "vmax", "clip"}
        _check_norm_invalid_keys(norm_name="LogNorm", values=values, valid_args=valid_args)
        return values


class SymLogNormSettings(BaseModel):
    linthresh: float
    linscale: Optional[float] = 1.0
    base: Optional[float] = 10
    vmin: Optional[float]
    vmax: Optional[float]
    clip: Optional[bool] = False

    @validator("linthresh")
    def validate_linthresh(cls, v):
        """Validate `linthresh` for SymLogNorm."""
        assert v > 0, "'linthresh' must be positive for 'SymLogNorm'."
        return v

    @validator("linscale", "base")
    def validate_linscale_base(cls, v, field):
        """Validate `linscale` and `base` for SymLogNorm."""
        if v is not None:
            assert v > 0, f"'{field.name}' must be positive for 'SymLogNorm'."
        return v

    @validator("clip")
    def validate_clip(cls, v):
        """Validate `clip` option for SymLogNorm."""
        _check_clip(v)
        return v

    @root_validator
    def check_vmin_vmax(cls, values):
        """Check `vmin` and `vmax` for SymLogNorm."""
        vmin, vmax = values.get("vmin"), values.get("vmax")
        _check_vmin_vmax(vmin, vmax)
        return values

    @root_validator
    def check_valid_args(cls, values):
        """Check for no excess parameters in SymLogNorm."""
        valid_args = ["linthresh", "linscale", "vmin", "vmax", "clip", "base"]
        _check_norm_invalid_keys(norm_name="SymLogNorm", values=values, valid_args=valid_args)
        return values


class PowerNormSettings(BaseModel):
    gamma: float
    vmin: Optional[float]
    vmax: Optional[float]
    clip: Optional[bool] = False

    @validator("gamma")
    def validate_gamma(cls, v):
        """Validate `gamma` for PowerNorm."""
        assert isinstance(v, (int, float)), "'gamma' must be an integer or float."
        return v

    @validator("clip")
    def validate_clip(cls, v):
        """Validate `clip` option for PowerNorm."""
        _check_clip(v)
        return v

    @root_validator
    def check_vmin_vmax(cls, values):
        """Check `vmin` and `vmax` for PowerNorm."""
        vmin, vmax = values.get("vmin"), values.get("vmax")
        _check_vmin_vmax(vmin, vmax)
        return values

    @root_validator
    def check_valid_args(cls, values):
        """Check for no excess parameters in PowerNorm."""
        valid_args = ["gamma", "vmin", "vmax", "clip"]
        _check_norm_invalid_keys(norm_name="PowerNorm", values=values, valid_args=valid_args)
        return values


class AsinhNormSettings(BaseModel):
    linear_width: Optional[Union[int, float]]
    vmin: Optional[float]
    vmax: Optional[float]
    clip: Optional[bool] = False

    @validator("linear_width")
    def validate_linear_width(cls, v):
        """Validate `linear_width` for AsinhNorm."""
        assert isinstance(v, (int, float)), "'linear_width' must be an integer or float."
        return v

    @validator("clip")
    def validate_clip(cls, v):
        """Validate `clip` option for AsinhNorm."""
        _check_clip(v)
        return v

    @root_validator
    def check_vmin_vmax(cls, values):
        """Check `vmin` and `vmax` for AsinhNorm."""
        vmin, vmax = values.get("vmin"), values.get("vmax")
        _check_vmin_vmax(vmin, vmax)
        return values

    @root_validator
    def check_valid_args(cls, values):
        """Check for no excess parameters in AsinhNorm."""
        valid_args = ["linear_width", "vmin", "vmax", "clip"]
        _check_norm_invalid_keys(norm_name="AsinhNorm", values=values, valid_args=valid_args)
        return values


def _check_valid_norm_name(name):
    valid_names = [
        "Norm",
        "NoNorm",
        "BoundaryNorm",
        "TwoSlopeNorm",
        "CenteredNorm",
        "LogNorm",
        "SymLogNorm",
        "PowerNorm",
        "AsinhNorm",
        "CategoryNorm",
    ]
    if name not in valid_names:
        raise ValueError(f"Invalid norm '{name}'. Valid options are {valid_names}.")


def check_norm_settings(norm_settings):
    # Check valid *Norm name
    name = norm_settings.get("name", "Norm")
    _check_valid_norm_name(name)
    # Define *Norm validators
    norm_settings_mapping = {
        "Norm": NormalizeSettings,
        "NoNorm": NoNormSettings,
        "BoundaryNorm": BoundaryNormSettings,
        "TwoSlopeNorm": TwoSlopeNormSettings,
        "CenteredNorm": CenteredNormSettings,
        "LogNorm": LogNormSettings,
        "SymLogNorm": SymLogNormSettings,
        "PowerNorm": PowerNormSettings,
        "AsinhNorm": AsinhNormSettings,
        "CategoryNorm": CategoryNormSettings,
    }
    # Validate Norm kwargs
    validator = norm_settings_mapping[name]
    norm_kwargs = norm_settings.copy()
    _ = norm_kwargs.pop("name", None)
    _ = validator(**norm_kwargs)


####-------------------------------------------------------------------------------------------------------------------.


class CbarSettings(BaseModel):
    extend: Optional[str]  # e.g., 'neither', 'both', 'min', 'max'
    extendfrac: Optional[Union[float, List[float]]]
    extendrect: Optional[bool]
    label: Optional[str]  # title of colorbar

    class Config:
        arbitrary_types_allowed = True

    @validator("extend")
    def validate_extend(cls, v):
        """Validate extend option."""
        if v is not None:
            _check_extend(v)
        return v

    @validator("extendfrac")
    def validate_extendfrac(cls, v):
        """Validate extend fraction."""
        if v is not None:
            if isinstance(v, list):
                assert all(
                    isinstance(frac, (float, int)) and 0 <= frac <= 1 for frac in v
                ), "Each extendfrac in the list must be a float or int between 0 and 1."
            else:
                assert isinstance(v, (float, int)) and 0 <= v <= 1, "extendfrac must be a float or int between 0 and 1."
        return v

    @validator("extendrect")
    def validate_extendrect(cls, v):
        """Validate extend rectangle option."""
        if v is not None:
            assert isinstance(v, bool), "extendrect must be a boolean value."
        return v

    @validator("label")
    def validate_label(cls, v):
        """Validate label as string."""
        if v is not None:
            assert isinstance(v, str), "label must be a string."
        return v


####-------------------------------------------------------------------------------------------------------------------.


def _check_cbar_reference(cbar_dict):
    import pycolorbar

    if len(list(cbar_dict)) > 1:
        raise ValueError("If 'reference' is specified, no other parameter is accepted.")
    reference = cbar_dict["reference"]
    if reference not in pycolorbar.colorbars.names:
        raise ValueError(f"The {reference} colorbar is not registered in pycolorbar. Invalid reference !")
    cbar_ref_dict = pycolorbar.colorbars.get_cbar_dict(reference)
    if "reference" in cbar_ref_dict:
        raise ValueError(f"The {reference} colorbar is again pointing to another colorbar. This is not allowed !")


def _check_discrete_norm_cmap_settings(cmap_settings, norm_settings):
    norm = norm_settings.get("name", "Norm")
    if norm not in ["CategoryNorm", "BoundaryNorm"]:
        return
    if norm == "CategoryNorm":
        ncolors = len(norm_settings["labels"])
    else:  # "BoundaryNorm"
        ncolors = _get_boundary_norm_expected_ncolors(norm_settings=norm_settings)

    n = cmap_settings.get("n", None)
    if n is not None:
        # Single Colormap
        if isinstance(n, int):
            assert n == ncolors, "'n' is optional and must be {ncolors} for the specified discrete norm."
        # Multiple colormaps
        else:
            assert sum(n) == ncolors, "The sum of 'n' must be {ncolors} for the specified discrete norm."


def validate_cbar_dict(cbar_dict: dict):
    # Check if cbar_dict reference to another colorbar settings
    if "reference" in cbar_dict:
        _check_cbar_reference(cbar_dict)
        return cbar_dict

    # Retrieve cmap, norm and cbar settings
    cmap_settings = cbar_dict["cmap"]
    norm_settings = cbar_dict.get("norm", {})
    cbar_settings = cbar_dict.get("cbar", {})

    # Test validity
    invalid_configuration = False

    try:
        _ = UnivariateCmapSettings(**cmap_settings)
    except Exception as e:
        invalid_configuration = True
        print(f"Colormap validation error: {e}")

    try:
        check_norm_settings(norm_settings)
    except Exception as e:
        invalid_configuration = True
        print(f"Norm validation error: {e}")

    try:
        _ = CbarSettings(**cbar_settings)
    except Exception as e:
        invalid_configuration = True
        print(f"Colorbar validation error: {e}")

    # Consistency checks
    try:
        _check_discrete_norm_cmap_settings(cmap_settings=cmap_settings, norm_settings=norm_settings)
    except Exception as e:
        invalid_configuration = True
        print(f"Categorical Colormap validation error: {e}")

    if invalid_configuration:
        raise ValueError("Invalid configuration")

    # Return dictionary
    return cbar_dict
