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
import matplotlib.pyplot as plt
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
from pycolorbar.settings.colormap_validator import is_monotonically_increasing


def _create_combined_cmap(names, n=None, new_n=None):
    """Combine multiple colormaps together."""
    # Check for defaults
    if n is None:
        n = [None] * len(names)  # 256 for LinearSegmentedColormap, the original number of colors for ListedColormap
    if new_n is None:  # TODO: define parameter in YAML file
        new_n = [256] * len(names)
    # First resample colormaps if asked
    list_cmaps = [pycolorbar.get_cmap(cmap_name, lut=lut) for cmap_name, lut in zip(names, n)]
    # Then retrieve a selection of colors from each colormap (256 from each currently !)
    cmap_colors = np.vstack([cmap(np.linspace(0, 1, lut)) for cmap, lut in zip(list_cmaps, new_n)])
    # Define the new colormap
    new_name = "_".join(names)
    return LinearSegmentedColormap.from_list(name=new_name, colors=cmap_colors)


def _get_cmap(cmap_settings):
    """Retrieve the colormap for a given validated colorbar setting."""
    name = cmap_settings.get("name")
    n = cmap_settings.get("n")
    # Define colormap
    return pycolorbar.get_cmap(name=name, lut=n) if isinstance(name, str) else _create_combined_cmap(names=name, n=n)


def _finalize_cmap(cmap, cmap_settings):
    """Set alpha and under, over and bad colors."""
    # Set over and under colors
    # - If not specified, do not set ---> It will be filled with the first/last color value
    # - If 'none' --> It will be depicted in white
    if cmap_settings.get("over_color"):
        cmap.set_over(color=cmap_settings.get("over_color"), alpha=cmap_settings.get("over_alpha"))
    if cmap_settings.get("under_color"):
        cmap.set_under(color=cmap_settings.get("under_color"), alpha=cmap_settings.get("under_alpha"))

    # Set (bad) color for masked values
    # - If alpha not 0, can cause cartopy bug ?
    # --> https://stackoverflow.com/questions/60324497/specify-non-transparent-color-for-missing-data-in-cartopy-map
    if cmap_settings.get("bad_color"):
        cmap.set_bad(
            color=cmap_settings.get("bad_color"),
            alpha=cmap_settings.get("bad_alpha"),
        )
    return cmap


def get_cmap(cbar_dict):
    """Retrieve the colormap from a validated colorbar configuration dictionary."""
    if "cmap" not in cbar_dict:
        return None
    # Retrieve settings
    cmap_settings = cbar_dict["cmap"]
    # Retrieve cmap
    cmap = _get_cmap(cmap_settings=cmap_settings)
    ### Set bad, under and over colors and transparency
    return _finalize_cmap(cmap, cmap_settings)


####-------------------------------------------------------------------------------------------.
#### CategoryNorm
def create_category_norm(labels, first_value=0):
    """Define a BoundaryNorm that deal with categorical data."""
    n_labels = len(labels)
    norm_bins = np.arange(first_value - 0.01, n_labels + first_value) + 0.5
    return mpl.colors.BoundaryNorm(boundaries=norm_bins, ncolors=n_labels)


####-------------------------------------------------------------------------------------------.
#### Norm utility


def get_norm_function(name):
    """Retrieve the norm function."""
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


def get_norm(norm_settings):
    """Define the norm instance from a validated cbar_dict."""
    norm_settings = norm_settings.copy()
    # Retrieve norm function
    norm_name = norm_settings.pop("name", "Norm")
    norm_func = get_norm_function(norm_name)
    # Define norm
    return norm_func(**norm_settings)


####-------------------------------------------------------------------------------------------.
#### pycolorbar default settings


# TODO:
# Check vmin and vmax are None if using BoundaryNorm
# Check vmin and vmax are None when providing a Norm
# --> Allow labels also for BoundaryNorm ? But remove from kwargs when norm generation ?
# --> Adapt cmap for 'labels' (define n)

