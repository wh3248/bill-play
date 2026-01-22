
import numpy as np
import mercantile
import rasterio
from rasterio.vrt import WarpedVRT
from rasterio.windows import from_bounds
from rasterio.enums import Resampling


def read_cog_mercator_tile(
    cog_url: str,
    x: int,
    y: int,
    z: int,
    *,
    tile_size: int = 256,
    indexes=None,
    resampling: str = "bilinear",
    add_vsicurl_prefix: bool = True,
    nodata=None,
):
    """
    Read a single Web Mercator (EPSG:3857) slippy-map tile (x,y,z) from a COG URL
    into a 256x256 (tile_size x tile_size) array, using HTTP range requests.

    Parameters
    ----------
    cog_url : str
        URL to a Cloud Optimized GeoTIFF that supports HTTP Range requests.
    x, y, z : int
        Slippy-map tile coordinates.
    tile_size : int
        Output tile size. Default 256.
    indexes : int or list[int] or None
        Band index(es) to read (1-based). None reads all bands.
        Examples: indexes=1 (single band), indexes=[1,2,3] (RGB).
    resampling : str
        One of: "nearest", "bilinear", "cubic", "average", "lanczos".
    add_vsicurl_prefix : bool
        If True, prefixes the URL with /vsicurl/ for GDAL.
    nodata : number or None
        Override nodata value. If None, uses dataset nodata.

    Returns
    -------
    tile : np.ndarray
        Array shape:
          - (tile_size, tile_size) for single band
          - (bands, tile_size, tile_size) for multiple bands
    mask : np.ndarray
        Valid-data mask as uint8, shape (tile_size, tile_size) where 255=valid, 0=nodata.
    meta : dict
        Useful metadata about the read (bounds, crs, etc.).
    """
    resampling_map = {
        "nearest": Resampling.nearest,
        "bilinear": Resampling.bilinear,
        "cubic": Resampling.cubic,
        "average": Resampling.average,
        "lanczos": Resampling.lanczos,
    }
    if resampling not in resampling_map:
        raise ValueError(f"Unsupported resampling={resampling!r}. Choose from {list(resampling_map)}")

    # Mercantile tile bounds in Web Mercator meters (EPSG:3857)
    b = mercantile.xy_bounds(x, y, z)  # left, bottom, right, top in EPSG:3857
    left, bottom, right, top = b.left, b.bottom, b.right, b.top

    # Encourage GDAL to use its HTTP random-access virtual filesystem
    src_path = f"/vsicurl/{cog_url}" if add_vsicurl_prefix and not cog_url.startswith("/vsicurl/") else cog_url

    print(src_path)
    with rasterio.Env():
        with rasterio.open(src_path) as src:
            print("OPENED")
            # Virtual reprojection to Web Mercator
            vrt_nodata = nodata if nodata is not None else src.nodata
            with WarpedVRT(
                src,
                crs="EPSG:3857",
                resampling=resampling_map[resampling],
                nodata=vrt_nodata,
            ) as vrt:
                # Window that covers the requested tile bounds in EPSG:3857
                window = from_bounds(left, bottom, right, top, transform=vrt.transform)

                # Read into exactly tile_size x tile_size
                data = vrt.read(
                    indexes=indexes,                      # None => all bands
                    window=window,
                    out_shape=(
                        vrt.count if indexes is None else (1 if isinstance(indexes, int) else len(indexes)),
                        tile_size,
                        tile_size,
                    ),
                    resampling=resampling_map[resampling],
                    boundless=True,
                    fill_value=vrt_nodata,
                )

                # Build an 8-bit validity mask (255 valid, 0 nodata) using the VRT mask
                mask = vrt.read_masks(
                    1 if (indexes is None or isinstance(indexes, int)) else indexes[0],
                    window=window,
                    out_shape=(tile_size, tile_size),
                    resampling=Resampling.nearest,
                ).astype(np.uint8)

    # Squeeze single-band to (H, W) for convenience
    if data.shape[0] == 1:
        data = data[0]

    meta = {
        "x": x, "y": y, "z": z,
        "tile_bounds_3857": (left, bottom, right, top),
        "dst_crs": "EPSG:3857",
        "tile_size": tile_size,
        "resampling": resampling,
    }
    return data, mask, meta


if __name__ == "__main__":
    # Example:
    url = "https://hydrogen.princeton.edu/api/cog?email=wh3248@princeton.edu&pin=0000"  # must support Range requests
    x, y, z = 8972, 13791, 15

    tile, mask, meta = read_cog_mercator_tile(
        url, x, y, z,
        indexes=1,            # read band 1
        resampling="bilinear" # or "nearest" for categorical rasters
    )

    print(meta)
    print("tile shape:", tile.shape)
    print("mask unique values:", np.unique(mask))

