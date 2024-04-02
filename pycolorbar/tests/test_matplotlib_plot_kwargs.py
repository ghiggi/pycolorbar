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
"""Test code to retrieve plot_kwargs and cbar_kwargs."""
import matplotlib.pyplot as plt
import numpy as np
import pytest
from deepdiff import DeepDiff
from matplotlib.colors import (
    AsinhNorm,
    BoundaryNorm,
    CenteredNorm,
    Colormap,
    LinearSegmentedColormap,
    ListedColormap,
    LogNorm,
    NoNorm,
    Normalize,
    PowerNorm,
    SymLogNorm,
    TwoSlopeNorm,
)

from pycolorbar.settings.matplotlib_kwargs import (
    get_cmap,
    get_default_cbar_kwargs,
    get_norm,
    get_plot_cbar_kwargs,
    update_plot_cbar_kwargs,
)


@pytest.fixture()
def basic_cbar_dict():
    """Provides a basic colorbar dictionary for testing."""
    return {
        "cmap": {
            "name": "viridis",
        },
        "norm": {},
        "cbar": {},
        "auxiliary": {},
    }


class TestGetCmapFromCbarDict:
    @pytest.mark.parametrize(
        "cmap_name, expected_type", [("viridis", ListedColormap), ("Spectral", LinearSegmentedColormap)]
    )
    def test_get_cmap_with_valid_names(self, basic_cbar_dict, cmap_name, expected_type):
        """Test get_cmap function with valid colormap names."""
        basic_cbar_dict["cmap"]["name"] = cmap_name
        cmap = get_cmap(basic_cbar_dict)
        assert isinstance(cmap, expected_type), "The returned object is not of the expected colormap type."

    def test_get_cmap_with_invalid_name(self, basic_cbar_dict):
        """Test _get_cmap function with an invalid colormap name."""
        basic_cbar_dict["cmap"]["name"] = "INVALID_NAME"
        with pytest.raises(ValueError):
            get_cmap(basic_cbar_dict)

    @pytest.mark.parametrize("n_values", [256, None])
    @pytest.mark.parametrize("cmap_name", ["viridis", "Spectral"])
    def test_get_cmap_n_parameter(self, basic_cbar_dict, n_values, cmap_name):
        """Test _get_cmap with and without 'n' parameter specified."""
        basic_cbar_dict["cmap"]["name"] = cmap_name
        basic_cbar_dict["cmap"]["n"] = n_values
        cmap = get_cmap(basic_cbar_dict)
        if n_values is not None:
            assert cmap.N == n_values, "The 'n' parameter does not match the expected number of colors."
        else:
            assert cmap.N == 256, "The default number of colors should be 256 when 'n' is not specified."

    @pytest.mark.parametrize(
        "cmap_names, n_values",
        [
            (["viridis", "plasma"], None),
            (["viridis", "plasma"], [128, 128]),
            (["viridis", "plasma", "inferno"], [86, 86, 86]),  # Dividing 256 approximately equally
        ],
    )
    def test_get_cmap_combined_colormaps(self, basic_cbar_dict, cmap_names, n_values):
        """Test _get_cmap function with a list of colormap names and corresponding 'n' values."""
        basic_cbar_dict["cmap"]["name"] = cmap_names
        basic_cbar_dict["cmap"]["n"] = n_values
        cmap = get_cmap(basic_cbar_dict)
        assert isinstance(cmap, LinearSegmentedColormap), "The returned object is not a LinearSegmentedColormap."

    def test_finalize_cmap_colors(self, basic_cbar_dict):
        """Test _finalize_cmap by setting 'bad_color', 'over_color', and 'under_color'."""
        basic_cbar_dict["cmap"].update(
            {
                "bad_color": "#000000",  # black for invalid data points
                "over_color": "#ff0000",  # red for over values
                "under_color": "#00ff00",  # green for under values
                "bad_alpha": 0.5,
                "over_alpha": 0.5,
                "under_alpha": 0.5,
            }
        )
        cmap = get_cmap(basic_cbar_dict)
        np.testing.assert_equal(
            cmap.get_bad(), np.array([0, 0, 0, 0.5])
        ), "The bad color or alpha is not correctly set."
        np.testing.assert_equal(
            cmap.get_over(), np.array([1, 0, 0, 0.5])
        ), "The over color or alpha is not correctly set."
        np.testing.assert_equal(
            cmap.get_under(), np.array([0, 1, 0, 0.5])
        ), "The under color or alpha is not correctly set."

    @pytest.mark.parametrize(
        "cmap_dict_update", [{"bad_color": "none"}, {"over_color": "none"}, {"under_color": "none"}]
    )
    def test_finalize_cmap_with_none_colors(self, basic_cbar_dict, cmap_dict_update):
        """Test _finalize_cmap handling of 'none' for colors."""
        basic_cbar_dict["cmap"].update(cmap_dict_update)
        cmap = get_cmap(basic_cbar_dict)
        # Simplified check for whether 'none' resulted in the absence (transparent) of specified colors
        if "bad_color" in cmap_dict_update:
            assert cmap.get_bad()[3] == 0, "The bad color transparency is not correctly handled."
        if "over_color" in cmap_dict_update:
            assert cmap.get_over()[3] == 0, "The over color transparency is not correctly handled."
        if "under_color" in cmap_dict_update:
            assert cmap.get_under()[3] == 0, "The under color transparency is not correctly handled."


