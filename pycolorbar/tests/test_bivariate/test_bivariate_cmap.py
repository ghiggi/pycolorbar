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
"""Test BivariateColormap functionalities."""
import geopandas as gpd
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest
import xarray as xr
from matplotlib.colors import BoundaryNorm, Normalize
from shapely.geometry import Point

from pycolorbar.bivariate.cmap import BivariateColormap, BivariateTransparencyColormap, available_bivariate_colormaps
from pycolorbar.norm import CategorizeNorm, CategoryNorm


class TestBivariateColormapMapping:
    """Test value mapping based on different Norm and objects."""

    @pytest.fixture
    def bivariate_cmap(self):
        """Fixture creating a small 3x3 bivariate colormap."""
        cmap = BivariateColormap.from_name(name="stevens.bluered", n=3)
        return cmap

    def check_mapped_output_shape_and_range(self, mapped, x_shape):
        """Helper assertion function to check shape and RGBA values."""
        # Check shape
        expected_shape = (*x_shape, 4)
        assert mapped.shape == expected_shape, f"Expected shape {expected_shape} but got {mapped.shape}"
        # Check values are in [0..1] (ignoring NaN if present)
        mapped_min = np.nanmin(mapped)
        mapped_max = np.nanmax(mapped)
        assert mapped_min >= 0.0, f"Mapped values below 0: min={mapped_min}"
        assert mapped_max <= 1.0, f"Mapped values above 1: max={mapped_max}"

    def test_mapping_order(self, bivariate_cmap):
        """Test how data are mapped onto the colormap."""
        norm_x = Normalize(vmin=0, vmax=1)
        norm_y = Normalize(vmin=0, vmax=1)
        # Test mapping order on y axis
        np.testing.assert_allclose(
            bivariate_cmap(0, 0, norm_x=norm_x, norm_y=norm_y),
            bivariate_cmap.rgba_array[-1, 0, :],
        )
        np.testing.assert_allclose(
            bivariate_cmap(0, 1, norm_x=norm_x, norm_y=norm_y),
            bivariate_cmap.rgba_array[0, 0, :],
        )
        # Test mapping order on x axis
        np.testing.assert_allclose(
            bivariate_cmap(0, 1, norm_x=norm_x, norm_y=norm_y),
            bivariate_cmap.rgba_array[0, 0, :],
        )
        np.testing.assert_allclose(
            bivariate_cmap(1, 1, norm_x=norm_x, norm_y=norm_y),
            bivariate_cmap.rgba_array[0, -1, :],
        )

    def test_numpy_no_norm(self, bivariate_cmap):
        """Test mapping numpy arrays without normalizations."""
        # Create some sample data
        x = np.array([0, 1, 2, 3, 4], dtype=float)
        y = np.array([30, 20, 15, 10, 5], dtype=float)

        # Call the bivariate colormap
        mapped = bivariate_cmap(x, y)
        self.check_mapped_output_shape_and_range(mapped, x.shape)

        # Check correct value
        np.testing.assert_allclose(bivariate_cmap.rgba_array[0, 0], mapped[0])
        np.testing.assert_allclose(bivariate_cmap.rgba_array[-1, -1], mapped[-1])

    def test_all_nan_values(self, bivariate_cmap):
        x = np.ones(4) * np.nan
        y = np.ones(4) * np.nan
        bad_color = (1, 1, 1, 0)
        bivariate_cmap.set_bad(bad_color)
        mapped = bivariate_cmap(x, y, norm_x=Normalize(0, 1), norm_y=Normalize(0, 1))

        assert mapped.shape == (4, 4)
        assert np.all(mapped == bad_color)

    def test_no_norm_and_single_value_case(self, bivariate_cmap):
        """Test raise error if norm not specified and all values are the same."""
        x = np.array([0, 0, 0], dtype=float)
        y = np.array([30, 20, 15, 10, 5], dtype=float)
        with pytest.raises(ValueError):
            bivariate_cmap(x, y)

    def test_different_types(self, bivariate_cmap):
        """Test raise error when input types are different."""
        x = np.array([1, 2, 3], dtype=float)
        y = [1, 2, 3]
        with pytest.raises(TypeError):
            bivariate_cmap(x, y)

    def test_different_shapes(self, bivariate_cmap):
        """Test raise error when input types are different."""
        x = np.array([1, 2, 3], dtype=float)
        y = np.array([1, 2], dtype=float)
        with pytest.raises(ValueError):
            bivariate_cmap(x, y)

    def test_numpy_with_normalize_clip_false(self, bivariate_cmap):
        """Test mapping with Normalize(clip=False)."""
        # Create sample data
        x = np.array([-1, 0, 2, np.nan, 5, 6])
        y = np.array([10, 10, 12, 2, 15, 16])

        # Create normalizers
        norm_x = Normalize(vmin=0, vmax=5)  # clip=False by default !
        norm_y = Normalize(vmin=10, vmax=15)

        # Call
        mapped = bivariate_cmap(x, y, norm_x=norm_x, norm_y=norm_y)

        # Check shape and range
        self.check_mapped_output_shape_and_range(mapped, x.shape)

        # Check bad color outside valid range
        np.testing.assert_allclose(mapped[0], bivariate_cmap._bad)
        np.testing.assert_allclose(mapped[-1], bivariate_cmap._bad)
        np.testing.assert_allclose(mapped[3], bivariate_cmap._bad)  # NaN input data

    def test_numpy_with_normalize_clip_true(self, bivariate_cmap):
        """Test mapping with Normalize(clip=True)."""
        # Create sample data
        x = np.array([-1, 0, 2, 5, 6])
        y = np.array([10, 10, 12, 15, 16])

        # Create normalizers
        norm_x = Normalize(vmin=0, vmax=5, clip=True)
        norm_y = Normalize(vmin=10, vmax=15, clip=True)

        # Call
        mapped = bivariate_cmap(x, y, norm_x=norm_x, norm_y=norm_y)

        # Check shape and range
        self.check_mapped_output_shape_and_range(mapped, x.shape)

        # Check no NaN outside valid range
        np.testing.assert_allclose(mapped[0], mapped[1])
        np.testing.assert_allclose(mapped[-1], mapped[-2])

    def test_numpy_with_boundarynorm(self, bivariate_cmap):
        """Test mapping with BoundaryNorm."""
        # Suppose our data ranges in [0..10], and we want 3 bins: [0-3, 3-6, 6-10]
        x = np.array([0, 1, 2, 6, 7, 9], dtype=float)
        y = np.array([1, 3, 5, 7, 9, 10], dtype=float)

        norm_x = BoundaryNorm(boundaries=[0, 3, 6, 10], ncolors=3)
        norm_y = BoundaryNorm(boundaries=[0, 2, 8, 10], ncolors=3)

        mapped = bivariate_cmap(x, y, norm_x=norm_x, norm_y=norm_y)
        self.check_mapped_output_shape_and_range(mapped, x.shape)

    def test_n_categories_disagree_with_cmap_n_colors(self, bivariate_cmap):
        """Test raise error if number categories differ from number of colors."""
        x = np.array([0, 1, 2, 6, 7, 9], dtype=float)
        y = np.array([1, 3, 5, 7, 9, 10], dtype=float)

        norm_x = BoundaryNorm(boundaries=[0, 3, 6, 10, 11], ncolors=4)
        norm_y = BoundaryNorm(boundaries=[0, 2, 8, 10, 11], ncolors=4)

        with pytest.raises(ValueError):
            bivariate_cmap(x, y, norm_x=norm_x, norm_y=None)

        with pytest.raises(ValueError):
            bivariate_cmap(x, y, norm_x=None, norm_y=norm_y)

    def test_pandas_series_numeric(self, bivariate_cmap):
        """Test mapping numeric Pandas Series."""
        x = pd.Series([0.0, 5.0, 10.0, np.nan])
        y = pd.Series([2.5, 2.5, 7.5, 10.0])

        mapped = bivariate_cmap(x, y)
        self.check_mapped_output_shape_and_range(mapped, x.shape)

        # Check raise error if different shape
        with pytest.raises(ValueError):
            bivariate_cmap(x, y[1:])

    def test_pandas_series_categorical(self, bivariate_cmap):
        """Test mapping categorical Pandas Series."""
        cats_x = pd.Series(["A", "B", "C"], dtype="category")  # 3 categories
        cats_y = pd.Series(["C", "D", "E"], dtype="category")  # 3 categories

        # This should automatically map categories to [0..1].
        mapped = bivariate_cmap(cats_x, cats_y)
        self.check_mapped_output_shape_and_range(mapped, cats_x.shape)

        # Check correct value
        np.testing.assert_allclose(bivariate_cmap.rgba_array[-1, 0], mapped[0])
        np.testing.assert_allclose(bivariate_cmap.rgba_array[0, -1], mapped[-1])

    def test_pandas_series_categorical_disagree_n_colors(self, bivariate_cmap):
        """Test mapping categorical Pandas Series."""
        series_numeric = pd.Series([1, 2, 3, 4])
        series_categorical = pd.Series(["C", "D", "E", "F"], dtype="category")  # 4 categories

        # This should automatically map categories to [0..1].
        with pytest.raises(ValueError):
            bivariate_cmap(x=series_numeric, y=series_categorical)
        with pytest.raises(ValueError):
            bivariate_cmap(x=series_categorical, y=series_numeric)

    def test_geopandas_series(self, bivariate_cmap):
        """Test mapping values from a GeoDataFrame."""
        # Build the GeoDataFrame
        var1 = [0, 2, 4, 6, 8]
        var2 = [3.2, 4.5, 5.5, 7.1, 10.2]
        geoms = [Point(i, i + 0.5) for i in range(5)]
        gdf = gpd.GeoDataFrame(
            {
                "var1": var1,
                "var2": var2,
                "geometry": geoms,
            },
        )

        mapped = bivariate_cmap(gdf["var1"], gdf["var2"])
        self.check_mapped_output_shape_and_range(mapped, gdf["var1"].shape)

    def test_xarray_dataarray(self, bivariate_cmap):
        """Test mapping xarray DataArray dimensioned."""
        # Create two xr.DataArrays with same shape
        x = xr.DataArray([0, 1, 2, 3], dims=("points",))
        y = xr.DataArray([10, 20, 10, 0], dims=("points",))

        mapped = bivariate_cmap(x, y)

        # For xarray, the shape will be points + ("rgba",)
        assert mapped.dims == ("points", "rgba")
        assert mapped.shape == (4, 4)

        # Check range in [0..1]
        mapped_min = float(mapped.min())
        mapped_max = float(mapped.max())
        assert mapped_min >= 0.0
        assert mapped_max <= 1.0

    def test_xarray_dataarray_broadcast(self, bivariate_cmap):
        """Test mapping xarray DataArrays requiring dimension broadcasting."""
        # Create two xr.DataArrays with dimension to be broadcasted
        x = xr.DataArray([0, 1, 2, 3], dims=("points",))
        y = xr.DataArray([[0, 10, 20, 30], [30, 20, 10, 0]], dims=("realizations", "points"))

        # x_broadcasted, y_broadcasted = xr.broadcast(x, y)

        # Map colors
        mapped = bivariate_cmap(x, y)

        # For xarray, the shape will be points + ("rgba",)
        assert mapped.dims == ("points", "realizations", "rgba")
        assert mapped.shape == (4, 2, 4)

        # Check range in [0..1]
        mapped_min = float(mapped.min())
        mapped_max = float(mapped.max())
        assert mapped_min >= 0.0
        assert mapped_max <= 1.0


