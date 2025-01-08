import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PatchCollection
from matplotlib.patches import Circle, Wedge
from mpl_toolkits.axes_grid1 import make_axes_locatable

from pycolorbar.utils.mpl_legend import add_colorbar_inset

# Alternative solution:
# - Draw pies and mask with inner disk: https://stackoverflow.com/questions/59877425/python-matplotlib-donut-chart-with-smaller-width-on-one-wedge
# - However does not allow for full transparency in the inner circle ...


def _create_wedges(r_min, r_max, n, center, theta_offset, direction):
    """
    Create a list of wedges (annular sectors) for a circular colorbar.

    Parameters
    ----------
    r_min : float
        Inner radius of the wedges.
    r_max : float
        Outer radius of the wedges.
    center: tuple, optional
        The coordinate center (x,y) around which to draw the circular colorbar.
        The default is (0.5, 0.5)
    n : int
        Number of discrete wedges to create.
    theta_offset : float
        Offset angle (in degrees) for the starting point of the wedges.
    direction : int
        Rotation direction (-1 for clockwise, 1 for counterclockwise).

    Returns
    -------
    list of Wedge
        List of matplotlib Wedge objects representing the colorbar sectors.
    """
    wedges = []
    width = r_max - r_min
    for i in range(n):
        # Define start angle
        theta1 = (direction * (360 * i / n) - theta_offset) % 360
        # Define end angle
        theta2 = (direction * (360 * (i + 1) / n) - theta_offset) % 360
        if direction == 1:
            wedge = Wedge(center, r_max, theta1, theta2, width=width)
        else:
            wedge = Wedge(center[0], r_max, theta2, theta1, width=width)
        wedges.append(wedge)
    return wedges


def _get_ticklabels_alignment(tick):
    """
    Determine horizontal and vertical alignment for tick labels based on their position.

    Parameters
    ----------
    tick : float
        The angle (in degrees) of the current tick.

    Returns
    -------
    tuple of (str, str)
        Horizontal and vertical alignment for the tick label. Possible values for horizontal alignment are
        'left', 'right', and 'center'. For vertical alignment, 'top', 'bottom', or 'center' are returned.
    """
    # Determine horizontal alignment (ha) based on quadrant
    tick = tick % 360
    ha = "left" if 0 <= tick < 90 or 270 <= tick < 360 else "right"
    # Special case for ticks near the top and bottom
    if 85 <= tick <= 95:
        ha = "center"
        va = "bottom"  # Labels at the top
    elif 265 <= tick <= 275:
        ha = "center"
        va = "top"  # Labels at the bottom
    else:
        # General vertical alignment: depends on top/bottom half of the circle
        va = "center" if 0 <= tick < 180 else "center"
    return ha, va


def _add_ticklabels(ax, center, ticks, ticklabels, r_max, direction, theta_offset, ticklabels_offset=0.05):
    """
    Add tick labels to the circular colorbar.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes on which to add the tick labels.
    ticks : array-like
        The angular positions of the ticks (in degrees).
    ticklabels : array-like
        List of labels to display at each tick.
    r_max : float
        Outer radius of the colorbar where the labels will be positioned.
    center: tuple, optional
        The coordinate center (x,y) around which to draw the circular colorbar.
        The default is (0.5, 0.5)
    direction : int
        Rotation direction (-1 for clockwise, 1 for counterclockwise).
    theta_offset : float
        Offset angle (in degrees) for the starting point of the ticks.
    ticklabels_offset : float, optional
        Radial offset for tick labels, by default 0.05.

    Returns
    -------
    None
    """
    ticks = (direction * ticks - theta_offset) % 360
    for tick, label in zip(ticks, ticklabels, strict=False):
        ha, va = _get_ticklabels_alignment(tick)
        ax.text(
            center[0] + np.cos(np.deg2rad(tick)) * (r_max + ticklabels_offset),
            center[1] + np.sin(np.deg2rad(tick)) * (r_max + ticklabels_offset),
            label,
            horizontalalignment=ha,
            verticalalignment=va,
        )


