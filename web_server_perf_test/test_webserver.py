"""
    Test the performance of the web server using a variety of options and write out the
    performance of making API calls using different values of those options and append
    the options and correspond performance statistics to a .csv file.

    Append results to file "log_webserver.csv" with columns:
        date                        
        server                      : one of gunicorn, k8_prod, k8_main (Web server called by this test)
        wy                          : water year of the start of hf_hydrodata read (change for cold run)
        scenario                    : Scenario of test (one of sleep, gridded-data)
        parallel                    : number of parallel client calls
        sleep_time                  : number of seconds for web server to sleep to simulate load
        subgrid_size                : number of cells in gridded-data returned
        days                        : number of days of data returned in each call
        temporal_resolution         : temporal ressolution of gridded-data: one of daily, hourly, static
        server_workers              : number of gunicorn worker processes
        server_threads              : number of gunicorn threads per worker process
        gunicorn_type               : gunicorn type: one of gevent, gthreads, or blank (for default)
        total_duration              : total duration in seconds (after all parallel calls complete)
        min_call_duration           : min duration in seconds of a successful single calls
        max_call_duration           : max duration in seconds of a successful single calls
        mean_call_duration          : mean duration in seconds of all successful paralle calls
        num_errors:                 : number of calls with errors
        min_error_duration          : min duration in seconds for each error call 
        max_error_duration          : max duration in seconds for each error call
"""

import os
import time
import datetime
import math
import json
import requests
import io
import hf_hydrodata as hf
import concurrent.futures
import numpy as np
import xarray as xr

def test_webserver(request):
    """Run performance test combinations specified on command line."""

    print()
    wy = int(request.config.getoption("--wy"))
    servers = request.config.getoption("--server")
    scenarios = request.config.getoption("--scenario")
    nparallels = request.config.getoption("--parallel")
    sleep_times = request.config.getoption("--sleep_time")
    days_options = request.config.getoption("--days")
    grid_sizes = request.config.getoption("--grid_size")
    temporal_resolution="hourly"

    test_number = 0
    options = {}
    options["temporal_resolution"] = temporal_resolution
    options["gunicorn_settings"] = get_gunicorn_settings()
    options["wy"] = wy
    for scenario in scenarios.split(","):
        options["scenario"] = scenario
        for nparallel in nparallels.split(","):
            options["nparallel"] = nparallel
            for server in servers.split(","):
                options["server"] = server
                if scenario == "sleep":
                    for sleep_time in sleep_times.split(","):
                        options["sleep_time"] = sleep_time
                        if server == "gunicorn":
                            test_number = test_number + 1
                            _run_test(test_number, options)
                elif scenario == "gridded-data":
                    for days in days_options.split(","):
                        options["days"] = days
                        for grid_size in grid_sizes.split(","):
                            options["grid_size"] = grid_size
                            test_number = test_number + 1
                            _run_test(test_number, options)           

def _run_test(test_number, options):
    """Run test using the combination of options specified."""

    nparallel = int(options["nparallel"])
    scenario = options["scenario"]
    temporal_resolution = options["temporal_resolution"]
    server = options["server"]
    base_url = _get_server_url(server)
    execute_results = [None for _ in range(nparallel)]
    if scenario == "sleep":
        sleep_time = int(options["sleep_time"])
        url = f"{base_url}/wait?wait_time={sleep_time}"
    elif scenario == "gridded-data":
        days = int(options["days"])
        grid_size = int(options["grid_size"])
        wy = options["wy"]
        start_time = f"{wy}-01-1"
        start_time_date = datetime.datetime.strptime(start_time, "%Y-%m-%d")
        end_time = (start_time_date + datetime.timedelta(days=days)).strftime("%Y-%m-%d")
        grid_start = 1000
        grid_end = grid_start + int(math.sqrt(grid_size))
        grid_bounds = f"[{grid_start},{grid_start},{grid_end},{grid_end}]"
        url = f"{base_url}/gridded-data?dataset=CW3E"
        url = url + "&dataset_version=1.0"
        url = url + f"&temporal_resolution={temporal_resolution}"
        url = url + f"&variable=precipitation"
        url = url + f"&grid_bounds={grid_bounds}"
        url = url + f"&start_time={start_time}"
        url = url + f"&end_time={end_time}"
    else:
        raise ValueError(f"Scenario '{scenario} is not supported.")
    total_start = time.time()
    _execute_parallel_calls(test_number, nparallel, url, execute_results, options)
    total_duration = round(time.time() - total_start, 2)

    write_log(execute_results, test_number, total_duration,  options)

def _execute_parallel_calls(test_number, nparallel, url, execute_results, options):
    with concurrent.futures.ThreadPoolExecutor(max_workers=nparallel) as executor:
        futures = []
        for calln in range(0, nparallel):
            future = executor.submit(
                _execute_call,
                url,
                execute_results,
                test_number,
                calln,
                options)
            futures.append(future)
        _ = [future.result() for future in concurrent.futures.as_completed(futures)]