class TestBivariateColormapCreation:

    def test_from_name_valid(self):
        """Test from_name works for a valid bivariate colormap name."""
        cmap = BivariateColormap.from_name("stevens.bluered", n=3)
        assert cmap.rgba_array.shape == (3, 3, 4)

    @pytest.mark.parametrize("name", available_bivariate_colormaps())
    def test_predfined_colormaps(self, name):
        """Test creation of all available bivariate colormaps."""
        cmap = BivariateColormap.from_name(name, n=3)
        assert cmap.rgba_array.shape == (3, 3, 4)

    def test_from_name_invalid(self):
        """Test from_name raises ValueError when a name is invalid."""
        with pytest.raises(ValueError):
            BivariateColormap.from_name("nonexistent_cmap", n=3)

        with pytest.raises(TypeError):
            BivariateColormap.from_name(1, n=3)

    def test_from_name_invalid_n(self):
        """Test from_name raises ValueError when n is < 2."""
        with pytest.raises(ValueError):
            BivariateColormap.from_name("stevens.bluered", n=1)
        with pytest.raises(ValueError):
            BivariateColormap.from_name("stevens.bluered", n=(2, 1))
        # Case with n=None
        with pytest.raises(ValueError):
            BivariateColormap.from_name("stevens.bluered", n=None)

    def test_from_colors(self):
        """Test from_colors method."""
        # Case 4
        cmap = BivariateColormap.from_colors(["red", "green", "blue", "yellow"], n=3)
        assert cmap.rgba_array.shape == (3, 3, 4)

        cmap1 = BivariateColormap.from_corners(["red", "green", "blue", "yellow"], n=3)
        assert cmap == cmap1

        # Case 5: Check black is assigned to center point
        cmap = BivariateColormap.from_colors(["red", "green", "blue", "yellow", "black"], n=3)
        assert cmap.rgba_array.shape == (3, 3, 4)
        np.testing.assert_allclose(cmap.rgba_array[1, 1, :], (0, 0, 0, 1))

    def test_from_colors_invalid(self):
        """Test from_colors raises ValueError when the number of color is invalid."""
        with pytest.raises(ValueError):
            BivariateColormap.from_colors(["red"], n=3)

    def test_from_cmaps(self):
        """Test from_cmaps method."""
        cmap = BivariateColormap.from_cmaps("Blues", "Reds", n=3)
        assert cmap.rgba_array.shape == (3, 3, 4)


