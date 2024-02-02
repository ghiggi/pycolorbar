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
"""Define functions to retrieve the plotting arguments."""

import matplotlib as mpl
import numpy as np
from matplotlib.colors import (
    AsinhNorm,
    BoundaryNorm,
    CenteredNorm,
    LinearSegmentedColormap,
    LogNorm,
    NoNorm,
    Normalize,
    PowerNorm,
    SymLogNorm,
    TwoSlopeNorm,
)

import pycolorbar


def _get_cmap(cmap_settings, norm_settings):
    """Retrieve the colormap for a given colorbar setting."""

    name = cmap_settings.get("name")

    # Define number of colors required
    n = cmap_settings.get("n", None)
    if "labels" in cmap_settings:
        n = len(cmap_settings["labels"])
    if "boundaries" in norm_settings:
        n = len(norm_settings["boundaries"]) - 1

    # Define colormap
    if isinstance(name, str):
        cmap = pycolorbar.get_cmap(name=name, lut=n)
        return cmap
    else:  # Colormap combination
        # - Define default arguments
        if n is None:
            n = [None] * len(name)

        new_n = [256] * len(
            name
        )  # this could become a YAML parameter (divisible by len(names) (only for stacked cmaps))
        new_name = "_".join(name)
        # - Define combined colormap
        list_cmaps = [pycolorbar.get_cmap(cmap_name, lut=lut) for cmap_name, lut in zip(name, n)]
        cmap_colors = np.vstack([cmap(np.linspace(0, 1, lut)) for cmap, lut in zip(list_cmaps, new_n)])
        cmap = LinearSegmentedColormap.from_list(name=new_name, colors=cmap_colors)
        return cmap


def _finalize_cmap(cmap, cmap_settings):
    """Set alpha and under, over and bad colors."""
    # Set over and under colors
    # - If not specified, do not set ---> It will be filled with the first/last color value
    # - If 'none' --> It will be depicted in white
    if cmap_settings.get("over_color", None):
        cmap.set_over(color=cmap_settings.get("over_color"), alpha=cmap_settings.get("over_alpha", None))
    if cmap_settings.get("under_color", None):
        cmap.set_under(color=cmap_settings.get("under_color"), alpha=cmap_settings.get("under_alpha", None))

    # Set bad color
    # - If not 0, can cause cartopy bug
    # --> https://stackoverflow.com/questions/60324497/specify-non-transparent-color-for-missing-data-in-cartopy-map
    cmap.set_bad(
        color=cmap_settings.get("bad_color", "none"),
        alpha=cmap_settings.get("bad_alpha", None),
    )
    return cmap


def get_cmap(cbar_dict):
    """Retrieve the colormap from a colorbar configuration dictionary."""
    # Retrieve settings
    cmap_settings = cbar_dict["cmap"]
    norm_settings = cbar_dict.get("norm", {})
    # Retrieve cmap
    cmap = _get_cmap(cmap_settings=cmap_settings, norm_settings=norm_settings)
    ### Set bad, under and over colors and transparency
    cmap = _finalize_cmap(cmap, cmap_settings)
    return cmap


####-------------------------------------------------------------------------------------------.
#### CategoryNorm
def create_category_norm(labels, first_value=0):
    """Define a BoundaryNorm that deal with categorical data."""
    n_labels = len(labels)
    norm_bins = np.arange(first_value - 0.01, n_labels + first_value) + 0.5
    norm = mpl.colors.BoundaryNorm(boundaries=norm_bins, ncolors=n_labels)
    return norm


####-------------------------------------------------------------------------------------------.
#### Norm utility


def get_norm_function(name):
    """Retrieve the norm function."""
    # Define norm function mapping
    norm_functions = {
        "Norm": Normalize,
        "NoNorm": NoNorm,
        "BoundaryNorm": BoundaryNorm,
        "TwoSlopeNorm": TwoSlopeNorm,
        "CenteredNorm": CenteredNorm,
        "LogNorm": LogNorm,
        "SymLogNorm": SymLogNorm,
        "PowerNorm": PowerNorm,
        "AsinhNorm": AsinhNorm,
        "CategoryNorm": create_category_norm,
    }
    return norm_functions[name]