@pytest.mark.parametrize(
    "norm_name, expected_type, norm_settings",
    [
        ("Norm", Normalize, {"vmin": 0, "vmax": 1}),
        ("NoNorm", NoNorm, {}),
        ("BoundaryNorm", BoundaryNorm, {"boundaries": [0, 0.5, 1], "ncolors": 2}),
        ("BoundaryNorm", BoundaryNorm, {"boundaries": [0, 0.5, 1], "ncolors": 3, "extend": "vmin"}),
        ("BoundaryNorm", BoundaryNorm, {"boundaries": [0, 0.5, 1], "ncolors": 4, "extend": "both"}),
        ("CategoryNorm", BoundaryNorm, {"labels": ["a", "b", "c"]}),
        ("TwoSlopeNorm", TwoSlopeNorm, {"vmin": 0, "vcenter": 0.5, "vmax": 1}),
        ("CenteredNorm", CenteredNorm, {"vcenter": 0.5}),
        ("LogNorm", LogNorm, {"vmin": 0.1, "vmax": 1}),
        ("SymLogNorm", SymLogNorm, {"linthresh": 0.01, "linscale": 1, "vmin": -1, "vmax": 1}),
        ("PowerNorm", PowerNorm, {"gamma": 0.5, "vmin": 0, "vmax": 1}),
        ("AsinhNorm", AsinhNorm, {"linear_width": 1}),
    ],
)
def test_get_norm(norm_name, expected_type, norm_settings):
    """Test that get_norm correctly creates normalization instances."""
    norm_settings["name"] = norm_name
    norm_instance = get_norm(norm_settings)
    assert isinstance(norm_instance, expected_type), f"Expected instance of {expected_type}, got {type(norm_instance)}"