class TestBivariateTransparencyColormap:

    def test_creation(self):
        """Test creation of BivariateTransparencyColormap."""
        cmap = BivariateTransparencyColormap(cmap="Blues", alpha_min=0.2, alpha_max=1, n=5)
        assert cmap.rgba_array.shape == (5, 5, 4)
        np.testing.assert_allclose(cmap.rgba_array[:, 0, 3], np.array([1.0, 0.8, 0.6, 0.4, 0.2]))


def test_equality():
    """Test BivariateColormap equality."""
    cmap1 = BivariateColormap.from_name("stevens.bluered", n=3)
    cmap2 = BivariateColormap.from_name("stevens.bluered", n=3)
    cmap3 = cmap2.copy()
    cmap3.set_bad("black")
    assert cmap1 == cmap2
    assert cmap2 != cmap3
    assert cmap1 != 1  # other object


def test_slicing():
    """Test __getitem__ method."""
    cmap = BivariateColormap.from_name("stevens.bluered", n=10)

    # Accepted
    cmap_sliced = cmap[slice(0, 5), slice(0, 4)]
    cmap_sliced1 = cmap[0:5, 0:4]
    assert cmap_sliced == cmap_sliced1
    assert isinstance(cmap_sliced, BivariateColormap)

    # Not accepted
    # - Need getting at least 2 elements per dimensions
    with pytest.raises(ValueError):
        cmap[0, 0]

    with pytest.raises(ValueError):
        cmap[slice(0, 2), slice(0, 1)]

    with pytest.raises(ValueError):
        cmap[slice(0, 1), slice(0, 2)]

    # Slicing on 2 dimensions required
    with pytest.raises(ValueError):
        cmap[0]

    with pytest.raises(ValueError):
        cmap[slice(0, 5)]

    # Only two slices are allowed
    with pytest.raises(ValueError):
        cmap[slice(0, 5), slice(0, 4), slice(0, 2)]