def _add_ticks(ax, ticks, r_max, direction, theta_offset, center, ticklength=0.03, tickcolor="black", tickwidth=2):
    """
    Add tick marks to the circular colorbar.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes on which to add the tick marks.
    ticks : array-like
        The angular positions of the ticks (in degrees).
    r_max : float
        Outer radius of the colorbar where the tick marks will be positioned.
    center: tuple, optional
        The coordinate center (x,y) around which to draw the circular colorbar.
        The default is (0.5, 0.5)
    direction : int
        Rotation direction (-1 for clockwise, 1 for counterclockwise).
    theta_offset : float
        Offset angle (in degrees) for the starting point of the ticks.
    ticklength : float, optional
        Length of the tick marks, by default 0.03.
    tickcolor : str, optional
        Color of the tick marks, by default 'black'.
    tickwidth : float, optional
        Line width of the tick marks, by default 2.

    Returns
    -------
    None
    """
    ticks = (direction * ticks - theta_offset) % 360
    for tick in ticks:
        # Add small tick lines
        tick_line_x = [
            center[0] + np.cos(np.deg2rad(tick)) * r_max,
            center[0] + np.cos(np.deg2rad(tick)) * (r_max + ticklength),
        ]  # Small extension for tick
        tick_line_y = [
            center[1] + np.sin(np.deg2rad(tick)) * r_max,
            center[1] + np.sin(np.deg2rad(tick)) * (r_max + ticklength),
        ]  # Small extension for tick
        ax.plot(tick_line_x, tick_line_y, color=tickcolor, lw=tickwidth)


def _set_adaptive_limits(ax, r_max, center, margin_factor=0.1):
    """
    Set adaptive x and y limits based on the given radii, with a margin.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes on which to set the limits.
    r_max : float
        Outer radius of the colorbar.
    center: tuple, optional
        The coordinate center (x,y) around which to draw the circular colorbar.
        The default is (0.5, 0.5)
    margin_factor : float, optional
        Fraction of `r_max` to use as margin around the colorbar, by default 0.1.

    Returns
    -------
    None
    """
    # Calculate margin based on the maximum radius
    margin = margin_factor * r_max
    # Calculate the limits for the axes
    xlim = center[0] - (r_max + margin), center[0] + (r_max + margin)
    ylim = center[1] - (r_max + margin), center[1] + (r_max + margin)
    # Set the limits
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)


