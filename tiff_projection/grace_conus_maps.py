"""
    Utility to create maps between conus2 points and Grace coordinates.
"""

import sys
import os
import time
from typing import Tuple
import xarray as xr
import hf_hydrodata as hf


def main():
    """
    Main routine of program.
    Reads a GRACE NetCDF file from command line argument with a default.
    """

    file_path = get_file_path()
    if file_path is None:
        return

    # Get lat,lon dimensions from the GRACE NetCDF file
    lat_values, lon_values = get_latlon_ranges(file_path)

    # Create the map from CONUS2 to GRACE coordinates and time it
    start_time = time.time()

    # Create forward map
    conus_to_grace_map = map_conus2_to_nc_coords(lat_values, lon_values)
    # Create reverse map
    grace_to_conus_map = reverse_map(conus_to_grace_map)
    
    duration = time.time() - start_time

    # Print the size and examples of the map
    print(f"Size of tuple map for all conus2 points {len(conus_to_grace_map)} entries")
    print(f"Example grace tuple associated with conus (0,0) = {conus_to_grace_map.get((0,0))}")
    conus2_list = grace_to_conus_map.get((123,224))
    print("List of conus2 tuples associated with grace point (123,224)")
    print(conus2_list)

    # Print the time duration (should be about 3 minutes without using parallel threads)
    print(f"Duration {duration} seconds.")


def map_conus2_to_nc_coords(
    lat_values: list[float], lon_values: list[float]
) -> dict[Tuple]:
    """
    Create a map from conus2 coordinates to the nc_coordintes.
    Parameters:
        lat_values:     a list of the lat coordinate values from the NetCDF file.
        lon_values:     a list of the lon coordinate values from the NetCDF file.
    Returns:
        A python dict mapping conus tuples (x,y) to a single Grace tuple (x,y).
    """
    conus2_shape = [3256, 4222]
    x_size = conus2_shape[1]
    y_size = conus2_shape[0]
    conus_to_grace_map = {}
    for conus_x in range(0, x_size):
        for conus_y in range(0, y_size):
            # Get conus2 lat,lon point of a conus x, y point
            lat, lon = hf.to_latlon("conus2", conus_x, conus_y)

            # Get the Grace x, y point that corresponds to the lat, lon value
            (nc_x, nc_y) = get_nc_coord(lat, lon, lat_values, lon_values)

            conus_to_grace_map[(conus_x, conus_y)] = (nc_x, nc_y)

    return conus_to_grace_map

def reverse_map(conus_to_grace_map:list[list[Tuple[int, int]]])->dict[Tuple[int, int]]:
    """
        Reverse the conus to grace map to a grace to conus map.
        Parameters:
            conus_to_grace_map:     A 2D array the maps conus2 points to a single Grace tuple.
        Returns:
            A python dict map that maps a grace tuple (x,y) to a list of conus2 tuple (x,y) points.
    """
    grace_to_conus_map = {}
    for conus_tuple in conus_to_grace_map:
        nc_tuple = conus_to_grace_map.get(conus_tuple)
        conus_list = grace_to_conus_map.get(nc_tuple)
        conus_list = [] if conus_list is None else conus_list
        conus_list.append(conus_tuple)
        grace_to_conus_map[nc_tuple] = conus_list
    return grace_to_conus_map

def get_latlon_ranges(file_path: str) -> Tuple[list[float], list[float]]:
    """
    Read the NetCDF file and return the lat and lon coordinates ranges of a NetCDF file.
    Parameters:
        file_path:    The path name to a NASA GRACE NetCDF file containing lat,lon coordinates.
    Returns:
        A tuple (lat_values, lon_values) with the list of lat and lon values of the coordinates

    Note the lon coordinates need to be shifted by -180 degress to match conus2 lon coordinates.
    """

    ds = xr.open_dataset(file_path)
    lat_values = ds["lat"].values
    lon_values = ds["lon"].values
    lon_values = [v - 180 for v in lon_values]
    return (lat_values, lon_values)


def get_nc_coord(
    lat: float, lon: float, lat_values: list[float], lon_values: list[float]
) -> Tuple[int, int]:
    """
    Get the NetCDF coordinates associated with a given lat, lon value.
    Parameters:
        lat:            a Latitude in degrees.
        lon:            a Longitute in degress.
        lat_values:     A list of lat values from the NetCDF coordinate dimensions.
        lon_values:     A list of lon values from the NetCDF coordinate dimensions.
    Returns:
        A tuple (x, y) of the coordinate in the NetCDF files the corresponds to the lat, lon value.
    """
    x = get_range_index(lon, lon_values)
    y = get_range_index(lat, lat_values)
    return (x, y)


def get_range_index(value: float, value_range: list[float]) -> int:
    """
    Return the x coordinate cell of the lon values using the lon_values ranges from nc file.
    Parameters:
        value:  A float value to be found in the value range.
        value_range:    A list of float values in increasing sorted order.
    Returns:
        The index in the value_range of the specified value.
    Performs a binary search to find the value.
    """

    low_index = 0
    high_index = len(value_range) - 1
    while low_index < high_index:
        mid_index = int((high_index + low_index) / 2)
        mid_value = value_range[mid_index]
        if mid_index == low_index:
            return mid_index
        if value < mid_value:
            high_index = mid_index
        elif value > mid_value:
            low_index = mid_index
        else:
            return mid_index
    return None


def get_file_path() -> str:
    """
    The the path name of a file passed in the command line.
    """
    nc_file_path = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "/scratch/xl3138/GRCTellus.JPL.200204_202501.GLO.RL06.3M.MSCNv04CRI.nc"
    )
    if nc_file_path is None:
        print("Specify NetCDF path as argument.")
        return None
    if not os.path.exists(nc_file_path):
        print(f"File '{nc_file_path}' does not exist.")
        return None
    return nc_file_path


main()