def test_setitem():
    """Test __setitem__ method."""
    cmap = BivariateColormap.from_name("stevens.bluered", n=3)
    cmap[0, 0] = (1.0, 0.5, 0.5, 1.0)
    assert np.allclose(cmap.rgba_array[0, 0], (1.0, 0.5, 0.5, 1.0))


def test_adapt_interval():
    """Test adapt_interval method."""
    cmap = BivariateColormap.from_name("stevens.bluered", n=10)
    # Check case where do not subset
    np.testing.assert_allclose(cmap.adapt_interval().rgba_array, cmap.rgba_array)
    # Check subsetting case on x and y
    assert cmap.adapt_interval(interval_x=(0, 0.5)).shape == (10, 5, 4)
    assert cmap.adapt_interval(interval_y=(0, 0.5)).shape == (5, 10, 4)
    assert cmap.adapt_interval(interval_x=(0, 0.2), interval_y=(0, 0.5)).shape == (5, 2, 4)
    # Check invalid interval
    with pytest.raises(ValueError):
        cmap.adapt_interval(interval_x=(-1, 0.5))
    with pytest.raises(ValueError):
        cmap.adapt_interval(interval_x=(0.4, 0.2))
    # Raise error if slicing leads to less than 2 colors
    with pytest.raises(ValueError):
        cmap.adapt_interval(interval_x=(0.1, 0.2))


