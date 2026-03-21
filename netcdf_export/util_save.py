import os
import time
import hf_hydrodata as hf
import xarray as xr
import netcdf_util
import xr_netcdf_util
import ndarray_util

def main():
    date_start = "2003-01-01"
    date_end = "2003-01-02"
    huc_id = "14010001"
    grid_point = [1000, 1000] 
    filter_options = {
        "dataset": "conus1_baseline_mod",
        "variable": "water_table_depth",
        "temporal_resolution": "daily",
        "date_start": date_start,
        "date_end": date_end,
        #"grid_bounds": [0, 0, 1000, 1000],
        "huc_id": huc_id
    }
    data = hf.get_gridded_data(filter_options)
    entry = hf.get_catalog_entry(filter_options)

    print()
    file_path = "xr_netcdf_util.nc"
    print(file_path)
    duration_start = time.time()
    xr_netcdf_util.generate_netcdf_file(data, entry, filter_options, file_path)
    duration = time.time() - duration_start
    file_size = os.path.getsize(file_path)
    print(f"{file_path} Bytes {file_size} Shape {data.shape} duration={duration}")

    print()
    file_path = "netcdf_util.nc"
    print(file_path)
    duration_start = time.time()
    netcdf_util.generate_netcdf_file(data, entry, filter_options, file_path)
    duration = time.time() - duration_start
    file_size = os.path.getsize(file_path)
    print(f"{file_path}    Bytes {file_size} Shape {data.shape} duration={duration}")

    print()
    file_path = "ndarray_util.nc"
    print(file_path)
    duration_start = time.time()
    ndarray_util.generate_ndarray_file(data, file_path)
    duration = time.time() - duration_start
    file_size = os.path.getsize(file_path)
    print(f"{file_path}   Bytes {file_size} Shape {data.shape} duration={duration}")
    print()

main()
