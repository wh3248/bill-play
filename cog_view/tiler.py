"""
    Use rio_tiler.io component to generate a 256x256 tile from a cog.
    This is very fast and works at all z levels.
    this main routine generates the file and writes it to a .tiff so it could be
    visualized with a jupter notebook.
"""
import numpy as np
from rio_tiler.io import COGReader
import rasterio
import write_tiff

def read_cog_xyz_tile(url: str, x: int, y: int, z: int, indexes=(1,2,3,4,5)):
    gdal_opts = {
        # reduce "extra" HTTP calls on open
        "GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR",  # prevents directory listing [3](https://developmentseed.org/titiler/advanced/performance_tuning/)
        "CPL_VSIL_CURL_ALLOWED_EXTENSIONS": ".tif,.tiff",  # restrict probing [3](https://developmentseed.org/titiler/advanced/performance_tuning/)

        # fewer HTTP requests by merging/multi-range
        "GDAL_HTTP_MERGE_CONSECUTIVE_RANGES": "YES",  # merge adjacent ranges [3](https://developmentseed.org/titiler/advanced/performance_tuning/)
        "GDAL_HTTP_MULTIRANGE": "YES",               # allow multi-range requests (if supported)

        # cache header + recently read chunks
        "VSI_CACHE": "TRUE",
        "VSI_CACHE_SIZE": str(128 * 1024 * 1024),  # 128MB
    }

    with COGReader(url) as cog:
        img = cog.tile(x, y, z, tilesize=256, indexes=indexes)
        # img.data is (bands, 256, 256)
        return img.data

x, y, z = 8973, 13791, 15
x, y, z = 280, 430,10
tile_size = 256
n_x = 4
n_y = 4
data = np.zeros((1, tile_size*n_y, tile_size*n_x))
for x1 in range(n_x):
    for y1 in range(n_y):
        arr = read_cog_xyz_tile(
            #url="https://hydrogen.princeton.edu/api/cog?email=wh3248@princeton.edu&pin=0000",
            url = "/hydrodata/temp/wh3248/cog/ma2025/wtd_mean_cog.tif",
            x=x+x1, y=y+y1, z=z,
            indexes=(1)
        )
        #arr = np.flip(arr, axis=2)
        target_x = tile_size * x1
        target_y = tile_size * y1
        data[0, target_y:target_y+tile_size:, target_x:target_x+tile_size] = arr
data = np.flip(data, axis=1)
print(data.shape)  # (5, 256, 256)
filename = "tiler.tiff"
write_tiff.write_tiff_file(data, filename, "conus2_wtd.30")
print(f"File '{filename}")