# TODO: rename matplotlib_plot_cbar_kwargs


def get_plot_cbar_kwargs(cbar_dict):
    """Retrieve the plot and colorbar kwargs from a validated colorbar dictionary."""
    cbar_dict = cbar_dict.copy()

    # ------------------------------------------------------------------------.
    # Set default colormap
    # if "cmap" not in  cbar_dict:
    #     cbar_dict["cmap"] = {"name": "jet"} --> leave to xarray/matplotlib/... defaults !
    if "norm" not in cbar_dict:
        cbar_dict["norm"] = {"name": "Norm"}

    # ------------------------------------------------------------------------.
    # Initialize kwargs
    plot_kwargs = {}
    cbar_kwargs = get_default_cbar_kwargs()

    # ------------------------------------------------------------------------.
    # Define cmap and norm based on colorbar dictionary settings
    plot_kwargs["cmap"] = get_cmap(cbar_dict)
    if "norm" in cbar_dict:
        # Add norm to plot_kwargs
        norm = get_norm(cbar_dict["norm"])
        plot_kwargs["norm"] = norm
    else:
        norm = None
    # ------------------------------------------------------------------------.
    # Define cbar_kwargs
    if "cbar" in cbar_dict:
        cbar_kwargs.update(cbar_dict["cbar"])

    # ------------------------------------------------------------------------.
    # Add default ticks and ticklabels for BoundaryNorm
    cbar_kwargs = _finalize_ticks_arguments(cbar_kwargs=cbar_kwargs, cbar_dict=cbar_dict, norm=norm)

    # ------------------------------------------------------------------------.
    return plot_kwargs, cbar_kwargs


def get_default_cbar_kwargs():
    """Define the default colorbar kwargs."""
    return {
        "ticks": None,
        # "ticklabels": None,  --> # Temporary ... because matplotlib.colorbar do not accept ticklabels
        "ticklocation": "auto",
        "spacing": "uniform",  # or proportional
        "extend": "neither",
        "extendfrac": "auto",
        "extendrect": False,
        "label": None,
        "drawedges": False,
        "shrink": 1,
    }


def _decimal_places(value, cap=4):
    """Determine the number of decimal places needed for formatting."""
    if value.is_integer():
        return 0  # No decimal places needed for integer values
    magnitude = np.abs(value)
    # Add only 1 decimal for values above 1
    if magnitude >= 1:
        return 1
    # Dynamically calculate decimal places based on magnitude (and cap at i.e. 4 decimals)
    return min(int(np.ceil(-np.log10(magnitude))) + 1, cap)


def _count_string_decimals(value):
    """Count the number of decimal places in a value."""
    if "." in value:
        return len(value) - value.index(".") - 1
    return 0


def _ensure_increasing_or_equal_values(arr):
    result = [arr[0]]  # Start with the first element
    for i in range(1, len(arr)):
        result.append(max(arr[i], result[-1]))  # Append maximum of current value and previous result
    return result


def _format_label(value, decimals, strip_zero=True):
    """Format the label based on the number of decimal places."""
    if decimals == 0:
        return str(int(value))
    formatting = f"{{:,.{decimals}f}}"
    formatted_value = formatting.format(value)
    if strip_zero:
        formatted_value = formatted_value.rstrip("0").rstrip(".")  # strip excess 0.080 --> 0.08
    return formatted_value


def _dynamic_formatting_floats(values, cap=4):
    """Dynamically format floats defining class limits of the colorbar.

    Assumptions:

    - Only positive values
    - At least two values
    """
    values = np.array(values, dtype=float)
    decimals_values = [_decimal_places(value, cap=cap) for value in values]
    labels = [_format_label(value, decimals) for value, decimals in zip(values, decimals_values)]
    # Ensure only decreasing decimals
    actual_decimals = [_count_string_decimals(label) for label in labels]
    final_decimals = _ensure_increasing_or_equal_values(actual_decimals[::-1])[::-1]
    labels = [_format_label(value, decimals, strip_zero=False) for value, decimals in zip(values, final_decimals)]
    return ["0" if float(label) == 0 else label for label in labels]


