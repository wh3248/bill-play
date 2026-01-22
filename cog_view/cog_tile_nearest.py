
"""
Example created by copilot to generate a 256x256 mercantile tile from an x/y/z point
and using the URL to a COG hydrogen.princeton.edu/api/cog.
This takes about 24 seconds to produce the file info and makes four calls to the URL.
First call to stream the header and check if it is a tiff.
Second call to read bytes 0-16383 (Seems redundant since that seems same as first call).
Third call to read bytes 3637248-3653631. (16383 bytes)
Fourth call to read bytes (98303)
Note the 256x256 result should be 262144 bytes.
Time to do the cog URL reads of the 4 calls is less than 0.5 seconds
"""
import numpy as np
import mercantile
import rasterio
from affine import Affine
from rasterio.enums import Resampling
from rasterio.warp import reproject
import write_tiff
import time

def read_mercantile_tile(
    cog_url: str,
    x: int,
    y: int,
    z: int,
    *,
    tile_size: int = 256,
    nodata=None,
    add_vsicurl_prefix: bool = True,
    gdal_env: dict | None = None,
) -> np.ndarray:
    """
    Read one slippy-map tile (x, y, z) from a COG into a fixed tile_size x tile_size
    array in Web Mercator (EPSG:3857), using nearest-neighbor resampling.

    - Single band only
    - Categorical-safe: Resampling.nearest
    - No 'boundless' reads (avoids WarpedVRT boundless limitations)
    - Returns exactly (tile_size, tile_size)

    Parameters
    ----------
    cog_url : str
        HTTP(S) URL to a Cloud Optimized GeoTIFF. Server should support byte range requests.
    x, y, z : int
        Slippy-map tile coordinates.
    tile_size : int
        Output resolution in pixels (default 256).
    nodata : numeric or None
        Output nodata. If None, uses src.nodata. If still None, defaults to 0.
        (For categorical rasters, you may want to set this explicitly.)
    add_vsicurl_prefix : bool
        If True, prefixes URL with /vsicurl/ to encourage GDAL HTTP random access.
    gdal_env : dict or None
        Optional GDAL/Rasterio environment options. Example:
          {"GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR"}

    Returns
    -------
    tile : np.ndarray
        (tile_size, tile_size) array in EPSG:3857 matching the exact tile bounds.
    """
    # Web Mercator bounds of the tile in meters
    b = mercantile.xy_bounds(x, y, z)  # left, bottom, right, top in EPSG:3857
    left, bottom, right, top = b.left, b.bottom, b.right, b.top

    # Destination transform: maps pixel (col,row) -> (x,y) in EPSG:3857
    # Pixel width/height in meters
    xres = (right - left) / tile_size
    yres = (top - bottom) / tile_size

    # Note: y pixel size must be negative for north-up rasters (top -> bottom)
    dst_transform = Affine(xres, 0.0, left,
                           0.0, -yres, top)

    # Prefer /vsicurl/ for HTTP random access via GDAL virtual filesystem. [1](https://rasterio.readthedocs.io/en/stable/api/rasterio.io.html?highlight=boundless)
    src_path = cog_url
    if add_vsicurl_prefix and not cog_url.startswith("/vsicurl/"):
        src_path = f"/vsicurl/{cog_url}"

    # Sensible defaults for cloud reads; user can override via gdal_env
    env_opts = {
        "GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR",  # avoids directory listing on open
    }
    if gdal_env:
        env_opts.update(gdal_env)

    with rasterio.Env(**env_opts):
        with rasterio.open(src_path) as src:
            if src.count != 1:
                raise ValueError(f"Expected single-band raster, but src.count={src.count}")

            src_nodata = src.nodata
            dst_nodata = nodata if nodata is not None else src_nodata
            if dst_nodata is None:
                # Fallback; better to pass nodata explicitly for categorical data
                dst_nodata = 0

            # Allocate destination tile, prefilled with nodata.
            # This guarantees the output is always 256x256 even when tile extends beyond data.
            dst = np.full((tile_size, tile_size), dst_nodata, dtype=src.dtypes[0])

            # Reproject directly into the destination tile grid.
            # This avoids WarpedVRT boundless reads and still gives you an exact tile. [2](https://gdal.org/en/stable/user/virtual_file_systems.html)
            reproject(
                source=rasterio.band(src, 1),
                destination=dst,
                src_transform=src.transform,
                src_crs=src.crs,
                src_nodata=src_nodata,
                dst_transform=dst_transform,
                dst_crs="EPSG:3857",
                dst_nodata=dst_nodata,
                resampling=Resampling.nearest,  # categorical-safe
                init_dest_nodata=True,          # keep nodata fill where there is no coverage
            )

    return dst


if __name__ == "__main__":
    url = "https://hydrogen.princeton.edu/api/cog?dataset=ma_2025&email=wh3248@princeton.edu&pin=0000"
    x, y, z = 8972, 13791, 15

    start_timer = time.time()
    tile = read_mercantile_tile(url, x, y, z, nodata=255)  # set nodata explicitly if you can
    duration = time.time() - start_timer
    print("DURATION", duration)
    print(tile.shape, tile.dtype)
    write_tiff.write_tiff_file(tile, "tile.tiff", "conus2_wtd.30")