def plot_circular_colorbar_discrete(
    cmap,
    *,
    ax=None,
    cax=None,
    n=None,
    r_min=0.2,
    r_max=0.5,
    center=(0.5, 0.5),
    adapt_limits=True,
    zero_location="N",
    clockwise=True,
    edgecolor="none",
    linewidths=None,
    antialiased=True,
    ticks=None,
    ticklabels=None,
    ticklabels_offset=0.05,
    add_ticks=True,
    add_contours=False,
    ticklength=0.02,
    tickcolor="black",
    tickwidth=1,
):
    """
    Plot a discrete circular colorbar.

    Parameters
    ----------
    cmap : matplotlib.colors.Colormap
        Colormap to use for the wedges.
        If a circular colormap, ensure to provide the discretized ListedColormap !
    n : int, optional
        Number of discrete color segments in the colorbar.
        If cmap is a ListedColormap and n is None, it is derived from cmap.N.
        Otherwise, if cmap is a LinearSegmentedColormap, the value must be specified.
    r_min : float, optional
        Inner radius of the colorbar, by default 0.2.
    r_max : float, optional
        Outer radius of the colorbar, by default 0.5.
    center: tuple, optional
        The coordinate center (x,y) around which to draw the circular colorbar.
        The default is (0.5, 0.5)
    zero_location : str or float, optional
        Starting location of the colorbar ('N', 'E', 'S', 'W') or an angle in degrees, by default "N".
    adapt_limits: bool, optional
        If True, automatically adjusts the the limits of the plot to include the circle colorbar if
        center and r_min or r_max are changed.
        The default is True.
    clockwise : bool, optional
        Direction of rotation; if True, clockwise; if False, counterclockwise, by default True.
    ticks : array-like, optional
        Positions of the ticks in degrees, by default None.
    ticklabels : array-like, optional
        Labels for the ticks, by default None.
    ticklabels_offset : float, optional
        Radial offset for the tick labels, by default 0.05.
    add_ticks : bool, optional
        Whether to add tick marks, by default True.
    ticklength : float, optional
        Length of the tick marks, by default 0.02.
    tickcolor : str, optional
        Color of the tick marks, by default "black".
    tickwidth : float, optional
        Line width of the tick marks, by default 1.
    ax : matplotlib.axes.Axes, optional
        Axes to draw on, by default None (creates a new figure).

    Returns
    -------
    ax: matplotlib.axes.Axes
    """
    # TODO:
    location = "right"
    size = "30%"
    pad = 0.3
    box_aspect = 1

    # Initialize arguments
    zero_location_dict = {"N": -90, "E": 0, "S": 90, "W": -180}
    theta_offset = zero_location_dict[zero_location] if isinstance(zero_location, str) else zero_location - 90
    direction = -1 if clockwise else 1

    # Define n
    if n is None:
        if hasattr(cmap, "N"):
            n = cmap.N
        else:
            raise ValueError("'n' must be specified for LinearSegmented Colormaps.")

    # Determine colorbar axis
    if cax is not None:
        pass
    elif ax is not None:  # and cax is None
        divider = make_axes_locatable(ax)
        cax = divider.append_axes(location, size=size, pad=pad, axes_class=plt.Axes)
        cax.set_box_aspect(box_aspect)
    else:
        cax = plt.gca()  #  fig, ax = plt.subplots()

    # Set equal axis ratio
    cax.set_aspect("equal")

    # Create list of wedges (annular patches)
    wedges = _create_wedges(
        r_min=r_min,
        r_max=r_max,
        n=n,
        center=center,
        theta_offset=theta_offset,
        direction=direction,
    )
    # Define values
    values = np.linspace(0, 1, n)
    # Create a patch collection with the color mapped to the values
    collection = PatchCollection(
        wedges,
        cmap=cmap,
        match_original=False,
        antialiased=antialiased,
        edgecolor=edgecolor,
        linewidths=linewidths,
    )  # edgecolor = "none")
    collection.set_array(values)
    # Add the collection to the axis
    cax.add_collection(collection)
    # Add custom ticks and labels
    if ticks is not None and ticklabels is not None:
        # Add ticks labels
        _add_ticklabels(
            ax=cax,
            ticks=ticks,
            ticklabels=ticklabels,
            r_max=r_max,
            center=center,
            direction=direction,
            theta_offset=theta_offset,
            ticklabels_offset=ticklabels_offset,
        )
        # Add ticks line
        if add_ticks:
            _ = _add_ticks(
                ax=cax,
                ticks=ticks,
                r_max=r_max,
                center=center,
                direction=direction,
                theta_offset=theta_offset,
                ticklength=ticklength,
                tickcolor=tickcolor,
                tickwidth=tickwidth,
            )
    # Add circle
    if add_contours:
        cax.add_patch(Circle(center, r_max, color=tickcolor, lw=1.5, fill=False))
        cax.add_patch(Circle(center, r_min, color=tickcolor, lw=1.5, fill=False))
    # Turn off axis
    cax.set_axis_off()
    # Adapt limits
    if adapt_limits:
        _ = _set_adaptive_limits(ax=cax, r_max=r_max, center=center, margin_factor=0.1)
    # Return ax
    return collection


# ----------------------------------
# TODO
# Enforce ticks to radians

# # Missing
# polar
# - n
# - zero_location
# - clockwise
# - edgecolor
# - linewidths
# - antialiased
# - ticklabels_offset (-->ticklabels_pad)
# discrete
# - ticklabels_pad
# - ticklabels_size


