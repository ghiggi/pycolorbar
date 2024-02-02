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
"""Define functions to build colormaps in multiple color spaces."""

# import numpy as np
# import matplotlib as mpl
# import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, ListedColormap


def convert_colors(colors, color_space):
    #  TODO: IMPLEMENT !
    pass
    return colors


def create_cmap(cmap_dict, name):
    cmap_type = cmap_dict["type"]
    colors = cmap_dict["colors"]
    color_space = cmap_dict["color_space"]

    # Convert colors to interpolation space
    # - if ListedColormap --> RGBA
    # - if LinearSegmentedColormap --> interpolation_space (default RGBA)
    colors = convert_colors(colors, color_space)

    # Create Colormap
    if cmap_type == "ListedColormap":
        n = cmap_dict.get("n", None)
        return ListedColormap(colors, name=name, N=n)
    else:
        n = cmap_dict.get("n", 256)
        gamma = cmap_dict.get("gamma", 1.0)
        if "segmentdata" not in cmap_dict:
            # Retrieve n colors in 'interpolation_space' (when type=LinearSegmentedColormap)
            # TODO

            # Retrieve colormap
            return LinearSegmentedColormap.from_list(name=name, colors=colors, N=n, gamma=gamma)
        else:
            segmentdata = cmap_dict["segmentdata"]
            return LinearSegmentedColormap(name=name, segmentdata=segmentdata, N=n, gamma=gamma)
