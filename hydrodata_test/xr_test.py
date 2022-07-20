import sys
import os
import time
import xarray as xr

def load_files(water_year):
    test_number = 1
    start_time = time.time()
    metadata_list = os.path.abspath(f"/hydrodata/forcing/processed_data/CONUS1/NLDAS2/daily/./conus1_nldas_daily_{water_year}.pfmetadata")
    metadata_list = metadata_list.replace("{KEY1}", str(water_year))
    print(metadata_list)
    ds = xr.open_dataset(metadata_list)
    grid_bounds = [1075, 719, 1124, 739]
    xmin = grid_bounds[0]  # ideces of bounding box of domain
    xmax = grid_bounds[2]
    ymin = grid_bounds[1]
    ymax = grid_bounds[3]
    start_temp = f"{water_year}-05-24"
    end_temp = f"{water_year}-08-21"

    variables = ["APCP", "Temp_min", "Temp_max", "Temp_mean", "DSWR"]
    ds_temp = ds.sel(time=slice(str(start_temp), str(end_temp)))[variables]
    ds_temp = ds_temp.isel(x=slice(xmin, xmax), y=slice(ymin, ymax)).squeeze()
    ds_temp = ds_temp.load()
    n = 1

    duration = round(time.time() - start_time, 1)
    print(f"Loaded {n} PFB files in {duration} seconds for test #{test_number}.")

def main():
    if len(sys.argv) < 2:
        print()
        print("Usage: python hydrodata_test <year>")
        print("   where <year> is between 2003 - 2006")
        print("   for example, python xr_test 2003")
        sys.exit(0)
    water_year = sys.argv[1]
    load_files(int(water_year))

main()
