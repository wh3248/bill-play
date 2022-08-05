import sys
import os
import time
import xarray as xr

def load_files(metadata_file, water_year, test_number):
    start_time = time.time()
    metadatafile = os.path.abspath(metadata_file)
    ds = xr.open_dataset(metadata_file)
    xmin = int(test_number/5) * 400
    ymin = int(test_number % 5) * 400 
    xmax = xmin + 50
    ymax = ymin + 50
    grid_bounds = [xmin, ymin, xmax, ymax]
    print(grid_bounds)
    start_temp = f"{water_year}-05-24"
    end_temp = f"{water_year}-08-21"

    variables = ["APCP", "Temp_min", "Temp_max", "Temp_mean", "DSWR"]
    ds_temp = ds.sel(time=slice(str(start_temp), str(end_temp)))[variables]
    ds_temp = ds_temp.isel(x=slice(xmin, xmax), y=slice(ymin, ymax)).squeeze()
    ds_temp = ds_temp.load()

    duration = round(time.time() - start_time, 1)
    print(f"Loaded PFB files in {duration} seconds.")

def main():
    if len(sys.argv) < 3:
        print()
        print("Usage: python hydrodata_test <year> <test_number> <filetype>]")
        print("")
        print("   where <year> is between 2003 - 2006")
        print("      and <test_number> is a number between 1-25")
        print("      and <filetype> is hydrodata or scratch")
        print("   for example, python xr_test.py  2003 1 hydrodata")
        sys.exit(0)
    water_year = sys.argv[1]
    test_number = sys.argv[2] if len(sys.argv) > 2 else 1
    file_source = sys.argv[3] if len(sys.argv) > 3 else "hydrodata"
    if file_source == "hydrodata":
        metadata_file = f"/hydrodata/forcing/processed_data/CONUS1/NLDAS2/daily/./conus1_nldas_daily_{water_year}.pfmetadata"
    elif file_source == "scratch":
        metadata_file = f"/scratch/wh3248/forcing/conus1_nldas_daily_{water_year}.pfmetadata"
    else:
        print("Third argument must be hydrodata or scratch")
        sys.exit(0)
    try:
        test_number = int(test_number)- 1
    except Exception:
        print("The <test_number> must a number")
        sys.exit(0)
    if test_number < 0 or test_number > 25:
        print("The <test_number> must be between 1- 25")
        sys.exit(0)
    print(metadata_file)
    load_files(metadata_file, int(water_year), test_number)

main()