class TestPlotCbarKwargs:
    def test_empty_dict(self):
        """Test empty dictionary results."""
        # Define cbar_dict
        cbar_dict = {}

        # Retrieve plot_kwargs and cbar_kwargs
        plot_kwargs, cbar_kwargs = get_plot_cbar_kwargs(cbar_dict)

        # Check cmap and norm
        assert "cmap" in plot_kwargs, "Missing 'cmap' in plot_kwargs"
        assert (
            plot_kwargs["cmap"] is None
        ), "The plot_kwargs 'cmap' is not None if cbar_dict does not contain the 'cmap' dictionary"
        assert "norm" in plot_kwargs, "Missing 'norm' in plot_kwargs"
        assert isinstance(plot_kwargs["norm"], Normalize), "The plot_kwargs 'norm' is not a norm instance"

        # Assert cbar_kwargs is the default one
        default_cbar_kwargs = get_default_cbar_kwargs()

        diff = DeepDiff(cbar_kwargs, default_cbar_kwargs)
        assert diff == {}, f"Dictionaries are not equal: {diff}"

        # Assert ticks and ticklabels are None
        assert cbar_kwargs["ticks"] is None, "Expected ticks to be None"
        assert "ticklabels" not in cbar_kwargs  # temporary ...
        # assert cbar_kwargs["ticklabels"] is None, "Expected ticklabels to be None"

    def test_custom_cmap_and_norm_settings(self):
        """Test with simple cmap and norm colorbar dictionary."""
        # Define cbar_dict
        cbar_dict = {"cmap": {"name": "viridis"}, "norm": {"name": "Norm", "vmin": 0, "vmax": 1}}

        # Retrieve plot_kwargs and cbar_kwargs
        plot_kwargs, cbar_kwargs = get_plot_cbar_kwargs(cbar_dict)

        # Check cmap and norm
        assert "cmap" in plot_kwargs, "Missing 'cmap' in plot_kwargs"
        assert isinstance(plot_kwargs["cmap"], Colormap), "The plot_kwargs 'cmap' is not a Colormap"
        assert "norm" in plot_kwargs, "Missing 'norm' in plot_kwargs"
        assert isinstance(plot_kwargs["norm"], Normalize), "The plot_kwargs 'norm' is not a norm instance"

        # Assert cbar_kwargs is the default one
        default_cbar_kwargs = get_default_cbar_kwargs()

        diff = DeepDiff(cbar_kwargs, default_cbar_kwargs)
        assert diff == {}, f"Dictionaries are not equal: {diff}"

        # Assert ticks and ticklabels are None
        assert cbar_kwargs["ticks"] is None, "Expected ticks to be None"
        assert "ticklabels" not in cbar_kwargs  # temporary ...
        # assert cbar_kwargs["ticklabels"] is None, "Expected ticklabels to be None"

    def test_custom_cbar_settings(self):
        """Test with custom cbar setting."""
        # Define cbar_dict
        custom_cbar_kwargs = {
            "ticklocation": "left",
            "spacing": "proportional",
            "extend": "both",
            "label": "my_colorbar_title",
            "drawedges": True,
            "shrink": 0.5,
        }
        cbar_dict = {"cmap": {"name": "Spectral"}, "cbar": custom_cbar_kwargs}

        # Retrieve plot_kwargs and cbar_kwargs
        plot_kwargs, cbar_kwargs = get_plot_cbar_kwargs(cbar_dict)

        # Check cmap and norm
        assert "cmap" in plot_kwargs, "Missing 'cmap' in plot_kwargs"
        assert isinstance(plot_kwargs["cmap"], Colormap), "The plot_kwargs 'cmap' is not a Colormap"
        assert "norm" in plot_kwargs, "Missing 'norm' in plot_kwargs"
        assert isinstance(plot_kwargs["norm"], Normalize), "The plot_kwargs 'norm' is not a norm instance"

        # Assert cbar_kwargs have been updated
        for key, value in custom_cbar_kwargs.items():
            assert cbar_kwargs[key] == value, f"The cbar_kwargs key '{key}' has not been updated to {value}"

    @pytest.mark.parametrize("ncolors,extend", [(2, "neither"), (3, "vmin"), (3, "vmax"), (4, "both")])
    def test_custom_discrete_colorbar(self, ncolors, extend):
        """Test behaviour for discrete colorbar and addition of ticklabels in cbar_kwargs."""
        # Define cbar_dict
        cbar_dict = {
            "cmap": {"name": "Set1"},
            "norm": {"name": "BoundaryNorm", "boundaries": [0, 0.5, 1], "ncolors": ncolors, "extend": extend},
        }
        # Retrieve plot_kwargs and cbar_kwargs
        plot_kwargs, cbar_kwargs = get_plot_cbar_kwargs(cbar_dict)

        # Check cmap and norm
        assert "cmap" in plot_kwargs, "Missing 'cmap' in plot_kwargs"
        assert isinstance(plot_kwargs["cmap"], Colormap), "The plot_kwargs 'cmap' is not a Colormap"
        assert "norm" in plot_kwargs, "Missing 'norm' in plot_kwargs"
        assert isinstance(plot_kwargs["norm"], BoundaryNorm), "The plot_kwargs 'norm' is not a BoundaryNorm instance"

        # Check for ticklabels
        assert "ticklabels" in cbar_kwargs
        assert cbar_kwargs["ticklabels"] == ["0", "0.5", "1"]
        assert cbar_kwargs["ticks"] == [0, 0.5, 1]

    def test_custom_categorical_colorbar(self):
        """Test behaviour for a categorical colorbar and addition of ticklabels in cbar_kwargs."""
        # Define cbar_dict
        cbar_dict = {"cmap": {"name": "Set1"}, "norm": {"name": "CategoryNorm", "labels": ["one", "two"]}}
        # Retrieve plot_kwargs and cbar_kwargs
        plot_kwargs, cbar_kwargs = get_plot_cbar_kwargs(cbar_dict)

        # Check cmap and norm
        assert "cmap" in plot_kwargs, "Missing 'cmap' in plot_kwargs"
        assert isinstance(plot_kwargs["cmap"], Colormap), "The plot_kwargs 'cmap' is not a Colormap"
        assert "norm" in plot_kwargs, "Missing 'norm' in plot_kwargs"
        assert isinstance(plot_kwargs["norm"], BoundaryNorm), "The plot_kwargs 'norm' is not a BoundaryNorm instance"

        # Check for ticklabels
        assert "ticklabels" in cbar_kwargs
        assert cbar_kwargs["ticklabels"] == ["one", "two"]
        assert cbar_kwargs["ticks"] == [0.99, 1.99]


