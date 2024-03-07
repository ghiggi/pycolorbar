#!/usr/bin/env python3
"""
Created on Thu Mar  7 13:47:59 2024

@author: ghiggi
"""


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
            "labels": ["Clear Sky", "Liquid", "SC Liquid", "Mixed", "Ice", "Unknown"],
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
