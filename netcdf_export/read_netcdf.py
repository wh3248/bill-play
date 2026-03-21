import time
import xarray as xr
import numpy as np

def main():
    files = ["xr_netcdf_util.nc", "netcdf_util.nc"]
    for path in files:
        print(path)
        try:
            ds = xr.open_dataset(path)
            print(ds)
            print("CRS TYPE", ds["crs"].dtype)
            print("CONVENTIONS", ds.attrs["Conventions"])
            print("VARIABLE", ds["water_table_depth"].attrs)
            print("UNIT X DIFFS", np.diff(ds.x[:5].values))
            print("UNIT Y DIFFS", np.diff(ds.y[:5].values))
            print()
            print("CRS ATTRS", ds["crs"].attrs)
            print("VALUE 0,0 =", ds["water_table_depth"].values[0,0,0])
        except Exception as e:
            print(f"Unable to read {path}")
        print()
main()
