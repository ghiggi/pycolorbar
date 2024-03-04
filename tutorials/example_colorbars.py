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

from matplotlib.colors import Normalize

import pycolorbar

# Register colormaps !
dst_dir = "/home/ghiggi/Python_Packages/pycolorbar/pycolorbar/etc/colormaps"
pycolorbar.register_colormaps(dst_dir)


dst_dir = "/home/ghiggi/Python_Packages/pycolorbar/pycolorbar/etc/colorbars"

pycolorbar.colorbars.names

pycolorbar.register_colorbars(dst_dir)

pycolorbar.colorbars.names

pycolorbar.colorbars.unregister("COD")

pycolorbar.colorbars.names

pycolorbar.register_colorbar(os.path.join(dst_dir, "GOES_L2_CLOUDS.yaml"))

pycolorbar.colorbars.register(os.path.join(dst_dir, "GOES_L2_CLOUDS.yaml"))

pycolorbar.colorbars.names

pycolorbar.colorbars.reset()

pycolorbar.colorbars.names

pycolorbar.register_colorbars(dst_dir)

pycolorbar.colorbars.names

# ------------------------------------------------------------------
#### List all available colorbars
pycolorbar.colorbars.available()
pycolorbar.available_colorbars()

pycolorbar.available_colorbars(category="not_existing")
pycolorbar.colorbars.available(category="not_existing")

pycolorbar.colorbars.available(exclude_referenced=True)

pycolorbar.available_colorbars(category="precipitation")

pycolorbar.available_colorbars(category="precipitation", exclude_referenced=True)

pycolorbar.available_colorbars(category="imerg")

# List colorbar settings that defines a colorbar (without reference)
pycolorbar.colorbars.get_standalone_settings()

# List colorbar settings that reference to another configuration
pycolorbar.colorbars.get_referenced_settings()

# --------------------------------------------------------------------------------
#### Retrieve cbar_dict
pycolorbar.get_cbar_dict("precipRate")
pycolorbar.get_cbar_dict("precipRate", resolve_reference=False)
pycolorbar.get_cbar_dict("precipRate", resolve_reference=True)

# --------------------------------------------------------------------------------
##### Colorbar Validation
cbar_dict = pycolorbar.get_cbar_dict("precipRate")
cbar_dict = pycolorbar.validate_cbar_dict(cbar_dict)


pycolorbar.colorbars.validate(name=None)
for name in pycolorbar.colorbars.names:
    pycolorbar.colorbars.validate(name=name)

cbar_dict = pycolorbar.colorbars.get_cbar_dict("IMERG_Solid")
cbar_dict
pycolorbar.validate_cbar_dict(cbar_dict)

cbar_dict = pycolorbar.colorbars.get_cbar_dict("dfrMeasured")
cbar_dict
pycolorbar.validate_cbar_dict(cbar_dict)

cbar_dict = pycolorbar.colorbars.get_cbar_dict("Brightness_Temperature")
cbar_dict
pycolorbar.validate_cbar_dict(cbar_dict)

cbar_dict = pycolorbar.colorbars.get_cbar_dict("Phase")
cbar_dict
pycolorbar.validate_cbar_dict(cbar_dict)

# -------------------------------------------------------------------------
#### Colorbar Dictionary Addition
cbar_dict = pycolorbar.colorbars.get_cbar_dict("COD")

pycolorbar.colorbars.add_cbar_dict(cbar_dict, name="NEW")

pycolorbar.colorbars.names

cbar_dict = pycolorbar.colorbars.get_cbar_dict("NEW")

cbar_dict

# --------------------------------------------------------------------------------
#### Colorbar Plotting Options retrievals
plot_kwargs, cbar_kwargs = pycolorbar.get_plot_kwargs(name="Brightness_Temperature")

plot_kwargs, cbar_kwargs = pycolorbar.get_plot_kwargs(name="precipRateNearSurface")

plot_kwargs, cbar_kwargs = pycolorbar.get_plot_kwargs(name="Phase")

plot_kwargs, cbar_kwargs = pycolorbar.get_plot_kwargs(name="whatever_name")

for name in pycolorbar.colorbars.names:
    pycolorbar.get_plot_kwargs(name=name)


plot_kwargs, cbar_kwargs = pycolorbar.get_plot_kwargs(name="whatever_name", user_plot_kwargs={"vmin": 2, "vmax": 3})

# --------------------------------------------------------------------------------
#### Colorbar Visualization
pycolorbar.show_colorbar("Brightness_Temperature")
pycolorbar.show_colorbar("precipRateNearSurface")
pycolorbar.show_colorbar("dfrFinal")
pycolorbar.show_colorbar("Phase")
pycolorbar.show_colorbar("CM")
pycolorbar.show_colorbar("Precip_Probability")

pycolorbar.show_colorbar("ir_cloud_top")  # CMB

pycolorbar.show_colorbars(category="not_existing")

pycolorbar.show_colorbars()

pycolorbar.show_colorbars(category="precipitation")

pycolorbar.show_colorbars(category="precipitation", exclude_referenced=True)

pycolorbar.show_colorbars(category="precipitation", exclude_referenced=False)

pycolorbar.show_colorbars(category="imerg")

# --------------------------------------------------------------------------------
#### Updated Colorbar Visualization

pycolorbar.show_colorbar("whatever_name")
pycolorbar.show_colorbar("whatever_name", user_plot_kwargs={"vmin": 2})  # do not set because missing vmin
pycolorbar.show_colorbar("whatever_name", user_plot_kwargs={"vmax": 2})  # do not set because missing vmax
pycolorbar.show_colorbar("whatever_name", user_plot_kwargs={"vmin": 2, "vmax": 3})
pycolorbar.show_colorbar("whatever_name", user_plot_kwargs={"norm": Normalize(vmin=2, vmax=3)})
pycolorbar.show_colorbar("whatever_name", user_plot_kwargs={"cmap": "Spectral"}, user_cbar_kwargs={"extend": "both"})
pycolorbar.show_colorbar("whatever_name", user_cbar_kwargs={"extend": "both"})  # bad shape triangles

pycolorbar.show_colorbar("Precip_Probability")
pycolorbar.show_colorbar("Precip_Probability", user_plot_kwargs={"cmap": "Spectral"})
pycolorbar.show_colorbar("Precip_Probability", user_cbar_kwargs={"extend": "max"})


pycolorbar.show_colorbar("precipRateNearSurface")
pycolorbar.show_colorbar("precipRateNearSurface", user_plot_kwargs={"cmap": "Spectral"})
pycolorbar.show_colorbar("precipRateNearSurface", user_plot_kwargs={"norm": Normalize(vmin=0, vmax=100)})
pycolorbar.show_colorbar(
    "precipRateNearSurface",
    user_plot_kwargs={"cmap": "Spectral", "norm": Normalize(vmin=0, vmax=100)},
)


pycolorbar.show_colorbar("Phase")
pycolorbar.show_colorbar("Phase", user_plot_kwargs={"cmap": "Spectral"})  # labels conserved !
pycolorbar.show_colorbar("Phase", user_plot_kwargs={"norm": Normalize(vmin=0, vmax=10)})
pycolorbar.show_colorbar("Phase", user_plot_kwargs={"cmap": "Spectral", "norm": Normalize(vmin=0, vmax=10)})

pycolorbar.show_colorbar("ir_cloud_top")  # CMB
pycolorbar.show_colorbar("ir_cloud_top", user_plot_kwargs={"cmap": "Spectral"})

# --------------------------------------------------------------------------------