def test_set_bad():
    """Test set_bad method."""
    cmap = BivariateColormap.from_name("stevens.bluered", n=3)
    cmap.set_bad((0, 0, 0, 0.5))
    assert np.allclose(cmap._bad, (0, 0, 0, 0.5))


def test_set_alpha():
    """Test set_alpha method."""
    cmap = BivariateColormap.from_name("stevens.bluered", n=3)
    cmap.set_alpha(0.7)
    # Check any pixel for alpha adjustment
    assert np.allclose(cmap.rgba_array[..., 3], 0.7)


def test_change_luminance_gradient():
    """Test change_luminance_gradient method."""
    cmap = BivariateColormap.from_name("stevens.bluered", n=3)
    cmap.change_luminance_gradient(1.2)
    # No exception check, minimal pass


def test_rot90():
    """Test rot90 method."""
    cmap = BivariateColormap.from_name("stevens.bluered", n=3)
    original = cmap.rgba_array.copy()
    new_cmap = cmap.rot90(clockwise=False)
    assert np.allclose(cmap.rgba_array, original)
    assert np.allclose(new_cmap.rgba_array, np.rot90(original))

    new_cmap = cmap.rot90()  # clockwise=True is default
    assert np.allclose(new_cmap.rgba_array, np.rot90(original, k=-1, axes=(0, 1)))


def test_rot180():
    """Test rot180 method."""
    cmap = BivariateColormap.from_name("stevens.bluered", n=3)
    original = cmap.rgba_array.copy()
    new_cmap = cmap.rot180(clockwise=False)
    assert np.allclose(cmap.rgba_array, original)
    assert np.allclose(new_cmap.rgba_array, np.rot90(np.rot90(original)))


def test_fliplr():
    """Test fliplr method."""
    cmap = BivariateColormap.from_name("stevens.bluered", n=3)
    original = cmap.rgba_array.copy()
    new_cmap = cmap.fliplr()
    assert np.allclose(cmap.rgba_array, original)
    assert np.allclose(new_cmap.rgba_array, np.fliplr(original))


