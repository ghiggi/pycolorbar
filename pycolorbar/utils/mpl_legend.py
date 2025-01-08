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
"""Utility to add legends or insets to a Matplotlib figure."""
import matplotlib.patches as mpatches
import numpy as np
from matplotlib.transforms import Bbox

# -----------------------------------------------------------------------------.
# NOTES
# How to rotate subplot by 45 degrees (not easy)
# - Create image, rotate, load image, attach to plot
# - https://stackoverflow.com/questions/62357483/how-to-rotate-a-subplot-by-45-degree-in-matplotlib


# Bbox([[xmin, ymin], [xmax, ymax]])
# Bbox.from_extents(xmin, ymin, xmax, ymax)
# Bbox.from_bounds(xmin, ymin, width, height)

# -----------------------------------------------------------------------------.


def get_locations_acronyms():
    """Get list of valid location acronyms."""
    locations = [
        "upper right",
        "upper left",
        "lower right",
        "lower left",
        "center left",
        "center right",
        "upper center",
        "lower center",
    ]
    return locations


def get_location_origin(loc, width, height, x_pad, y_pad):
    """Get the origin coordinates (x0, y0) for a given location on a plot.

    Parameters
    ----------
    loc : str
        The location string specifying the position. Accepted values are:
        'upper right', 'upper left', 'lower right', 'lower left',
        'center left', 'center right', 'upper center', 'lower center'.
    width : float
        The width of the element to be positioned.
    height : float
        The height of the element to be positioned.
    x_pad : float
        The horizontal padding from the specified location.
    y_pad : float
        The vertical padding from the specified location.

    Returns
    -------
    x0 : float
        The x-coordinate of the origin.
    y0 : float
        The y-coordinate of the origin.
    """
    # Define location mapping dictionary
    loc_mapping = {
        "upper right": (1 - width - x_pad, 1 - height - y_pad),
        "upper left": (0 + x_pad, 1 - height - y_pad),
        "lower right": (1 - width - x_pad, 0 + y_pad),
        "lower left": (0 + x_pad, 0 + y_pad),
        "center left": (0 + x_pad, 0.5 - height / 2 - y_pad),
        "center right": (1 - width - x_pad, 0.5 - height / 2 - y_pad),
        "upper center": (0.5 - width / 2 - x_pad, 1 - height / 2 - y_pad),
        "lower center": (0.5 - width / 2 - x_pad, 0 + y_pad),
    }
    valid_loc = list(loc_mapping)
    if loc not in loc_mapping:
        raise ValueError(f"Unsupported loc='{loc}'. Accepted 'loc' are {valid_loc}")

    # Define location x0, y0
    x0, y0 = loc_mapping[loc]
    return x0, y0


def get_inset_bounds(
    ax,
    loc="upper right",
    inset_height=0.2,
    inside_figure=True,
    aspect_ratio=1,
    border_pad=0,
):
    """Calculate the bounds for an inset axes in a matplotlib figure.

    This function computes the normalized figure coordinates for placing an inset axes within a figure,
    based on the specified location, size, and whether the inset should be fully inside the figure bounds.
    It is designed to be used with matplotlib figures to facilitate the addition of insets (e.g., for maps
    or zoomed plots) at predefined positions.

    Parameters
    ----------
    loc : str or tuple
        The location of the inset within the figure. Valid options are ``'lower left'``, ``'lower right'``,
        ``'upper left'``, and ``'upper right'``. The default is ``'upper right'``.
        Alternatively you can specify a tuple with the (x0, y0) figure coordinates.
    inset_height : float
        The size of the inset height, specified as a fraction of the figure's height.
        For example, a value of 0.2 indicates that the inset's height will be 20% of the figure's height.
        The aspect ratio will govern the ``inset_width``.
    aspect_ratio : float, optional
        The desired width-to-height ratio of the inset figure.
        A value greater than 1 indicates an inset figure wider than it is tall,
        and a value less than 1 indicates an inset figure taller than it is wide.
        The default value is 1.0, indicating a square inset figure.
    inside_figure : bool, optional
        Determines whether the inset is constrained to be fully inside the figure bounds. If  ``True`` (default),
        the inset is placed fully within the figure. If ``False``, the inset can extend beyond the figure's edges,
        allowing for a half-outside placement.
        This argument is used only if 'loc' is specified as a string.
    border_pad: int, float or tuple
        The padding to apply on the x and y direction.
        If a single value is supplied, applies the same padding in both directions.
        This arguments is used only if 'loc' is specified as a string.

    Returns
    -------
    inset_bounds : list of float
        The calculated bounds of the inset, in the format ``[x0, y0, width, height]``, where ``x0`` and ``y0``
        are the normalized figure coordinates of the lower left corner of the inset, and ``width`` and
        ``height`` are the normalized width and height of the inset, respectively.

    """
    # Define border_pad as tuple (x,y)
    if isinstance(border_pad, (int, float)):
        border_pad = (border_pad, border_pad)

    # ----------------------------------------------------------------.
    # Get the bounding box of the parent axes in figure coordinates
    bbox = ax.get_position()
    parent_width = bbox.width
    parent_height = bbox.height

    # Compute the relative inset width and height
    # - Take into account possible different aspect ratios
    inset_height_abs = inset_height * parent_height
    inset_width_abs = inset_height_abs * aspect_ratio
    inset_width = inset_width_abs / parent_width

    # ----------------------------------------------------------------.
    # Get axis position Bbox
    # ax_bbox = ax.get_position() # get the original position

    # # Get figure width and height
    # fig_width, fig_height = ax.figure.get_size_inches()

    # # Define width and height in inches
    # ax_height_in_inches = fig_height * ax_bbox.height
    # # ax_width_in_inches = fig_width * ax_bbox.width

    # # Now compute the inset width and height in inches
    # new_ax_height_in_inches = ax_height_in_inches*inset_height
    # new_ax_width_in_inches = new_ax_height_in_inches * aspect_ratio

    # # Now convert to relative position
    # new_ax_width = new_ax_width_in_inches/fig_width
    # new_ax_height = new_ax_height_in_inches/fig_height

    # inset_width = new_ax_width
    # inset_height = new_ax_height

    # #----------------------------------------------------------------.
    # print("Width:", inset_width)
    # print("Height:", inset_height)

    # ----------------------------------------------------------------.
    # If loc specify (x0,y0) return the inset bounds
    if isinstance(loc, (list, tuple)) and len(loc) == 2:
        return [loc[0], loc[1], inset_width, inset_height]

    # Compute the inset x0, y0 coordinates based on loc string
    inset_x, inset_y = get_location_origin(
        loc=loc,
        width=inset_width,
        height=inset_height,
        x_pad=border_pad[0],
        y_pad=border_pad[1],
    )

    # Adjust for insets that are allowed to be half outside of the figure
    if not inside_figure:
        inset_x += inset_width / 2 * (-1 if loc.endswith("left") else 1)
        inset_y += inset_height / 2 * (-1 if loc.startswith("lower") else 1)

    return [inset_x, inset_y, inset_width, inset_height]


