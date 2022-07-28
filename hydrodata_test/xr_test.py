import sys
import os
import time
import xarray as xr

def load_files(metadata_file, water_year):
    start_time = time.time()
    metadatafile = os.path.abspath(metadata_file)
    ds = xr.open_dataset(metadata_file)
    grid_bounds = [1075, 719, 1124, 739]
    xmin = grid_bounds[0] 
    xmax = grid_bounds[2]
    ymin = grid_bounds[1]
    ymax = grid_bounds[3]
    start_temp = f"{water_year}-05-24"
    end_temp = f"{water_year}-08-21"

    variables = ["APCP", "Temp_min", "Temp_max", "Temp_mean", "DSWR"]
    ds_temp = ds.sel(time=slice(str(start_temp), str(end_temp)))[variables]
    ds_temp = ds_temp.isel(x=slice(xmin, xmax), y=slice(ymin, ymax)).squeeze()
    ds_temp = ds_temp.load()

    duration = round(time.time() - start_time, 1)
    print(f"Loaded PFB files in {duration} seconds.")

def main():
    print("Start")
    print(len(sys.argv))
    if len(sys.argv) < 3:
        print()
        print("Usage: python hydrodata_test <year> [hydrodata | scratch]")
        print("   where <year> is between 2003 - 2006")
        print("   for example, python xr_test 2003")
        sys.exit(0)
    water_year = sys.argv[1]
    print(water_year)
    file_source = sys.argv[2] if len(sys.argv) > 2 else "hydrodata"
    if file_source == "hydrodata":
        metadata_file = f"/hydrodata/forcing/processed_data/CONUS1/NLDAS2/daily/./conus1_nldas_daily_{water_year}.pfmetadata"
    elif file_source == "scratch":
        metadata_file = f"/scratch/wh3248/forcing/conus1_nldas_daily_{water_year}.pfmetadata"
    else:
        print("Second argument must be hydrodata or scratch")
        sys.exit(0)
    print(metadata_file)
    load_files(metadata_file, int(water_year))

main()
