import math
import rasterio
import rasterio.warp
import numpy as np
import time
import pyproj
import mercantile
import hf_hydrodata as hf
import affine

def create_tile_from_tiff(variable, dataset, date_start, x, y, z, target_resolution):
    """Create tile and return numpy array size (256, 256) to return as tile response."""
    start = time.time()
    tile_minx, tile_miny, tile_maxx, tile_maxy = get_tile_bounds(x, y, z)
    grid = get_dc_grid(variable, dataset, z)
    west, south, east, north = get_tile_latlon(x, y, z)
    grid_bounds = hf.to_ij(grid, south, west, north, east)
    grid_crs, origin, resolution = get_grid_crs(grid)

    # Get Subgrid
    padding = 10
    grid_bounds[0] = grid_bounds[0] - padding
    grid_bounds[1] = grid_bounds[1] - padding
    grid_bounds[2] = grid_bounds[2] + padding
    grid_bounds[3] = grid_bounds[3] + padding
    subgrid = hf.get_gridded_data(dataset=dataset, variable=variable, grid=grid, grid_bounds=grid_bounds, date_start=date_start)
    if len(subgrid.shape) == 4:
        subgrid = subgrid[0, 0, :, :]
    elif len(subgrid.shape) == 3:
        subgrid = subgrid[0, :, :]
    subgrid = np.flip(subgrid, 0)        
    print("Tile x/y/z", x, y, z)
    print("Variable/Dataset", variable, dataset)
    print("Target resolution", target_resolution)
    print("GRID", grid)
    print("Grid Bounds", grid_bounds)
    print("Subgrid shape", subgrid.shape)
    print_data(subgrid, x_incr=64, y_incr=64)
    # Create crs and transforms
    dst_crs = "EPSG:3857"
    src_crs = pyproj.CRS.from_proj4(grid_crs)
    dst_array = np.zeros((target_resolution, target_resolution), dtype="float32")
    src_transform = get_src_transform(grid, grid_bounds)
    dst_transform = rasterio.transform.from_bounds(tile_minx, tile_miny, tile_maxx, tile_maxy, width=target_resolution, height=target_resolution)

    print("dst_transform", dst_transform)
    print("src_transform", src_transform)
    # Reproject subset
    rasterio.warp.reproject(
        source=subgrid,
        destination=dst_array,
        src_transform=src_transform,
        src_crs=src_crs,
        src_nodata=0,
        dst_transform=dst_transform,
        dst_crs=dst_crs,
        resampling=rasterio.warp.Resampling.nearest
    )
    duration = time.time() - start
    print("duration", round(duration, 2))
    print("FINAL ANSWER")
    print_data(dst_array, x_incr = 64, y_incr=64)

    return dst_array



def get_src_transform(grid, grid_bounds):
    """Construct the src_transform between the pixel of the grid_bounds to the LCC meters"""
    print("COMPUTE GRID", grid)
    grid_obj = hf.get_table_row("grid", id=grid)
    print(grid_obj)
    lcc_origin = grid_obj.get("origin")
    origin_x = lcc_origin[0]
    origin_y = lcc_origin[1]
    print("GRID ORIGIN", origin_x, origin_y)
    px = grid_bounds[0]
    py = grid_bounds[1]
    pixel_resolution = float(grid_obj.get("resolution_meters"))
    print("PIXEL RESOLUTION", pixel_resolution)
    top_left_x = px * pixel_resolution - origin_x
    top_left_y = py * pixel_resolution - origin_y
    #src_transform = affine.Affine(pixel_resolution, 0, -origin_x, 0, pixel_resolution, -origin_y)
    src_transform = affine.Affine(pixel_resolution, 0, px * pixel_resolution + origin_x, 0, pixel_resolution, py * pixel_resolution + origin_y)
    #src_transform = affine.Affine(pixel_resolution, 0, 0, 0, pixel_resolution, 0)
    return src_transform


def get_dc_grid(variable, dataset, z):
    """
    Get the path and grid from data catalog.
    Parameters:
        variable:   variable of data catalog
        dataset:    dataset name of data catalog
        z:          zoom level of visualization
    Returns:
        grid of the data catalog entry
    """
    entries = hf.get_catalog_entries(dataset=dataset, variable=variable)
    for entry in entries:
        grid = entry.get("grid")
        if "30" in grid:
            if z > 12:
                return grid
        elif "100" in grid:
            if z >=8 and z <= 12:
                return grid
        elif z < 8:
            return grid
    raise ValueError("No data catalog entry found")

def get_grid_crs(grid):
    grid_obj = hf.get_table_row("grid", id=grid)
    return grid_obj.get("crs"), grid_obj.get("origin"), float(grid_obj.get("resolution_meters"))

def get_tile_latlon(x, y, z):
    """
    Get the lat/lon bounds of the mercator tile.
    Returns:
        latlon_west, latlon_south, latlon_east, latlon_north
    """
    bounds = mercantile.bounds(x, y, z)
    return bounds.west, bounds.south, bounds.east, bounds.north

def get_tile_bounds(x, y, z):
    """Convert XYZ tile tile bounds in meters in EPSG:3857 coordinates."""
    tile = mercantile.Tile(x, y, z)
    xy_bounds = mercantile.xy_bounds(tile)
    return xy_bounds.left, xy_bounds.bottom, xy_bounds.right, xy_bounds.top

def print_data(subgrid, x_incr=64, y_incr=64):
    for row in range(0, subgrid.shape[0], y_incr):
        for col in range(0, subgrid.shape[1], x_incr):
            val = subgrid[row, col]
            print(f"[{row},{col}] = {val}")
        print(f"[{row}, {subgrid.shape[1]-1}] = {subgrid[row, subgrid.shape[1]-1]}")
    print(f"[{subgrid.shape[0]-1}, 0] = {subgrid[subgrid.shape[0]-1,0]}")
    print(f"[{subgrid.shape[0]-1}, {subgrid.shape[1]-1}] = {subgrid[subgrid.shape[0]-1,subgrid.shape[1]-1]}")


def test_tile():
    variable = "soil_moisture"
    dataset = "conus2_current_conditions"
    date_start="2025-08-21"
    x = 6
    y = 12
    z = 5
    x = 56899
    y = 103089
    z = 18
    x = 28
    y = 50
    z = 7
    #x = 56899
    #y = 103089
    #z = 18    
    target_resolution = 128
    data = create_tile_from_tiff(variable, dataset, date_start, x, y, z, target_resolution)
    # Bot left 6/12/5 WTD is 772,922 WTD=0.07 Lat/lng 31.7, -112 to Top, Right 40.7, -101.2
    # Above Amarillo Texas, West of Dalaas and Tulsa and Oklahoma City
    # Top right stream pair of second to highest spurs of river
    # Bot left 56899/103089/18 WTD is 100234,53280 WTD=27.421 Lat/lng 35.83338, -101.861093 to Top, Right 35.83448, -101.859741

test_tile()