def get_norm(cbar_dict):
    """Define the norm instance."""
    norm_settings = cbar_dict["norm"]
    norm_name = norm_settings.get("name", "Norm")
    # Retrieve norm function
    norm_func = get_norm_function(norm_name)
    # Retrieve norm arguments
    norm_kwargs = norm_settings.copy()
    _ = norm_kwargs.pop("name", None)
    # Set default values for BoundaryNorm
    if norm_name == "BoundaryNorm" and norm_kwargs.get("ncolors", None) is None:
        boundaries = norm_settings["boundaries"]
        ncolors = len(boundaries) - 1
        norm_kwargs["ncolors"] = ncolors
    # Define norm
    norm = norm_func(**norm_kwargs)
    return norm


####-------------------------------------------------------------------------------------------.
#### pycolorbar default settings


# TODO:
# Check vmin and vmax are None if using BoundaryNorm
# Check vmin and vmax are None when providing a Norm

# --> Allow labels also for BoundaryNorm ? But remove from kwargs when norm generation ?

# --> Adapt cmap for 'labels' (define n)


def get_plot_cbar_kwargs(cbar_dict):
    # ------------------------------------------------------------------------.
    # Set default colormap
    if cbar_dict == {}:
        cbar_dict["cmap"] = {"name": "jet"}
        cbar_dict["norm"] = {"name": "Norm"}

    # ------------------------------------------------------------------------.
    # Initialize kwargs
    plot_kwargs = {}
    cbar_kwargs = get_default_cbar_kwargs()

    # ------------------------------------------------------------------------.
    # Define cmap, norm, ticks and cbar appearance based on colorbar dictionary settings
    if "cmap" in cbar_dict:
        plot_kwargs["cmap"] = get_cmap(cbar_dict)
    if "norm" in cbar_dict:
        norm = get_norm(cbar_dict)
        ticks, ticklabels = _get_ticks_settings(cbar_dict, norm=norm)
        plot_kwargs["norm"] = norm
        # - TODO: Add only if not None ?
        cbar_kwargs["ticks"] = ticks
        cbar_kwargs["ticklabels"] = ticklabels
    if "cbar" in cbar_dict:
        cbar_kwargs.update(cbar_dict["cbar"])

    # ------------------------------------------------------------------------.
    return plot_kwargs, cbar_kwargs


def get_default_cbar_kwargs():
    cbar_kwargs = {
        "ticks": None,
        "ticklocation": "auto",
        "spacing": "uniform",  # or proportional
        "extend": "neither",
        "extendfrac": "auto",
        "extendrect": False,
        "label": None,
        "drawedges": False,
        "shrink": 1,
    }
    return cbar_kwargs


def _dynamic_formatting_floats(float_array):
    """Function to format the floats defining the class limits of the colorbar."""
    float_array = np.array(float_array, dtype=float)
    labels = []
    for label in float_array:
        if 0.1 <= label < 1:
            formatting = ",.2f"
        elif 0.01 <= label < 0.1:
            formatting = ",.2f"
        elif 0.001 <= label < 0.01:
            formatting = ",.3f"
        elif 0.0001 <= label < 0.001:
            formatting = ",.4f"
        elif label >= 1 and label.is_integer():
            formatting = "i"
        else:
            formatting = ",.1f"
        if formatting != "i":
            labels.append(format(label, formatting))
        else:
            labels.append(str(int(label)))
    return labels