def _execute_call(url, execute_results, test_number, calln, options):
    call_start = time.time()
    try:
        headers = None
        if options["server"] in ["k8_prod", "k8_main"]:
            headers = hf.data_model_access._get_api_headers()
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            success_fail = "success"
            if options["scenario"] == "gridded-data":
                print_result_shape(response)
        else:
            success_fail = "fail"
            print(response.content)
    except Exception as e:
        success_fail = "fail"
        print(e)
    call_duration = time.time() - call_start
    execute_results[calln] = (call_duration, success_fail)

def write_log(execute_results, test_number, total_duration, options):
    """Append an entry to the log file with performance statistics for test #test_number."""
    
    nparallel = int(options.get("nparallel"))
    scenario = options.get("scenario")
    server = options.get("server")
    num_errors =len([1 for item in execute_results if item[1] != "success"])
    min_error_call = 0
    max_error_call = 0
    min_call = 0
    max_call = 0
    mean_call = 0
    if num_errors < nparallel:
        min_call = round(min([item[0] for item in execute_results if item[1] == "success"]),2)
        max_call = round(max([item[0] for item in execute_results if item[1] == "success"]), 2)
        mean_call = round(sum([item[0] for item in execute_results if item[1] == "success"])/len([1 for item in execute_results if item[1] == "success"]), 2)
    if num_errors > 0:
        min_error_call = round(min([item[0] for item in execute_results if item[1] != "success"]),2)
        max_error_call = round(max([item[0] for item in execute_results if item[1] != "success"]),2)
    print(f"Test {test_number} {scenario} ({nparallel}) {server} duration = {total_duration} seconds. Min={min_call} Max={max_call} Mean={mean_call} Errors={num_errors} MinError={min_error_call} MaxError={max_error_call}")
    log_file_path = "./log_web_server.csv"
    column_names = ["date", "server", "wy", "scenario", "parallel", "sleep_time", "subgrid_size", "days", "temporal_resolution", "server_worker", "server_thread", "gunicorn_type", "total_duration", "min_call_duration", "max_call_duration", "mean_call_duration", "num_errors", "min_error_duration", "max_error_duration"]
    if not os.path.exists(log_file_path):
        with open(log_file_path, "w+") as fp:
            line = ",".join(column_names)
            fp.write(f"{line}\n")
    server_workers = str(options["gunicorn_settings"][0])
    server_threads = str(options["gunicorn_settings"][1])
    gunicorn_type = str(options["gunicorn_settings"][2])
    if server == "k8_prod":
        server_workers = "15"
        server_threads = "1"
    if server == "k3_main":
        server_workers = "3"
        server_threads = "1"
    with open(log_file_path, "a") as fp:
        line = ""
        line = line + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = line + "," + options["server"]
        line = line + "," + str(options["wy"])
        line = line + "," + str(options["scenario"])
        line = line + "," + str(options["nparallel"])
        line = line + "," + str(options.get("sleep_time", "1"))
        line = line + "," + str(options.get("grid_size", "8"))
        line = line + "," + str(options.get("days", "1"))
        line = line + "," + str(options.get("temporal_resolution", ""))
        line = line + "," + server_workers
        line = line + "," + server_threads
        line = line + "," + gunicorn_type
        line = line + "," + str(total_duration)
        line = line + "," + str(min_call)
        line = line + "," + str(max_call)
        line = line + "," + str(mean_call)
        line = line + "," + str(num_errors)
        line = line + "," + str(min_error_call)
        line = line + "," + str(max_error_call)
        fp.write(f"{line}\n")
        
def print_result_shape(response):
    """This is for debugging to print the gridded data response."""

    return
    file_obj = io.BytesIO(response.content)
    ds = xr.open_dataset(file_obj)
    print(ds)

def _get_server_url(server):
    """Get the server url for the combinations option specified."""

    if server == "gunicorn":
        result = "http://localhost:5300/api"
    elif server == "k8_prod":
        result = "https://hydrogen.princeton.edu/api"
    elif server == "k8_main":
        result = "https://hydro-dev.princeton.edu/api"
    else:
        raise ValueError(f"The server option '{server}' is not supported.")
    return result

def get_gunicorn_settings():
    base_url = _get_server_url("gunicorn")

    url = f"{base_url}/wait"
    threads = 1
    workers = 1
    gtype = "gthreads"
    try:
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            content = response.content.decode("utf-8")
            content_json = json.loads(content)
            threads = content_json.get("threads") if content_json.get("threads") else threads
            workers = content_json.get("workers") if content_json.get("workers") else workers
            gtype = content_json.get("gtype") if content_json.get("gtype") else gtype
    except Exception as e:
        print(f"Unable to connect to guncorn server: '{url}'")
    return (workers, threads, gtype)
    