def test_flipud():
    """Test flipud method."""
    cmap = BivariateColormap.from_name("stevens.bluered", n=3)
    original = cmap.rgba_array.copy()
    new_cmap = cmap.flipud()
    assert np.allclose(cmap.rgba_array, original)
    assert np.allclose(new_cmap.rgba_array, np.flipud(original))


def test_repr_methods():
    """Test repr methods."""
    cmap = BivariateColormap.from_name("stevens.bluered", n=3)
    cmap._repr_png_()  # assert bytes
    assert cmap._repr_html_().startswith("<div")


class TestBivariateColormapResampling:
    def test_downsampling(self):
        """Test resampled method for downsampling."""
        cmap = BivariateColormap.from_name("stevens.bluered", n=8)
        downsampled = cmap.resampled(n_x=3, n_y=5)
        assert downsampled.rgba_array.shape == (5, 3, 4)

    def test_oversampling(self):
        """Test resampled method for oversampling."""
        cmap = BivariateColormap.from_name("stevens.bluered", n=3)
        upsampled = cmap.resampled(n_x=8, n_y=5)
        assert upsampled.rgba_array.shape == (5, 8, 4)

    def test_only_one_dimension(self):
        """Test resampled method for oversampling."""
        cmap = BivariateColormap.from_name("stevens.bluered", n=3)
        assert cmap.resampled(n_x=8).shape == (3, 8, 4)
        assert cmap.resampled(n_y=8).shape == (8, 3, 4)


def test_plot():
    """Test plot method."""
    cmap = BivariateColormap.from_name("stevens.bluered", n=3)
    p = cmap.plot()
    assert isinstance(p, mpl.image.AxesImage)
    plt.close()


TEST_NORM_DICTS = {
    "Normalize": Normalize(0, 2),
    "BoundaryNorm": BoundaryNorm(boundaries=[0, 1, 2, 3], ncolors=3, clip=True),
    "Categorize": CategorizeNorm(boundaries=[0, 1, 2, 3], labels=["1", "2", "3"]),
    "CategoryNorm": CategoryNorm({0: "A", 1: "B", 2: "C"}),
}


@pytest.mark.parametrize("norm_type", list(TEST_NORM_DICTS))
def test_plot_colorbar(norm_type):
    """Test plot_colorbar method."""
    cmap = BivariateColormap.from_name("stevens.bluered", n=3)

    # Define norm
    norm = TEST_NORM_DICTS[norm_type]

    # Raise error if not mapped values first
    with pytest.raises(ValueError):
        p = cmap.plot_colorbar()

    # Map values
    img_rgb = cmap([0, 1, 2], [0, 1, 2], norm_x=norm, norm_y=norm)

    # Plot colorbar
    p = cmap.plot_colorbar(xlabel="X", ylabel="Y", title="TITLE")
    assert isinstance(p, mpl.image.AxesImage)
    plt.close()

    # Plot colorbar with inverted y axis
    p = cmap.plot_colorbar(origin="upper")
    assert isinstance(p, mpl.image.AxesImage)
    plt.close()

    # Plot colorbar to the sides of a plot ax
    fig, ax = plt.subplots()
    ax.imshow(img_rgb)
    p = cmap.plot_colorbar(origin="upper", ax=ax)
    assert isinstance(p, mpl.image.AxesImage)
    plt.close()

    # Plot colorbar into the specified cax
    fig, cax = plt.subplots()  # noqa: RUF059
    p = cmap.plot_colorbar(origin="upper", cax=cax)
    assert isinstance(p, mpl.image.AxesImage)
    plt.close()


def test_add_legend():
    """Test add_legend method."""
    cmap = BivariateColormap.from_name("stevens.bluered", n=3)

    # Map values
    img_rgb = cmap([0, 1, 2], [0, 1, 2])

    # Add legend to plot
    p = plt.imshow(img_rgb)  # dummy for creating an image
    p_cbar = cmap.add_legend(ax=p.axes)
    assert isinstance(p_cbar, mpl.image.AxesImage)
    plt.close()