def _get_ticks_settings(cbar_dict, norm=None):
    # Retrieve settings
    norm_settings = cbar_dict["norm"]
    boundaries = norm_settings.get("boundaries", None)
    labels = norm_settings.get("labels", None)
    # Define ticks and ticklabels for BoundaryNorm instances
    if isinstance(norm, BoundaryNorm):
        # Define ticks
        if boundaries is not None:  # BoundaryNorm
            ticks = boundaries
        else:  # CategoryNorm
            ticks = norm.boundaries[:-1] + 0.5
        # Define ticklabels
        if labels is None:  # BoundaryNorm
            # Generate color level strings with correct amount of decimal places
            ticklabels = _dynamic_formatting_floats(ticks)  # [f"{tick:.1f}" for tick in ticks] # for 0.1 probability
        else:
            # Define tick formatter and ticks
            fmt = mpl.ticker.FuncFormatter(lambda x, pos: labels[norm(x)])
            ticklabels = [fmt(tick) for tick in ticks]
    else:
        ticks = None
        ticklabels = None
    return ticks, ticklabels


####--------------------------------------------------------------------------------------------.
#### Update pycolorbar settings based on user arguments


def update_plot_cbar_kwargs(default_plot_kwargs, default_cbar_kwargs, user_plot_kwargs={}, user_cbar_kwargs={}):
    # If no user kwargs, return default kwargs
    if user_plot_kwargs == {} and user_cbar_kwargs == {}:
        return default_plot_kwargs, default_cbar_kwargs

    # If user cmap
    # - is a string, retrieve colormap
    # - is None --> delete the argument
    _parse_user_cmap(user_plot_kwargs=user_plot_kwargs)

    # If norm is specified, vmin and vmax must be None !
    _check_no_vmin_vmax_if_norm_specified(user_plot_kwargs=user_plot_kwargs)

    # TODO
    # - WHAT TO DO IF TICKS AND TICKLABELS SPECIFIED IN user_cbar_kwargs
    # --> If BoundaryNorm and change length --> Raise error?
    # --> If no BoundaryNorm?

    # Deal with categorical/discrete colorbar (when user specify new norm)
    # - Remove ticks and ticklabels when user specify new norm !
    # - Later on:
    #   - If user specify a new cmap --> the cmap is resampled based on len(ticklabels)
    #   - If vmin or vmax are specified --> a Normalize(vmin, vmax) replace BoundaryNorm
    if user_plot_kwargs.get("norm", None) is not None:
        _remove_defaults_ticks_and_ticklabels(default_cbar_kwargs=default_cbar_kwargs)

    # Deal with categorical/discrete labeled colorbar (when user provides a new cmap)
    # - Resample user-provided colormap
    if default_cbar_kwargs.get("ticklabels", None) is not None:
        _resample_user_cmap_for_labeled_colorbar(
            user_plot_kwargs=user_plot_kwargs, default_cbar_kwargs=default_cbar_kwargs
        )

    # Deal with xarray user_plot_kwargs 'levels' option
    # - Define a BoundaryNorm and resample the cmap accordingly
    if "levels" in user_plot_kwargs:
        _create_boundary_norm_from_levels(user_plot_kwargs=user_plot_kwargs, default_plot_kwargs=default_plot_kwargs)

    # If norm is not specified but vmin and vmax are specified
    # --> Check the default norm accepts vmin and vmax arguments
    # --> If yes, update the default norm to use specified vmin and vmax
    # --> If no, warn and define a Normalize(vmin, vmax)
    if user_plot_kwargs.get("norm", None) is None:
        _update_default_norm_using_vmin_and_vmax(
            user_plot_kwargs=user_plot_kwargs, default_plot_kwargs=default_plot_kwargs
        )

    # Drop vmin and vmax from user_plot_kwargs (not accepted by PolyCollection)
    _ = user_plot_kwargs.pop("vmin", None)
    _ = user_plot_kwargs.pop("vmax", None)

    # Deal with xarray optional 'extend' plot_kwargs
    # - extend is copied also in the user_cbar_kwargs
    if "extend" in user_plot_kwargs and "extend" not in user_cbar_kwargs:
        user_cbar_kwargs["extend"] = user_plot_kwargs["extend"]

    # Update defaults with custom kwargs
    default_plot_kwargs.update(user_plot_kwargs)
    default_cbar_kwargs.update(user_cbar_kwargs)

    return default_plot_kwargs, default_cbar_kwargs