def add_circular_colorbar(
    *,
    cmap,
    method="discrete",
    # Shared arguments
    ax=None,
    cax=None,
    r_min=0.2,
    r_max=0.5,
    center=(0.5, 0.5),
    add_contours=False,
    adapt_limits=True,
    # Discrete-specific
    n=None,
    zero_location="N",
    clockwise=True,
    edgecolor="none",
    linewidths=None,
    antialiased=True,
    # Polar-specific
    ticklabels_pad=4,
    ticklabels_size=10,
    # Ticks for both
    ticks=None,
    ticklabels=None,
    add_ticks=True,
    ticklabels_offset=0.05,
    ticklength=0.02,
    tickcolor="black",
    tickwidth=1,
    # Tick units
    tick_units="degrees",  # or "radians"
):
    """
    Plot a circular colorbar in either a discrete (wedge-based) or polar (continuous) style.

    Parameters
    ----------
    cmap : matplotlib.colors.Colormap
        The colormap to be used.
    ax : matplotlib.axes.Axes
            The Axes into which the colorbar will be inserted (or serve as the parent
            if `cax` is not provided). If None and `cax` is None, a new Axes/figure
            may be created automatically depending on the method.
    method : {'discrete', 'polar'}, optional
        - 'discrete': Use a wedge-based approach (similar to a ListedColormap).
        - 'polar': Use a polar projection with pcolormesh.
    cax : matplotlib.axes.Axes, optional
        If provided, draw the colorbar directly in this Axes. Otherwise,
        an inset Axes will be appended to `ax` (if `ax` is provided).
    r_min, r_max : float, optional
        Inner and outer radius for the circular colorbar.
        - For 'discrete' method, these define the annular wedge boundaries.
        - For 'polar' method, these define the radial range in the polar projection.
    center : 2-tuple of float, optional
        (x, y) center in Axes coordinates for the 'discrete' method.
        Ignored if `method='polar'` (where the origin is 0,0 in PolarAxes).
    add_contours : bool, optional
        Whether to draw a thin boundary circle at r_min and r_max.
        For the 'polar' method, it controls the colormap function call.
        For 'discrete' method, draws patches with `Circle(...)`.
    adapt_limits : bool, optional
        If True (and method='discrete'), automatically set the Axes limits so
        the entire circle is visible (based on `r_max` and `center`).
        Ignored if `method='polar'` since the polar Axes handles its own limits.

    n : int, optional
        Number of discrete color segments (only used if `method='discrete'`).
        If None, it tries to infer from a ListedColormap's `cmap.N`.
    zero_location : {'N', 'E', 'S', 'W'} or float, optional
        Where to start the discrete colorbar in degrees.
        - 'N' => top (i.e., -90 deg)
        - 'E' => right (0 deg)
        - 'S' => bottom (90 deg)
        - 'W' => left (-180 deg)
        Or supply a float angle in degrees. Only used if `method='discrete'`.
    clockwise : bool, optional
        Direction of color segments if `method='discrete'`.
        True => clockwise, False => counterclockwise.
    edgecolor : str, optional
        Wedge edge color for the discrete approach. Default is 'none'.
    linewidths : float, optional
        Wedge edge line width for the discrete approach.
    antialiased : bool, optional
        Whether the wedge patches are antialiased in the discrete approach.
    ticklabels_pad : float, optional
        Padding for polar tick labels (method='polar'). Default is 4.
    ticklabels_size : float, optional
        Font size for polar tick labels (method='polar'). Default is 10.
    ticks : array-like, optional
        Positions of tick marks.
        - For 'discrete': expects angles in degrees (0-360).
        - For 'polar': expects angles in radians (0-2π).
        This can be overridden by `tick_units`.
    ticklabels : array-like, optional
        Labels corresponding to `ticks`. Must match in length.
        If None, no labels are shown.
    add_ticks : bool, optional
        For 'discrete': Whether to draw wedge tick lines.
        Ignored if `method='polar'` (pcolormesh approach doesn't do radial lines).
    ticklabels_offset : float, optional
        Radial offset for wedge-based tick labels (method='discrete').
    ticklength : float, optional
        Length of wedge tick lines (method='discrete').
    tickcolor : str, optional
        Color of wedge tick lines (method='discrete').
    tickwidth : float, optional
        Line width of wedge tick lines (method='discrete').
    tick_units : {'degrees', 'radians'}, optional
        Specifies the unit of the `ticks` array.
        - 'degrees' => [0..360] for discrete, or automatically converted
          to [0..2π] if method='polar'.
        - 'radians' => [0..2π] for polar, or automatically converted
          to [0..360] if method='discrete'.

    Returns
    -------
    matplotlib.artist.Artist or matplotlib.axes.Axes
        - If `method='discrete'`, returns the PatchCollection representing
          the wedge patches.
        - If `method='polar'`, returns the Axes (PolarAxes) with the colorbar
          drawn.

    Notes
    -----
    - The 'polar' method does not support drawing tick lines.
    - The 'discrete' method uses wedge patches for each color segment.
    """
    raise NotImplementedError
    # ------------------------------------------------
    # Convert tick units if needed
    # --> TODO: convert discrete approach to radians !
    # - We'll internally feed degrees to 'discrete' approach, and radians to 'polar'.
    if ticks is not None:
        if method == "discrete" and tick_units == "radians":
            # Convert from radians to degrees
            ticks = np.degrees(ticks)
        elif method == "polar" and tick_units == "degrees":
            # Convert from degrees to radians
            ticks = np.radians(ticks)

    # ------------------------------------------------
    # - If user wants "discrete" => call the wedge-based approach
    if method == "discrete":
        # We need a function akin to your existing plot_circular_colorbar_discrete,
        # but updated slightly to accept all parameters.
        return plot_circular_colorbar_discrete(
            cmap=cmap,
            ax=ax,
            cax=cax,
            n=n,
            r_min=r_min,
            r_max=r_max,
            center=center,
            adapt_limits=adapt_limits,
            zero_location=zero_location,
            clockwise=clockwise,
            edgecolor=edgecolor,
            linewidths=linewidths,
            antialiased=antialiased,
            ticks=ticks,
            ticklabels=ticklabels,
            ticklabels_offset=ticklabels_offset,
            add_ticks=add_ticks,
            add_contours=add_contours,
            ticklength=ticklength,
            tickcolor=tickcolor,
            tickwidth=tickwidth,
        )

    # ------------------------------------------------
    # Otherwise, if user wants "polar" => use the polar approach
    ax = plot_circular_colorbar(
        cmap=cmap,
        ax=ax,
        cax=cax,
        r_min=r_min,
        r_max=r_max,
        add_contours=add_contours,
        ticks=ticks,
        ticklabels=ticklabels,
        ticklabels_pad=ticklabels_pad,
        ticklabels_size=ticklabels_size,
    )
    return ax


