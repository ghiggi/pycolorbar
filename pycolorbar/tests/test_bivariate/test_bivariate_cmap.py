import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
import xarray as xr
from matplotlib.colors import BoundaryNorm, Normalize
from shapely.geometry import Point

from pycolorbar.bivariate.cmap import BivariateColormap


@pytest.fixture
def bivariate_cmap():
    """Fixture creating a small 3x3 bivariate colormap."""
    cmap = BivariateColormap.from_name(name="stevens.bluered", n=3)
    return cmap


def check_mapped_output_shape_and_range(mapped, x_shape):
    """Helper assertion function to check shape and RGBA values."""
    # Check shape
    expected_shape = (*x_shape, 4)
    assert mapped.shape == expected_shape, f"Expected shape {expected_shape} but got {mapped.shape}"
    # Check values are in [0..1] (ignoring NaN if present)
    mapped_min = np.nanmin(mapped)
    mapped_max = np.nanmax(mapped)
    assert mapped_min >= 0.0, f"Mapped values below 0: min={mapped_min}"
    assert mapped_max <= 1.0, f"Mapped values above 1: max={mapped_max}"


def test_mapping_order(bivariate_cmap):
    norm_x = Normalize(vmin=0, vmax=1)
    norm_y = Normalize(vmin=0, vmax=1)
    # Test mapping order on y axis
    np.testing.assert_allclose(bivariate_cmap(0, 0, norm_x=norm_x, norm_y=norm_y), bivariate_cmap.rgba_array[-1, 0, :])
    np.testing.assert_allclose(bivariate_cmap(0, 1, norm_x=norm_x, norm_y=norm_y), bivariate_cmap.rgba_array[0, 0, :])
    # Test mapping order on x axis
    np.testing.assert_allclose(bivariate_cmap(0, 1, norm_x=norm_x, norm_y=norm_y), bivariate_cmap.rgba_array[0, 0, :])
    np.testing.assert_allclose(bivariate_cmap(1, 1, norm_x=norm_x, norm_y=norm_y), bivariate_cmap.rgba_array[0, -1, :])


def test_numpy_no_norm(bivariate_cmap):
    # Create some sample data
    x = np.array([0, 1, 2, 3, 4], dtype=float)
    y = np.array([30, 20, 15, 10, 5], dtype=float)

    # Call the bivariate colormap
    mapped = bivariate_cmap(x, y)
    check_mapped_output_shape_and_range(mapped, x.shape)

    # Check correct value
    np.testing.assert_allclose(bivariate_cmap.rgba_array[0, 0], mapped[0])
    np.testing.assert_allclose(bivariate_cmap.rgba_array[-1, -1], mapped[-1])


def test_numpy_with_normalize_clip_false(bivariate_cmap):
    # Create sample data
    x = np.array([-1, 0, 2, np.nan, 5, 6])
    y = np.array([10, 10, 12, 2, 15, 16])

    # Create normalizers
    norm_x = Normalize(vmin=0, vmax=5)  # clip=False by default !
    norm_y = Normalize(vmin=10, vmax=15)

    # Call
    mapped = bivariate_cmap(x, y, norm_x=norm_x, norm_y=norm_y)

    # Check shape and range
    check_mapped_output_shape_and_range(mapped, x.shape)

    # Check bad color outside valid range
    np.testing.assert_allclose(mapped[0], bivariate_cmap._bad)
    np.testing.assert_allclose(mapped[-1], bivariate_cmap._bad)
    np.testing.assert_allclose(mapped[3], bivariate_cmap._bad)  # NaN input data


def test_numpy_with_normalize_clip_true(bivariate_cmap):
    # Create sample data
    x = np.array([-1, 0, 2, 5, 6])
    y = np.array([10, 10, 12, 15, 16])

    # Create normalizers
    norm_x = Normalize(vmin=0, vmax=5, clip=True)
    norm_y = Normalize(vmin=10, vmax=15, clip=True)

    # Call
    mapped = bivariate_cmap(x, y, norm_x=norm_x, norm_y=norm_y)

    # Check shape and range
    check_mapped_output_shape_and_range(mapped, x.shape)

    # Check no NaN outside valid range
    np.testing.assert_allclose(mapped[0], mapped[1])
    np.testing.assert_allclose(mapped[-1], mapped[-2])


def test_numpy_with_boundarynorm(bivariate_cmap):
    # Suppose our data ranges in [0..10], and we want 3 bins: [0-3, 3-6, 6-10]
    x = np.array([0, 1, 2, 6, 7, 9], dtype=float)
    y = np.array([1, 3, 5, 7, 9, 10], dtype=float)

    norm_x = BoundaryNorm(boundaries=[0, 3, 6, 10], ncolors=3)
    norm_y = BoundaryNorm(boundaries=[0, 2, 8, 10], ncolors=3)

    mapped = bivariate_cmap(x, y, norm_x=norm_x, norm_y=norm_y)
    check_mapped_output_shape_and_range(mapped, x.shape)


def test_pandas_series_numeric(bivariate_cmap):
    x = pd.Series([0.0, 5.0, 10.0, np.nan])
    y = pd.Series([2.5, 2.5, 7.5, 10.0])

    mapped = bivariate_cmap(x, y)
    check_mapped_output_shape_and_range(mapped, x.shape)


def test_pandas_series_categorical(bivariate_cmap):
    cats_x = pd.Series(["A", "B", "C", "C"], dtype="category")
    cats_y = pd.Series(["C", "D", "D", "E"], dtype="category")

    # This should automatically map categories to [0..1].
    mapped = bivariate_cmap(cats_x, cats_y)
    check_mapped_output_shape_and_range(mapped, cats_x.shape)

    # Check correct value
    np.testing.assert_allclose(bivariate_cmap.rgba_array[-1, 0], mapped[0])
    np.testing.assert_allclose(bivariate_cmap.rgba_array[0, -1], mapped[-1])


def test_geopandas_series(bivariate_cmap):
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
    check_mapped_output_shape_and_range(mapped, gdf["var1"].shape)


def test_xarray_dataarray(bivariate_cmap):
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


def test_xarray_dataarray_broadcast(bivariate_cmap):
    # Create two xr.DataArrays with dimension to be broadcasted
    x = xr.DataArray([0, 1, 2, 3], dims=("points",))
    y = xr.DataArray([[0, 10, 20, 30], [30, 20, 10, 0]], dims=("realizations", "points"))
    x_broadcasted, y_broadcasted = xr.broadcast(x, y)

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
