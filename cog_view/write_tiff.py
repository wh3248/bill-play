"""Function to write a tiff file with projection"""

import os
import rasterio
import pyproj
import hf_hydrodata as hf
import numpy as np

def main():
    data = np.zeros((10, 10))
    file_name = "foo.tiff"
    grid = "conus2"
    write_tiff_file(data, file_name, grid)
    print("Write tiff")

def write_tiff_file(
    data: np.ndarray, file_name, grid
):
    """
    Create a geotiff file contining the data and the projection for that data.
    """

    if os.getenv("PROJ_LIB"):
        # Remove this environment variable to allow creation of geotiff using rasterio
        del os.environ["PROJ_LIB"]
    import rasterio

    file_name_dir = os.path.dirname(file_name)
    if file_name_dir and not os.path.exists(file_name_dir):
        os.makedirs(file_name_dir, exist_ok=True)
    grid_data = hf.get_table_row("grid", id=grid)
    crs_string = grid_data["crs"]
    x_origin = grid_data["origin"][0]
    y_origin = grid_data["origin"][1]
    resolution_meters = grid_data["resolution_meters"]
    if not resolution_meters:
        raise ValueError(f"Grid {grid} does not have resolution_meters defined.")
    left_origin = x_origin
    top_origin = y_origin + grid_data["shape"][1] * 1000

    # Remove false northing and false easting from CRS since this is handled by transform origins
    pos = crs_string.find("+x_0=")
    crs_string = crs_string[0:pos] if pos > 0 else crs_string

    transform = rasterio.transform.from_origin(
        left_origin, top_origin, float(resolution_meters), float(resolution_meters)
    )
    if len(data.shape) == 3:
        data = data[0, :, :]
    elif len(data.shape) == 4:
        data = data[0, 0, :, :]
    data = np.flip(data, 0)
    dst_profile = {
        "driver": "GTiff",
        "dtype": np.float32,
        "nodata": 9999,
        "width": data.shape[1],
        "height": data.shape[0],
        "count": 1,
        "crs": pyproj.crs.CustomConstructorCRS(crs_string),
        "transform": transform,
        "tiled": True,
    }
    dst_profile["compress"] = "lzw"
    with rasterio.open(file_name, "w", **dst_profile) as dst:
        dst.write_band(1, data)

if __name__ == "__main__":
    main()