import xarray as xr
import time
from concurrent.futures import ProcessPoolExecutor

def load_data(y, metadata_list):
    print(f"Started {y}")
    grid_bounds = [1075, 719, 1124, 739]
    xmin = grid_bounds[0]
    xmax = grid_bounds[2]
    ymin = grid_bounds[1]
    ymax = grid_bounds[3]
    ds = xr.open_dataset(metadata_list)
    start_temp = f"{y}-05-24"
    end_temp = f"{y}-08-21"
    ds_temp = ds.sel(time=slice(str(start_temp), str(end_temp)))
    ds_temp = ds_temp.isel(x=slice(xmin, xmax), y=slice(ymin, ymax)).squeeze()
    print(f"Load {y}")
    ds_temp.load()
    print(f"finished {y}")
    return "good"

def main():
    result_list = []
    executor = ProcessPoolExecutor(max_workers=4)
    start_time = time.time()
    for y in ['2003', '2004', '2005', '2006']:
        metadata_list = f"/hydrodata/forcing/processed_data/CONUS1/NLDAS2/daily/./conus1_nldas_daily_{y}.pfmetadata"
        #load_data(y, metadata_list)
        result_list.append(executor.submit(load_data, y, metadata_list))
    for r in result_list:
        print(r.result())
    duration = round(time.time() - start_time, 2)
    print(f"Duration {duration} sec")
main()