def plot_circular_colorbar(
    cmap,
    *,
    ax=None,
    cax=None,
    r_min=0.8,
    r_max=1,
    add_contours=True,
    # Ticklabels options
    ticks=None,
    ticklabels=None,
    ticklabels_pad=4,
    ticklabels_size=10,
):
    """
    Plot a circular colorbar.

    This function plots a circular colorbar representing the specified
    cyclc colormap. You can either provide:

    - An existing Axes (`ax`) in which to place the colorbar (the colorbar will
      be appended to one of its sides).
    - A dedicated Axes object (`cax`) for direct drawing of the colorbar
      on the specified `cax`.
    - Or no Axes at all, in which case a new figure and Axes are created.

    If both `ax` and `cax` are given, `ax` is ignored !.

    Parameters
    ----------
    cmap : matplotlib.colors.Colormap
        The colormap to be used for the bivariate colorbar.
    ax : matplotlib.axes.Axes, optional
        The Axes to which the colorbar should be appended. Ignored if
        `cax` is provided. If both `ax` and `cax` are None, a new figure
        and Axes are created.
    cax : matplotlib.axes.Axes, optional
        The Axes in which to directly draw the colorbar. If provided,
        `ax` is ignored.
    origin : {'lower', 'upper'}, optional
        Indicates where to locate the origin in the colorbar Axes.
        Default is 'lower'.
    location : {'right', 'left', 'top', 'bottom'}, optional
        The side of the plot where the colorbar should be placed
        (when `ax` is used). Default is 'right'.
    size : float or str, optional
        The size of the colorbar relative to the parent Axes when using
        `append_axes`. For instance, `'30%'` means 30% of the parent Axes
        width (or height, depending on `location`). Default is `'30%'`.
    pad : float, optional
        The padding between the parent Axes and the colorbar, in inches.
        Default is 0.45.
    box_aspect : float, optional
        The aspect ratio of the colorbar Axes box. Default is 1.
    """
    """
    Plot a circular colorbar with optional tick labels.

    This function use pcolormesh and the suplot polar projection to draw the colorbar.
    With this approach, it is not possible to add tick lines with this function !

    Parameters
    ----------
    cmap : Colormap
        The colormap to be used for the colorbar.
    r_min : float, optional
        The minimum radius for the colorbar circle. The default value is 0.8.
    r_max : float, optional
        The maximum radius for the colorbar circle. The default value is 1.
    add_contours : bool, optional
        Whether to add contour lines at the inner and outer boundaries. The default is True.
    ax : matplotlib.axes._subplots.PolarAxesSubplot, optional
        The axis on which to plot. If None, a new figure and axis are created. The default is None.
    ticks : array-like, optional
        Tick positions in radians between 0 and 2pi. The default is None.
    ticklabels : array-like, optional
        Tick labels corresponding to the tick positions. The default default None.
    ticklabels_pad : int, optional
        Padding for the tick labels. The default value is 4.
    ticklabels_size : int, optional
        Font size for the tick labels. The default value is 10.

    Returns
    -------
    ax : matplotlib.axes._subplots.PolarAxesSubplot
        The axis with the plotted circular colorbar.
    """

    from pycolorbar.univariate import plot_circular_colormap

    # TODO:
    location = "right"
    size = "30%"
    pad = 0.3
    # box_aspect = 1

    # Determine colorbar axis
    if cax is not None:
        pass
    elif ax is not None:  # and cax is None
        divider = make_axes_locatable(ax)
        cax = divider.append_axes(location, size=size, pad=pad, axes_class=mpl.projections.polar.PolarAxes)
    else:
        cax = None  # New plot created in plot_circular_colormap

    # Draw circular colormap
    p = plot_circular_colormap(
        cmap=cmap,
        r_min=r_min,
        r_max=r_max,
        add_cmap_name=False,
        add_contours=add_contours,
        ax=cax,
    )

    # Add ticks if necessary
    if ticks is not None and ticklabels is not None:
        p.axes.set_xticks(ticks)
        p.axes.set_xticklabels(ticklabels)

    # Improve ticklabels of the colorbar
    p.axes.tick_params(pad=ticklabels_pad, labelsize=ticklabels_size)
    return p


