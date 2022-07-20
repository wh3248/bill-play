from dask.distributed import dask, Client as DaskClient
import time
import dask
from threading import Thread

DASK_CLIENT = None

def get_dask_client():
    global DASK_CLIENT
    if DASK_CLIENT == None:
        DASK_CLIENT = DaskClient(n_workers=6)
    return DASK_CLIENT

def first_task(arg):
    print("First task")
    result = arg
    return result

def collect_run(scenario_id, year):
    print(f"Collect run {year} for scenario {scenario_id}")

def collect_runs(scenario_id):
    print(f"Collect runs for {scenario_id}")
    dask_results = []
    for y in ['2003', '2004', '2005']:
        dask_results.append(dask.delayed(collect_run)(scenario_id, y))
    combine = dask.delayed(lambda x:x)(dask_results)
    combine.compute()

def scenario_task(scenario_id):
    print(f"scenaro task {scenario_id}")
    collect_runs(scenario_id)
    print(f"scenaro task done {scenario_id}")

def run_job():
    client = get_dask_client()
    dask_first = client.submit(first_task, 1)
    client.gather(dask_first)
    scenario_list = []
    scenario_list.append(client.submit(scenario_task, "test_hot"))
    scenario_list.append(client.submit(scenario_task, "test_average"))
    client.gather(scenario_list)
    print("Run_job finished")

def run_group():
    client = get_dask_client()
    group_list = []
    group_list.append(client.submit(run_job))
    group_list.append(client.submit(run_job))

def main_delayed():
    dask_results = []
    dask_results.append(dask.delayed(run_job))
    dask.delayed(lambda x:x)(dask_results).compute()

def main_thread():
    threads = []
    for i in range(0, 2):
        thread = Thread(target=run_job)
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    
if __name__ == "__main__":
    #get_dask_client()
    main_thread()
    print("All done")