class TestUpdatePlotCbarKwargs:
    @pytest.fixture()
    def default_plot_kwargs(self):
        return {"cmap": plt.get_cmap("viridis"), "norm": Normalize(vmin=0, vmax=1)}

    @pytest.fixture()
    def default_cbar_kwargs(self):
        return {"extend": "neither", "label": "Default Label"}

    def test_no_user_kwargs(self):
        """Test that if no user kwargs specified, returns the default kwargs."""
        default_plot_kwargs = "dummy_input"
        default_cbar_kwargs = "dummy_input"
        plot_kwargs, cbar_kwargs = update_plot_cbar_kwargs(
            default_plot_kwargs=default_plot_kwargs, default_cbar_kwargs=default_cbar_kwargs
        )
        assert plot_kwargs == default_plot_kwargs, "The returned plot_kwargs are not the default ones"
        assert cbar_kwargs == default_cbar_kwargs, "The returned cbar_kwargs are not the default ones"

    def test_user_string_cmap(self, default_plot_kwargs, default_cbar_kwargs):
        """Test that a string cmap name in user_plot_kwargs is properly converted."""
        user_plot_kwargs = {"cmap": "plasma"}
        plot_kwargs, cbar_kwargs = update_plot_cbar_kwargs(
            default_plot_kwargs=default_plot_kwargs,
            default_cbar_kwargs=default_cbar_kwargs,
            user_plot_kwargs=user_plot_kwargs,
        )
        # Assert colormap has been updated (here we test just the name ...)
        assert isinstance(plot_kwargs["cmap"], Colormap)
        assert plot_kwargs["cmap"].name == "plasma"

        # Assert cbar_kwargs are the same as the default ones
        diff = DeepDiff(cbar_kwargs, default_cbar_kwargs)
        assert diff == {}, f"Dictionaries are not equal: {diff}"

    def test_user_norm_specified(self, default_plot_kwargs):
        """Test ticks and ticklabels are removed from default_cbar_kwargs if norm is specified by the user."""
        user_plot_kwargs = {"norm": Normalize(vmin=0, vmax=2)}
        default_cbar_kwargs = {"ticks": ["whatever"], "ticklabels": ["whatever"], "extend": "both"}
        plot_kwargs, cbar_kwargs = update_plot_cbar_kwargs(
            default_plot_kwargs=default_plot_kwargs,
            default_cbar_kwargs=default_cbar_kwargs,
            user_plot_kwargs=user_plot_kwargs,
        )
        # Assert cbar_kwargs does not contain anymore default_cbar_kwargs ticks and ticklabels
        assert "ticks" not in cbar_kwargs
        assert "ticklabels" not in cbar_kwargs
        # Assert that the others default_cbar_kwargs are kept
        assert "extend" in cbar_kwargs

    def test_user_levels_specified(self, default_plot_kwargs):
        """Test original ticks and ticklabels are removed from default_cbar_kwargs."""
        user_plot_kwargs = {"levels": [1000, 2000, 3000]}
        default_cbar_kwargs = {"ticks": ["whatever"], "ticklabels": ["whatever"], "extend": "both"}
        plot_kwargs, cbar_kwargs = update_plot_cbar_kwargs(
            default_plot_kwargs=default_plot_kwargs,
            default_cbar_kwargs=default_cbar_kwargs,
            user_plot_kwargs=user_plot_kwargs,
        )
        # Assert cbar_kwargs does not contain anymore default_cbar_kwargs ticks and ticklabels
        assert "ticks" not in cbar_kwargs
        assert "ticklabels" not in cbar_kwargs
        assert isinstance(plot_kwargs["norm"], BoundaryNorm)
        # Assert that the others default_cbar_kwargs are kept
        assert "extend" in cbar_kwargs

    def test_user_cmap_for_labeled_colorbar(self, default_plot_kwargs, default_cbar_kwargs):
        """Test resampling user-provided colormap for categorical and discrete colorbar."""
        user_plot_kwargs = {"cmap": plt.get_cmap("Spectral", 256)}
        default_cbar_kwargs["ticklabels"] = ["low", "medium", "high"]
        plot_kwargs, cbar_kwargs = update_plot_cbar_kwargs(
            default_plot_kwargs=default_plot_kwargs,
            default_cbar_kwargs=default_cbar_kwargs,
            user_plot_kwargs=user_plot_kwargs,
        )
        assert plot_kwargs["cmap"].N == 3

    def test_create_boundary_norm_from_levels_list(self, default_plot_kwargs, default_cbar_kwargs):
        """Test creating BoundaryNorm and resampling cmap based on 'levels' list in user_plot_kwargs."""
        user_plot_kwargs = {"cmap": plt.get_cmap("Spectral"), "levels": [0, 0.5, 1.0]}
        default_plot_kwargs["cmap"] = None  # this should also pass
        plot_kwargs, cbar_kwargs = update_plot_cbar_kwargs(
            default_plot_kwargs=default_plot_kwargs,
            default_cbar_kwargs=default_cbar_kwargs,
            user_plot_kwargs=user_plot_kwargs,
        )
        assert isinstance(plot_kwargs["norm"], BoundaryNorm)
        assert plot_kwargs["cmap"].N == 2  # Resampled to match number of boundaries - 1
        np.testing.assert_equal(plot_kwargs["norm"].boundaries, [0, 0.5, 1.0])

    def test_create_boundary_norm_from_levels_number(self, default_plot_kwargs, default_cbar_kwargs):
        """Test creating BoundaryNorm and resampling cmap based on a 'levels' number in user_plot_kwargs."""
        user_plot_kwargs = {"levels": 2, "vmin": 0, "vmax": 1}  # 3 levels linearly spaced between 0-1
        plot_kwargs, cbar_kwargs = update_plot_cbar_kwargs(
            default_plot_kwargs=default_plot_kwargs,
            default_cbar_kwargs=default_cbar_kwargs,
            user_plot_kwargs=user_plot_kwargs,
        )

        assert isinstance(plot_kwargs["norm"], BoundaryNorm)
        assert plot_kwargs["cmap"].N == 2  # Resampled to match number of boundaries - 1
        np.testing.assert_equal(plot_kwargs["norm"].boundaries, [0.0, 0.5, 1.0])

    def test_invalid_levels_user_kwargs(self, default_plot_kwargs, default_cbar_kwargs):
        """Test invalid user_kwargs together with the 'levels' argument."""
        # Assert raise an error if levels is a list and also vmin or max are specified
        user_plot_kwargs = {"levels": [0, 0.5, 1.0], "vmin": 0, "vmax": 1}
        with pytest.raises(ValueError):
            update_plot_cbar_kwargs(
                default_plot_kwargs=default_plot_kwargs,
                default_cbar_kwargs=default_cbar_kwargs,
                user_plot_kwargs=user_plot_kwargs,
            )

        # Assert raise an error if non-monotonic levels
        user_plot_kwargs = {"levels": [0, 1.0, 0.5]}
        with pytest.raises(ValueError):
            update_plot_cbar_kwargs(
                default_plot_kwargs=default_plot_kwargs,
                default_cbar_kwargs=default_cbar_kwargs,
                user_plot_kwargs=user_plot_kwargs,
            )

        # Assert raise an error if levels is an integer and vmin and max are not specified
        user_plot_kwargs = {"levels": 2}
        with pytest.raises(ValueError):
            update_plot_cbar_kwargs(
                default_plot_kwargs=default_plot_kwargs,
                default_cbar_kwargs=default_cbar_kwargs,
                user_plot_kwargs=user_plot_kwargs,
            )
        # Assert raise an error if 'levels' and 'norm' is specified
        user_plot_kwargs = {"levels": 2, "norm": Normalize(vmin=0, vmax=2)}
        with pytest.raises(ValueError):
            update_plot_cbar_kwargs(
                default_plot_kwargs=default_plot_kwargs,
                default_cbar_kwargs=default_cbar_kwargs,
                user_plot_kwargs=user_plot_kwargs,
            )

    def test_update_default_norm_using_vmin_vmax(self, default_plot_kwargs, default_cbar_kwargs):
        """Test updating default norm using vmin and vmax from user_plot_kwargs when norm not specified."""
        user_plot_kwargs = {"vmin": 0, "vmax": 2}
        plot_kwargs, cbar_kwargs = update_plot_cbar_kwargs(
            default_plot_kwargs=default_plot_kwargs,
            default_cbar_kwargs=default_cbar_kwargs,
            user_plot_kwargs=user_plot_kwargs,
        )
        assert plot_kwargs["norm"].vmin == 0
        assert plot_kwargs["norm"].vmax == 2

    def test_no_vmin_vmax_if_norm_specified(self, default_plot_kwargs, default_cbar_kwargs):
        """Ensure ValueError is raised if vmin/vmax specified alongside norm."""
        user_plot_kwargs = {"norm": Normalize(vmin=0, vmax=2), "vmin": 0, "vmax": 2}
        with pytest.raises(ValueError) as excinfo:
            update_plot_cbar_kwargs(default_plot_kwargs, default_cbar_kwargs, user_plot_kwargs=user_plot_kwargs)
        assert "If the 'norm' is specified, 'vmin' and 'vmax' must not be specified" in str(excinfo.value)

    def test_norm_incompatible_user_vmin_vmax(self):
        """Test if 'vmin' and 'vmax' are incompatible with the default 'norm', a Normalize norm is created."""
        default_plot_kwargs = {"cmap": plt.get_cmap("viridis"), "norm": BoundaryNorm(boundaries=[0, 0.5, 1], ncolors=2)}
        default_cbar_kwargs = {"ticks": [0, 1, 2], "ticklabels": ["A", "B", "C"]}
        user_plot_kwargs = {"vmin": 0, "vmax": 2}

        plot_kwargs, cbar_kwargs = update_plot_cbar_kwargs(
            default_plot_kwargs=default_plot_kwargs,
            default_cbar_kwargs=default_cbar_kwargs,
            user_plot_kwargs=user_plot_kwargs,
        )
        # Assert norm has changed to Normalize
        assert not isinstance(plot_kwargs["norm"], BoundaryNorm)
        assert isinstance(plot_kwargs["norm"], Normalize)
        # Assert norm vmin and vmax have been set
        assert plot_kwargs["norm"].vmin == 0
        assert plot_kwargs["norm"].vmax == 2
        # Assert ticks and ticklabels have been dropped (after norm change !)
        assert "ticks" not in cbar_kwargs
        assert "ticklabels" not in cbar_kwargs

        # Now check that user_cbar_kwargs are taken into account
        user_cbar_kwargs = {"ticks": [3, 4, 5, 6], "ticklabels": ["D", "E", "F", "G"]}
        plot_kwargs, cbar_kwargs = update_plot_cbar_kwargs(
            default_plot_kwargs=default_plot_kwargs,
            default_cbar_kwargs=default_cbar_kwargs,
            user_plot_kwargs=user_plot_kwargs,
            user_cbar_kwargs=user_cbar_kwargs,
        )
        assert not isinstance(plot_kwargs["norm"], BoundaryNorm)
        assert isinstance(plot_kwargs["norm"], Normalize)
        # Assert norm vmin and vmax have been set
        assert plot_kwargs["norm"].vmin == 0
        assert plot_kwargs["norm"].vmax == 2
        # Assert ticks and ticklabels are updated
        assert "ticks" in cbar_kwargs
        assert "ticklabels" in cbar_kwargs
        assert cbar_kwargs["ticks"] == [3, 4, 5, 6]
        assert cbar_kwargs["ticklabels"] == ["D", "E", "F", "G"]

    def test_valid_update_ticks_and_ticklabels(self):
        """Test valid updates of 'ticks' and 'ticklabels."""
        default_plot_kwargs = {"cmap": plt.get_cmap("viridis"), "norm": BoundaryNorm(boundaries=[0, 0.5, 1], ncolors=2)}
        default_cbar_kwargs = {"ticks": [0, 1, 2], "ticklabels": ["A", "B", "C"]}
        user_cbar_kwargs = {"ticks": [3, 4, 5, 6], "ticklabels": ["D", "E", "F", "G"]}
        plot_kwargs, cbar_kwargs = update_plot_cbar_kwargs(
            default_plot_kwargs=default_plot_kwargs,
            default_cbar_kwargs=default_cbar_kwargs,
            user_plot_kwargs={},
            user_cbar_kwargs=user_cbar_kwargs,
        )
        assert isinstance(plot_kwargs["norm"], BoundaryNorm)
        # Assert ticks and ticklabels are updated
        assert "ticks" in cbar_kwargs
        assert "ticklabels" in cbar_kwargs
        assert cbar_kwargs["ticks"] == [3, 4, 5, 6]
        assert cbar_kwargs["ticklabels"] == ["D", "E", "F", "G"]

    def test_invalid_update_ticks_and_ticklabels(self):
        """Test error is raised if 'vmin' and 'vmax' are not accepted by the default_plot_kwargs 'norm'."""
        default_plot_kwargs = {"cmap": plt.get_cmap("viridis"), "norm": BoundaryNorm(boundaries=[0, 0.5, 1], ncolors=2)}
        default_cbar_kwargs = {"ticks": [0, 1, 2], "ticklabels": ["A", "B", "C"]}

        # Test invalid user-ticks
        user_cbar_kwargs = {"ticks": [3, 4, 5, 6]}
        with pytest.raises(ValueError):
            update_plot_cbar_kwargs(
                default_plot_kwargs=default_plot_kwargs,
                default_cbar_kwargs=default_cbar_kwargs,
                user_plot_kwargs={},
                user_cbar_kwargs=user_cbar_kwargs,
            )
        # Test invalid user-ticklabels
        user_cbar_kwargs = {"ticklabels": ["D", "E", "F", "G"]}
        with pytest.raises(ValueError):
            update_plot_cbar_kwargs(
                default_plot_kwargs=default_plot_kwargs,
                default_cbar_kwargs=default_cbar_kwargs,
                user_plot_kwargs={},
                user_cbar_kwargs=user_cbar_kwargs,
            )

        # Test invalid user ticks and ticklabels length
        user_cbar_kwargs = {"ticks": [3, 4], "ticklabels": ["D", "E", "F", "G"]}
        with pytest.raises(ValueError):
            update_plot_cbar_kwargs(
                default_plot_kwargs=default_plot_kwargs,
                default_cbar_kwargs=default_cbar_kwargs,
                user_plot_kwargs={},
                user_cbar_kwargs=user_cbar_kwargs,
            )

    def test_extend_copied_to_user_cbar_kwargs_if_not_specified(self, default_plot_kwargs, default_cbar_kwargs):
        """Test 'extend' in user_plot_kwargs is copied to user_cbar_kwargs if not already specified."""
        user_plot_kwargs = {"extend": "both"}
        plot_kwargs, cbar_kwargs = update_plot_cbar_kwargs(
            default_plot_kwargs=default_plot_kwargs,
            default_cbar_kwargs=default_cbar_kwargs,
            user_plot_kwargs=user_plot_kwargs,
        )
        assert cbar_kwargs["extend"] == "both"


# get_plot_kwargs(name=None, user_plot_kwargs={}, user_cbar_kwargs={})
