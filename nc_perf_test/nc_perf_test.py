import sys
import os
import time
import parflow as pf
from parflow.tools.io import read_pfb, write_pfb
import numpy as np
import xarray as xr

OUT_DIR = "/hydrodata/temp/file_performance_testing/pfb_test8"

def create_test_data(output_dir):
    """Create test data in output_dir with 60 PRB files for 8 features and one features.nc file"""

    # Read pressure PFB files from an input directory
    in_feature = "press"
    input_dir = "/hydrodata/PFCLM/CONUS1_baseline/simulations/2003/raw_outputs/pressure"

    # Subset the files to size sg_nx,sg_ny
    sg_nx = 500
    sg_ny = 500
    sg_nz = 5
    sg_x = 150
    sg_y = 150
    sg_z = 0

    out_time_steps = 60

    # Create copy of subset PFB files for each output feature
    out_features = ["Temp", "APCP", "Press", "VGRD", "UGRD", "DSWR", "DLWR", "SPFH"]
    n = 0
    pfb_data = None
    variable_shape = (out_time_steps, sg_nx, sg_ny, sg_nz)
    nc_array = np.zeros(variable_shape, dtype=float)
    sum_s = 0
    for f in os.listdir(input_dir):
        if in_feature in f and not "dist" in f:
            if n >= 0:
                print(n)
                # Read PFB file
                input_path = f"{input_dir}/{f}"
                print(input_path)
                pfb_data = read_pfb(input_path)

                # Subset file to subgrid
                pfb_subset_data = pfb_data[:, sg_y:sg_y+sg_ny, sg_x:sg_x+sg_nx]

                # Reshape numpy array from z,y,z to x, y z into a new nc_array to be used for NC file
                data = np.moveaxis(pfb_subset_data, 1, 2)
                data = np.moveaxis(pfb_subset_data, 0, -1)
                nc_array[n, :, :, :] = data
                print(pfb_subset_data.shape)
                print(data.shape)

                # Write PFB files for each feature for this one timestep of n
                for out_feature in out_features:
                    outfile_name = f"{output_dir}/{out_feature}_{f}"
                    write_pfb(outfile_name, pfb_subset_data, p=1, q=1, r=1, dist=False)
            n = n + 1
            if n >= out_time_steps:
                # Only read pfb files for the number of timesteps
                break

    # add a copy of the nc_array for each output variables into the xarray data set
    ds = xr.Dataset()
    for out_feature in out_features:
        nc_array_copy = np.copy(nc_array)
        ds[out_feature] = (["time", "x", "y", "z"], nc_array_copy)
        s = np.sum(nc_array_copy)
        sum_s = sum_s + s
    
    print(f"Sum of values for 8 features from nc_array is {sum_s}")
    # Write out the xarray dataset as one .nc file
    outfile_name = f"{output_dir}/features.nc"
    ds.to_netcdf(outfile_name)
    print(f"Created {outfile_name}")
    # Sum of all values added from PFB Files in generation is 3393428073.428895

def read_nc_file(output_dir):
    start_time = time.time()
    outfile_name = f"{output_dir}/features.nc"
    ds = xr.open_dataset(outfile_name)
    s = 0
    sum_s = 0
    out_features = ["Temp", "APCP", "Press", "VGRD", "UGRD", "DSWR", "DLWR", "SPFH"]
    for feature in out_features:
        data = ds[feature]
        s = data.to_numpy().sum()
        sum_s = sum_s + s
    duration = time.time() - start_time
    print(f"Read {outfile_name} in {duration} seconds total sum = {sum_s} of 8 values {s} each")
    # 2.0 seconds for 8 features (Hot) sum = 3393428073.428895
    # 2.2 seconds for 8 features (Cold) sum = 3393428073.428895
    # 

def read_pfb_files(input_dir):
    out_features = ["Temp", "APCP", "Press", "VGRD", "UGRD", "DSWR", "DLWR", "SPFH"]
    s = 0
    sum_s = 0
    start_time = time.time()
    for feature in out_features:
        file_names = []
        for f in os.listdir(input_dir):
            if feature in f and f.endswith(".pfb"):
                file_names.append(os.path.join(input_dir, f))
        data = pf.read_pfb_sequence(file_names)
        s = data.sum()
        n_files = len(file_names)
        sum_s = sum_s + s
    duration = time.time() - start_time
    print(f"Read 8 * 59 PFB files in {duration} seconds total sum = {sum_s} of 8 values {s} each")
    # 25.5- seconds for 8 features (COLD) sum = 3393428073.4289017
    # 10.5- seconds for 8 features (HOT)  sum = 3393428073.4289017

def run():
    if len(sys.argv) <= 1:
        print("Usage: nc_perf_test [create | pfb | nc]")
        sys.exit(0)
    if sys.argv[1] == "create":
        create_test_data(OUT_DIR)
    elif sys.argv[1] == 'nc':
        read_nc_file(OUT_DIR)
    elif sys.argv[1] == 'pfb':
        read_pfb_files(OUT_DIR)
    else:
        print("You must specify 'create', 'nc' or 'pfb' as command line argument")

run()