def _finalize_ticks_arguments(cbar_kwargs, cbar_dict, norm):
    """Add ticks and ticklabels arguments for Discrete, Discretized and Categorical Colorbars."""
    # Retrieve settings
    norm_settings = cbar_dict.get("norm", {})
    norm_name = norm_settings.get("name", "Norm")

    # Define ticks and ticklabels for BoundaryNorm instances
    if norm_name not in ("BoundaryNorm", "CategoryNorm"):
        return cbar_kwargs

    # Retrieve discrete norm information
    boundaries = norm_settings.get("boundaries", None)
    labels = norm_settings.get("labels", None)
    ticks = cbar_kwargs.get("ticks", None)
    ticklabels = cbar_kwargs.get("ticklabels", None)

    # Define ticks
    if norm_name == "BoundaryNorm":  # Discrete /Discretized Colorbar
        if ticks is None and ticklabels is None:
            ticks = boundaries
        if ticklabels is None:
            # Generate color level strings with correct amount of decimal places
            ticklabels = _dynamic_formatting_floats(ticks)  # [f"{tick:.1f}" for tick in ticks] # for 0.1 probability
    elif norm_name == "CategoryNorm":  # Categorical Colorbar
        ticks = norm.boundaries[:-1] + 0.5
        # Define tick formatter and ticks
        fmt = mpl.ticker.FuncFormatter(lambda x, pos=None: labels[norm(x)])  # noqa
        ticklabels = [fmt(tick) for tick in ticks]

    # Format back to list
    cbar_kwargs["ticks"] = list(ticks)
    cbar_kwargs["ticklabels"] = list(ticklabels)
    return cbar_kwargs


####--------------------------------------------------------------------------------------------.
#### Update pycolorbar settings based on user arguments


def update_plot_cbar_kwargs(default_plot_kwargs, default_cbar_kwargs, user_plot_kwargs=None, user_cbar_kwargs=None):
    """Update the default plot and colorbar kwargs with user-provided arguments."""
    # If no user kwargs, return default kwargs
    user_plot_kwargs = {} if user_plot_kwargs is None else user_plot_kwargs
    user_cbar_kwargs = {} if user_cbar_kwargs is None else user_cbar_kwargs
    if user_plot_kwargs == {} and user_cbar_kwargs == {}:
        return default_plot_kwargs, default_cbar_kwargs

    # If user cmap
    # - is a string, retrieve colormap
    # - is None --> delete the argument
    user_plot_kwargs = _parse_user_cmap(user_plot_kwargs=user_plot_kwargs)

    # If norm is specified, vmin and vmax must be None !
    _check_no_vmin_vmax_if_norm_specified(user_plot_kwargs=user_plot_kwargs)
    _check_no_levels_if_norm_specified(user_plot_kwargs=user_plot_kwargs)

    # If norm is not specified in user_plot_kwargs
    # - Update vmin and vmax if specified in user_plot_kwargs
    # --> Check the default norm accepts vmin and vmax arguments
    # --> If yes, update the default norm to use specified vmin and vmax
    # --> If no, warn and define a Normalize(vmin, vmax)
    # --> If BoundaryNorm, remove ticks and ticklabels from default_cbar_kwargs !
    # - Update ticks and tickslabels
    if user_plot_kwargs.get("norm", None) is None:
        # Update norm based on user-provided vmin and vmax
        _update_default_norm_using_vmin_and_vmax(
            user_plot_kwargs=user_plot_kwargs,
            default_plot_kwargs=default_plot_kwargs,
            default_cbar_kwargs=default_cbar_kwargs,
        )
        # Check if valid update for user-specified ticklabels and ticks
        # --> If already present in defaults_kwargs (i.e. for BoundaryNorm), check that length match
        _check_valid_ticks_ticklabels(user_cbar_kwargs=user_cbar_kwargs, default_cbar_kwargs=default_cbar_kwargs)

    # -------------------------------------------------------------------------------
    # Deal with categorical/discrete colorbar
    # - Remove ticks and ticklabels when user specify new norm or 'levels' !
    # - Later on:
    #   - If user specify a new cmap --> the cmap is resampled based on len(ticklabels)
    #   - If vmin or vmax are specified --> a Normalize(vmin, vmax) replace BoundaryNorm
    if user_plot_kwargs.get("norm", None) is not None or user_plot_kwargs.get("levels", None) is not None:
        _remove_defaults_ticks_and_ticklabels(default_cbar_kwargs=default_cbar_kwargs)

    # Deal with categorical/discrete labeled colorbar (when user provides a new cmap)
    # - If user provided a colormap, resample the colormap
    if default_cbar_kwargs.get("ticklabels", None) is not None:
        _resample_user_cmap_for_labeled_colorbar(
            user_plot_kwargs=user_plot_kwargs,
            default_cbar_kwargs=default_cbar_kwargs,
        )

    # Deal with xarray user_plot_kwargs 'levels' option
    # - Define a BoundaryNorm and resample the cmap accordingly
    if "levels" in user_plot_kwargs:
        _create_boundary_norm_from_levels(user_plot_kwargs=user_plot_kwargs, default_plot_kwargs=default_plot_kwargs)

    # Drop vmin and vmax from user_plot_kwargs (not accepted by PolyCollection)
    # - This avoid also downstream bugs ...
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


