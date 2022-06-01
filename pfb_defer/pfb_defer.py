import os
import time
import dask

from parflow.tools.io import read_pfb, write_pfb
from hydrogen_subsetter.hydrogen_subsetter import HydrogenSubSetter


def subset_file(file_dir, file_name, grid_bounds):
    subsetter = HydrogenSubSetter()
    path = f"{file_dir}/{file_name}"
    out_path = f"/home/wh3248/tmp/{file_name}"
    if not os.path.exists(path):
        return {"status": "fail", "message": f"File {path} does not exist."}
    try:
        start_time = time.time()
        data = read_pfb(path)
        small_data = subsetter.subset_np_array(data, grid_bounds=grid_bounds)
        read_duration = time.time() - start_time
        write_pfb(out_path, small_data)
        duration = time.time() - start_time
        message = f"Process '{file_name}' in {duration} seconds read in {read_duration}."

        return {"status": "success", "message" : message}
    except Exception as e:
        return {"status": "fail", "message": str(e)}

def collect_status(status_list):
    results = []
    for status in status_list:
        if status.get("status", None) != "success":
            results.append(status.get("message", "No message"))
        else:
            message = status.get("message", None)
            if message:
                results.append(message)
    return results

def run_parallel_job():

    bounds = [
        -87.91134900070706,
        41.70037385521472,
        -87.52726577959893,
        42.346374776339125,
    ]
    subsetter = HydrogenSubSetter()
    subsetter.set_lat_lon_bounds(bounds, conus="conus2")
    grid_bounds = subsetter.get_grid_bounds()

    start = time.time()
    p_subset_file = dask.delayed(subset_file)
    p_collect_status = dask.delayed(collect_status)
    status = []
    input_dir = "/hydrodata/Forcing/processed_data/CONUS2/NLDAS3/WY2006"
    n = 0
    for f in os.listdir(input_dir):
        if "Temp" in f:
            status.append(p_subset_file(input_dir, f, grid_bounds))
            n = n + 1
        if n >= 20:
            break

    collected_status = p_collect_status(status).compute(num_workers=6)
    print(collected_status)
    duration = time.time() - start
    print(f"Ran parallel job in {duration} seconds.")

run_parallel_job()
