import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PatchCollection
from matplotlib.patches import Circle, Wedge

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
    add_boundary=False,
    ticklength=0.02,
    tickcolor="black",
    tickwidth=1,
    ax=None,
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
    # Create figure and axis
    if ax is None:
        fig, ax = plt.subplots()
    # Set equal axis ration
    ax.set_aspect("equal")
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
    ax.add_collection(collection)
    # Add custom ticks and labels
    if ticks is not None and ticklabels is not None:
        # Add ticks labels
        _add_ticklabels(
            ax=ax,
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
                ax=ax,
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
    if add_boundary:
        ax.add_patch(Circle(center, r_max, color=tickcolor, lw=1.5, fill=False))
        ax.add_patch(Circle(center, r_min, color=tickcolor, lw=1.5, fill=False))
    # Turn off axis
    ax.set_axis_off()
    # Adapt limits
    if adapt_limits:
        _ = _set_adaptive_limits(ax=ax, r_max=r_max, center=center, margin_factor=0.1)
    # Return ax
    return ax


def plot_circular_colorbar(
    cmap,
    r_min=0.8,
    r_max=1,
    add_contours=True,
    ax=None,
    # Ticklabels options
    ticks=None,
    ticklabels=None,
    ticklabels_pad=4,
    ticklabels_size=10,
):
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

    # Draw circular colormap
    ax = plot_circular_colormap(
        cmap=cmap,
        r_min=r_min,
        r_max=r_max,
        add_cmap_name=False,
        add_contours=add_contours,
        ax=ax,
    )
    # Add ticks if necessary
    if ticks is not None and ticklabels is not None:
        ax.set_xticks(ticks)
        ax.set_xticklabels(ticklabels)
    # Improve ticklabels of the colorbar
    ax.tick_params(pad=ticklabels_pad, labelsize=ticklabels_size)
    return ax