def _remove_defaults_ticks_and_ticklabels(default_cbar_kwargs):
    default_ticks = default_cbar_kwargs.get("ticks", None)
    default_ticklabels = default_cbar_kwargs.get("ticklabels", None)
    if default_ticks is not None or default_ticklabels is not None:
        default_cbar_kwargs.pop("ticks", None)
        default_cbar_kwargs.pop("ticklabels", None)


def _resample_user_cmap_for_labeled_colorbar(user_plot_kwargs, default_cbar_kwargs):
    default_ticklabels = default_cbar_kwargs.get("ticklabels", None)
    n_labels = len(default_ticklabels)
    if user_plot_kwargs.get("cmap", None) is not None:
        cmap = user_plot_kwargs["cmap"]
        if n_labels != cmap.N:
            cmap = cmap.resampled(n_labels)
            user_plot_kwargs["cmap"] = cmap


def _create_boundary_norm_from_levels(user_plot_kwargs, default_plot_kwargs):
    # xarray user_plot_kwargs 'levels' option
    # - Resample cmap and define BoundaryNorm

    # Get user settings
    vmin = user_plot_kwargs.get("vmin", None)
    vmax = user_plot_kwargs.get("vmax", None)
    levels = user_plot_kwargs["levels"]

    # Check norm is not defined
    if "norm" in user_plot_kwargs:
        raise ValueError("Either specify 'norm' or 'levels'.")
    # Define boundaries
    if isinstance(levels, int):
        if vmin is None or vmax is None:
            raise ValueError("If 'levels' is an integer, you must specify 'vmin' and 'vmax'.")
        boundaries = np.linspace(vmin, vmax, levels)
    else:
        boundaries = list(levels)
    ncolors = len(boundaries) - 1
    # Define boundary norm
    norm = BoundaryNorm(boundaries=boundaries, ncolors=ncolors)
    # Resample colormap
    if "cmap" in user_plot_kwargs:
        user_plot_kwargs["cmap"] = user_plot_kwargs["cmap"].resampled(ncolors)
    else:
        default_plot_kwargs["cmap"] = default_plot_kwargs["cmap"].resampled(ncolors)
    # Add "BoundaryNorm" to user_plot_kwargs
    user_plot_kwargs["norm"] = norm
    # Remove "levels"
    _ = user_plot_kwargs.pop("levels")


def _update_default_norm_using_vmin_and_vmax(user_plot_kwargs, default_plot_kwargs):
    vmin = user_plot_kwargs.get("vmin", None)
    vmax = user_plot_kwargs.get("vmax", None)
    if vmin is not None or vmax is not None:
        # If default accept vmin, vmax --> update vmin/vmax attributes
        try:
            if vmin is not None:
                default_plot_kwargs["norm"].vmin = vmin
            if vmax is not None:
                default_plot_kwargs["norm"].vmax = vmax
            user_plot_kwargs["norm"] = default_plot_kwargs["norm"]
        # Otherwise define a new Normalize norm
        except Exception:
            norm_class = type(default_plot_kwargs["norm"])
            print(
                f"The default pycolorbar norm is a {norm_class} and does not accept 'vmin' and 'vmax'.\n "
                f"Switching the norm to Normalize(vmin={vmin}, vmax={vmax}) !"
            )
            user_plot_kwargs["norm"] = Normalize(vmin=vmin, vmax=vmax)


def _check_no_vmin_vmax_if_norm_specified(user_plot_kwargs):
    vmin = user_plot_kwargs.get("vmin", None)
    vmax = user_plot_kwargs.get("vmax", None)
    norm = user_plot_kwargs.get("norm", None)
    if norm is not None:
        if vmin is not None or vmax is not None:
            raise ValueError("If the 'norm' is specified, 'vmin' and 'vmax' must not be specified.")


def _parse_user_cmap(user_plot_kwargs):
    cmap = user_plot_kwargs.get("cmap", None)
    if isinstance(cmap, str):
        user_plot_kwargs["cmap"] = pycolorbar.get_cmap(name=cmap)
    if cmap is None:
        _ = user_plot_kwargs.pop("cmap", None)
