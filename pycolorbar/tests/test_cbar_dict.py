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


TEST_CBAR_DICT = {
    "DISCRETE_CBAR": {
        "cmap": {
            "name": "spectral",
            "bad_alpha": 0.5,
            "bad_color": "gray",
            "over_color": "#8c149c",
            "under_color": "none",
        },
        "norm": {
            "name": "BoundaryNorm",
            "boundaries": [0.1, 0.2, 0.3, 0.5, 1, 2, 3, 5, 10, 20, 50],
        },
        "cbar": {
            "extend": "max",
            "label": "Colorbar Title",
        },
        "auxiliary": {
            "category": ["category", "CATEGORY1"],
        },
    },
    "CONTINUOUS_LOG_CBAR": {
        "cmap": {
            "name": "RdBu_r",
            "bad_alpha": 0.5,
            "bad_color": "gray",
        },
        "norm": {
            "name": "SymLogNorm",
            "vmin": -400,
            "vmax": 400,
            "linthresh": 1,
            "base": 10,
        },
        "cbar": {
            "extend": "both",
            "extendfrac": 0.05,
            "label": "Colorbar Title",
        },
    },
    "CONTINUOUS_CBAR": {
        "cmap": {
            "name": "YlGnBu",
            "bad_alpha": 0.5,
            "bad_color": "gray",
            "under_color": "none",
        },
        "norm": {
            "name": "Norm",
            "vmin": 0.1,
            "vmax": 20,
        },
        "cbar": {
            "extend": "max",
            "extendfrac": 0.05,
            "label": "Colorbar Title",
        },
    },
    "PROBABILITY_CBAR": {
        "cmap": {
            "name": "OrRd",
            "bad_alpha": 0.5,
            "bad_color": "gray",
            "over_color": "none",
            "under_color": "none",
        },
        "norm": {
            "name": "BoundaryNorm",
            "boundaries": [0.001, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        },
        "auxiliary": {
            "category": "probability",
            "citation": "pycolorbar",
            "citation_url": "pycolorbar",
            "comment": "0.001 is set to display the 0s transparently",
        },
    },
    "CATEGORICAL_CBAR": {
        "cmap": {
            "name": "GOES_CloudPhase",
            "bad_alpha": 0.5,
            "bad_color": "gray",
        },
        "norm": {
            "name": "CategoryNorm",
            "categories": {0: "Clear Sky", 1: "Liquid", 2: "SC Liquid", 3: "Mixed", 4: "Ice", 5: "Unknown"},
        },
    },
    "TWO_CMAP_CBAR": {
        "cmap": {
            "name": ["Spectral", "gray"],
            "n": [256, 256],
        },
        "norm": {
            "name": "TwoSlopeNorm",
            "vmin": 200,
            "vcenter": 280,
            "vmax": 400,
        },
        "cbar": {
            "extend": "both",
            "extendfrac": 0.05,
            "label": "Brightness Temperature [K]",
        },
    },
}
