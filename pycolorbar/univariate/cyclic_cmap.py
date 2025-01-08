import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap


def get_discrete_cyclic_cmap(cmap, n):
    """Create a discrete cyclic color palette."""
    values = np.linspace(0, 1 - 1 / n, n)
    return ListedColormap(colors=cmap(values), name=cmap.name)


def _create_circular_mesh(
    r_min=0.5,
    r_max=1,
    amplitude=np.pi / 5,
    n_cycles=50,
    power=4,
    shape=(50, 1000),
):
    """
    Create a circular mesh grid with an optional sinusoidal pattern following the method of Kovesi (2015).

    Parameters
    ----------
    r_min : float, optional
        The minimum radius of the mesh, by default 0.5.
    r_max : float, optional
        The maximum radius of the mesh, by default 1.
    amplitude : float, optional
        Amplitude of the sine wave component, by default np.pi/5.
    n_cycles : int, optional
        The number of sine wave cycles in the radial direction, by default 50.
    power : int, optional
        The power to which the radius is raised, controlling the ramp steepness, by default 4.
    shape : tuple of int, optional
        The shape of the mesh grid (radial points, angular points), by default (50, 1000).

    Returns
    -------
    theta_mesh : numpy.ndarray
        2D array of angular coordinates (in radians) corresponding to each mesh point.
    radius_mesh : numpy.ndarray
        2D array of radial coordinates corresponding to each mesh point.
    values : numpy.ndarray
        Normalized 2D array of values between 0 and 1, with optional spiral ramp applied.

    References
    ----------
    Kovesi, P., 2015. "Good Colour Maps: How to Design Them." arXiv preprint arXiv:1509.03700.
    """
    radius = np.linspace(r_min, r_max, shape[0])
    theta = np.linspace(0, 2 * np.pi, shape[1])
    radius_mesh, theta_mesh = np.meshgrid(radius, theta)
    # Apply formula of Kovesi
    normalized_radius = (radius_mesh - r_min) / (r_max - r_min)
    values = amplitude * normalized_radius**power * np.sin(n_cycles * theta_mesh) + theta_mesh
    # Normalize values to [0-1] and discard last row duplicate
    values = np.mod(values, 2 * np.pi)
    values = values[:-1, :-1] / (2 * np.pi)
    return theta_mesh, radius_mesh, values


def plot_circular_colormap(
    cmap,
    r_min=0.2,
    r_max=1,
    ax=None,
    add_contours=True,
    add_cmap_name=True,
    # Options for sine ramp of Kovesi
    n_cycles=0,  # 50
    amplitude=np.pi / 5,
    power=4,
):
    """
    Plot a circular colormap with an optional sinusoidal pattern.

    Parameters
    ----------
    cmap : Colormap
        The colormap to be used for the plot.
    r_min : float, optional
        The minimum radius for the colormap circle. The default value is 0.2.
    r_max : float, optional
        The maximum radius for the colormap circle. The default value is  1.
    ax : matplotlib.axes._subplots.PolarAxesSubplot, optional
        The axis on which to plot. If None, a new figure and axis are created. The default is None.
    add_contours : bool, optional
        Whether to add contour lines at the inner and outer boundaries.
        The default is True.
    add_cmap_name: bool, optional
        Whether to add colormap name. The default is True.
    n_cycles : int, optional
        The number of sine wave cycles in the radial direction. Set to 0 to omit the spiral pattern.
        The default is 0.
    amplitude : float, optional
        Amplitude of the sine wave component in the spiral pattern. The default value is np.pi/5.
    power : int, optional
        Power of the radial distance in the spiral pattern. The default value is 4.

    Returns
    -------
    ax : matplotlib.axes._subplots.PolarAxesSubplot
        The axis with the plotted circular colormap.

    References
    ----------
    Kovesi, P., 2015. "Good Colour Maps: How to Design Them." arXiv preprint arXiv:1509.03700.
    """
    # Define the number of segments to define the circle
    nties = 512

    # Define (range, theta) tuple
    shape = (50, nties) if n_cycles > 0 else (2, nties)

    # Define mesh
    theta_mesh, radius_mesh, values = _create_circular_mesh(
        r_min=r_min,
        r_max=r_max,
        n_cycles=n_cycles,
        amplitude=amplitude,
        power=power,
        shape=shape,
    )
    # theta = np.linspace(0, 2*np.pi, nties)
    # radius = np.linspace(r_min, r_max, 2)
    # radius_mesh, theta_mesh = np.meshgrid(radius, theta)      # create a r,theta meshgrid
    # # Define values between 0 and 1 for colors
    # values = np.expand_dims(np.linspace(0, 1, nties)[:-1], axis=1)

    # Create figure and axis
    if ax is None:
        fig, ax = plt.subplots(subplot_kw={"projection": "polar"})
    if not isinstance(ax, mpl.projections.polar.PolarAxes):
        msg = "plot_circular_colormap require a matplotlib.projection.PolarAxes. " + "Set projection='polar'"
        raise ValueError(msg)

    # Set the 0° location to the top (zenith) instead of the default right
    ax.set_theta_zero_location("N")  # "N" stands for North (top)
    # Make the angle increase in the clockwise direction
    ax.set_theta_direction(-1)
    # Plot the colormesh on axis with colormap
    p = ax.pcolormesh(theta_mesh, radius_mesh, values, cmap=cmap)
    # Draw inner and outer circle line
    if add_contours:
        theta = np.linspace(0, 2 * np.pi, nties)
        ax.plot(theta, np.ones(theta.shape) * r_min, c="black")
        ax.plot(theta, np.ones(theta.shape) * r_max, c="black")
    # Turnoff radial tick labels (yticks)
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    # Add cmap name
    if add_cmap_name:
        ax.set_title(cmap.name, fontsize=10, weight="bold")
    # Disable polar grid lines
    ax.grid(False)
    return p