def add_circular_colorbar_legend(
    *,
    cmap,
    ax,
    # Inset options
    box_aspect=1,
    height=0.2,
    pad=0.005,
    loc="upper right",
    inside_figure=True,
    optimize_layout=True,
    # Fancybox options
    fancybox=False,
    fancybox_pad=0,
    fancybox_fc="white",
    fancybox_ec="none",
    fancybox_lw=0.5,
    fancybox_alpha=0.4,
    fancybox_shape="square",
    # Colorbar options
    discrete=True,
    **kwargs,
):
    """
    Add the circular colorbar legend to a plot.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to which the colorbar legend will be added.
    cmap: matplotlib.colors.Colormap
        A cyclic matplotlib colormap.
    box_aspect : float, optional
        Aspect ratio of the inset Axes. Default is 1.
    height : float, optional
        Height of the inset as a fraction [0-1] of the main Axes. Default is 0.2.
    pad : float, optional
        Padding between the inset and main Axes in figure coordinates. Default is 0.005.
    loc : str or tuple, optional
        Location of the inset. Default is 'upper right'.
    inside_figure : bool, optional
        Whether inset is inside the figure region. Default is True.
    optimize_layout : bool, optional
        Whether to auto-adjust the inset position for ticklabels. Default is True.
        NOTE: If True, do not call `fig.tight_layout()` afterwards.
    fancybox : bool, optional
        Whether to draw a fancy box behind the inset. Default is False.
    fancybox_pad : float, optional
        Padding of the fancy box in figure coordinates. Default is 0.
    fancybox_fc : str, optional
        Face color of the fancy box. Default is 'white'.
    fancybox_ec : str, optional
        Edge color of the fancy box. Default is 'none'.
    fancybox_lw : float, optional
        Line width of the fancy box. Default is 0.5.
    fancybox_alpha : float, optional
        Alpha of the fancy box. Default is 0.4.
    fancybox_shape : {'circle', 'square'}, optional
        Shape of the fancy box. Default is 'square'.
    discrete: float, optional
        Whether to plot a discrete or continuous circular colorbar.
        If True (the default) call the plot_circular_colorbar_discrete function.
        Otherwise call the plot_circular_colorbar function
    **kwargs : dict
        Additional keyword arguments passed to the circular colorbar.
        See the plot_circular_colorbar_discrete and plot_circular_colorbar documentation.

    Returns
    -------
    matplotlib.image.AxesImage
        The image object representing the circular colorbar.

    """
    # The actual colorbar plotting function
    # --------------------------------------------------.
    # - CUSTOM CODE HERE
    if discrete:
        colorbar_func = plot_circular_colorbar_discrete
        projection = None
    else:
        colorbar_func = plot_circular_colorbar
        projection = "polar"

    colorbar_func_kwargs = dict(
        cmap=cmap,
        **kwargs,
    )
    # --------------------------------------------------.
    p_cbar = add_colorbar_inset(
        ax=ax,
        colorbar_func=colorbar_func,
        colorbar_func_kwargs=colorbar_func_kwargs,
        # Inset options
        projection=projection,
        box_aspect=box_aspect,
        height=height,
        pad=pad,
        loc=loc,
        inside_figure=inside_figure,
        optimize_layout=optimize_layout,
        fancybox=fancybox,
        fancybox_pad=fancybox_pad,
        fancybox_fc=fancybox_fc,
        fancybox_ec=fancybox_ec,
        fancybox_lw=fancybox_lw,
        fancybox_alpha=fancybox_alpha,
        fancybox_shape=fancybox_shape,
    )
    return p_cbar

    # # --------------------------------------------------.
    # # - CUSTOM CODE HERE
    # if discrete:
    #     func = plot_circular_colorbar_discrete
    #     projection = None
    # else:
    #     func = plot_circular_colorbar
    #     projection = "polar"

    # # --------------------------------------------------.
    # # Define inset location relative to main plot (ax) in normalized units
    # # - Lower-left corner of inset Axes, and its width and height
    # # - [x0, y0, width, height]
    # # - If loc is (x0,y0) it just compute width and height.
    # cax_bounds = get_inset_bounds(
    #     ax=ax,
    #     loc=loc,
    #     inset_height=height,
    #     inside_figure=inside_figure,
    #     aspect_ratio=box_aspect,
    #     border_pad=pad,
    # )

    # # Define inset position
    # cax = ax.inset_axes(
    #     bounds=cax_bounds,  # [x0, y0, width, height]
    #     projection=projection,
    # )

    # # Increase order to give space for fancy box !
    # fancybox_zorder = cax.get_zorder() + 1
    # cax.set_zorder(cax.get_zorder() + 2)

    # # Plot colorbar
    # p_cbar = func(
    #         cax=cax,
    #         cmap=cmap,
    #         **kwargs,
    #     )

    # # --------------------------------------------------.
    # # Adapt the cax position to include ticks and ticklabels
    # if optimize_layout and inside_figure:
    #     # Set new position
    #     # - If 'inset_axes' was used, cax has an AxesLocator
    #     # - We remove that to manually control it.
    #     new_cax_pos = optimize_inset_position(ax=ax, cax=cax, pad=pad)
    #     cax.set_axes_locator(None)
    #     cax.set_position(new_cax_pos)

    # # Add fancy box in background
    # if fancybox:
    #     fancy_bbox = get_tightbbox_position(cax)
    #     _ = add_fancybox(
    #         ax=ax,
    #         bbox=fancy_bbox,
    #         fc=fancybox_fc,
    #         ec=fancybox_ec,
    #         lw=fancybox_lw,
    #         shape=fancybox_shape,
    #         alpha=fancybox_alpha,
    #         pad=fancybox_pad,
    #         zorder=fancybox_zorder,
    #     )

    # return p_cbar
