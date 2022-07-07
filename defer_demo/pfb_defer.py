"""Demo program to read and write PFB files in parallel with dask deferred."""
import os
import time
import dask

from parflow.tools.io import read_pfb, write_pfb


def copy_file(file_dir, file_name):
    """Copy a single file PFB file from a directory and write a different file with a different P,Q,R"""

    # Create the path names for input and output files
    path = f"{file_dir}/{file_name}"
    out_path = f"/hydrodata/temp/defer_test2/{file_name}"

    if not os.path.exists(path):
        return {"status": "fail", "message": f"File {path} does not exist."}
    try:
        start_time = time.time()
        data = read_pfb(path)
        read_duration = time.time() - start_time
        write_pfb(out_path, data, dist=False, p=12, q=12, r=24)
        duration = time.time() - start_time
        message = f"Process '{file_name}' in {duration} seconds read in {read_duration}."

        return {"status": "success", "message" : message}
    except Exception as e:
        return {"status": "fail", "message": str(e)}

def collect_status(status_list):
    """Collect the status return results from a list of parallel jobs."""

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
    """Run a collection of calls to copy_file in parallel."""

    start = time.time()
    p_copy_file = dask.delayed(copy_file)
    p_collect_status = dask.delayed(collect_status)
    status = []
    input_dir = "/hydrodata/forcing/processed_data/CONUS2/NLDAS3/WY2006"
    #input_dir = "/hydrodata/temp/defer_test2/"
    n = 0
    for f in os.listdir(input_dir):
        if "Temp" in f:
            status.append(p_copy_file(input_dir, f))
            n = n + 1
        if n >= 2:
            break

    collected_status = p_collect_status(status).compute(num_workers=6)
    duration = time.time() - start
    print("\n".join(collected_status))
    print(f"Ran parallel job in {duration} seconds.")

"""Main routine call."""
run_parallel_job()
