from dask.distributed import dask, Client as DaskClient
import time
import dask

DASK_CLIENT = None

def get_dask_client():
    global DASK_CLIENT
    if DASK_CLIENT == None:
        DASK_CLIENT = DaskClient(n_workers=6)
    return DASK_CLIENT

def first_task(arg):
    print("First task")
    time.sleep(1)
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
    time.sleep(1)
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

if __name__ == "__main__":
    get_dask_client()
    run_job()
    print("All done")
