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
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np


def get_mpl_named_colors():
    """
    Retrieves the list of valid named colors available in matplotlib.

    Returns
    -------
    np.ndarray
        An array of valid named colors.

    Notes
    -----
    This function combines colors from TABLEAU_COLORS, BASE_COLORS, CSS4_COLORS, and XKCD_COLORS in matplotlib.
    """
    named_colors = list(mcolors.get_named_colors_mapping())
    # named_colors = (
    #     list(mcolors.TABLEAU_COLORS) +
    #     list(mcolors.BASE_COLORS)    +
    #     list(mcolors.CSS4_COLORS)    +
    #     list(mcolors.XKCD_COLORS)
    # )
    named_colors = np.array(named_colors, dtype=str)
    return named_colors


def get_mpl_colormaps():
    return plt.colormaps()