def get_tightbbox_position(ax):
    """Return the axis Bbox position in figure coordinates.

    This Bbox includes also the area with axis ticklabels, labels and the title.
    """
    fig = ax.figure

    # Force a draw so Matplotlib computes the correct positions.
    fig.canvas.draw_idle()  # or draw() if you're sure you won't change anything else

    # Get the tight bounding box in DISPLAY (pixel) coordinates
    # - get_tightbbox() includes the area with labels, tick labels, etc
    renderer = fig.canvas.get_renderer()
    bbox = ax.get_tightbbox(renderer=renderer)

    # Convert that Bbox to FIGURE coordinates (0..1 range).
    bbox_fig = bbox.transformed(fig.transFigure.inverted())
    return bbox_fig


def optimize_inset_position(ax, cax, pad=0):
    """Optimize the inset position to not touch the main plot region."""
    # Define border_pad as tuple (x,y)
    if isinstance(pad, (int, float)):
        pad = (pad, pad)

    # Retrieve axis positions
    ax_pos = ax.get_position(original=False)
    cax_pos = cax.get_position(original=False)
    cax_outer_pos = get_tightbbox_position(cax)

    # Compute margin required (if positive)
    left_margin = np.maximum(0, ax_pos.x0 - cax_outer_pos.x0 + pad[0])
    right_margin = np.maximum(0, cax_outer_pos.x1 - ax_pos.x1 + pad[0])
    upper_margin = np.maximum(0, cax_outer_pos.y1 - ax_pos.y1 + pad[1])
    bottom_margin = np.maximum(0, ax_pos.y0 - cax_outer_pos.y0 + pad[1])

    # If not possible to optimize, return current position
    if (left_margin > 0 and right_margin > 0) or (upper_margin > 0 and bottom_margin > 0):
        return cax_pos

    # Define new position
    new_pos = Bbox.from_extents(
        [
            cax_pos.x0 + left_margin - right_margin,
            cax_pos.y0 + bottom_margin - upper_margin,
            cax_pos.x1 + left_margin - right_margin,
            cax_pos.y1 + bottom_margin - upper_margin,
        ],
    )
    return new_pos


def add_fancybox(ax, bbox, fc="white", ec="none", lw=0.5, alpha=0.5, pad=0, shape="square", zorder=None):
    """Add fancy box.

    The bbox can be derived using get_tightbbox_position(ax_legend).
    """
    fancy_patch = mpatches.FancyBboxPatch(
        (bbox.x0, bbox.y0),
        width=bbox.width,
        height=bbox.height,
        boxstyle=f"{shape},pad={pad}",
        fc=fc,  # facecolor
        ec=ec,  # edgecolor
        lw=lw,  # linewidth
        alpha=alpha,
        transform=ax.figure.transFigure,  # so these coords are figure coords
        zorder=zorder,
        clip_on=False,
    )
    return ax.add_artist(fancy_patch)
