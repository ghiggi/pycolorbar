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
import os

import pycolorbar
from pycolorbar.settings.colormap_io import read_cmap_dict
from pycolorbar.settings.colormap_utility import create_cmap

##### Colormap Registry
dst_dir = "/home/ghiggi/Python_Packages/pycolorbar/pycolorbar/etc/colormaps"
name = "STEPS-MCH"


pycolorbar.colormaps.names

pycolorbar.register_colormaps(dst_dir)

pycolorbar.colormaps.names

pycolorbar.colormaps.unregister("STEPS-MCH")

pycolorbar.colormaps.names

pycolorbar.register_colormap(os.path.join(dst_dir, "precipitation", f"{name}.yaml"))

pycolorbar.colormaps.register(os.path.join(dst_dir, "precipitation", f"{name}.yaml"))

pycolorbar.colormaps.names

pycolorbar.colormaps.reset()

pycolorbar.colormaps.names

pycolorbar.register_colormaps(dst_dir)

pycolorbar.colormaps.names  # only pycolorbar
# ------------------------------------------------------------------
#### List all available colormaps (pycolorbar)
pycolorbar.colormaps.available()
pycolorbar.colormaps.available(include_reversed=True)
pycolorbar.colormaps.available(category="not_existing")

# ------------------------------------------------------------------
#### List all available colormaps (matplotlib + pycolorbar)
pycolorbar.available_colormaps()
pycolorbar.available_colormaps(category="precipitation")
pycolorbar.available_colormaps(category="imerg")

pycolorbar.available_colormaps(category="not_existing")

pycolorbar.available_colormaps(category="sequential")
pycolorbar.available_colormaps(category="diverging")
pycolorbar.available_colormaps(category="categorical")
pycolorbar.available_colormaps(category="qualitative")
pycolorbar.available_colormaps(category="cyclic")
pycolorbar.available_colormaps(category="perceptual")

pycolorbar.available_colormaps(category="diverging", include_reversed=True)

# ------------------------------------------------------------------
#### Colormap Configuration Filepath
filepath = pycolorbar.colormaps.get_cmap_filepath(name)
cmap_dict = read_cmap_dict(filepath)

# ------------------------------------------------------------------
#### Colormap Dictionary Retrieval
cmap_dict = pycolorbar.colormaps.get_cmap_dict(name)

cmap_dict = pycolorbar.colormaps.get_cmap_dict("IMERG_Liquid")

pycolorbar.get_cmap_dict("IMERG_Liquid")

# ------------------------------------------------------------------
##### Colormap Validation
cmap_dict = pycolorbar.validate_cmap_dict(cmap_dict)

pycolorbar.colormaps.validate(name=None)

# ------------------------------------------------------------------
##### Colormap Dictionary Addition
pycolorbar.colormaps.add_cmap_dict(cmap_dict, name="NEW")
pycolorbar.colormaps.names
cmap_dict = pycolorbar.colormaps.get_cmap_dict("NEW")
cmap_dict

# ------------------------------------------------------------------
#### Colormap Retrieval
cmap_dict = pycolorbar.colormaps.get_cmap_dict("GOES_CloudPhase")
cmap = create_cmap(cmap_dict=cmap_dict, name="new")
cmap

# Retrieve colormap from pycolorbar.registry or matplotlib
pycolorbar.get_cmap("STEPS-MCH")
pycolorbar.get_cmap("STEPS-MCH", 80)
pycolorbar.get_cmap("STEPS-MCH", 10)
pycolorbar.get_cmap("STEPS-MCH", 15)
pycolorbar.get_cmap("STEPS-MCH", 5)

pycolorbar.get_cmap("viridis")
pycolorbar.get_cmap("RdBu")
pycolorbar.get_cmap("Set1")

# Retrieve colormap from pycolorbar.registry
pycolorbar.colormaps.get_cmap("STEPS-MCH")

## Error. get_cmap from pycolorbar registry does not allow resampling !
# pycolorbar.colormaps.get_cmap("STEPS-MCH", 5)

## Error. get_cmap from pycolorbar registry does not retrieve matplotlib colormaps !
# pycolorbar.colormaps.get_cmap("viridis")

# ListedColormap color: truncation and repetition
cmap = pycolorbar.get_cmap("Set1")
cmap.N
cmap

cmap_repeated = pycolorbar.get_cmap("Set1", 12)
cmap_repeated.N
cmap_repeated.colors
cmap_repeated

cmap_truncated = pycolorbar.get_cmap("Set1", 3)
cmap_truncated.N
cmap_truncated.colors
cmap_truncated

# Retrieve colormap from pycolorbar.colorbars registry !
dst_dir = "/home/ghiggi/Python_Packages/pycolorbar/pycolorbar/etc/colorbars"
pycolorbar.colorbars.names
pycolorbar.register_colorbars(dst_dir)
pycolorbar.colorbars.names
pycolorbar.colorbars.get_cmap("REFC")
pycolorbar.colorbars.get_cmap("RRQPE")

# --------------------------------------------------------------------------------
#### Colormap Visualization
cmap = pycolorbar.colormaps.get_cmap("STEPS-MCH")
cmap

pycolorbar.show_colormap(cmap)
pycolorbar.show_colormap("STEPS-MCH")

pycolorbar.colormaps.show_colormaps()  # only pycolorbar
pycolorbar.show_colormaps()  # pycolorbar + matplotlib

# Subset by category --> auxiliary[category]
pycolorbar.show_colormaps(category="precipitation")
pycolorbar.show_colormaps(category="imerg")

pycolorbar.show_colormaps(category="not_existing")

pycolorbar.show_colormaps(category="sequential")
pycolorbar.show_colormaps(category="diverging")
pycolorbar.show_colormaps(category="categorical")
pycolorbar.show_colormaps(category="qualitative")
pycolorbar.show_colormaps(category="cyclic")
pycolorbar.show_colormaps(category="perceptual")

pycolorbar.colormaps.show_colormaps(include_reversed=True)  # only pycolorbar
pycolorbar.show_colormaps(include_reversed=True)

# --------------------------------------------------------------------------------
