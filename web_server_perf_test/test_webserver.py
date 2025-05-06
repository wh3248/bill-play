"""
    Test the performance of the web server using a variety of options and write out the
    performance of making API calls using different values of those options and append
    the options and correspond performance statistics to a .csv file.

    Append results to file "log_webserver.csv" with columns:
        date                        
        server                      : one of gunicorn, k8_prod, k8_main (Web server called by this test)
        wy                          : water year of the start of hf_hydrodata read (change for cold run)
        scenario                    : Scenario of test (one of sleep, gridded-data)
        nparallel                   : number of parallel client calls
        sleep_time                  : number of seconds for web server to sleep to simulate load
        subgrid_size                : number of cells in gridded-data returned
        days                        : number of days of data returned in each call
        temporal_resolution         : temporal ressolution of gridded-data: one of daily, hourly, static
        server_workers              : number of gunicorn worker processes
        server_threads              : number of gunicorn threads per worker process
        gunicorn_type               : gunicorn "--gevent" or "--gthreads"
        total_duration              : total duration in seconds (after all parallel calls complete)
        min_call_duration           : min duration in seconds of a single call
        max_call_duration           : max duration in seconds of a single calls
        mean_call_duration          : mean duration in seconds of all paralle calls
        num_errors                   : number of parallel calls that timeout or failed
"""

import time
import requests
import concurrent.futures

def test_webserver(request):
    """Run performance test combinations specified on command line."""

    print()
    wy = int(request.config.getoption("--wy"))
    servers = request.config.getoption("--servers")
    scenarios = request.config.getoption("--scenarios")
    nparallels = request.config.getoption("--nparallel")
    sleep_times = request.config.getoption("--sleep_time")
    subgrid_size = 4
    days_options = "4"
    temporal_resolution="hours"

    test_number = 0
    options = {}
    options["subgrid_size"] = subgrid_size
    options["temporal_resolution"] = temporal_resolution
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
                        test_number = test_number + 1
                        _run_test(test_number, options)           

def _run_test(test_number, options):
    """Run test using the combination of options specified."""

    nparallel = int(options["nparallel"])
    sleep_time = int(options["sleep_time"])
    scenario = options["scenario"]
    base_url = _get_server_url(options)
    execute_results = [() for _ in range(nparallel)]
    if scenario == "sleep":
        url = f"{base_url}/wait?wait_time={sleep_time}"
    else:
        raise ValueError(f"Scenario '{scenario} is not supported.")
    print(f"Test {test_number} ({nparallel}) - {url}")
    _execute_parallel_calls(test_number, nparallel, url, execute_results)

def _execute_parallel_calls(test_number, nparallel, url, execute_results):
    total_start = time.time()
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = []
        for calln in range(0, nparallel):
            future = executor.submit(
                _execute_call,
                url,
                execute_results,
                test_number,
                calln)
            futures.append(future)
        _ = [future.result() for future in concurrent.futures.as_completed(futures)]
    total_duration = time.time() - total_start
    print(f"Total duration [test {test_number}] = {total_duration} seconds.")

def _execute_call(url, execute_results, test_number, calln):
    call_start = time.time()
    try:
        response = requests.get(url)
        if response.status_code == 200:
            successs_fail = "success"
        else:
            successs_fail = "fail"
    except Exception as e:
        success_fail = "fail"
    call_duration = time.time() - call_start
    print(f"Call {test_number}.{calln+1} duration = {call_duration}")


def _get_server_url(options):
    """Get the server url for the combinations option specified."""

    server = options.get("server")
    if server == "gunicorn":
        result = "http://localhost:5300/api"
    elif server == "k8_prod":
        result = "https://hydrogen.princeton.edu/api"
    elif server == "k8_main":
        result = "https://hydro-dev.princeton.edu/api"
    else:
        raise ValueError(f"The server option '{server}' is not supported.")
    return result