def _count_length(v):
    if v is None:
        return 0
    return len(v)


def _check_valid_ticks_ticklabels(user_cbar_kwargs, default_cbar_kwargs):
    user_ticks = user_cbar_kwargs.get("ticks", None)
    user_ticklabels = user_cbar_kwargs.get("ticklabels", None)
    if user_ticks is not None or user_ticklabels is not None:
        user_ticks = user_cbar_kwargs.get("ticks", None)
        user_ticklabels = user_cbar_kwargs.get("ticklabels", None)
        default_ticks = default_cbar_kwargs.get("ticks", None)
        default_ticklabels = default_cbar_kwargs.get("ticklabels", None)
        user_ticks_length = _count_length(user_ticks)
        user_ticklabels_length = _count_length(user_ticklabels)
        default_ticks_length = _count_length(default_ticks)
        default_ticklabels_length = _count_length(default_ticklabels)
        if user_ticks is not None and user_ticklabels is not None:
            if user_ticks_length != user_ticklabels_length:
                raise ValueError(
                    "'ticks' and 'ticklabels' must have same length: {user_ticks_length} vs {user_ticklabels_length}.",
                )
        # Case: user_ticklabels provided
        elif user_ticks is None and default_ticks is not None:
            if user_ticklabels_length != default_ticks_length:
                raise ValueError(
                    "If you don't specify 'ticks', expecting a 'ticklabels' list of length {default_ticks_length}.",
                )
        # Case: user_ticks provided
        elif (
            user_ticklabels is None
            and default_ticklabels is not None
            and user_ticks_length != default_ticklabels_length
        ):
            raise ValueError(
                "If you don't specify 'ticklabels', expecting a 'ticks' list of length {default_ticklabels_length}.",
            )


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


def _check_no_levels_if_norm_specified(user_plot_kwargs):
    """Check either 'levels' or 'norm' are specified in user_plot_kwargs."""
    # Check norm is not defined
    if "norm" in user_plot_kwargs and "levels" in user_plot_kwargs:
        raise ValueError("Either specify 'norm' or 'levels'.")


def _create_boundary_norm_from_levels(user_plot_kwargs, default_plot_kwargs):
    """It parse the xarray 'levels' argument to resample the colormap and define a BoundaryNorm."""
    # Get user settings
    vmin = user_plot_kwargs.get("vmin", None)
    vmax = user_plot_kwargs.get("vmax", None)
    levels = user_plot_kwargs["levels"]

    # Define boundaries
    if isinstance(levels, (int, float)):
        if vmin is None or vmax is None:
            raise ValueError("If 'levels' is an integer, you must specify 'vmin' and 'vmax'.")
        boundaries = list(np.linspace(vmin, vmax, int(levels + 1)))
    else:
        if vmin is not None or vmax is not None:
            raise ValueError("If you specify 'levels' as a list, you don't have to specify 'vmin' and 'vmax'.")
        boundaries = list(levels)
        # Check levels are monotonic increasing
        if not is_monotonically_increasing(boundaries):
            raise ValueError("'levels' must be monotonically increasing !")

    ncolors = len(boundaries) - 1
    # Define boundary norm
    norm = BoundaryNorm(boundaries=boundaries, ncolors=ncolors)
    # Resample colormap
    if user_plot_kwargs.get("cmap", None) is not None:
        user_plot_kwargs["cmap"] = user_plot_kwargs["cmap"].resampled(ncolors)
    else:
        if default_plot_kwargs.get("cmap", None) is None:
            default_plot_kwargs["cmap"] = plt.get_cmap()
        default_plot_kwargs["cmap"] = default_plot_kwargs["cmap"].resampled(ncolors)
    # Add "BoundaryNorm" to user_plot_kwargs
    user_plot_kwargs["norm"] = norm
    # Remove "levels" from user kwargs
    _ = user_plot_kwargs.pop("levels")


def _update_default_norm_using_vmin_and_vmax(user_plot_kwargs, default_plot_kwargs, default_cbar_kwargs):
    """Update the norm vmin and vmax settings if possible."""
    vmin = user_plot_kwargs.get("vmin", None)
    vmax = user_plot_kwargs.get("vmax", None)
    if vmin is not None or vmax is not None:
        # If the norm does not accepts vmin or vmax, set a Normalize(vmin, vmax) norm
        if isinstance(default_plot_kwargs["norm"], (BoundaryNorm, CenteredNorm)):
            norm_class = type(default_plot_kwargs["norm"])
            print(
                f"The default pycolorbar norm is a {norm_class} and does not accept 'vmin' and 'vmax'.\n "
                f"Switching the norm to Normalize(vmin={vmin}, vmax={vmax}) !",
            )
            user_plot_kwargs["norm"] = Normalize(vmin=vmin, vmax=vmax)
            default_plot_kwargs["norm"] = Normalize(vmin=vmin, vmax=vmax)
            if isinstance(default_plot_kwargs["norm"], BoundaryNorm):
                _remove_defaults_ticks_and_ticklabels(default_cbar_kwargs=default_cbar_kwargs)
        # Else update vmin/vmax attributes
        else:
            if vmin is not None:
                default_plot_kwargs["norm"].vmin = vmin
            if vmax is not None:
                default_plot_kwargs["norm"].vmax = vmax
            user_plot_kwargs["norm"] = default_plot_kwargs["norm"]

        # Update also the default_plot_kwargs
        # --> For possible update/checks of ticks and ticklabels
        default_plot_kwargs["norm"] = user_plot_kwargs["norm"]


def _check_no_vmin_vmax_if_norm_specified(user_plot_kwargs):
    vmin = user_plot_kwargs.get("vmin", None)
    vmax = user_plot_kwargs.get("vmax", None)
    norm = user_plot_kwargs.get("norm", None)
    if norm is not None and (vmin is not None or vmax is not None):
        raise ValueError("If the 'norm' is specified, 'vmin' and 'vmax' must not be specified.")


def _parse_user_cmap(user_plot_kwargs):
    cmap = user_plot_kwargs.get("cmap", None)
    if isinstance(cmap, str):
        user_plot_kwargs["cmap"] = pycolorbar.get_cmap(name=cmap)
    if cmap is None:
        _ = user_plot_kwargs.pop("cmap", None)
    return user_plot_kwargs
